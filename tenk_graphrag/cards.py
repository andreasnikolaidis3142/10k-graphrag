"""
Retrieval documents beyond plain paragraphs. Three general problems, three mechanisms:

1. CONTEXT LOSS: a paragraph cut out of a 10-K loses the heading that says what it is about ("Net revenue was
   $70.1 billion, up 28%." only makes sense under "CONSUMER & COMMUNITY BANKING"; a bullet only makes sense after its
   lead-in "Compensation expense increased driven by:").  -> HeadingContext gives every chunk a context path.

2. NUMBERS LOCKED IN TABLES: most hard numbers live only in tables, which a text retriever cannot see.
   -> table_cards() turns every table row into a self-describing "number card": where the table sits (context,
   title), what the row is, which column/period each value belongs to, the scale ("in millions"), and the value
   VERBALISED the way people say it ("$70,148" in millions -> "$70.1 billion") plus the year-over-year change.
   -> xbrl_cards() does the same for every inline-XBRL series, using the element's standard name ("Deposits",
   "Financing Receivable Allowance For Credit Loss ...") as built-in vocabulary, so a number is findable even when no
   table caption or taxonomy entry mentions it.

3. VOCABULARY MISMATCH: analysts and filings use different words for the same thing (NIM vs "net yield", buybacks vs
   "repurchases", ROE vs "return on equity"). -> expand_query() adds the filing-side synonyms to the lexical query.
"""
import re
from collections import Counter

# ------------------------------------------------------------------ cell / text helpers
FOOTNOTE = re.compile(r"^(\([a-z]{1,2}\))+$|^\*+$|^[¹²³⁴⁵⁶⁷⁸⁹]+$", re.I)
_NUMCELL = re.compile(r"^[\$€£]?\s?\(?-?\$?\s?[\d,]*\.?\d+\s?\)?\s?%?\)?$")
_DASH = {"—", "–", "-", "— %", "—%", "n/a", "N/A", "NM", "N/M", "nm"}
UNIT_NOTE = re.compile(r"\(?\s*(?:dollars |\$ |amounts |shares |\w+ )?in (thousands|millions|billions)\b|except (per share|ratio|where)", re.I)
BULLET = ("•", "–", "—", "◦", "▪", "●", "- ")

_YEARCELL = re.compile(r"^(?:FY\s?|Fiscal\s)?(19|20)\d{2}$", re.I)

def is_num(c):
    c = c.strip()
    return bool(_NUMCELL.match(c)) or c in _DASH

def is_val(c):
    """A value cell: numeric and not a bare year (a year in a table is a column header)."""
    return is_num(c) and not _YEARCELL.match(c.strip())

def _unit_only(c):
    """'(in millions, except ratios)' is a unit note; 'Aggregate purchase price (in millions)' is a column label."""
    c = c.strip()
    return bool(UNIT_NOTE.search(c)) and (c.startswith("(") or len(UNIT_NOTE.sub("", c).strip(" ()$,.:")) < 4)

def _to_float(c):
    neg = "(" in c or c.strip().startswith("-")
    m = re.search(r"[\d,]*\.?\d+", c)
    if not m:
        return None
    try:
        v = float(m.group(0).replace(",", ""))
    except ValueError:
        return None
    return -v if neg else v

def money(v):
    """Base-unit dollars -> '$70.1 billion'."""
    a = abs(v)
    for div, w in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million"), (1e3, "thousand")):
        if a >= div:
            return f"{'-' if v < 0 else ''}${a / div:,.1f} {w}"
    return f"{'-' if v < 0 else ''}${a:,.0f}"

def _scale_of(unit_text):
    m = re.search(r"in (thousands|millions|billions)", unit_text or "", re.I)
    return {"thousands": 1e3, "millions": 1e6, "billions": 1e9}.get(m.group(1).lower()) if m else None

# ------------------------------------------------------------------ 1. heading context
def _is_heading(s, footer):
    s = s.strip()
    if not (3 <= len(s) <= 90) or s.endswith((".", ";", ",")) or s.startswith(("(", "•", "–", "—", "*")):
        return False
    if footer(s) is not None or not re.search(r"[A-Za-z]{3}", s):
        return False
    return sum(ch.isdigit() for ch in s) <= len(s) * 0.5

class HeadingContext:
    """Tracks the heading path above the current block: a MAJOR heading (ALL CAPS or 'Item N'), a MINOR heading
    (short title-like line), and the LEAD-IN of a bullet list (a paragraph ending with ':')."""

    def __init__(self, footer=lambda s: None):
        self.major = self.minor = self.lead = ""
        self.footer = footer

    def see(self, text):
        """Feed a paragraph / single-cell table text. Returns True when it was a heading (not content)."""
        s = re.sub(r"\s+", " ", text).strip()
        if s.startswith(BULLET):
            return False
        if _is_heading(s, self.footer) and not s.endswith(":"):
            letters = [ch for ch in s if ch.isalpha()]
            if letters and (sum(ch.isupper() for ch in letters) / len(letters) > 0.85 or re.match(r"(Item|Note)\s+\d", s, re.I)):
                self.major, self.minor = s, ""
            else:
                self.minor = s
            self.lead = ""
            return True
        self.lead = s if s.endswith(":") else ""
        return False

    def path(self, text="", section=""):
        parts = [p for p in (self.major, self.minor) if p]
        if text.strip().startswith(BULLET) and self.lead:
            parts.append(self.lead[:160])
        return " > ".join(parts)

# ------------------------------------------------------------------ 2a. table row cards
def _header_labels(headers, n):
    """Column labels for n value columns from the header rows; spanning headers (a segment name over 3 year columns)
    are expanded."""
    col = [""] * n
    for h in headers:
        cells = [c for c in h if c and not _unit_only(c) and not FOOTNOTE.match(c)]
        if not cells or (len(cells) == 1 and n > 1):            # a single-cell row is a title, not a column label
            continue
        if len(cells) > n:
            cells = cells[-n:]
        elif n % len(cells) and len(cells) > 1 and n % (len(cells) - 1) == 0:
            cells = cells[1:]                                   # a stub label such as "Year ended December 31,"
        if not cells or n % len(cells):
            continue
        span = n // len(cells)
        for j in range(n):
            col[j] = (col[j] + " " + cells[j // span]).strip()
    return col

def _yoy(col, vals, scale, pct_row):
    """'2023 vs 2022: +28.0%' when the first two columns are consecutive years of the same thing."""
    if len(vals) < 2 or len(col) < 2 or pct_row:
        return ""
    y = [re.search(r"\b(19|20)\d{2}\b", c or "") for c in col[:2]]
    if not all(y) or col[0].replace(y[0].group(0), "") != col[1].replace(y[1].group(0), ""):
        return ""
    a, b = _to_float(vals[0]), _to_float(vals[1])
    if a is None or b is None or not b:
        return ""
    return f"; {y[0].group(0)} vs {y[1].group(0)}: {(a / b - 1) * 100:+.1f}%" + (f" ({money((a - b) * scale)})" if scale else "")

def table_cards(rows, context="", title="", caption=""):
    """-> [card text] for one table: one card per data row."""
    rows = [[c for c in r if c and not FOOTNOTE.match(c.strip())] for r in rows]
    rows = [r for r in rows if r]
    data = [i for i, r in enumerate(rows) if len(r) >= 2 and any(is_val(c) for c in r[1:])]
    if len(rows) < 2 or not data:
        return []
    n = Counter(sum(is_num(c) for c in rows[i][1:]) for i in data).most_common(1)[0][0]
    if n < 1:
        return []
    headers = rows[:data[0]]
    unit = next((c for r in rows[:data[0] + 1] for c in r if UNIT_NOTE.search(c)), "")
    if not unit:
        m = UNIT_NOTE.search(caption or "")
        unit = m.group(0) if m else ""
    scale = _scale_of(unit) or _scale_of(caption)
    col = _header_labels(headers, n)
    titles = [h[0] for h in headers if len([c for c in h if not _unit_only(c)]) == 1 and not _unit_only(h[0])]
    head = " | ".join(x for x in (context, title if title and title not in context else "", " ".join(titles)[:100],
                                  (UNIT_NOTE.search(unit).group(0) if unit else "").strip("() ")) if x)
    cards, sub = [], ""
    for i, r in enumerate(rows):
        if i < data[0]:
            continue
        nums = [c for c in r[1:] if is_num(c)] if not is_num(r[0]) else [c for c in r if is_num(c)]
        if not any(is_val(c) for c in nums):                    # a sub-heading row ("Noncompensation expense:")
            if not nums:
                sub = " ".join(r)[:80].rstrip(":")
            continue
        label = r[0] if not is_num(r[0]) else (sub or "value")
        what = f"{sub} {label}"
        pct_row = bool(re.search(r"%|ratio|per share|margin|rate\b|yield|price", what, re.I))
        share_row = bool(re.search(r"\bshares?\b|\bunits?\b|employees|headcount", what, re.I)) and not pct_row
        parts = []
        for j, v in enumerate(nums[:n] if len(nums) >= n else nums):
            c = col[j] if j < len(col) else ""
            x = _to_float(v)
            cs = _scale_of(c) if _scale_of(c) else (None if re.search(r"per share|price|number of|shares|%|ratio", c, re.I) else scale)
            verbal = ""
            if cs and x is not None and "%" not in v and not pct_row:
                verbal = f" ({x * cs / 1e6:,.1f} million)" if share_row else f" ({money(x * cs)})"
            parts.append(f"{c + ': ' if c else ''}{v}{verbal}")
        lab = f"{sub} — {label}" if sub and sub != label else label
        cards.append(f"{head} || {lab}: " + "; ".join(parts) + _yoy(col, nums, scale, pct_row))
    return cards

# ------------------------------------------------------------------ 2b. XBRL series cards
def humanize(name):
    name = name.split(":")[-1]
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)
    return name.replace(" And ", " and ").replace(" Of ", " of ").replace(" To ", " to ").replace(" In ", " in ")

def _fmt(v, unit):
    if unit == "percent":
        return f"{v:.1f}%"
    if unit == "USD/share":
        return f"${v:.2f}"
    if unit in ("shares", "count"):
        return f"{v:,.0f}" + (f" ({v / 1e9:.2f} billion)" if abs(v) >= 1e9 else f" ({v / 1e6:.1f} million)" if abs(v) >= 1e6 else "")
    if unit == "USD":
        return f"{v:,.0f} dollars ({money(v)})"
    return f"{v:,.4g} {unit}"

def xbrl_cards(fg):
    """-> [(card id, text)] one card per inline-XBRL series (element + dimensions), periods newest first."""
    groups = {}
    for n, d in fg.facts(lambda d: d["source"] == "ixbrl" and d["role"] in ("level", "shadowed")):
        elem = (d.get("location") or "").replace("ix:", "")
        if not elem:
            continue
        key = (elem, tuple(sorted(d["dims"].items())))
        g = groups.setdefault(key, {"facts": {}, "where": set()})
        g["facts"].setdefault(d["period"], (d["end"], d["value"], d["unit"]))
        for t in d.get("appears_in") or []:
            if isinstance(t, dict):                                # {'table_title': ..., 'row': ...} -> "title: row"
                t = ": ".join(x for x in (t.get("table_title") or f"table {t.get('table_no', '')}", t.get("row", "")) if x)
            g["where"].add(str(t)[:70])
    out = []
    for k, ((elem, dims), g) in enumerate(sorted(groups.items())):
        pts = sorted(g["facts"].items(), key=lambda kv: kv[1][0], reverse=True)[:4]
        unit = pts[0][1][2]
        dim_txt = ", ".join(f"{humanize(a)} = {humanize(m)}" for a, m in dims)
        vals = "; ".join(f"{per}: {_fmt(v, u)}" for per, (_, v, u) in pts)
        yoy = ""
        if len(pts) >= 2 and pts[1][1][1] and unit not in ("percent",) and pts[0][0].startswith("FY") == pts[1][0].startswith("FY"):
            a, b = pts[0][1][1], pts[1][1][1]
            yoy = f"; change {pts[1][0]} -> {pts[0][0]}: {(a / b - 1) * 100:+.1f}%" if b else ""
        where = (" | shown in: " + "; ".join(sorted(g["where"])[:2])) if g["where"] else ""
        scope = "slice" if dims else "total"                       # a segment/product/region slice vs the company total
        text = f"{'Company total: ' if scope == 'total' else ''}{humanize(elem)}{' [' + dim_txt + ']' if dim_txt else ''} ({elem}): {vals}{yoy}{where}"
        out.append((f"X{k:05d}", text, scope))
    return out

_GENERIC_MEMBERS = re.compile(r"consolidat|reconcil|eliminat|operating segment|corporate non|intersegment|parent|subsidiar|"
                              r"scenario|range|minimum|maximum|weighted average|revenue|income|expense|\bsales\b", re.I)

def _scope_norm(s):
    s = re.sub(r"(?<=[a-z])and(?=[A-Z])", "And", s)                  # 'AssetandWealth' -> 'AssetAndWealth'
    return re.sub(r"\s+", " ", re.sub(r"&|\band\b", " ", s.lower())).strip()
_SCOPE_AXES = re.compile(r"segment|geograph|productorservice|region|countr|businessunit|reportingunit", re.I)

def member_words(ix_facts):
    """Segment / product / region names of THIS filing, from the members of its scope axes (not instrument types such as
    'commercial paper' or equity components such as 'retained earnings')."""
    out = set()
    for f in ix_facts:
        for ax, m in (f.dims or {}).items():
            if not _SCOPE_AXES.search(str(ax)):
                continue
            w = _scope_norm(humanize(re.sub(r"(?<=[a-z])and(?=[A-Z])", "And", re.sub(r"(Segment)?(Member)?$", "", str(m)))))
            w = re.sub(r"\b([a-z]) (?=[a-z]{2})", r"\1", w)            # 'i phone' -> 'iphone'
            if len(w) > 3 and not _GENERIC_MEMBERS.search(w):
                out.add(w)
    return out

def card_scope(card_text, members):
    """'slice' when a table-row card is about one segment / product / region; '' (neutral) otherwise. A 'Total ...'
    row stays neutral even inside a segment table: it is the consolidated figure."""
    head, _, rest = card_text.partition(" || ")
    label = _scope_norm(rest.split(":")[0])
    if label.startswith("total") and not any(m in label for m in members):
        return ""
    hay = f"{_scope_norm(head)} {label}"
    return "slice" if any(re.search(r"(?<![a-z])" + re.escape(m) + r"(?![a-z])", hay) for m in members) else ""

# ------------------------------------------------------------------ 4. scope of a question
SCOPE_WORDS = re.compile(r"\bsegments?\b|\bregions?\b|geograph|\bproducts?\b|\bdivisions?\b|\bbusiness(es)? (unit|line)|"
                         r"\binternational\b|\bdomestic\b|\bby (country|market)\b|\bcountr(y|ies)\b", re.I)

def asks_for_slice(q, members=()):
    """True when the question names a segment / product / region (or a known dimension member)."""
    ql = q.lower().replace("-", "")
    return bool(SCOPE_WORDS.search(q)) or any(len(m) > 3 and m.lower() in ql for m in members)

# ------------------------------------------------------------------ 5. plain-English gloss for the reranker
# The cross-encoder reads the question literally; analyst jargon ("capex", "top line") is glossed in plain words.
JARGON = [
    (r"\bcapex\b", "capital expenditures, payments for property, plant and equipment"),
    (r"\btop line\b", "total revenue, net sales"),
    (r"\bbottom line\b", "net income"),
    (r"(?<!operating )(?<!gross )\bprofit\b(?! margin| rate)", "net income"),
    (r"\bbuy ?backs?\b|buying back", "repurchases of common stock"),
    (r"owe (its |their )?suppliers", "accounts payable"),
    (r"\btrade receivables\b", "accounts receivable"),
    (r"\bnet interest margin\b|\bnim\b", "net yield on interest-earning assets"),
    (r"\broe\b", "return on equity"),
    (r"\beps\b", "earnings per share"),
    (r"efficiency ratio", "overhead ratio"),
    (r"loan book", "total loans"),
    (r"reserves? (held )?against loan losses", "allowance for credit losses"),
    (r"set aside for (expected )?credit losses", "provision for credit losses"),
    (r"fee and other non-interest revenue", "noninterest revenue"),
    (r"operating profit", "operating income"),
    (r"cash (did )?(the )?operations generate|operating cash flow", "net cash provided by operating activities"),
    (r"interest expense .*borrowings", "interest expense on debt"),
    (r"income tax charge", "provision for income taxes"),
]
_JARGON = [(re.compile(p, re.I), g) for p, g in JARGON]

def gloss_query(q):
    gl = [g for rx, g in _JARGON if rx.search(q)]
    return f"{q} ({'; '.join(gl)})" if gl else q

# ------------------------------------------------------------------ 3. query vocabulary expansion
# (analyst wording -> wording 10-K filings use). Generic finance vocabulary, no company names.
FIN_SYNONYMS = [
    (r"\bnet interest margin\b|\bnim\b", "net yield interest-earning assets"),
    (r"\bbuy ?backs?\b|\bbuying back\b|bought back", "repurchase repurchases repurchased common stock"),
    (r"\broe\b|\breturn on (common |average )?equity\b", "roe return on equity"),
    (r"\befficiency ratio\b", "overhead ratio noninterest expense percentage of total net revenue"),
    (r"\bcapex\b|capital expenditure|invested in (property|capital)", "capital expenditures purchases payments property plant equipment"),
    (r"\btop line\b|total revenue|\bsales\b", "revenue revenues net sales total net revenue"),
    (r"\bbottom line\b|\bprofit\b(?! margin)", "net income earnings"),
    (r"\beps\b|earnings per share", "earnings per share diluted basic"),
    (r"\bheadcount\b|employ|\bpeople\b|workforce", "employees associates headcount"),
    (r"cash (did )?(the )?operations generate|operating cash flow|cash flow from operations", "net cash provided by operating activities"),
    (r"loan book|total loans|\bloans\b", "loans retained total loans"),
    (r"reserves? (held )?against loan losses|loan loss reserve", "allowance for credit losses allowance for loan losses"),
    (r"set aside for (expected )?credit losses|credit loss provision", "provision for credit losses"),
    (r"stock-based|share-based|equity compensation", "stock-based share-based compensation expense"),
    (r"\bowe(s|d)? (its )?suppliers\b|\bpayables?\b", "accounts payable"),
    (r"\btrade receivables?\b|\breceivables?\b", "accounts receivable"),
    (r"book equity|shareholders'? equity|stockholders'? equity", "total stockholders equity shareholders equity"),
    (r"size of the balance sheet|total assets|how large was the balance sheet", "total assets"),
    (r"income before tax|pre-?tax income", "income before income taxes provision for income taxes"),
    (r"tax charge|tax provision|income tax expense", "provision for income taxes income tax expense"),
    (r"effective(ly)? (tax )?rate|tax rate", "effective tax rate statutory"),
    (r"\bdividends?\b|\bpaid out\b", "dividends declared paid cash dividends"),
    (r"matures? within|due within (one|the next) year|current portion", "current portion long-term debt due within one year current maturities"),
    (r"short-term borrowings|commercial paper", "short-term borrowings commercial paper"),
    (r"remaining performance obligations?|\bbacklog\b", "remaining performance obligations backlog"),
    (r"impairment", "impairment charges impairments"),
    (r"acquisitions?\b", "acquisitions acquisition of businesses net of cash acquired"),
    (r"non-?interest revenue|fee and other non-interest", "noninterest revenue noninterest income"),
    (r"non-?interest expense", "noninterest expense"),
    (r"employee compensation|compensation (cost|expense)", "compensation expense salaries benefits"),
    (r"net interest income|\bnii\b", "net interest income nii"),
    (r"cost of (goods|sales|revenue)|cost to produce", "cost of sales cost of revenue cost of goods sold"),
    (r"r&d|research and development", "research and development"),
    (r"sg&a|selling, general", "selling general and administrative"),
    (r"depreciation|amortization|\bd&a\b", "depreciation amortization depletion"),
    (r"operating (profit|income)|\bebit\b", "operating income"),
    (r"deferred revenue|unearned revenue", "deferred revenue contract liabilities"),
    (r"lease (liabilit|obligation|payment)", "operating lease liabilities lease payments"),
    (r"repaid|repayments?", "repayments of long-term debt"),
    (r"raised|issued|issuance", "proceeds from issuance"),
    (r"guidance|outlook|expects?|next year", "expects outlook approximately"),
    (r"deposits?", "deposits"),
    (r"accumulated other comprehensive", "accumulated other comprehensive income loss"),
    (r"treasury stock", "treasury stock"),
    (r"goodwill", "goodwill"),
    (r"segment", "segment segments reportable"),
]
_SYN = [(re.compile(p, re.I), add) for p, add in FIN_SYNONYMS]

def expand_query(q):
    """The question plus filing-side vocabulary for the concepts it mentions (lexical retrieval only)."""
    extra = [add for rx, add in _SYN if rx.search(q)]
    return q + (" " + " ".join(extra) if extra else "")
