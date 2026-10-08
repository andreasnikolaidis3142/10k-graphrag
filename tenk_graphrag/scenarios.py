"""
Scenario engine (post sections 8-10). The LLM never ranks; we pre-compute projections, ranking, driver diffs vs the
baseline, and where scenarios converge/diverge. The LLM only interprets.
"""
import statistics
from .derived import Lookup
from .signals import fmt
from . import llm

def base_drivers(fg):
    lk = Lookup(fg)
    fy = max(k[1] for k in lk.m)
    def v(c, y=fy, k="flow"):
        fid, d = lk.get(c, y, k); return (d["value"] if d else None), fid
    rev, f_rev = v("Revenues"); prev, _ = v("Revenues", fy - 1)
    gp, _ = v("GrossProfit"); oi, _ = v("OperatingIncomeLoss"); da, _ = v("DepreciationDepletionAndAmortization")
    capex, _ = v("PaymentsToAcquirePropertyPlantAndEquipment"); intr, _ = v("InterestExpense")
    tax, _ = v("EffectiveTaxRatePct"); fcf, f_fcf = v("FreeCashFlow")
    if not rev: raise ValueError("Revenues not found - cannot build scenarios")
    gm = gp / rev if gp else None
    opex_pct = (gp - oi) / rev if gp and oi is not None else None
    return dict(fy=fy, revenue=rev, revenue_growth=(rev / prev - 1) if prev else 0.05, gross_margin=gm, opex_pct=opex_pct,
                da_pct=(da or 0) / rev, capex_pct=abs(capex or 0) / rev, interest=abs(intr or 0), tax_rate=(tax or 21) / 100,
                nwc_pct=0.10, sources=[f for f in (f_rev, f_fcf) if f], base_fcf=fcf)

def project(base, over, years=3):
    d = {**{k: base[k] for k in ("revenue_growth", "gross_margin", "opex_pct", "da_pct", "capex_pct", "tax_rate", "nwc_pct")}, **over}
    rev, rows = base["revenue"], []
    for i in range(1, years + 1):
        new = rev * (1 + d["revenue_growth"]); gp = new * d["gross_margin"]; ebit = gp - new * d["opex_pct"]
        ebt = ebit - base["interest"]; ni = ebt - max(0, ebt) * d["tax_rate"]
        fcf = ni + new * d["da_pct"] - new * d["capex_pct"] - (new - rev) * d["nwc_pct"]
        rows.append(dict(year=base["fy"] + i, revenue=new, ebit=ebit, op_margin=ebit / new * 100, net_income=ni, fcf=fcf)); rev = new
    return rows

def run_scenarios(fg, scenarios, years=3):
    base = base_drivers(fg)
    names = list(scenarios)
    res = {n: project(base, scenarios[n], years) for n in names}
    summ = {n: dict(cum_fcf=sum(r["fcf"] for r in rows), min_fcf=min(r["fcf"] for r in rows), avg_op_margin=statistics.mean(r["op_margin"] for r in rows),
                    final_ni=rows[-1]["net_income"], vol=statistics.pstdev([r["fcf"] for r in rows]) / (abs(statistics.mean([r["fcf"] for r in rows])) or 1) * 100)
            for n, rows in res.items()}
    ranking = sorted(names, key=lambda n: -summ[n]["cum_fcf"])
    spread = []
    for i in range(years):
        vals = [res[n][i]["ebit"] for n in names]
        hi, lo = max(vals), min(vals)
        spread.append(dict(year=base["fy"] + i + 1, spread_pct=(hi - lo) / abs(hi) * 100 if hi else 0, best=names[vals.index(hi)], worst=names[vals.index(lo)]))
    return dict(base=base, results=res, summary=summ, ranking=ranking, spread=spread, diffs={n: scenarios[n] for n in names})

def scenario_prompt(out):
    L = [f"SCENARIO COMPARISON MODE ({len(out['ranking'])} scenarios). Baseline = FY{out['base']['fy']} actuals from the 10-K {out['base']['sources']}.",
         "PERFORMANCE RANKING BY CUMULATIVE FREE CASH FLOW (pre-computed - do not re-rank):"]
    for i, n in enumerate(out["ranking"], 1):
        s = out["summary"][n]
        L.append(f'{i}. "{n}": cum FCF {fmt(s["cum_fcf"], "USD")}, worst-year FCF {fmt(s["min_fcf"], "USD")}, avg op margin {s["avg_op_margin"]:.1f}%, final NI {fmt(s["final_ni"], "USD")}, FCF volatility {s["vol"]:.0f}%')
    L.append("SCENARIO VARIATIONS vs baseline drivers:")
    for n, d in out["diffs"].items():
        L.append(f'- "{n}": ' + (", ".join(f"{k}={v:.3f}" for k, v in d.items()) or "baseline"))
    L.append("CONVERGENCE / DIVERGENCE (EBIT spread best vs worst):")
    for s in out["spread"]:
        L.append(f"- FY{s['year']}: spread {s['spread_pct']:.0f}% ({'DIVERGENT - high leverage decision point' if s['spread_pct'] > 20 else 'convergent'}); best '{s['best']}', worst '{s['worst']}'")
    L.append('Return JSON: {"recommended_scenario":"","recommendation_rationale":"2-3 sentences","avoid_scenarios":[],"avoid_rationale":"","critical_decisions":["which single driver change moves the ranking most"]}')
    return "\n".join(L)

def explain_scenarios(out):
    obj, model = llm.chat_json([{"role": "system", "content": "You are a financial planning analyst. Use ONLY the numbers given. Do not recompute."},
                                {"role": "user", "content": scenario_prompt(out)}])
    return obj
