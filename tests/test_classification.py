"""Regression: an unrelated paragraph ("financial condition") must not turn a segment table into a balance sheet;
deferred-tax components must not masquerade as balance-sheet items."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph

def _build(html):
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(html); return build_graph(p)

SEG = '''<html><body><p>For the fiscal year ended September 30, 2023</p><p>ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS</p>
<p>Liquidity and Capital Resources. The following discussion should be read together with the Company's financial condition and results.</p>
<p>The Company believes its balances of cash, cash equivalents and unrestricted marketable securities will be sufficient to satisfy its needs.</p>
<p>Apple Inc. | 2023 Form 10-K | 21</p>
<p>The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):</p>
<table><tr><td></td><td>2023</td><td>2022</td><td>2021</td></tr>
<tr><td>Americas</td><td>$</td><td>162,560</td><td>$</td><td>169,658</td><td>$</td><td>153,306</td></tr>
<tr><td>Europe</td><td>94,294</td><td>95,118</td><td>89,307</td></tr>
<tr><td>Total net sales</td><td>256,854</td><td>264,776</td><td>242,613</td></tr></table>
<p>Apple Inc. | 2023 Form 10-K | 22</p></body></html>'''

def test_unrelated_words_in_earlier_paragraphs_do_not_reclassify_a_table():
    fg = _build(SEG)
    am = next(d for _, d in fg.facts(lambda d: d["source"] == "table" and d["period"] == "FY2023" and d["dims"].get("segment") == "Americas"))
    assert am["concept"] == "Revenues" and am["ptype"] == "duration" and am["stmt"] != "BS"
    assert not [1 for _, d in fg.facts(lambda d: d["concept"].startswith("custom:") and d["source"] == "table")]

def test_those_segments_still_roll_up_to_the_total():
    fg = _build(SEG)
    tot = next(n for n, d in fg.facts(lambda d: d["concept"] == "Revenues" and d["period"] == "FY2023" and not d["dims"]))
    assert len([u for u, _, k in fg.G.in_edges(tot, keys=True) if k == "ROLLS_UP_TO"]) == 2

TAX = '''<html><body><p>For the fiscal year ended September 30, 2023</p><p>ITEM 8. FINANCIAL STATEMENTS</p>
<p>CONSOLIDATED BALANCE SHEETS</p><p>(In millions)</p>
<table><tr><td></td><td>September 30, 2023</td></tr><tr><td>Current liabilities:</td></tr>
<tr><td>Deferred revenue</td><td>8,061</td></tr></table>
<p>Deferred Tax Assets and Liabilities</p><p>(In millions)</p>
<table><tr><td></td><td>2023</td></tr><tr><td>Deferred tax assets:</td></tr>
<tr><td>Deferred revenue</td><td>5,744</td></tr><tr><td>Total deferred tax assets</td><td>5,744</td></tr></table></body></html>'''

def test_deferred_tax_components_do_not_become_balance_sheet_items():
    fg = _build(TAX)
    bs = [d for _, d in fg.facts(lambda d: d["concept"] == "ContractWithCustomerLiabilityCurrent" and d["source"] == "table")]
    assert len(bs) == 1 and bs[0]["value"] == 8_061e6                         # the real balance-sheet deferred revenue only
    tax = [d for _, d in fg.facts(lambda d: d["concept"] == "custom:tax_deferred_revenue")]
    assert tax and tax[0]["value"] == 5_744e6
    assert not [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
