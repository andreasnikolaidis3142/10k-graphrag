"""Typed representation of a number. A Fact is a number that *knows what it is*."""
from dataclasses import dataclass, field, asdict
from datetime import date
import re

@dataclass
class Fact:
    id: str = ""
    concept: str = ""            # canonical key (us-gaap local name) or custom:<slug>
    label: str = ""              # label exactly as printed
    value: float = 0.0           # normalised to BASE units (dollars, shares, percent points, ...)
    unit: str = "USD"            # USD | USD/share | shares | percent | bps | ratio | multiple | count | pure
    scale: float = 1.0           # multiplier that was applied (1e3 for "in thousands")
    precision: float = 0.0       # smallest displayed unit in base units (rounding tolerance = precision/2)
    period: str = ""             # period id, see make_period
    ptype: str = "duration"      # duration | instant
    start: str = ""
    end: str = ""
    months: int = 0              # for durations
    fy: int = 0
    dims: dict = field(default_factory=dict)   # {"segment": "Americas"}
    stmt: str = ""               # IS BS CF EQ SEG GEO TAX DEBT LEASE EPS NONGAAP TEXT ...
    section: str = ""            # e.g. "Item 7 MD&A"
    source: str = "table"        # ixbrl | table | text | derived
    role: str = "level"          # level | change_abs | change_pct | guidance | threshold | contractual | prior_level | derived
    location: str = ""
    context: str = ""            # sentence / row text
    confidence: float = 1.0
    is_total: bool = False
    parens_negative: bool = False
    formula: str = ""
    flags: list = field(default_factory=list)
    # ---- provenance: WHERE in the filing this number came from
    table_no: int = 0            # 1-based ordinal of the table in the filing (0 = not from a table)
    table_title: str = ""        # nearest heading above the table, e.g. "CONSOLIDATED STATEMENTS OF OPERATIONS"
    column: str = ""             # the column header the number sat under, e.g. "September 30, 2023"
    page: int = 0                 # best-effort page number (from page footers in the filing; 0 = unknown)
    appears_in: list = field(default_factory=list)   # XBRL facts: tables where the same number is also displayed

    def to_dict(self):
        return asdict(self)

    def dims_key(self):
        return "|".join(f"{k}={v}" for k, v in sorted(self.dims.items()))


_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

def month_num(s: str) -> int:
    return _MONTHS[s[:3].lower()]

def fiscal_year_of(end: date, fy_end_month: int) -> int:
    return end.year + (1 if (fy_end_month != 12 and end.month > fy_end_month) else 0)

def make_period(ptype: str, end: date, months: int = 12, fy_end_month: int = 12):
    """-> (period_id, fy). IDs: FY2023 | Q2-2023 | 6M@2023-06-30 | @2023-12-31 (instant)."""
    fy = fiscal_year_of(end, fy_end_month)
    iso = end.isoformat()
    if ptype == "instant":
        return f"@{iso}", fy
    if months in (12, 13) or months >= 11:
        return f"FY{fy}", fy
    if months == 3:
        q = ((end.month - fy_end_month - 1) % 12) // 3 + 1
        return f"Q{q}-{fy}", fy
    return f"{months}M@{iso}", fy

def parse_date(text: str):
    """Find first full date in text -> date | None."""
    m = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", text, re.I)
    if m:
        try: return date(int(m.group(3)), month_num(m.group(1)), int(m.group(2)))
        except ValueError: return None
    m = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+(\d{4})", text, re.I)
    if m:
        try: return date(int(m.group(3)), month_num(m.group(2)), int(m.group(1)))
        except ValueError: return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        try: return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError: return None
    return None
