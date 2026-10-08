import os, json, tempfile
from tenk_graphrag.graph_builder import build_graph, FilingGraph
from tenk_graphrag.numparse import parse_cell, detect_scale
from tenk_graphrag.answer import check_grounding, ask
from tenk_graphrag.retrieval import Retriever
from tenk_graphrag import scenarios as sc, llm

HERE = os.path.dirname(__file__)
FG = build_graph(os.path.join(HERE, "sample_10k.htm"))

def val(concept, period, dims=None, source=("table", "ixbrl")):
    for _, d in FG.facts(lambda d: d["concept"] == concept and d["period"] == period and d["dims"] == (dims or {}) and d["source"] in source):
        return d["value"]

def test_number_forms():
    assert parse_cell("(1,234)").value == -1234
    assert parse_cell("$(5)").value == -5
    assert parse_cell("—").kind == "nil"
    assert parse_cell("12.5%").kind == "percent"
    assert parse_cell("n/m") is None
    assert detect_scale("(in thousands, except per share data)") == {"money": 1e3, "shares": 1e3}

def test_scale_and_period_alignment():
    assert val("Revenues", "FY2023") == 4.62e9
    assert val("Revenues", "FY2023", {"segment": "Industrial"}) == 2.31e9      # thousands table -> same base unit
    assert val("CashAndCashEquivalentsAtCarryingValue", "@2023-12-31") == 9e8   # instant for balance sheet

def test_sign_semantics():
    assert val("PaymentsToAcquirePropertyPlantAndEquipment", "FY2023") == 3e8   # outflow stored as magnitude
    assert val("NetCashProvidedByUsedInInvestingActivities", "FY2023") == -3e8  # printed negative stays negative
    assert val("OtherNonoperatingIncomeExpense", "FY2023") == -2e7

def test_identities_and_rollups():
    vs = [d for _, d in FG.G.nodes(data=True) if d.get("type") == "Validation"]
    assert vs and all(v["status"] == "pass" for v in vs)
    rev = next(n for n, d in FG.facts(lambda d: d["concept"] == "Revenues" and d["period"] == "FY2023" and not d["dims"] and d["source"] == "table"))
    kids = [u for u, _, k in FG.G.in_edges(rev, keys=True) if k == "ROLLS_UP_TO"]
    assert len(kids) == 3

def test_narrative_checked_against_tables():
    flags = {d["label"]: d["flags"] for _, d in FG.facts(lambda d: d["source"] == "text")}
    assert "verified_by_table" in flags["$4.6 billion"]
    assert "narrative_mismatch" in flags["150 basis points"]          # sample text intentionally disagrees (-95 bps in tables)

def test_derived_provenance():
    n, d = next(FG.facts(lambda d: d["concept"] == "GrossMarginPct" and d["period"] == "FY2023" and d["source"] == "derived"))
    assert abs(d["value"] - 43.29) < 0.01
    srcs = [t for _, t, k in FG.G.out_edges(n, keys=True) if k == "DERIVED_FROM"]
    assert len(srcs) == 2

def test_roundtrip_and_retrieval(tmp_path):
    p = tmp_path / "g.json"; FG.save(p); g2 = FilingGraph.load(p)
    r = Retriever(g2); plan = r.plan("Which segment drove revenue growth in 2023?")
    ctx = r.build_context(r.retrieve(plan))
    assert "Industrial" in ctx and "50.0% of total" in ctx

def test_grounding_verifier():
    r = Retriever(FG); ctx = r.build_context(r.retrieve(r.plan("revenue trend")))
    assert check_grounding(FG, ctx, "Revenue was $4.62B in FY2023, up 12.0% [F00013]") == []
    assert check_grounding(FG, ctx, "Revenue was $9.9B") != []

def test_ask_with_mock_llm(monkeypatch):
    def fake(msgs, **kw):
        return ({"summary": "Net sales were $4.62B [F00013], up 12.0%; Industrial was 50.0% of total.", "status": "positive"}, "mock")
    monkeypatch.setattr(llm, "chat_json", fake)
    res = ask(FG, "How did revenue do?")
    assert res["ungrounded"] == [] and res["model"] == "mock"

def test_scenarios():
    out = sc.run_scenarios(FG, {"Base": {}, "Bear": {"revenue_growth": -0.05, "gross_margin": 0.38}, "Bull": {"revenue_growth": 0.15}})
    assert out["ranking"][0] == "Bull" and out["ranking"][-1] == "Bear"
    assert "SCENARIO COMPARISON MODE" in sc.scenario_prompt(out)

IXBRL = """<html><body><ix:header><ix:resources>
<xbrli:context id="c1"><xbrli:entity><xbrli:identifier>1</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>2023-01-01</xbrli:startDate><xbrli:endDate>2023-12-31</xbrli:endDate></xbrli:period></xbrli:context>
<xbrli:context id="c2"><xbrli:entity><xbrli:identifier>1</xbrli:identifier><xbrli:segment><xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">acme:IndustrialMember</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:startDate>2023-01-01</xbrli:startDate><xbrli:endDate>2023-12-31</xbrli:endDate></xbrli:period></xbrli:context>
<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit></ix:resources></ix:header>
<p>For the fiscal year ended December 31, 2023</p>
<p>Revenue <ix:nonFraction name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextRef="c1" unitRef="usd" decimals="-6" scale="6">4,620</ix:nonFraction>
 Industrial <ix:nonFraction name="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax" contextRef="c2" unitRef="usd" decimals="-6" scale="6">2,310</ix:nonFraction>
 Loss <ix:nonFraction name="us-gaap:NetIncomeLoss" contextRef="c1" unitRef="usd" decimals="-6" scale="6" sign="-">12</ix:nonFraction></p></body></html>"""

def test_inline_xbrl(tmp_path):
    p = tmp_path / "x.htm"; p.write_text(IXBRL)
    g = build_graph(str(p))
    got = {(d["concept"], tuple(d["dims"].items())): d["value"] for _, d in g.facts(lambda d: d["source"] == "ixbrl")}
    assert got[("Revenues", ())] == 4.62e9
    assert got[("Revenues", (("StatementBusinessSegments", "acme:Industrial".split(":")[1]),))] == 2.31e9
    assert got[("NetIncomeLoss", ())] == -12e6


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
