"""
Derived metrics with provenance. Every ratio is a *Fact node* with DERIVED_FROM edges to the exact input facts,
so the LLM never has to do arithmetic and every number it quotes can be traced back to a table cell.
"""
from .models import Fact
from .taxonomy import CONCEPTS

# (name, unit, label, formula text, inputs[(var, concept, kind, required)], fn)
# kind: flow = 12-month duration, stock = instant at fiscal year end, avg = average of this & prior stock
def _d(name, unit, label, formula, inputs, fn, skip_if_exists=False):
    return dict(name=name, unit=unit, label=label, formula=formula, inputs=inputs, fn=fn, skip=skip_if_exists)

R = lambda v, c, k="flow", req=True: (v, c, k, req)
DERIVED = [
    _d("GrossProfit", "USD", "Gross profit (derived)", "Revenues - CostOfRevenue", [R("r", "Revenues"), R("c", "CostOfRevenue")], lambda r, c: r - c, True),
    _d("Ebitda", "USD", "EBITDA (derived)", "OperatingIncome + D&A", [R("o", "OperatingIncomeLoss"), R("d", "DepreciationDepletionAndAmortization")], lambda o, d: o + d, True),
    _d("FreeCashFlow", "USD", "Free cash flow (derived)", "CFO - Capex", [R("o", "NetCashProvidedByUsedInOperatingActivities"), R("c", "PaymentsToAcquirePropertyPlantAndEquipment")], lambda o, c: o - abs(c), True),
    _d("GrossMarginPct", "percent", "Gross margin %", "GrossProfit / Revenues x 100", [R("g", "GrossProfit"), R("r", "Revenues")], lambda g, r: g / r * 100 if r else None),
    _d("OperatingMarginPct", "percent", "Operating margin %", "OperatingIncome / Revenues x 100", [R("o", "OperatingIncomeLoss"), R("r", "Revenues")], lambda o, r: o / r * 100 if r else None),
    _d("NetMarginPct", "percent", "Net margin %", "NetIncome / Revenues x 100", [R("n", "NetIncomeLoss"), R("r", "Revenues")], lambda n, r: n / r * 100 if r else None),
    _d("EbitdaMarginPct", "percent", "EBITDA margin %", "EBITDA / Revenues x 100", [R("e", "Ebitda"), R("r", "Revenues")], lambda e, r: e / r * 100 if r else None),
    _d("FcfMarginPct", "percent", "FCF margin %", "FCF / Revenues x 100", [R("f", "FreeCashFlow"), R("r", "Revenues")], lambda f, r: f / r * 100 if r else None),
    _d("EffectiveTaxRatePct", "percent", "Effective tax rate % (derived)", "IncomeTax / PreTaxIncome x 100", [R("t", "IncomeTaxExpenseBenefit"), R("p", "IncomeLossBeforeIncomeTaxes")], lambda t, p: t / p * 100 if p else None),
    _d("CashConversion", "multiple", "Cash conversion (CFO / Net income)", "CFO / NetIncome", [R("o", "NetCashProvidedByUsedInOperatingActivities"), R("n", "NetIncomeLoss")], lambda o, n: o / n if n and n > 0 else None),
    _d("RdIntensityPct", "percent", "R&D % of revenue", "R&D / Revenues x 100", [R("x", "ResearchAndDevelopmentExpense"), R("r", "Revenues")], lambda x, r: x / r * 100 if r else None),
    _d("SbcIntensityPct", "percent", "SBC % of revenue", "SBC / Revenues x 100", [R("x", "ShareBasedCompensation"), R("r", "Revenues")], lambda x, r: x / r * 100 if r else None),
    _d("CapexIntensityPct", "percent", "Capex % of revenue", "Capex / Revenues x 100", [R("x", "PaymentsToAcquirePropertyPlantAndEquipment"), R("r", "Revenues")], lambda x, r: abs(x) / r * 100 if r else None),
    _d("CurrentRatio", "multiple", "Current ratio", "CurrentAssets / CurrentLiabilities", [R("a", "AssetsCurrent", "stock"), R("l", "LiabilitiesCurrent", "stock")], lambda a, l: a / l if l else None),
    _d("TotalDebt", "USD", "Total debt (derived)", "LT debt + current debt + short-term borrowings + commercial paper", [R("a", "LongTermDebtNoncurrent", "stock"), R("b", "LongTermDebtCurrent", "stock", False), R("s", "ShortTermBorrowings", "stock", False), R("p", "CommercialPaper", "stock", False)], lambda a, b=0, s=0, p=0: a + (b or 0) + (s or 0) + (p or 0)),
    _d("NetDebt", "USD", "Net debt (derived; NEGATIVE = net cash)", "TotalDebt - Cash - ShortTermInvestments - NonCurrentMarketableSecurities", [R("d", "TotalDebt", "stock"), R("c", "CashAndCashEquivalentsAtCarryingValue", "stock"), R("s", "ShortTermInvestments", "stock", False), R("l", "MarketableSecuritiesNoncurrent", "stock", False)], lambda d, c, s=0, l=0: d - c - (s or 0) - (l or 0)),
    _d("DebtToEquity", "multiple", "Debt / equity", "TotalDebt / Equity", [R("d", "TotalDebt", "stock"), R("e", "StockholdersEquity", "stock")], lambda d, e: d / e if e and e > 0 else None),
    _d("NetDebtToEbitda", "multiple", "Net debt / EBITDA", "NetDebt / EBITDA", [R("n", "NetDebt", "stock"), R("e", "Ebitda")], lambda n, e: n / e if e and e > 0 else None),
    _d("InterestCoverage", "multiple", "Interest coverage (EBIT / interest)", "OperatingIncome / InterestExpense", [R("o", "OperatingIncomeLoss"), R("i", "InterestExpense")], lambda o, i: o / abs(i) if i else None),
    _d("RoePct", "percent", "ROE % (avg equity)", "NetIncome / avg(Equity) x 100", [R("n", "NetIncomeLoss"), R("e", "StockholdersEquity", "avg")], lambda n, e: n / e * 100 if e else None),
    _d("RoaPct", "percent", "ROA % (avg assets)", "NetIncome / avg(Assets) x 100", [R("n", "NetIncomeLoss"), R("a", "Assets", "avg")], lambda n, a: n / a * 100 if a else None),
    _d("AssetTurnover", "multiple", "Asset turnover", "Revenues / avg(Assets)", [R("r", "Revenues"), R("a", "Assets", "avg")], lambda r, a: r / a if a else None),
    _d("DSO", "days", "Days sales outstanding", "AR / Revenues x 365", [R("a", "AccountsReceivableNetCurrent", "stock"), R("r", "Revenues")], lambda a, r: a / r * 365 if r else None),
    _d("DIO", "days", "Days inventory outstanding", "Inventory / COGS x 365", [R("i", "InventoryNet", "stock"), R("c", "CostOfRevenue")], lambda i, c: i / c * 365 if c else None),
    _d("DPO", "days", "Days payables outstanding", "AP / COGS x 365", [R("p", "AccountsPayableCurrent", "stock"), R("c", "CostOfRevenue")], lambda p, c: p / c * 365 if c else None),
    _d("GoodwillToAssetsPct", "percent", "Goodwill % of assets", "Goodwill / Assets x 100", [R("g", "Goodwill", "stock"), R("a", "Assets", "stock")], lambda g, a: g / a * 100 if a else None),
    _d("ShareholderReturns", "USD", "Dividends + buybacks", "Dividends + Repurchases", [R("d", "PaymentsOfDividends", "flow", False), R("b", "PaymentsForRepurchaseOfCommonStock", "flow", False)], lambda d=0, b=0: (d or 0) + (b or 0)),
    _d("PayoutOfFcfPct", "percent", "Shareholder returns % of FCF", "Returns / FCF x 100", [R("s", "ShareholderReturns"), R("f", "FreeCashFlow")], lambda s, f: s / f * 100 if f and f > 0 else None),
]

class Lookup:
    """(concept, fy, kind) -> (fact id, fact dict). Only primary facts (no dims, not text).
    Choice: most TRUSTWORTHY fact first (XBRL > known scale > primary statement ...), then the later snapshot date."""
    def __init__(self, fg):
        from datetime import date
        self.fg, best = fg, {}
        for n, d in fg.facts(lambda d: not d["dims"] and d["source"] != "text" and d["role"] in ("level", "derived")):
            if d["ptype"] == "duration" and d["months"] in (12, 13): k = "flow"
            elif d["ptype"] == "instant": k = "stock"
            else: continue
            key = (d["concept"], d["fy"], k)
            rank = fg._trust_rank(n)[:-1] + (-date.fromisoformat(d["end"]).toordinal(),)
            if key not in best or rank < best[key][0]:
                best[key] = (rank, n)
        self.m = {k: v[1] for k, v in best.items()}
    def get(self, concept, fy, kind):
        fid = self.m.get((concept, fy, "stock" if kind == "avg" else kind))
        return (fid, self.fg.F(fid)) if fid else (None, None)

def add_derived_metrics(fg):
    lk = Lookup(fg)
    fys = sorted({k[1] for k in lk.m})
    for spec in DERIVED:
        for fy in fys:
            if spec["skip"] and (spec["name"], fy, "flow") in lk.m:
                continue
            vals, srcs, ok, partial = [], [], True, False
            for var, concept, kind, req in spec["inputs"]:
                fid, d = lk.get(concept, fy, kind)
                if d is None:
                    if req: ok = False; break
                    vals.append(None); partial = True; continue
                v = d["value"]
                if kind == "avg":
                    pid, pd = lk.get(concept, fy - 1, "stock")
                    if pd: v = (v + pd["value"]) / 2; srcs.append(pid)
                vals.append(v); srcs.append(fid)
            if not ok or not srcs: continue
            try:
                res = spec["fn"](*[v for v in vals])
            except (TypeError, ZeroDivisionError):
                res = None
            if res is None: continue
            base = fg.F(srcs[0])
            stock_out = all(k in ("stock",) for _, _, k, _ in spec["inputs"] if k != "avg") and spec["name"] in (
                "CurrentRatio", "TotalDebt", "NetDebt", "DebtToEquity", "GoodwillToAssetsPct")
            ref = next((fg.F(s) for s in srcs if fg.F(s)["ptype"] == ("instant" if stock_out else "duration")), base)
            f = Fact(concept=spec["name"], label=spec["label"], value=float(res), unit=spec["unit"], scale=1.0,
                     precision=0.005, period=ref["period"], ptype=ref["ptype"], end=ref["end"], months=ref["months"],
                     fy=fy, stmt="DERIVED", source="derived", role="derived", formula=spec["formula"],
                     context=spec["formula"], confidence=min(fg.F(s)["confidence"] for s in srcs),
                     flags=["derived"] + (["optional_inputs_missing"] if partial else []))
            fid = fg.add_fact(f)
            for s in srcs:
                fg.G.add_edge(fid, s, key="DERIVED_FROM")
            lk.m[(spec["name"], fy, "stock" if stock_out else "flow")] = fid
    # YoY growth for every flow/stock series with a PRIOR_PERIOD edge (incl. segment members)
    for n, d in list(fg.facts(lambda d: d["source"] in ("ixbrl", "table") and d["role"] == "level" and d["unit"] in ("USD", "shares", "USD/share", "count"))):
        for _, prev, k, e in fg.G.out_edges(n, keys=True, data=True):
            if k == "PRIOR_PERIOD" and e.get("pct") is not None:
                f = Fact(concept=d["concept"] + ":yoy", label=f"{d['label']} YoY %", value=e["pct"], unit="percent", precision=0.05,
                         period=d["period"], ptype=d["ptype"], end=d["end"], months=d["months"], fy=d["fy"], dims=dict(d["dims"]),
                         stmt="DERIVED", source="derived", role="derived", formula="(current / prior - 1) x 100", flags=["derived", "yoy"])
                fid = fg.add_fact(f)
                fg.G.add_edge(fid, n, key="DERIVED_FROM"); fg.G.add_edge(fid, prev, key="DERIVED_FROM")
