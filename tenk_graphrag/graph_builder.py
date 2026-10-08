"""
Typed property graph over a 10-K.

Node types : Company, Concept, Period, Fact, Dim, Section, Chunk, Validation
Edge types : OF_CONCEPT, IN_PERIOD, IN_SECTION, HAS_DIM, FROM_CHUNK
             ROLLS_UP_TO    child fact -> parent total (attribution)
             PRIOR_PERIOD   fact -> same series, previous year (time series spine)
             DERIVED_FROM   derived fact -> input facts (provenance of every ratio)
             VALIDATES/USES accounting-identity checks (A = L + E ...)
             VERIFIES/CONTRADICTS   MD&A number <-> table number
             MENTIONS/EXPLAINS      narrative chunk -> fact / concept
             COMPONENT_OF   concept -> concept (taxonomy structure)
"""
import json, re
from collections import Counter, defaultdict
from datetime import date
from typing import cast
import networkx as nx
from .models import Fact
from .taxonomy import CONCEPTS, IDENTITIES, find_concepts_in_text
from .loader import load_filing
from .cards import HeadingContext, table_cards, xbrl_cards, member_words, card_scope
from .table_parser import process_table
from .narrative import extract_numbers

STMT_PRIORITY = {"IS": 0, "BS": 0, "CF": 0, "EQ": 1, "SEG": 2, "GEO": 2, "REV": 2, "NONGAAP": 3, "TAX": 3, "TEXT": 9}

def printed_value(f):
    """Value with the sign as printed (capex shown in parentheses is stored as magnitude)."""
    spec = CONCEPTS.get(f["concept"])
    if spec and spec["abs"] and f.get("parens_negative"):
        return -abs(f["value"])
    return f["value"]

class FilingGraph:
    def __init__(self, meta=None):
        self.G = nx.MultiDiGraph()
        self.meta = meta or {}
        self._n = 0
        self._key = {}            # (concept, period, dims, unit) -> [fact ids]
        self._instants = defaultdict(list)   # fy -> [(end, period id)] of XBRL balance-sheet dates

    # ------------------------------------------------------------ nodes
    def _node(self, nid, **attrs):
        if nid not in self.G:
            self.G.add_node(nid, **attrs)
        return nid

    def _snap_instant(self, f):
        """A balance-sheet date is ONE snapshot: a table with a year-only header says 'Sept 30', XBRL says 'Sept 24'.
        Snap table/text instants to the XBRL date of the same fiscal year (within 10 days) so they share one period id."""
        try:
            e = date.fromisoformat(f.end)
        except ValueError:
            return f
        for end, period in self._instants.get(f.fy, ()):
            if abs((date.fromisoformat(end) - e).days) <= 10:
                f.end, f.period = end, period
                break
        return f

    def add_fact(self, f: Fact):
        if f.ptype == "instant" and f.source not in ("ixbrl", "derived"):
            f = self._snap_instant(f)
        key = (f.concept, f.period, f.dims_key(), f.unit, f.source == "text")
        for fid in self._key.get(key, []):
            ex = self.G.nodes[fid]
            tol = max(ex["precision"], f.precision) / 2 * 1.01 + abs(ex["value"]) * 1e-9
            if f.source != "derived" and abs(ex["value"] - f.value) <= tol:
                ex.setdefault("also_in", []).append(
                    f'table #{f.table_no} "{f.table_title or "untitled"}"' + (f' (page {f.page})' if f.page else "") + f', row "{f.label}"'
                    if f.table_no else f.location)  # same number, another table => one node
                return fid
        self._n += 1
        f.id = f"F{self._n:05d}"
        d = f.to_dict(); d["type"] = "Fact"
        if self._key.get(key) and f.source not in ("derived", "text"):
            for other in self._key[key]:
                ex = self.G.nodes[other]
                if abs(ex["value"] - f.value) <= max(ex["precision"], f.precision) / 2 * 1.01 + abs(ex["value"]) * 1e-9:
                    return other
            d["flags"].append("conflict_same_key")
            for other in self._key[key]:
                self.G.nodes[other]["flags"].append("conflict_same_key")
        self.G.add_node(f.id, **d)
        self._key.setdefault(key, []).append(f.id)
        if f.source == "ixbrl" and f.ptype == "instant" and (f.end, f.period) not in self._instants[f.fy]:
            self._instants[f.fy].append((f.end, f.period))
        spec = CONCEPTS.get(f.concept, {})
        self._node("c:" + f.concept, type="Concept", key=f.concept, label=spec.get("label", f.label[:60]),
                   stmt=spec.get("stmt", f.stmt), ptype=spec.get("ptype", f.ptype), unit=spec.get("unit", f.unit))
        self._node("p:" + f.period, type="Period", id=f.period, ptype=f.ptype, end=f.end, fy=f.fy, months=f.months)
        self.G.add_edge(f.id, "c:" + f.concept, key="OF_CONCEPT")
        self.G.add_edge(f.id, "p:" + f.period, key="IN_PERIOD")
        for ax, mem in f.dims.items():
            self._node(f"d:{ax}={mem}", type="Dim", axis=ax, member=mem)
            self.G.add_edge(f.id, f"d:{ax}={mem}", key="HAS_DIM")
        if f.section:
            self._node("s:" + f.section, type="Section", name=f.section)
            self.G.add_edge(f.id, "s:" + f.section, key="IN_SECTION")
        return f.id

    def F(self, fid):
        return self.G.nodes[fid]

    def facts(self, pred=None):
        for n, d in self.G.nodes(data=True):
            if d.get("type") == "Fact" and (pred is None or pred(d)):
                yield n, d

    # ------------------------------------------------------------ roll-ups (attribution)
    def infer_rollups(self, groups):
        """Stack algorithm: a 'total' row collapses the shortest contiguous suffix of rows that sums to it."""
        cnt = Counter(p for g in groups for p in g["facts"])
        if not cnt:
            return
        ref = cnt.most_common(1)[0][0]
        stack = []
        for g in groups:
            f = g["facts"].get(ref)
            if not f:
                continue
            fid = f.id
            fv = printed_value(self.F(fid))
            if g["is_total"] and len(stack) >= 2:
                acc, matched = 0.0, 0
                for k in range(1, len(stack) + 1):
                    acc += printed_value(self.F(stack[-k]["f"].id))
                    tol = (k + 1) * max(self.F(fid)["precision"], 1e-9) / 2 * 1.01
                    if k >= 2 and abs(acc - fv) <= tol:
                        matched = k; break
                if matched:
                    kids = stack[-matched:]; del stack[-matched:]
                    for kid in kids:
                        for per, cf in kid["g"]["facts"].items():
                            pf = g["facts"].get(per)
                            if pf and cf.id != pf.id:
                                self.G.add_edge(cf.id, pf.id, key="ROLLS_UP_TO", via="table_structure", period=per)
                    # verify every period column
                    for per, pf in g["facts"].items():
                        s = sum(printed_value(self.F(k["g"]["facts"][per].id)) for k in kids if per in k["g"]["facts"])
                        ok = abs(s - printed_value(self.F(pf.id))) <= (len(kids) + 1) * self.F(pf.id)["precision"] / 2 * 1.01
                        self.F(pf.id)["flags"].append("rollup_verified" if ok else "rollup_failed")
                        self.F(pf.id)["children_sum"] = s
                    for kid in kids:
                        child_concept = self.F(kid["f"].id)["concept"]
                        parent_concept = self.F(fid)["concept"]
                        if child_concept != parent_concept and not kid["g"]["dims"]:
                            self.G.add_edge("c:" + child_concept, "c:" + parent_concept, key="COMPONENT_OF")
            stack.append({"g": g, "f": f})

    # ------------------------------------------------------------ identities
    def _series(self, concept, period):
        c = [(n, d) for n, d in self.facts(lambda d: d["concept"] == concept and d["period"] == period and not d["dims"]
                                          and d["source"] != "text" and d["role"] == "level")]
        c.sort(key=lambda x: STMT_PRIORITY.get(x[1]["stmt"], 5))
        return c[0] if c else None

    def verify_identities(self):
        periods = {d["period"] for _, d in self.facts() if d["source"] != "text"}
        n = 0
        for target, terms, optional, name in IDENTITIES:
            for per in periods:
                t = self._series(target, per)
                if not t: continue
                got = [(self._series(c, per), s) for c, s in terms]
                if any(g is None for g, _ in got): continue
                opt = [(self._series(c, per), s) for c, s in optional]
                opt = [(g, s) for g, s in opt if g]
                used = got + opt
                expected = sum(
                    s * (printed_value(g[1]) if CONCEPTS[g[1]["concept"]]["abs"] is False
                         else abs(g[1]["value"]))
                    for g, s in used if g is not None
                )
                actual = t[1]["value"]
                tol = (len(used) + 1) * max(x[1]["precision"] for x in [t] + [g for g, _ in used] if x is not None) / 2 * 1.01
                diff = actual - expected
                status = "pass" if abs(diff) <= tol else "fail"
                n += 1
                vid = f"V{n:04d}"
                self.G.add_node(vid, type="Validation", name=name, period=per, status=status, expected=expected,
                                actual=actual, diff=diff, tol=tol)
                self.G.add_edge(vid, t[0], key="VALIDATES")
                for g, _ in used:
                    if g is not None:
                        self.G.add_edge(vid, g[0], key="USES")
                self.F(t[0])["flags"].append(f"identity_{status}:{name}")

    # ------------------------------------------------------------ time spine
    def link_time(self):
        series = {}
        for n, d in self.facts(lambda d: d["role"] in ("level", "derived") and d["source"] != "text"
                               and (d["ptype"] == "instant" or d["months"] in (12, 13))):
            series.setdefault((d["concept"], tuple(sorted(d["dims"].items())), d["unit"], d["ptype"]), []).append((d["end"], n))
        for items in series.values():
            best = {}                                          # duplicates for the same period end must not link to each other
            for e, n in items:
                rank = (STMT_PRIORITY.get(self.F(n)["stmt"], 5), n)
                if e not in best or rank < best[e][0]: best[e] = (rank, n)
            items = sorted((e, v[1]) for e, v in best.items())
            for (e0, a), (e1, b) in zip(items, items[1:]):
                gap = (date.fromisoformat(e1) - date.fromisoformat(e0)).days
                if 330 <= gap <= 400:
                    va, vb = self.F(a)["value"], self.F(b)["value"]
                    self.G.add_edge(b, a, key="PRIOR_PERIOD", delta=vb - va, pct=(vb / va - 1) * 100 if va else None)

    # ------------------------------------------------------------ narrative <-> tables
    def add_card(self, cid, text, section, **attrs):
        """A retrieval-only document: a table row or an XBRL series written out as a self-describing sentence."""
        self.G.add_node(cid, type="Card", text=text, section=section, **attrs)

    def add_chunk(self, text, section, idx, facts, ctx=""):
        cid = f"T{idx:05d}"
        self.G.add_node(cid, type="Chunk", text=text, section=section, ctx=ctx)
        for f in facts:
            self.G.add_edge(cid, f, key="MENTIONS")
        seen = set()
        for _, _, key, _ in find_concepts_in_text(text):
            if key not in seen and "c:" + key in self.G:
                self.G.add_edge(cid, "c:" + key, key="EXPLAINS"); seen.add(key)
        if section:
            self._node("s:" + section, type="Section", name=section)
            self.G.add_edge(cid, "s:" + section, key="IN_SECTION")

    def reconcile_narrative(self):
        for n, d in list(self.facts(lambda d: d["source"] == "text" and not d["concept"].startswith("text:"))):
            if d["dims"] or d["role"] not in ("level", "change_pct", "change_abs"):
                continue
            scope = self._text_scope(d)
            if scope is None:                                   # sentence is about an unknown slice ("Services net sales ...")
                d["flags"].append("scope_unresolved"); continue
            d["scope"] = scope
            tab = [(m, x) for m, x in self.facts(lambda x: x["concept"] == d["concept"] and x["dims"] == scope and
                   x["source"] != "text" and x["role"] != "shadowed" and x["unit"] == (d["unit"] if d["role"] == "level" else x["unit"]))]
            if not tab:
                continue
            tab.sort(key=lambda t: STMT_PRIORITY.get(t[1]["stmt"], 5))
            by_period = {}
            for m, x in tab: by_period.setdefault(x["period"], (m, x))
            if d["role"] == "level":
                cand = by_period.get(d["period"])
                tol = lambda x: (d["precision"] + x["precision"]) / 2 * 1.01 + 1e-9
                if cand and abs(cand[1]["value"] - d["value"]) <= tol(cand[1]):
                    self.G.add_edge(n, cand[0], key="VERIFIES"); d["flags"].append("verified_by_table"); continue
                alt = [(m, x) for m, x in by_period.values() if abs(x["value"] - d["value"]) <= tol(x)]
                if alt:
                    self.G.add_edge(n, alt[0][0], key="VERIFIES"); d["flags"].append("verified_other_period"); d["period"] = alt[0][1]["period"]; continue
                if cand:
                    ratio = abs(d["value"] / cand[1]["value"]) if cand[1]["value"] else None
                    if ratio is None or not (LEVEL_SCOPE_BAND[0] <= ratio <= LEVEL_SCOPE_BAND[1]):
                        d["flags"].append("scope_mismatch")       # far from the statement line => a different item, not an error
                        continue
                    diff = d["value"] - cand[1]["value"]
                    self.G.add_edge(n, cand[0], key="CONTRADICTS", diff=diff)
                    d["flags"].append("narrative_mismatch")
            else:
                cands = [by_period[d["period"]]] if d["period"] in by_period else []
                cands += [v for k, v in by_period.items() if k != d["period"]]
                verdict, last = None, None
                for m, x in cands:
                    pe = next((self.G.get_edge_data(m, t, key="PRIOR_PERIOD") for _, t, k in self.G.out_edges(m, keys=True) if k == "PRIOR_PERIOD"), None)
                    if not pe: continue
                    last = (m, pe)
                    if d["unit"] == "bps":
                        comp, tol, same_sign = pe["delta"] * 100, d["precision"] / 2 * 1.01 + 0.5, True
                        if x["unit"] != "percent": continue
                    elif d["role"] == "change_pct" and d["unit"] == "percent" and pe.get("pct") is not None:
                        comp, tol, same_sign = pe["pct"], d["precision"] / 2 * 1.01 + 0.05, True
                    elif d["role"] == "change_abs":
                        comp, tol, same_sign = pe["delta"], d["precision"] / 2 * 1.01 + 1e-9, True
                    else:
                        continue
                    if abs(comp - d["value"]) <= tol:
                        verdict = (m, comp, x); break
                if verdict:
                    self.G.add_edge(n, verdict[0], key="VERIFIES", computed=verdict[1])
                    d["flags"].append("verified_by_table"); d["period"] = verdict[2]["period"]
                elif last:
                    comp = last[1]["delta"] * 100 if d["unit"] == "bps" else (last[1].get("pct") if d["role"] == "change_pct" else last[1]["delta"])
                    self.G.add_edge(n, last[0], key="CONTRADICTS", computed=comp)
                    d["flags"].append("narrative_mismatch"); d["computed_from_tables"] = comp

    # ------------------------------------------------------------ XBRL first
    def index_xbrl(self, min_facts=50):
        """XBRL-first mode: when the filing carries inline XBRL, tagged numbers are the source of truth and tables only
        add provenance (and structure). Returns True if the mode is on."""
        self._xbrl_index = defaultdict(list)
        for n, d in self.facts(lambda d: d["source"] == "ixbrl"):
            self._xbrl_index[(d["period"], d["unit"])].append(n)
        if sum(len(v) for v in self._xbrl_index.values()) < min_facts:
            self._xbrl_index = defaultdict(list)
        return bool(self._xbrl_index)

    _AXIS_HINT = {"segment": r"segment", "geography": r"geograph|region|country|area", "product": r"product|service|categor", "customer": r"customer"}

    @staticmethod
    def _norm_member(x):
        return re.sub(r"[^a-z0-9]", "", str(x).lower())

    def _match_xbrl(self, f):
        """The unique XBRL fact with the same period, unit and value (sign-insensitive).
        A consolidated number can only match a consolidated fact; a sliced number only a sliced fact, and when several
        slices share the value (e.g. segment 'Greater China' and geography 'China') the slice NAME decides."""
        cands = []
        for xid in self._xbrl_index.get((f.period, f.unit), ()):
            x = self.F(xid)
            if abs(abs(x["value"]) - abs(f.value)) <= max(x["precision"], f.precision) / 2 * 1.01 + 1e-9 \
                    and bool(x["dims"]) == bool(f.dims):
                cands.append(xid)
        if f.dims and len(cands) > 1:
            axis = next(iter(f.dims))                       # table axis: segment | geography | product | customer
            rx = self._AXIS_HINT.get(axis)
            by_axis = [x for x in cands if rx and any(re.search(rx, str(a).lower()) for a in self.F(x)["dims"])]
            cands = by_axis or cands                        # 'geography' must not match a *Segments* axis, and vice versa
            want = self._norm_member(next(iter(f.dims.values())))
            named = [x for x in cands if want and any(want in self._norm_member(m) or self._norm_member(m) in want
                                                      for m in self.F(x)["dims"].values())]
            cands = named or cands
        same = [x for x in cands if self.F(x)["concept"] == f.concept]
        pick = same if same else cands
        if len(pick) > 1 and f.value != 0:
            ident = {(self.F(x)["concept"], tuple(sorted(self.F(x)["dims"].items()))) for x in pick}
            if len(ident) == 1:                              # the same logical fact tagged more than once: interchangeable
                return min(pick)
        return pick[0] if len(pick) == 1 and f.value != 0 else None

    def add_table_fact(self, f):
        """Table number -> graph. In XBRL-first mode a table number that IS a tagged XBRL fact is not stored again; the
        XBRL node simply records that (and where) the filing also displays it in a table."""
        if getattr(self, "_xbrl_index", None):
            xid = self._match_xbrl(f)
            if xid:
                x = self.F(xid)
                x.setdefault("appears_in", []).append(dict(table_no=f.table_no, table_title=f.table_title, row=f.label,
                                                           column=f.column, location=f.location, page=f.page))
                if f.parens_negative: x["parens_negative"] = True          # the printed sign is needed for roll-up sums
                if f.is_total: x["is_total"] = True
                return xid
        return self.add_fact(f)

    # ------------------------------------------------------------ conflicting duplicates
    def _trust_rank(self, n):
        """Lower = more trustworthy: XBRL > known scale > caption-identified statement > primary statements > mapped label."""
        d = self.F(n)
        return (d["source"] != "ixbrl", "scale_unknown" in d["flags"], "stmt_inferred" in d["flags"],
                STMT_PRIORITY.get(d["stmt"], 5), "unmapped_label" in d["flags"], n)

    def resolve_conflicts(self):
        """Same concept + period + slice but different values (e.g. a segment table that was read as company-wide):
        keep the most trustworthy fact, set the others aside (role='shadowed') so series, ratios and roll-ups ignore them."""
        for key, ids in self._key.items():
            live = [n for n in ids if self.F(n)["role"] == "level" and self.F(n)["source"] in ("table", "ixbrl")]
            if key[-1] or len(live) < 2 or str(key[0]).startswith("custom:"):
                continue                       # generic rows ("Total", "Other", "Level 1") from different tables are NOT the same item
            live.sort(key=self._trust_rank)
            for loser in live[1:]:
                if self._trust_rank(loser)[:-1] == self._trust_rank(live[0])[:-1]:     # equally trustworthy: we cannot tell which is right
                    for n in (live[0], loser):
                        if "ambiguous_duplicate" not in self.F(n)["flags"]:
                            self.F(n)["flags"].append("ambiguous_duplicate")            # ...so keep both instead of discarding data
                    continue
                self.F(loser)["role"] = "shadowed"
                self.F(loser)["flags"].append(f"shadowed_by:{live[0]}")
                self.G.add_edge(loser, live[0], key="SHADOWED_BY")

    # ------------------------------------------------------------ roll-ups by dimension (segments sum to the consolidated total)
    def infer_dimension_rollups(self):
        groups, cons = defaultdict(list), defaultdict(list)
        for n, d in self.facts(lambda d: d["source"] in ("table", "ixbrl") and d["role"] == "level"):
            if not d["dims"]:
                cons[(d["concept"], d["period"], d["unit"])].append(n)
            elif len(d["dims"]) == 1:
                groups[(d["concept"], d["period"], d["unit"], next(iter(d["dims"])))].append(n)
        for (concept, period, unit, axis), members in groups.items():
            if len(members) < 2:
                continue
            for tot in cons.get((concept, period, unit), []):
                tv = self.F(tot)
                tol = (len(members) + 1) * max([tv["precision"]] + [self.F(m)["precision"] for m in members]) / 2 * 1.01
                if abs(sum(self.F(m)["value"] for m in members) - tv["value"]) <= tol:
                    for m in members:
                        if not self.G.has_edge(m, tot, key="ROLLS_UP_TO"):
                            self.G.add_edge(m, tot, key="ROLLS_UP_TO", via="dimension_sum", period=period)
                        if "rollup_verified" not in self.F(m)["flags"]:
                            self.F(m)["flags"].append("rollup_verified")
                    if "rollup_verified" not in tv["flags"]:
                        tv["flags"].append("rollup_verified")
                    break

    # ------------------------------------------------------------ which slice is a sentence talking about?
    _GENERIC_LEAD = {"Total", "Consolidated", "Our", "The", "Company", "Annual", "Overall", "Worldwide", "Global", "Net", "Gross",
                     "Combined", "In", "For", "During", "Over", "While", "Although", "However", "As", "We", "Fiscal", "Year", "And", "But"}
    _NARROWING = {"foreign", "domestic", "federal", "state", "cash", "unrecognized", "accrued", "adjusted", "noncurrent", "non-current"}

    def _text_scope(self, d):
        """-> {} (company total) | {axis: member} (a known slice) | None (a slice we can't identify)."""
        sent, lab = d.get("context", ""), d.get("label", "")
        pos = sent.find(lab)
        before = sent[:pos] if pos > 0 else sent
        low, best = before.lower(), None
        for _, dd in self.G.nodes(data=True):
            if dd.get("type") == "Dim":
                i = low.rfind(dd["member"].lower())
                if i >= 0 and (best is None or i > best[0] or (i == best[0] and len(dd["member"]) > len(best[1]["member"]))):
                    best = (i, dd)
        if best:
            return {best[1]["axis"]: best[1]["member"]}
        hits = [h for h in find_concepts_in_text(sent) if h[2] == d["concept"] and h[0] <= max(pos, 0)]
        if hits:
            prev = re.findall(r"[A-Za-z][\w&'’-]*", sent[:hits[-1][0]])
            if prev and any(c.isupper() for c in prev[-1]) and prev[-1] not in self._GENERIC_LEAD:
                return None
            if any(w.lower() in self._NARROWING for w in prev[-3:]):          # "foreign pretax earnings", "cash paid for income taxes"
                return None
        return {}

    # ------------------------------------------------------------ persistence
    def save(self, path):
        data = {"meta": self.meta, "n": self._n,
                "nodes": [[n, d] for n, d in self.G.nodes(data=True)],
                "edges": [[u, v, k, d] for u, v, k, d in self.G.edges(keys=True, data=True)]}
        json.dump(data, open(path, "w"), default=str)

    @classmethod
    def load(cls, path):
        data = json.load(open(path))
        g = cls(data["meta"]); g._n = data["n"]
        for n, d in data["nodes"]:
            g.G.add_node(n, **d)
            if d.get("type") == "Fact":
                g._key.setdefault((d["concept"], d["period"], "|".join(f"{k}={v}" for k, v in sorted(d["dims"].items())), d["unit"], d["source"] == "text"), []).append(n)
        for u, v, k, d in data["edges"]:
            g.G.add_edge(u, v, key=k, **d)
        return g

# ================================================================== pipeline
def _doc_context(meta, blocks):
    fe = meta.get("fy_end")
    if fe:
        d = date.fromisoformat(fe)
    else:
        years = Counter(int(y) for b in blocks[:80] if b["type"] != "table" for y in re.findall(r"\b(20\d{2})\b", b["text"]))
        d = date(years.most_common(1)[0][0] if years else date.today().year - 1, 12, 31)
    return dict(fy=d.year, fy_end_month=d.month, fy_end_day=d.day)

LEVEL_SCOPE_BAND = (0.65, 1.55)     # a prose LEVEL this far from the statement line is a different (narrower/broader) item, not an error

_FOOTERS = [re.compile(r"^.{0,60}?\|\s*(?:19|20)\d{2}\s+Form\s+10-K\s*\|\s*(\d{1,3})\s*$", re.I),    # "Apple Inc. | 2023 Form 10-K | 34"
            re.compile(r"^\s*page\s+(\d{1,3})(?:\s+of\s+\d+)?\s*$", re.I),                             # "Page 34" / "Page 34 of 90"
            re.compile(r"^\s*[-–—]?\s*(\d{1,3})\s*[-–—]?\s*$")]                                         # "34" / "- 34 -"

def _footer_page(text):
    t = text.strip()
    for rx in _FOOTERS:
        m = rx.match(t)
        if m: return int(m.group(1))
    return None

def _page_numbers(blocks):
    """Footers sit at the BOTTOM of a page, so a block belongs to the page whose footer comes next (0 = unknown)."""
    pages, nxt = [0] * len(blocks), 0
    for i in range(len(blocks) - 1, -1, -1):
        if blocks[i]["type"] != "table":
            pg = _footer_page(blocks[i]["text"])
            if pg is not None: nxt = pg
        pages[i] = nxt
    return pages

_SCALE_NOTE = re.compile(r"\(\s*(?:in\s+|\$\s*in\s+)?(?:thousands|millions|billions)", re.I)

def _table_title(recent):
    """Nearest short line above a table that is not just a '(in millions)' note."""
    for t in reversed(recent):
        t = t.strip()
        if 8 <= len(t) <= 120 and not _SCALE_NOTE.search(t) and _footer_page(t) is None:
            return t
    return ""

def build_graph(path, company=None, use_derived=True, xbrl_first=True, xbrl_min_facts=50):
    from .derived import add_derived_metrics
    blocks, ix_facts, meta = load_filing(path)
    doc = _doc_context(meta, blocks)
    meta.update(doc)  # type: ignore[arg-type]
    meta["company"] = company or meta.get("company") or "Company"
    fg = FilingGraph(meta)
    fg._node("co:" + meta["company"], type="Company", name=meta["company"])
    for f in ix_facts:
        fg.add_fact(f)
    cast(dict[str, object], meta).update(ixbrl_facts=len(ix_facts))
    cast(dict[str, object], meta)["xbrl_first"] = fg.index_xbrl(xbrl_min_facts) if xbrl_first else False
    pages = _page_numbers(blocks)
    recent, table_no = [], 0
    hc = HeadingContext(footer=_footer_page)
    members = member_words(ix_facts)                             # this filing's segment / product / region names
    for b in blocks:
        if b["type"] == "table" and len(b["rows"]) == 1 and len(b["rows"][0]) == 1:     # a layout box, not a data table
            cell = b["rows"][0][0]
            if len(cell) <= 120:
                hc.see(cell)                                     # e.g. "CONSUMER & COMMUNITY BANKING"
                continue
            b = dict(b, type="para", text=cell)                  # prose that sits in a one-cell table
        if b["type"] in ("para", "heading"):
            if _footer_page(b["text"]) is None:
                recent = (recent + [b["text"]])[-6:]
            heading = hc.see(b["text"])
            short_number = (8 <= len(b["text"]) <= 40 and re.search(r"\d", b["text"]) and not heading
                            and _footer_page(b["text"]) is None)          # "Net revenue was $70.1 billion, up 28%."
            if b["type"] == "para" and (len(b["text"]) > 40 or short_number):
                nf = extract_numbers(b["text"], doc, b["section"], b["idx"])
                for f in nf: f.page = pages[b["idx"]]
                ids = [fg.add_fact(f) for f in nf]
                fg.add_chunk(b["text"], b["section"], b["idx"], ids, ctx=hc.path(b["text"]))
                fg.G.nodes[f"T{b['idx']:05d}"]["page"] = pages[b["idx"]]
        else:
            caption = " ".join(t for t in recent[-3:] if len(t) < 300)[-400:]
            table_no += 1
            title = _table_title(recent)
            for k, txt in enumerate(table_cards(b["rows"], hc.path(), title, caption)):
                fg.add_card(f"R{b['idx']:05d}_{k:03d}", txt, b["section"], kind="table", table_no=table_no, page=pages[b["idx"]],
                            scope=card_scope(txt, members))
            facts, groups = process_table(b["rows"], caption, doc, b["section"], b["idx"],
                                          title=title, table_no=table_no)
            for f in facts:
                f.page = pages[b["idx"]]
                fg_id = fg.add_table_fact(f)
                f.id = fg_id
            # row groups hold Fact objects; ensure they carry resolved ids
            fg.infer_rollups(groups)
            recent = []
    fg.resolve_conflicts()
    fg.infer_dimension_rollups()
    fg.verify_identities()
    fg.link_time()
    if use_derived:
        add_derived_metrics(fg)
        fg.link_time()
    fg.reconcile_narrative()
    for cid, txt, scope in xbrl_cards(fg):                       # every XBRL series as a searchable number card
        fg.add_card(cid, txt, "", kind="xbrl", scope=scope)
    return fg
