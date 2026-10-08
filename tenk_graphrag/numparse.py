"""
Number recognition: every way a number can be *printed* in a 10-K.

  (1,234)  $(1,234)  -1,234  —  –  n/m  12.5%  (0.5)%  2.5x  150 bps  .75  $1.2 billion  three segments
"""
import re
from dataclasses import dataclass
from typing import Optional

NIL = {"—", "–", "-", "−", "―", "— —", "$—", "$ —", "$-", "$ -", "$–"}
NA = {"nm", "n/m", "n/a", "na", "*", "**", "not meaningful", "not applicable", "nmf"}
SCALE_WORDS = {"thousand": 1e3, "thousands": 1e3, "k": 1e3, "million": 1e6, "millions": 1e6, "mm": 1e6, "mn": 1e6,
               "m": 1e6, "billion": 1e9, "billions": 1e9, "bn": 1e9, "b": 1e9, "trillion": 1e12, "tn": 1e12}
WORD_NUMS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())}
WORD_NUMS.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
                  "ninety": 90, "hundred": 100})

_CELL = re.compile(
    r"^\s*(?P<p1>\()?\s*(?P<minus>[-−–])?\s*(?P<cur>[$€£¥]|US\$)?\s*(?P<p2>\()?\s*"
    r"(?P<num>\d[\d,]*(?:\.\d+)?|\.\d+)\s*(?P<unit>%|x|bps|bp)?\s*(?P<c1>\))?\s*(?P<pct2>%)?\s*(?P<c2>\))?\s*$", re.I)

@dataclass
class Cell:
    value: float
    raw: str
    neg_parens: bool = False
    kind: str = "number"      # number | percent | multiple | bps | nil
    decimals: int = 0
    currency: Optional[str] = None

def is_year_like(t: str) -> bool:
    return bool(re.fullmatch(r"(19|20)\d\d", t.strip()))

def parse_cell(text: str) -> Optional[Cell]:
    t = (text or "").replace("\u00a0", " ").strip()
    if not t:
        return None
    if t in NIL:
        return Cell(0.0, t, kind="nil")
    if t.lower() in NA:
        return None
    m = _CELL.match(t)
    if not m:
        return None
    num = m.group("num")
    dec = len(num.split(".")[1]) if "." in num else 0
    v = float(num.replace(",", ""))
    neg_parens = bool(m.group("p1") or m.group("p2"))
    neg = neg_parens or bool(m.group("minus"))
    unit = (m.group("unit") or "").lower()
    kind = "percent" if (unit == "%" or m.group("pct2")) else {"x": "multiple", "bps": "bps", "bp": "bps"}.get(unit, "number")
    cur = None
    if m.group("cur"):
        cur = {"$": "USD", "US$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}[m.group("cur").upper().replace("US$", "US$")]
    return Cell(-v if neg else v, t, neg_parens, kind, dec, cur)

# ---------------- scale detection ("(in thousands, except per share data)") ----------------
def detect_scale(text: str) -> dict:
    """-> {"money": 1e6, "shares": 1e6|1e3|1}. Defaults to 1 (unknown scale => flagged by caller)."""
    t = text.lower()
    out = {"money": None, "shares": None}
    m = re.search(r"(?:in|\$\s*in|dollars in|amounts in|usd in|expressed in)\s+(thousands|millions|billions)", t) or \
        re.search(r"\b(thousands|millions|billions)\s+of\s+(?:u\.?s\.?\s+)?dollars", t) or \
        re.search(r"\(\s*\$?\s*(thousands|millions|billions)\s*\)", t)
    if m:
        out["money"] = SCALE_WORDS[m.group(1)]
    m = re.search(r"\bshares?(?:\s+(?:are|is))?\s+(?:reflected\s+|expressed\s+|presented\s+)?in\s+(thousands|millions)", t) or \
        re.search(r"number of shares[^.;)]{0,40}?(?:reflected|expressed|presented)\s+in\s+(thousands|millions)", t) or \
        re.search(r"(thousands|millions)\s+of\s+shares", t)
    if m:
        out["shares"] = SCALE_WORDS[m.group(1)]
    elif out["money"] and re.search(r"except[^)]{0,80}(share|per share)", t):
        out["shares"] = out["money"]          # SEC convention: "(in thousands, except per share data)"
    return out

def money_to_base(num_str: str, scale_word: Optional[str]) -> tuple:
    v = float(num_str.replace(",", ""))
    dec = len(num_str.split(".")[1]) if "." in num_str else 0
    mult = SCALE_WORDS.get((scale_word or "").lower(), 1.0)
    return round(v * mult, 4), round((10 ** -dec) * mult, 6)
