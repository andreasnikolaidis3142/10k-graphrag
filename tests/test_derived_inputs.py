"""A derived ratio also retrieves the series it is computed from, so the answer can say WHY it moved."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder
from tests.test_balance_sheet import build as build_bs

OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

def _plan(fg, q):
    return Retriever(fg, embedder=OFFLINE()).plan(q)["concepts"]

def test_interest_coverage_brings_operating_income_and_interest_expense():
    fg = build_graph(os.path.join(os.path.dirname(__file__), "apple_like.htm"))
    c = _plan(fg, "Is interest coverage a concern?")
    assert c[0] == "InterestCoverage" and {"OperatingIncomeLoss", "InterestExpense"} <= set(c)

def test_nested_derived_metrics_are_expanded_up_to_the_cap():
    fg = build_bs()
    c = _plan(fg, "How much net debt does the company have?")
    assert c[0] == "NetDebt" and {"TotalDebt", "CashAndCashEquivalentsAtCarryingValue", "MarketableSecuritiesNoncurrent", "LongTermDebtNoncurrent"} <= set(c)
    assert len(_plan(fg, "Give me an overview and summary of the company")) <= 12

def test_the_inputs_actually_appear_in_the_evidence():
    fg = build_bs(); r = Retriever(fg, embedder=OFFLINE())
    assert "SERIES LongTermDebtNoncurrent" in r.build_context(r.retrieve(r.plan("How much net debt does the company have?")))

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
