"""Question planning and slice selection bugs found on a January-year retailer (no company-specific logic):
'current ratio' is not a time word, 'latest' is the filing's year (not a 2029 maturity bucket), an empty dimension member never
matches, margin questions get the operating-income slices, XBRL slices beat table-row pseudo-segments, equally-trusted XBRL twins
(total revenues vs net sales) are both shown, lease / tax-reconciliation / membership wording reaches the standard us-gaap
elements, and a hyphenated or two-axis member (e-commerce x segment) is found."""
import os
from bs4 import BeautifulSoup
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.loader import parse_ixbrl
from tenk_graphrag.models import Fact
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)
OFF = lambda: Embedder(model_name="definitely/not-a-model")

def _fg(name="apple_like.htm"):
    return build_graph(os.path.join(HERE, name), xbrl_min_facts=1)

def _fact(**kw):
    base = dict(unit="USD", precision=1e6, ptype="duration", period="FY2023", end="2023-12-31", months=12, fy=2023, source="ixbrl")
    base.update(kw); return Fact(**base)

def test_current_ratio_is_not_a_time_word_and_latest_is_the_filing_year():
    fg = _fg()
    fg.add_fact(_fact(concept="LongTermDebtNoncurrent", value=5e8, ptype="instant", period="@2029-12-31", end="2029-12-31",
                      months=0, fy=2029, source="table"))          # a debt-maturity bucket far in the future
    r = Retriever(fg, embedder=OFF())
    assert r.plan("What are the current ratio and inventory levels?")["years"] == []
    assert r.plan("What was revenue in the most recent year?")["years"] == [fg.meta["fy"]]

def test_an_empty_dimension_member_never_matches():
    r = Retriever(_fg(), embedder=OFF()); r.dims["segment"].add("")
    assert "" not in [m for ms in r.plan("Which segment had the highest operating margin?")["dims"].values() for m in ms]

def test_margin_question_gets_operating_income_slices():
    r = Retriever(_fg(), embedder=OFF())
    ev = r.retrieve(r.plan("Which segment had the highest operating margin?"))
    assert any(s["concept"] == "OperatingIncomeLoss" and s["dims"] for s in ev["series"])

def test_table_pseudo_segments_are_hidden_when_xbrl_slices_exist():
    fg = _fg("ixbrl_tagged.htm")
    fg.add_fact(_fact(concept="Revenues", value=4.6e9, source="table", dims={"segment": "Unit counts at period end"}))
    r = Retriever(fg, embedder=OFF())
    ev = r.retrieve(r.plan("Which segment drove revenue growth?"))
    assert not [s for s in ev["series"] if s["dims"].get("segment") == "Unit counts at period end"]
    assert [s for s in ev["series"] if "StatementBusinessSegments" in s["dims"]]

def test_equally_trusted_xbrl_twins_are_both_shown():
    fg = _fg("ixbrl_tagged.htm")
    main = next(n for n, d in fg.facts(lambda d: d["concept"] == "Revenues" and d["source"] == "ixbrl" and not d["dims"]
                                       and d["fy"] == 2023))
    twin = fg.add_fact(_fact(concept="Revenues", value=fg.F(main)["value"] * 1.01, end=fg.F(main)["end"], period=fg.F(main)["period"],
                             location="ix:us-gaap:Revenues", label="us-gaap:Revenues", flags=["ambiguous_duplicate"]))
    fg.F(main)["flags"].append("ambiguous_duplicate")
    r = Retriever(fg, embedder=OFF())
    ctx = r.build_context(r.retrieve(r.plan("How did total revenue change?")))
    assert f"[{main}]" in ctx and f"[{twin}]" in ctx

def test_lease_tax_reconciliation_and_membership_wording():
    r = Retriever(_fg(), embedder=OFF())
    assert "OperatingLeaseLiability" in r.plan("What are the lease obligations?")["concepts"]
    assert "OperatingLeaseLiability" not in r.plan("What did the earnings release say about revenue?")["concepts"]
    assert "EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate" in \
        r.plan("What drove the difference between the effective tax rate and the statutory rate?")["concepts"]
    assert "OtherIncome" in r.plan("What happened to membership and other income?")["concepts"]

def test_hyphenated_two_axis_member_is_found():
    fg = _fg("ixbrl_tagged.htm")
    a = fg.add_fact(_fact(concept="Revenues", value=6.5e10, dims={"MajorCustomers": "ECommerce", "StatementBusinessSegments": "Retail"}))
    r = Retriever(fg, embedder=OFF())
    p = r.plan("What happened to e-commerce sales?")
    assert p["dims"].get("MajorCustomers") == ["ECommerce"]
    assert any(n == a for s in r.retrieve(p)["series"] for _, n in s["items"])

def test_member_names_lose_only_a_trailing_member_suffix():
    html = ('<html><body><ix:header><ix:resources><xbrli:context id="c"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier>'
            '<xbrli:segment><xbrldi:explicitMember dimension="srt:ProductOrServiceAxis">wmt:MembershipFeesMember</xbrldi:explicitMember>'
            '</xbrli:segment></xbrli:entity><xbrli:period><xbrli:startDate>2023-01-01</xbrli:startDate><xbrli:endDate>2023-12-31'
            '</xbrli:endDate></xbrli:period></xbrli:context><xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '</ix:resources></ix:header><ix:nonFraction name="us-gaap:OtherIncome" contextRef="c" unitRef="usd" decimals="-6" scale="6">'
            '3,100</ix:nonFraction></body></html>')
    facts, _ = parse_ixbrl(BeautifulSoup(html, "lxml"))
    assert facts and facts[0].dims == {"ProductOrService": "MembershipFees"}

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
