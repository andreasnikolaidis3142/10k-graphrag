"""The 'duplicates set aside' note must only count conflicts that touch the metrics being shown."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)

def _ctx(question):
    html = open(os.path.join(HERE, "apple_mdna.htm")).read().replace("<p>Rest of Asia Pacific</p>", "<p>Rest of Asia Pacific</p>\n<p>(In millions)</p>")
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(html)
    fg = build_graph(p)
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    return r.build_context(r.retrieve(r.plan(question)))

def test_note_counts_only_conflicts_for_the_metrics_shown():
    ctx = _ctx("operating income trend")
    assert "NOTE: for the metrics above, 2 duplicate facts" in ctx          # the 2 shadowed OperatingIncomeLoss facts, not all 4

def test_no_note_when_the_metrics_shown_have_no_conflicts():
    ctx = _ctx("cash and cash equivalents balance")
    assert "NOTE: for the metrics above" not in ctx

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
