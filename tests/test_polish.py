"""Source-block hygiene: no duplicate 'custom:' components next to XBRL slices; titles must look like titles."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder


def _nf(name, ctx, val):
    return f'<ix:nonFraction name="{name}" contextRef="{ctx}" unitRef="usd" decimals="-6" scale="6">{val}</ix:nonFraction>'


def _ctx(i, mem=None):
    seg = (f'<xbrli:segment><xbrldi:explicitMember dimension="us-gaap:ProductOrServiceAxis">acme:{mem}Member</xbrldi:explicitMember></xbrli:segment>' if mem else "")
    return (f'<xbrli:context id="{i}"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier>{seg}</xbrli:entity><xbrli:period>'
            '<xbrli:startDate>2022-10-01</xbrli:startDate><xbrli:endDate>2023-09-30</xbrli:endDate></xbrli:period></xbrli:context>')


R = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
HTML = f'''<html><body><ix:header><ix:resources>{_ctx("c")}{_ctx("p", "Product")}{_ctx("s", "Service")}<xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit></ix:resources></ix:header>
<p>For the fiscal year ended <ix:nonNumeric name="dei:DocumentPeriodEndDate" contextRef="c">September 30, 2023</ix:nonNumeric></p>
<p>CONSOLIDATED STATEMENTS OF OPERATIONS</p><p>(In millions)</p>
<table><tr><td>Years ended</td><td>September 30, 2023</td></tr>
<tr><td>Net sales:</td></tr><tr><td>Products</td><td>{_nf(R, "p", "60")}</td></tr><tr><td>Services</td><td>{_nf(R, "s", "40")}</td></tr>
<tr><td>Total net sales</td><td>{_nf(R, "c", "100")}</td></tr></table>
<p>SBC</p><table><tr><td></td><td>2023</td></tr><tr><td>U.S.</td><td>70</td></tr><tr><td>Other</td><td>30</td></tr></table></body></html>'''


def _graph():
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(HTML); return build_graph(p, xbrl_min_facts=1)


def test_custom_rows_do_not_duplicate_xbrl_slices_in_the_attribution():
    fg = _graph()
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model")); ev = r.retrieve(r.plan("revenue by product"))
    assert {a["axis"] for a in ev["attribution"]} == {"ProductOrService"}
    assert all(c["d"]["source"] == "ixbrl" for a in ev["attribution"] for c in a["children"])


def test_custom_rows_are_kept_when_there_is_nothing_better():
    html = HTML.replace(_nf(R, "p", "60"), "60").replace(_nf(R, "s", "40"), "40")
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(html)
    fg = build_graph(p, xbrl_min_facts=1)
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model")); ev = r.retrieve(r.plan("revenue by product"))
    assert [c["d"]["concept"] for a in ev["attribution"] for c in a["children"] if a["axis"] == "component"] == ["custom:products", "custom:services"]


def test_a_three_letter_line_is_not_a_table_title():
    fg = _graph()
    titles = {d["table_title"] for _, d in fg.facts(lambda d: d["source"] == "table")}
    assert "SBC" not in titles and "CONSOLIDATED STATEMENTS OF OPERATIONS" in titles


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
