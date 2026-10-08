"""Noise reduction: trailing commas, generic labels from unrelated tables, and saving answers to UTF-8 files."""
import os, sys, json, tempfile, pathlib
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.answer import numbers_in, check_grounding
from tenk_graphrag import answer, llm

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(HERE))

def test_a_year_followed_by_a_comma_is_still_a_year():
    assert numbers_in("for FY2022, while tables show") == []
    kinds = {r: v for k, v, d, r in numbers_in("revenue was $1,234.5 million, up 3.5%")}
    assert kinds["$1,234.5 million"] == 1_234_500_000 and kinds["3.5%"] == 3.5

def test_generic_rows_from_unrelated_tables_are_not_conflicts():
    html = '''<html><body><p>For the fiscal year ended September 30, 2023</p>
<p>Fair value measurements</p><table><tr><td></td><td>2023</td></tr><tr><td>Level 1</td><td>10</td></tr><tr><td>Total</td><td>100</td></tr></table>
<p>Lease liabilities</p><table><tr><td></td><td>2023</td></tr><tr><td>Operating</td><td>7</td></tr><tr><td>Total</td><td>200</td></tr></table></body></html>'''
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(html)
    fg = build_graph(p)
    assert not [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]

def test_real_conflicts_are_still_set_aside():
    fg = build_graph(os.path.join(HERE, "apple_mdna.htm"))
    assert [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]

def test_ask_to_file_writes_utf8_json_and_a_readable_markdown(monkeypatch=None):
    import ask_to_file
    html = open(os.path.join(HERE, "ixbrl_tagged.htm"), encoding="utf-8").read().replace(
        "<p>Segment Information</p>", "<p>Note 13 \u2013 Segment Information</p>")
    d = tempfile.mkdtemp(); g = os.path.join(d, "g.htm"); open(g, "w", encoding="utf-8").write(html)
    fg = build_graph(g, xbrl_min_facts=1); gp = os.path.join(d, "g.json"); fg.save(gp)
    rev = next(n for n, x in fg.facts(lambda x: x["concept"] == "Revenues" and x["period"] == "FY2023" and x["source"] == "ixbrl" and not x["dims"]))
    original = llm.chat_json
    llm.chat_json = lambda m, **k: ({"summary": f"Revenue was $383.29B [{rev}].", "status": "negative"}, "mock")
    try:
        ask_to_file.main([gp, "How did revenue do?", os.path.join(d, "ans")])
    finally:
        llm.chat_json = original
    j = json.loads(pathlib.Path(d, "ans.json").read_text(encoding="utf-8"))
    md = pathlib.Path(d, "ans.md").read_text(encoding="utf-8")
    assert j["model"] == "mock" and rev in j["answer"]["sources"]
    assert "\u2013" in md and "\u00fb" not in md and "table #" in md and rev in md

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
