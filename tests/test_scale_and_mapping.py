"""Findings from the real Apple conflict audit: share scales, non-current items, Basic/Diluted blocks, XBRL ties."""
import os, tempfile
from tenk_graphrag.numparse import detect_scale
from tenk_graphrag.taxonomy import match_concept
from tenk_graphrag.graph_builder import build_graph, FilingGraph
from tenk_graphrag.models import Fact


def _build(html, **kw):
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w", encoding="utf-8").write(html); return build_graph(p, **kw)


def _val(fg, concept, period=None, **kw):
    return [d for _, d in fg.facts(lambda d: d["concept"] == concept and d["source"] == "table" and d["role"] == "level"
                                   and (period is None or d["period"] == period))]


def test_share_scale_is_not_taken_from_per_share_phrases():
    assert detect_scale("computation of basic and diluted earnings per share for 2023 (net income in millions and shares in thousands):") == {"money": 1e6, "shares": 1e3}
    assert detect_scale("(In millions, except number of shares, which are reflected in thousands, and per-share amounts)") == {"money": 1e6, "shares": 1e3}
    assert detect_scale("(in thousands, except per share data)") == {"money": 1e3, "shares": 1e3}


def test_non_current_labels_do_not_fuzzy_match_current_concepts():
    assert match_concept("Other non-current assets", "BS")[0] == "OtherAssetsNoncurrent"
    assert match_concept("Other non-current liabilities", "BS")[0] == "OtherLiabilitiesNoncurrent"
    assert match_concept("Other current assets", "BS")[0] == "PrepaidExpenseAndOtherAssetsCurrent"


BS = '''<html><body><p>For the fiscal year ended September 30, 2023</p><p>CONSOLIDATED BALANCE SHEETS</p><p>(In millions)</p>
<table><tr><td></td><td>September 30, 2023</td></tr>
<tr><td>Current assets:</td></tr><tr><td>Marketable securities</td><td>31,590</td></tr><tr><td>Other current assets</td><td>14,695</td></tr>
<tr><td>Non-current assets:</td></tr><tr><td>Marketable securities</td><td>100,544</td></tr><tr><td>Other non-current assets</td><td>64,758</td></tr></table></body></html>'''


def test_same_label_under_current_and_non_current_headings_gets_different_concepts():
    fg = _build(BS)
    assert _val(fg, "ShortTermInvestments")[0]["value"] == 31_590e6
    assert _val(fg, "MarketableSecuritiesNoncurrent")[0]["value"] == 100_544e6
    assert _val(fg, "PrepaidExpenseAndOtherAssetsCurrent")[0]["value"] == 14_695e6
    assert _val(fg, "OtherAssetsNoncurrent")[0]["value"] == 64_758e6
    assert not [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]


EPS = '''<html><body><p>For the fiscal year ended September 30, 2023</p><p>CONSOLIDATED STATEMENTS OF OPERATIONS</p>
<p>(In millions, except number of shares, which are reflected in thousands, and per-share amounts)</p>
<table><tr><td>Years ended</td><td>September 30, 2023</td></tr>
<tr><td>Earnings per share:</td></tr><tr><td>Basic</td><td>$</td><td>6.16</td></tr><tr><td>Diluted</td><td>$</td><td>6.13</td></tr>
<tr><td>Shares used in computing earnings per share:</td></tr><tr><td>Basic</td><td>15,744,231</td></tr><tr><td>Diluted</td><td>15,812,547</td></tr></table></body></html>'''


def test_basic_and_diluted_in_the_share_count_block_are_share_counts_not_eps():
    fg = _build(EPS)
    assert _val(fg, "EarningsPerShareBasic")[0]["value"] == 6.16 and _val(fg, "EarningsPerShareDiluted")[0]["value"] == 6.13
    assert _val(fg, "WeightedAverageNumberOfSharesOutstandingBasic")[0]["value"] == 15_744_231e3
    assert _val(fg, "WeightedAverageNumberOfDilutedSharesOutstanding")[0]["value"] == 15_812_547e3
    assert not [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]


def _nf(name, ctx, val):
    return f'<ix:nonFraction name="{name}" contextRef="{ctx}" unitRef="usd" decimals="-6" scale="6">{val}</ix:nonFraction>'


def test_equally_trusted_xbrl_facts_are_both_kept_and_flagged_not_discarded():
    ctx = ('<xbrli:context id="c"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier></xbrli:entity><xbrli:period>'
           '<xbrli:startDate>2022-10-01</xbrli:startDate><xbrli:endDate>2023-09-30</xbrli:endDate></xbrli:period></xbrli:context>')
    html = f'''<html><body><ix:header><ix:resources>{ctx}<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit></ix:resources></ix:header>
<p>For the fiscal year ended <ix:nonNumeric name="dei:DocumentPeriodEndDate" contextRef="c">September 30, 2023</ix:nonNumeric></p>
<p>Disclosure A</p><table><tr><td></td><td>2023</td></tr><tr><td>Net sales</td><td>{_nf("us-gaap:Revenues", "c", "100")}</td></tr></table>
<p>Disclosure B</p><table><tr><td></td><td>2023</td></tr><tr><td>Net sales</td><td>{_nf("us-gaap:Revenues", "c", "200")}</td></tr></table></body></html>'''
    fg = _build(html, xbrl_min_facts=1)
    live = [d for _, d in fg.facts(lambda d: d["source"] == "ixbrl" and d["concept"] == "Revenues" and d["role"] == "level")]
    assert sorted(d["value"] for d in live) == [100e6, 200e6] and all("ambiguous_duplicate" in d["flags"] for d in live)


def test_the_same_xbrl_fact_tagged_twice_is_interchangeable_for_table_matching():
    fg = FilingGraph()
    mk = lambda v, prec, src="ixbrl", dims=None, **kw: Fact(concept="Revenues", value=v, unit="USD", precision=prec, period="FY2023", ptype="duration",
                                                          end="2023-09-30", months=12, fy=2023, dims=dims or {"ProductOrService": "Service"}, source=src, **kw)
    a = fg.add_fact(mk(85.2e9, 1e3)); b = fg.add_fact(mk(85.2e9 + 4e5, 1e3))
    assert a != b
    fg.index_xbrl(1)
    got = fg.add_table_fact(mk(85.2e9, 1e6, "table", {"product": "Services"}, label="Services", table_no=8))
    assert got == min(a, b) and fg.F(got)["appears_in"][0]["row"] == "Services"


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
