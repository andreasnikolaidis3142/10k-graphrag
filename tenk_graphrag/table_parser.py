"""
Deterministic table -> typed Facts.

Handles: header periods (dates / bare years / "three months ended"), scale ("in thousands"),
parentheses negatives, dashes, % columns, per-share rows, share counts, subheaders
(Current assets: ...), segment/geography tables (rows = members), metric-column tables, footnote markers.
"""
import re
from datetime import date
from .models import Fact, make_period, month_num, parse_date
from .numparse import parse_cell, detect_scale, is_year_like, SCALE_WORDS
from .taxonomy import CONCEPTS, PCT_TWIN, AGG_CONCEPTS, match_concept, norm

STMT_RULES = [
    ("BS", r"balance sheets?|financial position|financial condition"),
    ("CF", r"cash flows?"),
    ("EQ", r"stockholders'? equity|shareholders'? equity|changes in equity"),
    ("IS", r"statements? of (?:consolidated )?(?:operations|income|earnings|comprehensive)|income statements?|results of operations"),
    ("SEG", r"segment"), ("GEO", r"geograph|by region|by country|international"),
    ("TAX", r"income tax|tax rate|effective tax|deferred tax"), ("DEBT", r"\bdebt\b|notes payable|borrowings|credit facilit|senior notes"),
    ("LEASE", r"\bleases?\b"), ("EPS", r"earnings per share|net income per share"),
    ("SBC", r"stock[- ]based|share[- ]based|restricted stock|stock options"),
    ("NONGAAP", r"non-gaap|reconciliation|adjusted ebitda"),
    ("REV", r"disaggregat|revenue by|net sales by|by product|by customer"),
]
DIM_AXIS = [("segment", r"segment"), ("geography", r"geograph|region|country|international|americas|emea|europe|asia"),
            ("product", r"product|service|category"), ("customer", r"customer")]
MOD_RE = re.compile(r"(?P<n>three|six|nine|twelve|13|3|6|9|12)\s+months?\s+ended|(?:fiscal\s+)?years?\s+ended|"
                    r"(?P<asof>as\s+of|at\s+(?:december|january|february|march|april|may|june|july|august|september|october|november))", re.I)
DATE_RE = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", re.I)
_N = {"three": 3, "six": 6, "nine": 9, "twelve": 12}

_TAX_CONCEPTS = {"IncomeTaxExpenseBenefit", "IncomeLossBeforeIncomeTaxes", "EffectiveIncomeTaxRate", "NetIncomeLoss"}

def classify_text(text: str):
    t = text.lower()
    for stmt, rx in STMT_RULES:
        if re.search(rx, t):
            return stmt
    return ""

def parse_header_periods(cells, stmt, fy_end_month, fy_end_day):
    """Scan header cells left->right; modifiers ('Year Ended', 'As of') carry forward."""
    periods, mod_months, asof = [], 12, stmt == "BS"
    for c in cells:
        mm = MOD_RE.search(c)
        if mm:
            if mm.group("asof"): asof = True
            else:
                asof = False
                n = mm.group("n"); mod_months = (_N[n.lower()] if n.lower() in _N else int(n)) if n else 12
        found = [(m.start(), date(int(m.group(3)), month_num(m.group(1)), int(m.group(2)))) for m in DATE_RE.finditer(c)]
        masked = DATE_RE.sub(" ", c)
        for m in re.finditer(r"(?<![\d,.$])(19|20)\d{2}(?!\d|,\d|%)", masked):
            y = int(m.group(0))
            try: d = date(y, fy_end_month, min(fy_end_day, 28 if fy_end_month == 2 else fy_end_day))
            except ValueError: d = date(y, fy_end_month, 28)
            found.append((m.start() + 10_000, d))      # years sort after full dates inside same cell
        for _, d in sorted(found):
            ptype = "instant" if asof else "duration"
            pid, fy = make_period(ptype, d, mod_months, fy_end_month)
            periods.append(dict(id=pid, ptype=ptype, end=d.isoformat(), months=0 if asof else mod_months, fy=fy, col=re.sub(r"\s+", " ", c).strip()[:60]))
    return periods

def _strip_footnote(label):
    return re.sub(r"\s*(\(\d{1,2}\)|\(\w\)|[¹²³⁴⁵⁶⁷⁸⁹*†‡]+)\s*$", "", label).strip()

def process_table(rows, caption, doc, section, tidx, title="", table_no=0):
    """-> (facts, row_groups). row_groups feed roll-up inference: [{label, concept, is_total, facts:{period: Fact}}]"""
    # 1) header rows = rows before first real numeric row
    hdr_end = 0
    for i, r in enumerate(rows):
        vals = [parse_cell(c) for c in r[1:]]
        real = [v for v, c in zip(vals, r[1:]) if v is not None and not is_year_like(c)]
        if real:
            hdr_end = i
            break
    else:
        return [], []
    # a lone label row right before the first data row ("Americas:") is a SUBHEADER, not part of the column header
    while hdr_end > 0 and len(rows[hdr_end - 1]) == 1 and \
            not re.search(r"\d|ended|as of|fiscal|thousands|millions|billions", rows[hdr_end - 1][0], re.I) and \
            any(re.search(r"(19|20)\d\d", " ".join(r)) for r in rows[:hdr_end - 1]):
        hdr_end -= 1
    header = [c for r in rows[:hdr_end] for c in r]
    ctx_text = f"{caption} {' '.join(header)}"
    scale = detect_scale(ctx_text)
    # classify from the NEAREST title; only use the wider caption text when there is no title (a 400-char blob of
    # preceding paragraphs can mention "financial condition" or "cash flows" and mislabel an unrelated table)
    stmt = (classify_text(title) if title else classify_text(caption)) or classify_text(" ".join(header))
    periods = parse_header_periods(header, stmt, doc["fy_end_month"], doc["fy_end_day"])
    metric_cols = []
    if not periods:
        # metric-column table (segment rows x metric columns): header cells are concepts
        metric_cols = [match_concept(h)[0] for h in (rows[hdr_end - 1][1:] if hdr_end else [])]
        d = parse_date(ctx_text)
        pid, fy = make_period("duration", d or date(doc["fy"], doc["fy_end_month"], doc["fy_end_day"]), 12, doc["fy_end_month"])
        periods = [dict(id=pid, ptype="duration", end=(d or date(doc["fy"], doc["fy_end_month"], doc["fy_end_day"])).isoformat(), months=12, fy=fy)]
    flags_t = []
    if scale["money"] is None:
        flags_t.append("scale_unknown")
    money_scale = scale["money"] or 1.0
    facts, groups, subhead = [], [], ""
    mapped_stmts = []
    for r in rows[hdr_end:]:
        label = _strip_footnote(r[0]) if not parse_cell(r[0]) else ""
        hint = re.search(r"\(\s*(?:in\s+)?(thousands|millions|billions)[^)]*\)", label, re.I)
        row_scale = SCALE_WORDS[hint.group(1).lower()] if hint else None
        if hint:
            label = re.sub(r"\s*\(\s*(?:in\s+)?(thousands|millions|billions)[^)]*\)", "", label, flags=re.I).strip()
        cells = r[1:] if label or not parse_cell(r[0]) else r
        parsed = [(parse_cell(c), c) for c in cells]
        parsed = [(p, c) for p, c in parsed if p is not None]
        if not parsed:
            if label:
                subhead = label.rstrip(":")
            continue
        # split money-like vs percent-like columns
        money = [p for p, _ in parsed if p.kind in ("number", "nil", "multiple", "bps")]
        pcts = [p for p, _ in parsed if p.kind == "percent"]
        concept, score = match_concept(label, stmt)
        if not concept and subhead:
            concept, score = match_concept(f"{subhead} {label}", stmt)
        dims = {}
        seg_mode = stmt in ("SEG", "GEO", "REV") or re.search(r"by (segment|geograph|region|product|customer)", subhead.lower() + caption.lower())
        score_flag = None
        if seg_mode and label.lower().startswith("total"):
            if not concept:
                concept, score = "Revenues", 0.5                      # bare "Total" row in a segment table
        elif seg_mode:
            axis = next((a for a, rx in DIM_AXIS if re.search(rx, (subhead + " " + caption + " " + stmt).lower())), "segment")
            sub_is_member = bool(subhead) and not match_concept(subhead)[0]
            if concept and sub_is_member:                             # "Americas:" -> "Net sales" / "Operating income"
                dims = {axis: subhead}
            elif not concept:                                         # member rows: "iPhone", "Industrial", ...
                base = match_concept(subhead)[0] or match_concept(caption)[0] or "Revenues"
                dims = {axis: label}
                concept, score, score_flag = base, 0.5, "concept_assumed"
        if concept in ("LongTermDebtNoncurrent", "LongTermDebtCurrent") and subhead:
            if re.search(r"non-?\s?current liabilities", subhead, re.I): concept = "LongTermDebtNoncurrent"
            elif re.search(r"\bcurrent liabilities\b", subhead, re.I): concept = "LongTermDebtCurrent"
        if stmt == "TAX" and concept and concept not in _TAX_CONCEPTS and not label.lower().startswith("total"):
            concept = None                                  # a deferred-tax COMPONENT ("Deferred revenue" in the tax note) is not the balance-sheet item
        if subhead and re.search(r"non-?\s?current", subhead, re.I):          # "Marketable securities" under "Non-current assets:"
            concept = {"ShortTermInvestments": "MarketableSecuritiesNoncurrent", "PrepaidExpenseAndOtherAssetsCurrent": "OtherAssetsNoncurrent",
                       "AccruedLiabilitiesCurrent": "OtherLiabilitiesNoncurrent"}.get(concept, concept)
        if concept in ("EarningsPerShareBasic", "EarningsPerShareDiluted") and subhead and \
                re.search(r"shares used|weighted|number of shares|shares outstanding", subhead, re.I):      # "Basic"/"Diluted" in the SHARE-COUNT block
            concept = ("WeightedAverageNumberOfSharesOutstandingBasic" if concept.endswith("Basic")
                       else "WeightedAverageNumberOfDilutedSharesOutstanding")
        key = concept or "custom:" + ("tax_" if stmt == "TAX" else "") + re.sub(r"\s+", "_", norm(label))[:50]
        flags = list(flags_t) + ([] if concept else ["unmapped_label"])
        if score_flag: flags.append(score_flag)
        spec = CONCEPTS.get(key)
        if spec: mapped_stmts.append(spec["stmt"])
        is_total = label.lower().startswith("total") or key in AGG_CONCEPTS
        row_facts = {}
        def emit(p, per, kind_override=None, concept_key=None):
            ck = concept_key or key
            sp = CONCEPTS.get(ck)
            unit, scale_applied = "USD", (row_scale or money_scale)
            if p.kind == "percent": unit, scale_applied = "percent", 1.0
            elif p.kind == "bps": unit, scale_applied = "bps", 1.0
            elif p.kind == "multiple": unit, scale_applied = "multiple", 1.0
            elif sp and sp["unit"] == "USD/share" or re.search(r"per (diluted |basic |common )?share|per-share", label.lower()):
                unit, scale_applied = "USD/share", 1.0
            elif sp and sp["unit"] == "shares" or re.search(r"\bshares\b.*(outstanding|weighted)|weighted.*shares", label.lower()):
                unit, scale_applied = "shares", row_scale or scale["shares"] or money_scale
            elif sp and sp["unit"] == "count":
                unit, scale_applied = "count", 1.0
            elif p.currency and p.currency != "USD":
                unit = p.currency
            v = p.value * scale_applied
            if sp and sp["abs"]: v = abs(v)
            f = Fact(concept=ck, label=r[0], value=v, unit=unit, scale=scale_applied,
                     precision=(10 ** -p.decimals) * scale_applied, period=per["id"], ptype=per["ptype"],
                     end=per["end"], months=per["months"], fy=per["fy"], dims=dict(dims), stmt=(sp or {}).get("stmt") or stmt,
                     section=section, source="table", location=f"table#{tidx}", context=" | ".join(r)[:300],
                     table_no=table_no, table_title=title, column=per.get("col", ""),
                     confidence=score if concept else 0.4, is_total=is_total, parens_negative=p.neg_parens, flags=list(flags))
            if p.kind == "nil": f.flags.append("printed_as_dash")
            return f
        if metric_cols:                                       # rows = members, columns = metrics
            cell_list = [p for p, _ in parsed]
            for mk, p in zip(metric_cols, cell_list):
                if mk and p.kind != "percent":
                    f = emit(p, periods[0], concept_key=mk); f.dims = {"segment": label} if not label.lower().startswith("total") else {}
                    f.flags.append("metric_column_table"); facts.append(f)
            continue
        if len(money) >= len(periods):
            for per, p in zip(periods, money[:len(periods)]):
                f = emit(p, per); facts.append(f); row_facts[per["id"]] = f
        elif money:
            flags.append("column_count_mismatch")
            for per, p in zip(periods, money):
                f = emit(p, per); f.flags.append("column_count_mismatch"); facts.append(f); row_facts[per["id"]] = f
        if pcts:
            pk = PCT_TWIN.get(key, key + ":pct") if (concept or label) else "custom:pct"
            for per, p in zip(periods, pcts[:len(periods)]):
                f = emit(p, per, concept_key=pk); f.flags.append("percent_column"); facts.append(f)
        if row_facts:
            groups.append(dict(label=label, concept=key, is_total=is_total, facts=row_facts, dims=dict(dims)))
    # statement fallback from mapped concepts
    if not stmt and mapped_stmts:
        stmt = max(set(mapped_stmts), key=mapped_stmts.count)
        for f in facts:
            f.flags.append("stmt_inferred")                    # the caption did not say which statement this table is
            if not f.stmt: f.stmt = stmt
    # instants for balance sheet-ish tables without 'as of'
    if stmt == "BS":
        for f in facts:
            if f.ptype == "duration":
                f.ptype = "instant"; f.months = 0
                f.period, f.fy = make_period("instant", date.fromisoformat(f.end), 0, doc["fy_end_month"])
    return facts, groups
