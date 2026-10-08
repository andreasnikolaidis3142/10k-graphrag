"""
Numbers hidden in prose (MD&A, notes, risk factors): "$4.6 billion", "increased 12%", "approximately 45,000
employees", "three reportable segments", "$10 to $12 million", "150 basis points", "2.5x".
Each gets a concept, period, role (level / change / guidance / threshold / contractual) and a sign.
"""
import re
from datetime import date
from .models import Fact, make_period
from .numparse import SCALE_WORDS, WORD_NUMS, money_to_base
from .taxonomy import find_concepts_in_text, CONCEPTS

NOISE_BEFORE = re.compile(r"(item|note|part|section|page|exhibit|no\.|rule|form|topic|asc|article|schedule|regulation)\s*$", re.I)
UP = r"increas\w*|grew|grow\w*|rose|rise\w*|up|higher|improv\w*|expan\w*"
DOWN = r"decreas\w*|declin\w*|fell|fall\w*|down|lower|reduc\w*|drop\w*|contracted"
DIR_RE = re.compile(rf"\b(?P<up>{UP})\b|\b(?P<down>{DOWN})\b", re.I)
FORWARD = re.compile(r"\b(expect\w*|anticipat\w*|forecast\w*|project\w*|guidance|outlook|we plan|will be|estimate[sd]?|target\w*|intend)\b", re.I)
THRESH = re.compile(r"\b(at least|not (?:to )?exceed|no more than|no less than|minimum|maximum|covenant|up to|in excess of|threshold)\b", re.I)
CONTRACT = re.compile(r"\b(due (?:in )?(?:fiscal )?(?:20\d\d|\d{4})|matur\w+|notes? due|expire[sd]?|coupon|bear\w* interest)\b", re.I)
COUNT_NOUNS = r"(?:full[- ]time |part[- ]time )?(employees|associates|stores|locations|customers|patents|facilities|countries|segments|reportable segments|restaurants|branches|subscribers|users|clients|vessels|aircraft|properties|shares)"
MONEY = re.compile(r"(?P<neg>\()?\s*(?P<cur>US\$|\$|€|£|¥)\s?(?P<neg2>\()?(?P<num>\d[\d,]*(?:\.\d+)?)\)?\s*(?P<scale>thousand|million|billion|trillion|bn|mm|m|k|b)?\b(?!\w)", re.I)
RANGE = re.compile(r"(?P<btw>between\s+)?(?P<cur>\$|€|£)\s?(?P<a>\d[\d,]*(?:\.\d+)?)\s*(?P<sa>thousand|million|billion)?\s*(?P<conn>to|and|-|–|—)\s*\$?\s?(?P<b>\d[\d,]*(?:\.\d+)?)\s*(?P<sb>thousand|million|billion)", re.I)
PCT = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s?(?P<u>%|percentage points?|percent\b|basis points?|bps)", re.I)
COUNT = re.compile(rf"(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<scale>million|thousand|billion)?\s+{COUNT_NOUNS}", re.I)
WORDCOUNT = re.compile(rf"\b(?P<w>{'|'.join(sorted(WORD_NUMS, key=len, reverse=True))})\s+(?:\w+\s+)?{COUNT_NOUNS}", re.I)
MULT = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s?x\b|(?P<num2>\d+(?:\.\d+)?)\s+times\b", re.I)
YEAR = re.compile(r"(?<![\d$,.])((?:19|20)\d{2})(?!\d|,\d|%)")

def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(\"“$])", text) if len(s.strip()) > 20]

def _period_for(sentence, pos, doc, prefer_prior=False, force_fy=None):
    years = [(m.start(), int(m.group(1))) for m in YEAR.finditer(sentence)]
    cand = None
    right = [y for p, y in years if 0 <= p - pos <= 70]
    left = [y for p, y in years if 0 < pos - p <= 70]
    if right: cand = right[0]
    elif left: cand = left[-1]
    elif years: cand = years[0][1]
    assumed = cand is None and force_fy is None
    fy = force_fy or cand or doc["fy"]
    inst = re.search(r"\bas of\b|\bat (?:the )?end\b|outstanding|balance", sentence[max(0, pos - 80):pos + 40], re.I)
    end = date(fy, doc["fy_end_month"], min(doc["fy_end_day"], 28 if doc["fy_end_month"] == 2 else 31))
    if inst:
        pid, f = make_period("instant", end, 0, doc["fy_end_month"]); return pid, "instant", end.isoformat(), 0, f, assumed
    pid, f = make_period("duration", end, 12, doc["fy_end_month"]); return pid, "duration", end.isoformat(), 12, f, assumed

YEAR_RUN = re.compile(r"(?<![\d$,.])(?:19|20)\d{2}(?:\s*(?:,\s*and|,|and)\s*(?:19|20)\d{2})+(?!\d)")

def _align_years(s, out, start, pos_of, doc):
    """'$8.7B, $8.5B and $9.5B during 2023, 2022 and 2021, respectively': the k-th amount belongs to the k-th year."""
    run = YEAR_RUN.search(s)
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", run.group(0))] if run else []
    if not years and re.search(r"\brespectively\b", s, re.I):
        years = [int(m.group(1)) for m in YEAR.finditer(s)]
    if len(years) < 2:
        return
    by_unit = {}
    for i in range(start, len(out)):
        if out[i].role == "level":
            by_unit.setdefault(out[i].unit, []).append(i)
    for unit, idxs in by_unit.items():
        if len(idxs) != len(years):
            continue
        for i, fy in zip(sorted(idxs, key=lambda i: pos_of[i]), years):
            f = out[i]
            pid, ptype, pend, months, fyv, _ = _period_for(s, pos_of[i], doc, force_fy=fy)
            f.period, f.ptype, f.end, f.months, f.fy = pid, ptype, pend, months, fyv
            f.flags = [x for x in f.flags if x != "period_assumed"] + ["period_by_position"]


def _concept_near(sentence, pos):
    hits = find_concepts_in_text(sentence)
    before = [h for h in hits if h[1] <= pos + 3 and pos - h[1] < 140]
    pick = before[-1] if before else (min(hits, key=lambda h: abs(h[0] - pos)) if hits else None)
    return (pick[2], pick[3]) if pick else (None, "")

def _role_and_sign(sentence, pos, num_end, kind, concept_phrase):
    pre = sentence[max(0, pos - 90):pos]
    d = None
    for m in DIR_RE.finditer(pre):
        d = "up" if m.group("up") else "down"
    sign = 1
    role = "level"
    pre_s = pre.rstrip()
    after_dir = re.search(rf"\b({UP}|{DOWN})\b\s*(?:by|of)?\s*(?:approximately|about)?$", pre_s, re.I)          # "decreased $11.0 billion", "increased by $240 million"
    pct_or = re.search(rf"\b({UP}|{DOWN})\b\s+(?:by\s+)?[\d.,]+\s?(?:%|percent)\s*,?\s*or\s*(?:approximately|about)?$", pre_s, re.I)  # "decreased 3% or $11.0 billion"
    if kind in ("money", "count") and (after_dir or pct_or):
        role = "change_abs"
        sign = -1 if d == "down" else 1
    elif kind == "pct":
        if d: role, sign = "change_pct", (-1 if d == "down" else 1)
    if FORWARD.search(sentence): role = "guidance" if role == "level" else role
    if THRESH.search(sentence[max(0, pos - 60):pos + 40]): role = "threshold"
    if CONTRACT.search(sentence): role = "contractual" if kind in ("money", "pct") and role == "level" else role
    if re.search(r"\bnet loss|operating loss|loss from operations|loss before", concept_phrase or "", re.I) or \
       (re.search(r"\b(net loss|operating loss|loss of)\b", pre[-40:], re.I) and role == "level"):
        sign = -1
    return role, sign

def extract_numbers(text, doc, section, block_idx):
    """-> list[Fact] for all quantitative statements in a paragraph."""
    out = []
    for si, s in enumerate(split_sentences(text)):
        seen = []
        start, pos_of = len(out), {}
        def add(kind, value, unit, prec, pos, end, label, extra_flags=()):
            if any(not (end <= a or pos >= b) for a, b in seen): return
            if NOISE_BEFORE.search(s[max(0, pos - 14):pos]): return
            seen.append((pos, end))
            concept, phrase = _concept_near(s, pos)
            role, sign = _role_and_sign(s, pos, end, kind, phrase)
            pid, ptype, pend, months, fy, assumed = _period_for(s, pos, doc)
            if kind == "count":
                noun = next((f[5:] for f in extra_flags if f.startswith("noun:")), "")
                concept = "NumberOfEmployees" if "employee" in noun or noun == "associates" else "Count:" + re.sub(r"\W+", "_", noun)
            sp = CONCEPTS.get(concept or "", {})
            extra = []
            if role == "contractual":
                ym = re.search(r"due (?:in )?(?:fiscal )?((?:19|20)\d{2})|matur\w+ (?:in )?((?:19|20)\d{2})", s, re.I)
                if ym: extra.append("matures:" + (ym.group(1) or ym.group(2)))
                concept = "DebtInstrumentInterestRateStatedPercentage" if kind == "pct" else "DebtInstrumentFaceAmount" if kind == "money" else concept
                pid, ptype, pend, months, fy, assumed = _period_for("", 0, doc)
            if kind == "pct" and concept in ("GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss") and role != "level":
                concept = {"GrossProfit": "GrossMarginPct", "OperatingIncomeLoss": "OperatingMarginPct", "NetIncomeLoss": "NetMarginPct"}[concept]
            v = value * (sign if role in ("change_abs", "change_pct", "level") else 1)
            if kind == "pct" and role == "level" and sign == 1 and concept in ("NetIncomeLoss", "OperatingIncomeLoss"):
                concept = {"NetIncomeLoss": "NetMarginPct", "OperatingIncomeLoss": "OperatingMarginPct"}[concept]
            if kind == "pct" and role == "level" and concept == "GrossProfit": concept = "GrossMarginPct"
            fl = list(extra_flags) + extra + (["period_assumed"] if assumed else []) + ([] if concept else ["unmapped_concept"])
            out.append(Fact(concept=concept or "text:number", label=label, value=v, unit=unit, scale=1.0, precision=prec,
                            period=pid, ptype=ptype, end=pend, months=months, fy=fy, stmt="TEXT", section=section,
                            source="text", role=role, location=f"block#{block_idx}.s{si}", context=s[:400],
                            confidence=0.6 if concept else 0.3, flags=fl))
            pos_of[len(out) - 1] = pos
        for m in RANGE.finditer(s):
            if m.group("conn").lower() == "and" and not m.group("btw"):
                continue                                         # "$8.5 billion and $9.5 billion" is a LIST, not a range
            sa = m.group("sa") or m.group("sb")
            for tag, n, sc in (("range_low", m.group("a"), sa), ("range_high", m.group("b"), m.group("sb"))):
                v, prec = money_to_base(n, sc)
                add("money", v, "USD", prec, m.start("a" if tag == "range_low" else "b"), m.end("a" if tag == "range_low" else "b"), m.group(0), [tag, "guidance_range"])
        for m in MONEY.finditer(s):
            v, prec = money_to_base(m.group("num"), m.group("scale"))
            neg = bool(m.group("neg") or m.group("neg2"))
            unit = {"$": "USD", "US$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}[m.group("cur").upper().replace("US$", "US$")]
            tail = s[m.end():m.end() + 40]
            if re.match(r"\s*per\s+(?:diluted\s+|basic\s+|common\s+)?(?:share|ADS)", tail, re.I):
                unit = "USD/share"; v = v / SCALE_WORDS.get((m.group("scale") or "").lower(), 1.0) if m.group("scale") else v
            add("money", -v if neg else v, unit, prec, m.start(), m.end(), m.group(0).strip())
        for m in PCT.finditer(s):
            u = m.group("u").lower()
            unit = "bps" if u.startswith(("basis", "bps")) else "percent"
            add("pct", float(m.group("num")), unit, 10 ** -(len(m.group("num").split(".")[1]) if "." in m.group("num") else 0),
                m.start(), m.end(), m.group(0), ["percentage_points"] if u.startswith("percentage") else [])
        for m in COUNT.finditer(s):
            v, prec = money_to_base(m.group("num"), m.group("scale"))
            if m.group(3).lower().startswith("share"): continue
            add("count", v, "count", prec, m.start(), m.end(), m.group(0), [f"noun:{m.group(3).lower()}"])
        for m in WORDCOUNT.finditer(s):
            add("count", float(WORD_NUMS[m.group("w").lower()]), "count", 1, m.start(), m.end(), m.group(0), ["number_word", f"noun:{m.group(2).lower()}"])
        for m in MULT.finditer(s):
            add("mult", float(m.group("num") or m.group("num2")), "multiple", 0.1, m.start(), m.end(), m.group(0))
        _align_years(s, out, start, pos_of, doc)
    return out
