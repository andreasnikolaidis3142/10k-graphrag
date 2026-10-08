"""Findings from the margin question: shares above 100% are not shown, margin questions pull in cost lines, and the prompt knows
that gross margin dollars and gross margin percentage can move in opposite directions."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag import answer

HERE = os.path.dirname(__file__)
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

HTML = '''<html><body><p>For the fiscal year ended September 30, 2023</p><p>Net sales by category</p><p>(In millions)</p>
<table><tr><td></td><td>2023</td><td>2022</td></tr>
<tr><td>Products</td><td>108,803</td><td>114,728</td></tr><tr><td>Services</td><td>60,345</td><td>56,058</td></tr>
<tr><td>Total net sales</td><td>169,148</td><td>170,786</td></tr></table></body></html>'''

def test_a_component_swing_larger_than_the_net_change_gets_no_percentage_share():
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(HTML)
    fg = build_graph(p); r = Retriever(fg, embedder=OFFLINE())
    ctx = r.build_context(r.retrieve(r.plan("how did net sales by category change")))
    assert "NET total change of only" in ctx and "no percentage share is meaningful" in ctx
    assert "362%" not in ctx and "262%" not in ctx and "<- LARGEST CONTRIBUTOR TO THE CHANGE" in ctx

def test_shares_within_100_percent_are_still_shown():
    fg = build_graph(os.path.join(HERE, "apple_like.htm")); r = Retriever(fg, embedder=OFFLINE())
    ctx = r.build_context(r.retrieve(r.plan("Which segment drove the change in revenue?")))
    assert "98% of the total change" in ctx and "offsets 64% of it" in ctx

def test_margin_questions_also_retrieve_the_cost_lines_that_explain_them():
    fg = build_graph(os.path.join(HERE, "apple_like.htm")); r = Retriever(fg, embedder=OFFLINE())
    c = r.plan("How have gross margin and operating margin changed, and what drove the change?")["concepts"]
    assert {"GrossMarginPct", "OperatingMarginPct", "ResearchAndDevelopmentExpense", "SellingGeneralAndAdministrativeExpense"} <= set(c)

def test_the_prompt_explains_gross_margin_dollars_versus_percentage():
    assert "gross margin percentage" in answer.SYSTEM and "never quote a percentage share above 100%" in answer.SYSTEM

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
