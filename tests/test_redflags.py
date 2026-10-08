"""Red-flag screen: declines, severity scaling, readable labels."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.signals import red_flags, FLAG_LABELS
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)
FG = lambda: build_graph(os.path.join(HERE, "apple_like.htm"))

def test_revenue_and_operating_income_decline_flagged_low():
    by = {x["code"]: x for x in red_flags(FG())}
    assert by["REVENUE_DECLINE"]["severity"] == "low"          # ~3% dip is not alarming
    assert by["OPINC_DECLINE"]["severity"] == "low"
    assert "FY2023" in by["REVENUE_DECLINE"]["text"]

def test_every_flag_has_a_readable_label():
    for x in red_flags(FG()):
        assert x["label"] and x["label"] != x["code"]
        assert x["code"] in FLAG_LABELS

def test_context_shows_label_not_code():
    fg = FG(); r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    ctx = r.build_context(r.retrieve(r.plan("Are there any red flags?")))
    assert "Revenue decline" in ctx and "REVENUE_DECLINE" not in ctx

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
