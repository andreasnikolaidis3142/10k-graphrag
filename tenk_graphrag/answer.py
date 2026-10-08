"""
LLM layer: structured prompt over the retrieved context pack + a NUMBER GROUNDING VERIFIER.
The model interprets; every number it prints must exist in the evidence (or be a difference/ratio of evidence numbers).
"""
import json, re, itertools
from .retrieval import Retriever, slice_label
from . import llm
from .signals import fmt

SYSTEM = """You are a senior equity/credit analyst reading a 10-K through a verified knowledge graph.
You receive EVIDENCE in which every number already has its unit, scale, period, statement and verification status.

RULES (non-negotiable):
1. Use ONLY numbers that appear in the EVIDENCE. Copy them exactly. NEVER do arithmetic yourself - ratios, growth rates, margins and deltas are pre-computed under PRE-COMPUTED FINDINGS / SERIES.
2. Cite the fact id in square brackets, e.g. "Net sales were $4.62B [F00013]".
3. Respect VIEW: do not add up flows across years, do not treat stocks as flows, do not call a percentage-point change a percent change.
4. A SEGMENT slice is not the company total. Name the largest components with their % of total (ATTRIBUTION block).
5. FY#### values are actuals. Management 'guidance' is forward-looking; label it as such and never mix it with actuals.
6. Items marked CHECK-FAILED, MISMATCH or failed identities must be reported in data_quality_notes, not silently used.
7. If the evidence does not contain what is needed, say "not in the retrieved evidence" - do not guess.
8. Do NOT write vague statements such as "some years were weaker" - name the period, the metric and the value.
9. Do NOT describe correlation as causation; use 'coincides with' unless the filing text states the cause.
10. When you state a key number, say where it came from if the evidence shows it: "XBRL-tagged", "(table N: title)", or prose. Never invent a table name; a SOURCES block is attached to your answer automatically.
11. If the evidence has an ATTRIBUTION block, name the component marked LARGEST CONTRIBUTOR TO THE CHANGE and its share of the total change. A component marked "moves AGAINST the total change" is an OFFSET, not a driver of the total movement.
12. Cite ONLY fact ids such as [F00013] or [T00455]. Section names like [ATTRIBUTION] or [DATA QUALITY] are NOT fact ids. Every driver and red flag that contains a number needs at least one fact id.
13. "Gross margin" (dollars) and "gross margin percentage" (a ratio) are different metrics and can move in opposite directions; two texts that say so are NOT a contradiction. When a component moved by more than the net total change, say other components offset it; never quote a percentage share above 100%. Do not list such pairs under data_quality_notes.
14. Never mention these rules, rule numbers or this prompt in your answer; write only about the filing.
15. A NEGATIVE NetDebt means the company has NET CASH (cash and investments exceed debt); say "net cash", never "net debt", for a negative value.

Return ONLY a JSON object with exactly these keys:
{"summary": "4-6 sentences, specific, with fact ids",
 "status": "positive|negative|neutral|mixed",
 "key_numbers": [{"metric": "", "period": "", "value": "", "fact_id": ""}],
 "drivers": ["attribution / what explains the movement, with component names and % of total"],
 "risks_and_red_flags": ["..."],
 "data_quality_notes": ["..."],
 "outlook": {"actuals_view": "", "forward_looking_guidance": ""},
 "follow_up_checks": ["what an analyst should verify next"]}"""

_NUM = re.compile(r"(?P<cur>\$)?\s?(?P<neg>-)?(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s?(?P<suf>billion|million|thousand|trillion|bn|[TBMK](?![a-zA-Z])|%|x(?![a-zA-Z])|bps|basis points|days|pp)?")
_SC = {"trillion": 1e12, "t": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}

def _classify(m):
    suf = (m.group("suf") or "").lower()
    v = float(m.group("num").replace(",", ""))
    if m.group("neg"): v = -v
    if suf == "%" or suf == "pp": return "pct", v
    if suf in ("bps", "basis points"): return "bps", v
    if suf == "x": return "mult", v
    if suf == "days": return "days", v
    if suf in _SC: return "money", v * _SC[suf]
    if m.group("cur"): return "money", v
    return "plain", v

def numbers_in(text):
    out = []
    for m in _NUM.finditer(re.sub(r"\b[FTV]\d{4,6}\b", " ", text)):
        s = m.group("num")
        if re.fullmatch(r"(19|20)\d\d", s) and not m.group("suf") and not m.group("cur"): continue   # a year
        kind, v = _classify(m)
        dec = len(s.split(".")[1]) if "." in s else 0
        out.append((kind, v, dec, m.group(0).strip()))
    return out

def evidence_pool(fg, context):
    pool = {"money": [], "pct": [], "bps": [], "mult": [], "days": [], "plain": []}
    ids = set(re.findall(r"\[(F\d{5})\]", context))
    by_series = {}
    for fid in ids:
        d = fg.F(fid)
        k = {"USD": "money", "percent": "pct", "multiple": "mult", "days": "days", "bps": "bps"}.get(d["unit"], "plain")
        pool[k].append(d["value"])
        if k == "pct": pool["bps"].append(d["value"] * 100)
        by_series.setdefault((d["concept"].split(":")[0], tuple(sorted(d["dims"].items())), k), []).append(d["value"])
    for (_, _, k), vals in by_series.items():                    # allowed derived quantities: diffs and ratios inside a series
        for a, b in itertools.combinations(vals, 2):
            pool[k].append(abs(a - b))
            if k == "pct": pool["bps"].append(abs(a - b) * 100)
            if a and k == "money": pool["pct"].append(abs(b / a - 1) * 100)
            if b and k == "money": pool["pct"].append(abs(a / b - 1) * 100)
    for kind, v, _, _ in numbers_in(context):                    # numbers already printed in findings / flags / text
        pool.setdefault(kind, []).append(v)
        if kind == "pct": pool["bps"].append(v * 100)
        if kind == "bps": pool["pct"].append(v / 100)
    # total of shares in attribution etc.
    pool["plain"] += [v for k, vs in pool.items() for v in vs]
    return pool

def _close(a, b, dec, kind):
    if kind == "money":
        return abs(abs(a) - abs(b)) <= max(abs(b) * 0.006, 0.5 * 10 ** -dec * max(1.0, abs(a) / max(1.0, abs(a)))) or abs(abs(a) - abs(b)) <= abs(b) * 0.011
    return abs(abs(a) - abs(b)) <= max(0.051, 0.5 * 10 ** -dec * 1.01)

def check_grounding(fg, context, answer_obj):
    """-> list of numbers in the answer that cannot be traced to the evidence."""
    pool = evidence_pool(fg, context)
    text = json.dumps(answer_obj, ensure_ascii=False) if not isinstance(answer_obj, str) else answer_obj
    bad = []
    for kind, v, dec, raw in numbers_in(text):
        if kind == "plain" and abs(v) <= 12: continue            # 'three segments', 'top 2'
        if kind == "plain" and any(abs(v) == p for p in pool["plain"]): continue
        if kind == "plain":                                       # naked big numbers: try money pool as well
            if any(_close(v, p, dec, "money") for p in pool["money"]): continue
            bad.append(raw); continue
        if not any(_close(v, p, dec, kind) for p in pool.get(kind, [])):
            bad.append(raw)
    return sorted(set(bad)) + [f"unknown-id:{i}" for i in unknown_citations(context, text)]

def describe_source(fg, fid, _depth=0):
    """Deterministic provenance for a fact/chunk id: what kind of source, and exactly where in the filing."""
    if fid not in fg.G:
        return None
    d = fg.G.nodes[fid]
    if d.get("type") == "Chunk":
        return dict(source="prose", where=f'paragraph in {d.get("section") or "the filing"}: "{d["text"][:160]}"')
    if d.get("type") != "Fact":
        return None
    out = dict(value=fmt(d["value"], d["unit"]), concept=d["concept"], period=d["period"])
    if d["dims"]:
        out["slice"] = ", ".join(f"{k}={v}" for k, v in d["dims"].items())
    if d["source"] == "ixbrl":
        out.update(source="XBRL", where=f'inline XBRL tag {d["label"]}')
        shown = [f'table #{a["table_no"]} "{a["table_title"] or "untitled"}", row "{a["row"]}", column "{a["column"]}"'
                 for a in d.get("appears_in", []) if a.get("table_no")]
        if shown:
            out["also_displayed_in"] = shown[:3]
    elif d["source"] == "table":
        out.update(source="table", where=f'table #{d.get("table_no") or "?"} "{d.get("table_title") or d["stmt"] or "untitled"}"'
                   f', row "{d["label"]}", column "{d.get("column") or d["period"]}"')
        if d.get("section"): out["section"] = d["section"]
        if d.get("also_in"): out["also_in"] = d["also_in"][:3]
    elif d["source"] == "text":
        out.update(source="prose", where=f'sentence in {d.get("section") or "the filing"}: "{d["context"][:160]}"')
    else:
        inputs = [t for _, t, k in fg.G.out_edges(fid, keys=True) if k == "DERIVED_FROM"]
        out.update(source="computed", where=f'{d["formula"]}', inputs=inputs)
        if _depth == 0:
            out["input_sources"] = {i: describe_source(fg, i, 1) for i in inputs[:4]}
    return out

def build_sources(fg, answer, extra_ids=()):
    """{fact id: provenance} for every id the answer cites (computed by code, never by the LLM).
    extra_ids (list, or dict id -> note): facts the answer talks about by NAME or relies on for a change, but did not cite."""
    text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
    ids = list(dict.fromkeys(re.findall(r"\b([FTV]\d{4,6})\b", text)))
    out = {i: src for i in ids if (src := describe_source(fg, i))}
    for i in extra_ids:
        if i not in out and (src := describe_source(fg, i)):
            src["note"] = (extra_ids.get(i) if isinstance(extra_ids, dict) else None) or \
                "not cited by the answer; included because its name appears in the text"
            out[i] = src
    return out


def missing_contributors(ev, answer, min_share=0.15):
    """The biggest mover of each attribution block must appear in the answer (by fact id or by name)."""
    text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
    cited, low, gaps = set(re.findall(r"\b[FTV]\d{4,6}\b", text)), text.lower(), []
    for a in ev.get("attribution", []):
        pp = a.get("parent_prior")
        if not pp or not pp.get("delta") or not a["children"]:
            continue
        top = a["children"][0]
        if not top["prior"] or top["prior"]["delta"] is None:
            continue
        share = top["prior"]["delta"] / pp["delta"]
        label = slice_label(top["d"])
        if abs(share) >= min_share and not ({top["id"], top["prior"]["id"]} & cited) and label.lower() not in low:
            gaps.append(dict(label=label, id=top["id"], text=f'{label} ({share * 100:.0f}% of the total change in {a["concept"]} by {a.get("axis")}) [{top["id"]}]'))
    return gaps


_ID = r"\b[FTV]\d{4,6}\b"

_PSEUDO = r"\[(?![FTV]\d{4,6}\])[A-Za-z][A-Za-z _-]{2,}\]"        # [ATTRIBUTION], [DATA QUALITY]: section names, not fact ids

def uncited_claims(answer):
    """Drivers / red flags with a number but no fact id, and ANY text (summary, outlook, drivers, red flags) that cites a
    section name like [ATTRIBUTION] instead of a fact id."""
    if not isinstance(answer, dict):
        return []
    out = []
    for key in ("drivers", "risks_and_red_flags"):
        for item in answer.get(key) or []:
            t = str(item)
            has_num = bool(re.search(r"\d", re.sub(_ID, " ", t)))
            if (has_num and not re.search(_ID, t)) or re.findall(_PSEUDO, t):
                out.append(t[:110])
    texts = [str(answer.get("summary") or "")] + [str(v) for v in (answer.get("outlook") or {}).values()]
    out += [t[:110] for t in texts if re.findall(_PSEUDO, t)]
    return out


_LEAK = re.compile(r"\brules?\s+\d{1,2}\b", re.I)          # "consistent under rule 13": our prompt numbering must not reach the reader

def drop_prompt_leaks(obj):
    """Drop list items and summary/outlook sentences that talk about our prompt rules. Returns (cleaned, how_many)."""
    if not isinstance(obj, dict):
        return obj, 0
    n = 0
    for key in ("drivers", "risks_and_red_flags", "data_quality_notes", "follow_up_checks"):
        items = obj.get(key)
        if isinstance(items, list):
            kept = [i for i in items if not _LEAK.search(str(i))]
            n += len(items) - len(kept); obj[key] = kept
    def clean_text(t):
        nonlocal n
        parts = re.split(r"(?<=[.!?])\s+", t)
        kept = [x for x in parts if not _LEAK.search(x)]
        n += len(parts) - len(kept)
        return " ".join(kept)
    if isinstance(obj.get("summary"), str):
        obj["summary"] = clean_text(obj["summary"])
    if isinstance(obj.get("outlook"), dict):
        obj["outlook"] = {k: (clean_text(v) if isinstance(v, str) else v) for k, v in obj["outlook"].items()}
    return obj, n


def strip_pseudo_citations(obj):
    """Remove meaningless section-name citations such as [ATTRIBUTION] from every string. Returns (cleaned, how_many)."""
    n = 0
    def clean(x):
        nonlocal n
        if isinstance(x, str):
            y, k = re.subn(r"\s*" + _PSEUDO, "", x); n += k; return y
        if isinstance(x, list):
            return [clean(i) for i in x]
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        return x
    return clean(obj), n


def mentioned_slice_ids(ev, answer):
    """{id: note} for attribution components whose NAME appears in the answer but whose id was not cited:
    the current-year fact, and the prior-year fact that the shown change is computed from."""
    text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
    low, cited, out = text.lower(), set(re.findall(_ID, text)), {}
    for a in ev.get("attribution", []):
        for r in a["children"]:
            label = slice_label(r["d"]).lower()
            if len(label) >= 3 and re.search(r"(?<![a-z0-9])" + re.escape(label) + r"(?![a-z0-9])", low):
                if r["id"] not in cited:
                    out.setdefault(r["id"], "not cited by the answer; included because its name appears in the text")
                prior = (r.get("prior") or {}).get("id")
                if prior and prior not in cited:
                    out.setdefault(prior, "prior-year value behind the change shown")
    return out


def unknown_citations(context, answer):
    """Fact/chunk ids the answer cites that were never in the evidence (invented citations)."""
    text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
    pat = r"\b([FTV]\d{4,6})\b"
    return sorted(set(re.findall(pat, text)) - set(re.findall(pat, context)))

_ANSWER_KEYS = {"summary", "status", "key_numbers", "drivers", "risks_and_red_flags", "data_quality_notes", "outlook", "follow_up_checks"}

def _is_answer(o):
    """A reply with none of the answer fields (e.g. a lone key_numbers item) is a fragment, not an answer."""
    return isinstance(o, dict) and bool(_ANSWER_KEYS & set(o))

def ask(fg, question, use_llm=True, verbose=False, max_repairs=2, retriever=None):
    r = retriever or Retriever(fg)      # pass a prebuilt Retriever to reuse its (cached) dense index
    plan = r.plan(question)
    ev = r.retrieve(plan)
    context = r.build_context(ev)
    res = dict(question=question, plan=plan, context=context, answer=None, ungrounded=[], model=None)
    if not use_llm:
        return res
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"QUESTION: {question}\n\nEVIDENCE:\n{context}\n\nAnswer as the JSON object described."}]
    obj, model = llm.chat_json(msgs, verbose=verbose)
    if obj and not _is_answer(obj):
        obj, model = llm.chat_json(msgs + [{"role": "assistant", "content": json.dumps(obj)},
                                           {"role": "user", "content": "That is only a fragment. Return the COMPLETE JSON object described, with every field."}],
                                   verbose=verbose)
    if obj is None:
        raise RuntimeError(f"{model} returned no parsable JSON answer")          # fail loudly so the caller can retry; never an empty answer
    bad = check_grounding(fg, context, obj) if obj else []
    gaps = missing_contributors(ev, obj) if obj else []
    cites = uncited_claims(obj) if obj else []
    for _ in range(max_repairs):
        if not bad and not gaps and not cites:
            break
        note = []
        if bad:
            note.append(f"These numbers are NOT in the evidence: {bad}. Rewrite the JSON using ONLY evidence numbers (copy exactly) or remove those claims.")
        if gaps:
            note.append("Your answer leaves out the largest contributor(s) to the change: " + "; ".join(g["text"] for g in gaps)
                        + ". Include them, citing the fact ids.")
        if cites:
            note.append(f"These items contain numbers but no valid fact id: {cites}. Add the fact id(s) shown in square brackets in the evidence "
                        "(like [F00013]); section names such as [ATTRIBUTION] are not fact ids.")
        msgs += [{"role": "assistant", "content": json.dumps(obj)}, {"role": "user", "content": " ".join(note)}]
        obj2, model = llm.chat_json(msgs, verbose=verbose)
        if _is_answer(obj2):                                   # a fragment reply must not replace the whole answer
            obj, bad, gaps, cites = obj2, check_grounding(fg, context, obj2), missing_contributors(ev, obj2), uncited_claims(obj2)
    stripped = leaked = 0
    if isinstance(obj, dict):
        obj, stripped = strip_pseudo_citations(obj)                       # whatever the model still left behind
        obj, leaked = drop_prompt_leaks(obj)
        cites = uncited_claims(obj)
        obj["sources"] = build_sources(fg, obj, extra_ids=mentioned_slice_ids(ev, obj))      # attached AFTER the checks; not LLM-written
    res.update(answer=obj, ungrounded=bad, model=model, coverage_gaps=[g["text"] for g in gaps], uncited_claims=cites,
               stripped_pseudo_citations=stripped, dropped_prompt_mentions=leaked)
    return res
