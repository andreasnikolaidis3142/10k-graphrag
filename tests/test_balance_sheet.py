"""Balance-sheet bugs found in the real Apple answer: one snapshot date, XBRL beats a table, net cash counts non-current securities."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph, FilingGraph
from tenk_graphrag.models import Fact
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag.narrative import extract_numbers

def nf(name,ctx,val,scale=6): return f'<ix:nonFraction name="{name}" contextRef="{ctx}" unitRef="usd" decimals="-6" scale="{scale}">{val}</ix:nonFraction>'
def inst(i,d): return f'<xbrli:context id="{i}"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>{d}</xbrli:instant></xbrli:period></xbrli:context>'
DUR='<xbrli:context id="d"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>2022-09-25</xbrli:startDate><xbrli:endDate>2023-09-30</xbrli:endDate></xbrli:period></xbrli:context>'
ROWS=[("Cash and cash equivalents","CashAndCashEquivalentsAtCarryingValue",29965,23646),("Marketable securities","MarketableSecuritiesCurrent",31590,24658),
      ("Commercial paper","CommercialPaper",5985,9982),("Term debt","LongTermDebtCurrent",9822,11128)]
NONCUR=[("Marketable securities","MarketableSecuritiesNoncurrent",100544,120805),("Term debt","LongTermDebtNoncurrent",95281,98959)]
def html():
    def row(l,n,a,b): return f'<tr><td>{l}</td><td>{nf("us-gaap:"+n,"i23",f"{a:,}")}</td><td>{nf("us-gaap:"+n,"i22",f"{b:,}")}</td></tr>'
    return f'''<html><body><ix:header><ix:resources>{inst("i23","2023-09-30")}{inst("i22","2022-09-24")}{DUR}<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit></ix:resources></ix:header>
<p>For the fiscal year ended <ix:nonNumeric name="dei:DocumentPeriodEndDate" contextRef="d">September 30, 2023</ix:nonNumeric></p>
<p>Interest rate risk</p><table><tr><td></td><td>2023</td><td>2022</td></tr><tr><td>Term debt</td><td>150</td><td>201</td></tr></table>
<p>CONSOLIDATED BALANCE SHEETS</p><p>(In millions)</p>
<table><tr><td></td><td>September 30, 2023</td><td>September 24, 2022</td></tr>
<tr><td>Current assets:</td></tr>{row(*ROWS[0])}{row(*ROWS[1])}<tr><td>Current liabilities:</td></tr>{row(*ROWS[2])}{row(*ROWS[3])}
<tr><td>Non-current assets:</td></tr>{row(*NONCUR[0])}<tr><td>Non-current liabilities:</td></tr>{row(*NONCUR[1])}</table>
<p>Cash and marketable securities detail</p><p>(In millions)</p>
<table><tr><td></td><td>2023</td><td>2022</td></tr><tr><td>Cash</td><td>18</td><td>18.55</td></tr><tr><td>Commercial paper</td><td>5</td><td>718</td></tr></table></body></html>'''
def build():
    from tenk_graphrag.graph_builder import build_graph
    p=os.path.join(tempfile.mkdtemp(),"f.htm"); open(p,"w").write(html()); return build_graph(p, xbrl_min_facts=1)

def _derived(fg, concept):
    return {d["period"]: d["value"] for _, d in fg.facts(lambda d: d["concept"] == concept and d["source"] == "derived")}

def test_total_debt_uses_the_xbrl_balance_sheet_for_both_years():
    d = _derived(build(), "TotalDebt")
    assert round(d["@2023-09-30"] / 1e6) == 111_088 and round(d["@2022-09-24"] / 1e6) == 120_069

def test_net_debt_counts_non_current_securities_and_is_negative_for_net_cash():
    fg = build(); d = _derived(fg, "NetDebt")
    assert round(d["@2023-09-30"] / 1e6) == -51_011 and round(d["@2022-09-24"] / 1e6) == -49_040
    assert "NEGATIVE = net cash" in next(x["label"] for _, x in fg.facts(lambda x: x["concept"] == "NetDebt"))

def test_a_junk_table_fact_on_a_slightly_different_date_shares_the_period_and_loses_to_xbrl():
    fg = build()
    facts = sorted((d["period"], d["source"], d["role"]) for _, d in fg.facts(
        lambda d: d["concept"] == "CashAndCashEquivalentsAtCarryingValue" and d["fy"] == 2022))
    assert facts == [("@2022-09-24", "ixbrl", "level"), ("@2022-09-24", "table", "shadowed")]

def test_instants_snap_only_within_ten_days_and_never_for_durations():
    fg = FilingGraph()
    def mk(end, src, value=1.0, pt="instant", months=0):
        return Fact(concept="Assets", value=value, unit="USD", precision=1, ptype=pt, end=end, months=months, fy=2022, source=src,
                    period=("@" + end) if pt == "instant" else "FY2022")
    fg.add_fact(mk("2022-09-24", "ixbrl"))
    near = fg.add_fact(mk("2022-09-30", "table", value=2.0))        # 6 days away  -> same snapshot
    far = fg.add_fact(mk("2022-12-31", "table", value=3.0))         # 98 days away -> a different date
    dur = fg.add_fact(mk("2022-09-30", "table", value=4.0, pt="duration", months=12))
    assert fg.F(near)["period"] == "@2022-09-24" and fg.F(far)["period"] == "@2022-12-31" and fg.F(dur)["period"] == "FY2022"

def test_unrelated_narrative_differences_are_not_shown_for_a_balance_sheet_question():
    fg = build_graph(os.path.join(os.path.dirname(__file__), "sample_10k.htm"))
    for f in extract_numbers("Net income was $600 million in 2023.", dict(fy=2023, fy_end_month=12, fy_end_day=31), "x", 99):
        fg.add_fact(f)
    fg.reconcile_narrative()
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    assert "Text differs from table" not in r.build_context(r.retrieve(r.plan("Is the balance sheet healthy? Look at liquidity and debt.")))
    assert "Text differs from table" in r.build_context(r.retrieve(r.plan("Any red flags in net income?")))

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
