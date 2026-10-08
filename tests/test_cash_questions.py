"""'How much cash did X generate and how did it return it to shareholders?' must retrieve cash-flow metrics, not ROE/ROA."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

FG = build_graph(os.path.join(os.path.dirname(__file__), "apple_like.htm"))
def _plan(q): return Retriever(FG, embedder=Embedder(model_name="definitely/not-a-model")).plan(q)["concepts"]

def test_cash_generated_and_returned_retrieves_cash_flow_and_shareholder_returns():
    c = _plan("How much cash did Apple generate in FY2023, and how did it return it to shareholders?")
    assert {"NetCashProvidedByUsedInOperatingActivities", "FreeCashFlow", "ShareholderReturns", "PayoutOfFcfPct"} <= set(c)
    assert not {"RoePct", "RoaPct", "AssetTurnover"} & set(c)

def test_return_on_equity_still_retrieves_the_return_ratios():
    assert {"RoePct", "RoaPct"} <= set(_plan("What is the return on equity and return on assets?"))

def test_operating_cash_phrases_also_count_as_cash_flow_questions():
    for q in ("How much cash from operations did it produce?", "What was operating cash last year?", "Did the company generate cash?"):
        assert "NetCashProvidedByUsedInOperatingActivities" in _plan(q), q

def test_inputs_of_a_ratio_get_a_series_but_no_attribution_block():
    r = Retriever(FG, embedder=Embedder(model_name="definitely/not-a-model"))
    ev = r.retrieve(r.plan("What is the net margin?"))
    assert "Revenues" in {s["concept"] for s in ev["series"]}                  # still shown, so the model can explain the ratio
    assert [a for a in ev["attribution"] if a["concept"] == "Revenues"] == []
    ev2 = r.retrieve(r.plan("Which segment drove revenue growth?"))            # asked about directly -> breakdown is kept
    assert {a["axis"] for a in ev2["attribution"] if a["concept"] == "Revenues"} == {"product", "segment"}

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
