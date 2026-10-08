"""
Pre-computed statistical findings handed to the LLM *as facts* (Layer 4 of the Reddit post), plus a cross-statement
red-flag screen. The LLM interprets; it never has to detect.
"""
from .config import INFLECTION_THRESHOLD
from .derived import Lookup

def fmt(v, unit):
    if unit == "percent": return f"{v:.1f}%"
    if unit == "bps": return f"{v:.0f} bps"
    if unit in ("multiple",): return f"{v:.2f}x"
    if unit == "days": return f"{v:.0f} days"
    if unit == "USD/share": return f"${v:.2f}"
    if unit in ("count", "shares"): return f"{v:,.0f}"
    a = abs(v)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= div: return f"{'-' if v < 0 else ''}${a / div:,.2f}{suf}"
    return f"${v:,.2f}"

def get_series(fg, concept, dims=None):
    """Annual (12M or instant) series sorted by period end: [(end, fid)]."""
    out = []
    for n, d in fg.facts(lambda d: d["concept"] == concept and d["source"] != "text" and d["role"] in ("level", "derived")
                         and (d["dims"] == (dims or {})) and (d["ptype"] == "instant" or d["months"] in (12, 13))):
        out.append((d["end"], n, d["period"]))
    out.sort()
    seen, res = set(), []
    for e, n, per in out:
        if per in seen: continue
        seen.add(per); res.append((e, n))
    return res

def series_findings(fg, series):
    if len(series) < 2: return []
    pts = [(e, n, fg.F(n)) for e, n in series]
    u = pts[0][2]["unit"]; out = []
    vals = [p[2]["value"] for p in pts]
    for i in range(1, len(pts)):
        a, b = vals[i - 1], vals[i]
        if u == "percent":
            out.append(f"{pts[i][2]['period']}: {fmt(b, u)} vs {fmt(a, u)} ({(b - a) * 100:+.0f} bps) [{pts[i][1]}]")
        elif a:
            out.append(f"{pts[i][2]['period']}: {(b / a - 1) * 100:+.1f}% YoY ({fmt(a, u)} -> {fmt(b, u)}) [{pts[i][1]}]")
        if a and b and (a > 0) != (b > 0):
            out.append(f"SIGN FLIP in {pts[i][2]['period']}: {fmt(a, u)} -> {fmt(b, u)} [{pts[i][1]}]")
    for i in range(2, len(pts)):                         # inflection vs local average (post, Layer 4)
        prev = (vals[i - 2] + vals[i - 1]) / 2
        if prev and u != "percent":
            ch = (vals[i] - prev) / abs(prev)
            if abs(ch) > INFLECTION_THRESHOLD:
                out.append(f"INFLECTION {pts[i][2]['period']}: {'spike' if ch > 0 else 'drop'} of {abs(ch) * 100:.0f}% vs prior-2-period average [{pts[i][1]}]")
    if vals[0] and u != "percent" and len(vals) >= 3 and vals[0] > 0 and vals[-1] > 0:
        yrs = len(vals) - 1
        out.append(f"CAGR {pts[0][2]['period']}->{pts[-1][2]['period']}: {((vals[-1] / vals[0]) ** (1 / yrs) - 1) * 100:.1f}%")
    if vals[0]:
        tot = (vals[-1] - vals[0]) / abs(vals[0]) * 100
        if u != "percent":
            direction = "increasing" if tot > 10 else "decreasing" if tot < -10 else "stable"
            strength = "strong" if abs(tot) > 50 else "moderate" if abs(tot) > 20 else "weak"
            out.append(f"TREND: {direction} ({strength}), {tot:+.0f}% over the window")
    return out

FLAG_LABELS = {"EARNINGS_QUALITY": "Earnings quality", "COVERAGE": "Interest coverage", "COVERAGE_DROP": "Interest coverage drop",
               "LIQUIDITY": "Liquidity", "LEVERAGE": "Leverage", "GOODWILL": "Goodwill weight", "SBC": "Stock compensation",
               "TAX_RATE": "Tax rate", "NEG_FCF": "Negative free cash flow", "PAYOUT": "Shareholder payout vs free cash flow",
               "MARGIN_GM": "Gross margin decline", "MARGIN_OM": "Operating margin decline", "AR_VS_REV": "Receivables vs revenue",
               "INV_VS_COGS": "Inventory vs cost of sales", "DILUTION": "Share dilution", "IDENTITY_FAIL": "Accounting identity check",
               "NARRATIVE_MISMATCH": "Text vs table mismatch", "NARRATIVE_DIFFERS": "Text differs from table",
               "REVENUE_DECLINE": "Revenue decline", "OPINC_DECLINE": "Operating income decline", "OCF_DECLINE": "Operating cash flow decline"}

def red_flags(fg):
    lk, flags = Lookup(fg), []
    fys = sorted({k[1] for k in lk.m})
    def g(name, fy, kind="flow"): return lk.get(name, fy, kind)
    def add(sev, code, text, *fids): flags.append(dict(severity=sev, code=code, label=FLAG_LABELS.get(code, code), text=text, facts=[f for f in fids if f]))
    for fy in fys[-3:]:
        fid, c = g("CashConversion", fy)
        if c and c["value"] < 0.8: add("medium", "EARNINGS_QUALITY", f"FY{fy}: operating cash flow is only {c['value']:.2f}x net income (accrual-heavy earnings).", fid)
        fid, ic = g("InterestCoverage", fy)
        if ic and ic["value"] < 3: add("high" if ic["value"] < 1.5 else "medium", "COVERAGE", f"FY{fy}: interest coverage {ic['value']:.1f}x.", fid)
        fid, cr = g("CurrentRatio", fy, "stock")
        if cr and cr["value"] < 1: add("medium", "LIQUIDITY", f"FY{fy}: current ratio {cr['value']:.2f} (<1).", fid)
        fid, lev = g("NetDebtToEbitda", fy, "stock")
        if lev and lev["value"] > 3: add("high" if lev["value"] > 4.5 else "medium", "LEVERAGE", f"FY{fy}: net debt / EBITDA {lev['value']:.1f}x.", fid)
        fid, gw = g("GoodwillToAssetsPct", fy, "stock")
        if gw and gw["value"] > 30: add("low", "GOODWILL", f"FY{fy}: goodwill is {gw['value']:.0f}% of total assets (impairment sensitivity).", fid)
        fid, sbc = g("SbcIntensityPct", fy)
        if sbc and sbc["value"] > 10: add("low", "SBC", f"FY{fy}: stock comp is {sbc['value']:.1f}% of revenue.", fid)
        fid, etr = g("EffectiveTaxRatePct", fy)
        if etr and not 12 <= etr["value"] <= 30: add("low", "TAX_RATE", f"FY{fy}: effective tax rate {etr['value']:.1f}% is outside the typical 12-30% band.", fid)
        fid, fcf = g("FreeCashFlow", fy)
        if fcf and fcf["value"] < 0: add("high", "NEG_FCF", f"FY{fy}: free cash flow negative ({fmt(fcf['value'], 'USD')}).", fid)
        fid2, ret = g("ShareholderReturns", fy)
        if fcf and ret and fcf["value"] > 0 and ret["value"] > fcf["value"] * 1.1:
            add("medium", "PAYOUT", f"FY{fy}: dividends+buybacks ({fmt(ret['value'], 'USD')}) exceed free cash flow ({fmt(fcf['value'], 'USD')}).", fid2, fid)
        elif fcf and ret and fcf["value"] > 0 and ret["value"] >= fcf["value"] * 0.9:
            add("low", "PAYOUT", f"FY{fy}: dividends+buybacks ({fmt(ret['value'], 'USD')}) are {ret['value'] / fcf['value'] * 100:.0f}% of free cash flow ({fmt(fcf['value'], 'USD')}); little room to absorb a downturn.", fid2, fid)
        if fy - 1 in fys:
            for name, lim, code, txt in (("GrossMarginPct", -2.0, "MARGIN_GM", "gross margin"), ("OperatingMarginPct", -3.0, "MARGIN_OM", "operating margin")):
                a, b = g(name, fy - 1)[1], g(name, fy)
                if a and b[1] and b[1]["value"] - a["value"] <= lim:
                    add("medium", code, f"FY{fy}: {txt} fell {abs(b[1]['value'] - a['value']) * 100:.0f} bps ({a['value']:.1f}% -> {b[1]['value']:.1f}%).", b[0])
            for name, base, code, txt in (("AccountsReceivableNetCurrent", "Revenues", "AR_VS_REV", "receivables"), ("InventoryNet", "CostOfRevenue", "INV_VS_COGS", "inventory")):
                kind_a = "stock"
                a1, a2 = g(name, fy - 1, kind_a)[1], g(name, fy, kind_a)
                b1, b2 = g(base, fy - 1)[1], g(base, fy)
                if a1 and a2[1] and b1 and b2[1] and a1["value"] and b1["value"]:
                    ga, gb = a2[1]["value"] / a1["value"] - 1, b2[1]["value"] / b1["value"] - 1
                    if ga - gb > 0.10:
                        add("medium", code, f"FY{fy}: {txt} grew {ga * 100:.0f}% vs {base} {gb * 100:.0f}% (collection / build-up risk).", a2[0], b2[0])
            def _sev(drop):          # severity scales with the size of the decline
                return "high" if drop >= 0.20 else "medium" if drop >= 0.08 else "low"
            for name, code, txt in (("Revenues", "REVENUE_DECLINE", "revenue"),
                                    ("OperatingIncomeLoss", "OPINC_DECLINE", "operating income"),
                                    ("NetCashProvidedByUsedInOperatingActivities", "OCF_DECLINE", "operating cash flow")):
                a, b = g(name, fy - 1)[1], g(name, fy)
                if a and b[1] and a["value"] and a["value"] > 0 and b[1]["value"] < a["value"]:
                    drop = 1 - b[1]["value"] / a["value"]
                    if drop >= 0.02:
                        add(_sev(drop), code, f"FY{fy}: {txt} fell {drop * 100:.1f}% ({fmt(a['value'], 'USD')} -> {fmt(b[1]['value'], 'USD')}).", b[0])
            ic1, ic2 = g("InterestCoverage", fy - 1)[1], g("InterestCoverage", fy)
            if ic1 and ic2[1] and ic1["value"] > 0 and ic2[1]["value"] <= ic1["value"] * 0.75:
                add("low" if ic2[1]["value"] >= 10 else "medium", "COVERAGE_DROP",
                    f"FY{fy}: interest coverage fell {(1 - ic2[1]['value'] / ic1['value']) * 100:.0f}% ({ic1['value']:.1f}x -> {ic2[1]['value']:.1f}x).", ic2[0])
            s1, s2 = g("WeightedAverageNumberOfDilutedSharesOutstanding", fy - 1)[1], g("WeightedAverageNumberOfDilutedSharesOutstanding", fy)
            if s1 and s2[1] and s1["value"] and s2[1]["value"] / s1["value"] - 1 > 0.03:
                add("low", "DILUTION", f"FY{fy}: diluted share count up {(s2[1]['value'] / s1['value'] - 1) * 100:.1f}%.", s2[0])
    for n, d in fg.G.nodes(data=True):
        if d.get("type") == "Validation" and d["status"] == "fail":
            add("high", "IDENTITY_FAIL", f"{d['period']}: '{d['name']}' fails by {fmt(d['diff'], 'USD')} (tolerance {fmt(d['tol'], 'USD')}). Possible parsing error or non-standard presentation.", *[t for _, t, k in fg.G.out_edges(n, keys=True) if k == "VALIDATES"])
    for n, d in fg.facts(lambda d: d["source"] == "text" and d["role"] == "level"):
        if "verified_by_table" in d["flags"] or "verified_other_period" in d["flags"]:
            continue
        tab = [(m, x) for m, x in fg.facts(lambda x: x["concept"] == d["concept"] and x["dims"] == d["dims"]
               and x["source"] != "text" and x["role"] != "shadowed" and x["unit"] == d["unit"]) if x["period"] == d["period"]]
        if not tab:
            continue
        cand = tab[0][1]
        if not cand["value"]:
            continue
        ratio = abs(d["value"] / cand["value"])
        if (ratio < 0.65 or ratio > 1.55) and "narrative_mismatch" not in d["flags"]:
            shown = f" The table shows {fmt(cand['value'], cand['unit'])} [{tab[0][0]}]."
            add("low", "NARRATIVE_DIFFERS", f"Text says '{d['label']}' for {d['concept']} {d['period']} ({d['context'][:90]}...).{shown} "
                "It may describe a narrower item than the statement line; verify before treating it as an error.", n, tab[0][0])
    for n, d in fg.facts(lambda d: "narrative_mismatch" in d["flags"]):
        change = d["role"] in ("change_pct", "change_abs") or d["unit"] == "bps"
        tgt = next((t for _, t, k in fg.G.out_edges(n, keys=True) if k == "CONTRADICTS"), None)
        if change:
            comp = d.get("computed_from_tables")
            add("medium", "NARRATIVE_MISMATCH", f"Text says '{d['label']}' ({d['context'][:90]}...) but the tables imply "
                + (f"{comp:.1f}." if comp is not None else "a different change."), n, tgt)
        else:   # a LEVEL in prose that differs from the statement line is often just a narrower item (e.g. 'foreign pretax earnings')
            shown = f" The table shows {fmt(fg.F(tgt)['value'], fg.F(tgt)['unit'])} [{tgt}]." if tgt else ""
            add("low", "NARRATIVE_DIFFERS", f"Text says '{d['label']}' for {d['concept']} {d['period']} ({d['context'][:90]}...).{shown} "
                "It may describe a narrower item than the statement line; verify before treating it as an error.", n)
    return flags
