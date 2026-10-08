"""
Filing loader: SEC HTML / inline-XBRL / markdown / plain text  ->  ordered blocks + (optional) iXBRL facts.

Block = {"type": "heading"|"para"|"table", "text": str, "rows": list[list[str]], "idx": int, "section": str}
"""
import re
from datetime import date
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
from .models import Fact, make_period, parse_date
from .taxonomy import canonical, CONCEPTS

SECTION_RE = re.compile(r"^\s*(?:PART\s+[IV]+\b[\s.,:-]*)?ITEM\s+(\d{1,2}[A-C]?)\s*[.:\-–—]?\s*(.*)$", re.I)
ITEM_NAMES = {"1": "Business", "1A": "Risk Factors", "1B": "Unresolved Staff Comments", "2": "Properties",
              "3": "Legal Proceedings", "5": "Market/Equity", "7": "MD&A", "7A": "Market Risk",
              "8": "Financial Statements", "9A": "Controls", "15": "Exhibits"}
_PLACEHOLDER = "[[TABLE:{}]]"

def _clean_row(cells):
    """Merge SEC-style split cells: '$' | '1,234' | ')'  ->  '$1,234)' ; drop empties."""
    out, pending = [], ""
    for c in cells:
        c = re.sub(r"\s+", " ", c.replace("\u00a0", " ")).strip()
        if not c:
            continue
        if c in {"$", "€", "£", "(", "$(", "($", "US$"}:
            pending += c
            continue
        if c in {")", "%", ")%", "%)", "pts", "bps"} and out:
            out[-1] += c
            continue
        out.append(pending + c)
        pending = ""
    return out

def _is_html(raw: str, path: str) -> bool:
    return path.lower().endswith((".htm", ".html", ".xhtml")) or raw.lstrip()[:200].lower().count("<") > 3

def load_filing(path: str):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    ix_facts, ix_meta = [], {}
    if _is_html(raw, path):
        soup = BeautifulSoup(raw, "lxml")
        ix_facts, ix_meta = parse_ixbrl(soup)
        blocks = _blocks_from_html(soup)
    else:
        blocks = _blocks_from_text(raw)
    _assign_sections(blocks)
    meta: dict[str, str | None] = detect_meta(blocks)
    meta.update({k: v for k, v in ix_meta.items() if v})
    return blocks, ix_facts, meta

# ------------------------------------------------------------------ HTML
def _blocks_from_html(soup):
    for t in soup(["script", "style"]):
        t.decompose()
    for h in soup.find_all(re.compile(r"^ix:header$")):
        h.decompose()                                   # hidden contexts/units: not narrative
    tables = []
    for tb in soup.find_all("table"):
        rows = []
        for tr in tb.find_all("tr"):
            r = _clean_row([td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])])
            if r:
                rows.append(r)
        idx = len(tables)
        tables.append(rows)
        tb.replace_with(soup.new_string("\n" + _PLACEHOLDER.format(idx) + "\n"))
    for el in soup.find_all(["p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]):
        el.append("\n\n")                              # block boundary => paragraph boundary
    text = soup.get_text(" ")
    blocks, buf = [], []
    def flush():
        if buf:
            t = re.sub(r"\s+", " ", " ".join(buf)).strip()
            if t:
                blocks.append({"type": "para", "text": t, "idx": len(blocks)})
            buf.clear()
    for line in text.split("\n"):
        line = line.strip()
        m = re.fullmatch(r"\[\[TABLE:(\d+)\]\]", line)
        if m:
            flush()
            rows = tables[int(m.group(1))]
            if rows:
                blocks.append({"type": "table", "text": "", "rows": rows, "idx": len(blocks)})
        elif not line:
            flush()
        else:
            buf.append(line)
            if len(" ".join(buf)) > 1500 or line.endswith((".", ":")) and len(line) > 160:
                flush()
    flush()
    return blocks

# ------------------------------------------------------------------ text / markdown
def _blocks_from_text(raw):
    blocks, para, trows = [], [], []
    def fp():
        if para:
            blocks.append({"type": "para", "text": re.sub(r"\s+", " ", " ".join(para)).strip(), "idx": len(blocks)})
            para.clear()
    def ft():
        if trows:
            blocks.append({"type": "table", "text": "", "rows": [r for r in trows], "idx": len(blocks)})
            trows.clear()
    for line in raw.splitlines():
        s = line.strip()
        if "|" in s and s.count("|") >= 2:
            if re.fullmatch(r"[\|\s:\-]+", s):
                continue
            fp()
            trows.append(_clean_row([c for c in s.strip("|").split("|")]))
        else:
            ft()
            if not s:
                fp()
            elif len(s) < 140 and (SECTION_RE.match(s) or s.isupper() or s.endswith(":")):
                fp(); blocks.append({"type": "para", "text": s, "idx": len(blocks)})
            else:
                para.append(s)
    fp(); ft()
    return blocks

def _assign_sections(blocks):
    cur = ""
    for b in blocks:
        if b["type"] == "para":
            m = SECTION_RE.match(b["text"]) if len(b["text"]) < 200 else None
            if m:
                code = m.group(1).upper()
                cur = f"Item {code} {ITEM_NAMES.get(code, m.group(2)[:40])}".strip()
                b["type"] = "heading"
        b["section"] = cur

def detect_meta(blocks):
    head = " ".join(b["text"] for b in blocks[:60] if b["type"] != "table")[:6000]
    meta: dict[str, str | None] = {"fy_end": None, "company": None}
    m = re.search(r"fiscal\s+year\s+ended:?\s*([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})", head, re.I)
    if m:
        d = parse_date(m.group(1))
        if d: meta["fy_end"] = d.isoformat()
    for b in blocks[:80]:
        if b["type"] != "table" and "exact name of registrant" in b["text"].lower():
            name = re.split(r"\(\s*exact name", b["text"], flags=re.I)[0].strip(" .,-")
            name = re.sub(r"^.*?(?:commission file number[:\s]*[\d-]+|\b10-K\b|fiscal year ended[^A-Za-z]*[A-Za-z]+ \d{1,2}, \d{4})", "", name, flags=re.I).strip()
            meta["company"] = name[-70:] or None
            break
    return meta

# ------------------------------------------------------------------ inline XBRL
def _num_from_ix(el):
    txt = el.get_text(strip=True)
    fmt = (el.get("format") or "").lower()
    if "zerodash" in fmt or "fixed-zero" in fmt or txt in {"—", "-", "–"}:
        v = 0.0
    else:
        t = txt.replace(",", "").replace(" ", "")
        if "comma-decimal" in fmt or "numcommadecimal" in fmt:
            t = txt.replace(".", "").replace(",", ".")
        try: v = float(re.sub(r"[^\d.]", "", t))
        except ValueError: return None, 0
    dec = len(txt.split(".")[1].strip()) if "." in txt else 0
    scale = int(el.get("scale") or 0)
    v *= 10 ** scale
    if el.get("sign") == "-":
        v = -v
    return v, (10 ** (scale - dec))

def parse_ixbrl(soup):
    nf = soup.find_all(re.compile(r"^ix:nonfraction$"))
    if not nf:
        return [], {}
    ctx = {}
    for c in soup.find_all(re.compile(r"^xbrli:context$")):
        per = c.find(re.compile(r"xbrli:period"))
        inst = per.find(re.compile(r"xbrli:instant")) if per else None
        sd = per.find(re.compile(r"xbrli:startdate")) if per else None
        ed = per.find(re.compile(r"xbrli:enddate")) if per else None
        dims = {}
        for mem in c.find_all(re.compile(r"xbrldi:explicitmember")):
            axis = re.sub(r"Axis$", "", (mem.get("dimension") or "").split(":")[-1])
            dims[axis] = re.sub(r"Member$", "", mem.get_text(strip=True).split(":")[-1])      # "MembershipFeesMember" -> "MembershipFees"
        ctx[c.get("id")] = dict(instant=inst.get_text(strip=True) if inst else None,
                                start=sd.get_text(strip=True) if sd else None,
                                end=ed.get_text(strip=True) if ed else None, dims=dims)
    units = {}
    for u in soup.find_all(re.compile(r"^xbrli:unit$")):
        txt = u.get_text(" ", strip=True).lower()
        units[u.get("id")] = ("USD/share" if "/" in txt or "divide" in str(u).lower() else
                              "USD" if "usd" in txt else "shares" if "shares" in txt else
                              "percent" if "pure" in txt else txt or "pure")
    fy_end = None
    for el in soup.find_all(re.compile(r"^ix:nonnumeric$")):
        if (el.get("name") or "").endswith("DocumentPeriodEndDate"):
            d = parse_date(el.get_text(strip=True))
            if d: fy_end = d
    fy_month = fy_end.month if fy_end else 12
    facts = []
    for el in nf:
        c = ctx.get(el.get("contextref"))
        if not c:
            continue
        v, prec = _num_from_ix(el)
        if v is None:
            continue
        name = el.get("name", "")
        key = canonical(name) or name.split(":")[-1]
        unit = units.get(el.get("unitref"), "USD")
        try:
            if c["instant"]:
                end = date.fromisoformat(c["instant"]); pid, fy = make_period("instant", end, 0, fy_month); ptype, months, start = "instant", 0, ""
            else:
                s, e = date.fromisoformat(c["start"]), date.fromisoformat(c["end"])
                months = round((e - s).days / 30.4); pid, fy = make_period("duration", e, months, fy_month)
                end, ptype, start = e, "duration", s.isoformat()
        except (TypeError, ValueError):
            continue
        spec = CONCEPTS.get(key)
        if spec and spec["abs"]:
            v = abs(v)
        if unit == "percent":
            v *= 100; prec *= 100
        facts.append(Fact(concept=key, label=name, value=v, unit=unit, scale=10 ** int(el.get("scale") or 0),
                          precision=prec, period=pid, ptype=ptype, start=start, end=end.isoformat(), months=months,
                          fy=fy, dims=c["dims"], stmt=(spec or {}).get("stmt", ""), source="ixbrl",
                          location=f"ix:{name}", context=name, confidence=1.0,
                          flags=[] if spec else ["non_canonical_tag"]))
    return facts, {"fy_end": fy_end.isoformat() if fy_end else None}
