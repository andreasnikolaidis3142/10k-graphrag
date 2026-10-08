"""Question -> concepts: everyday analyst wording must reach the right series (no semantic model needed)."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)
R = lambda: Retriever(build_graph(os.path.join(HERE, "apple_like.htm")), embedder=Embedder(model_name="definitely/not-a-model"))

def test_ampersand_abbreviations_map_to_expense_lines():
    p = R().plan("What did the company spend on R&D and SG&A, and how did that change relative to revenue?")
    assert "ResearchAndDevelopmentExpense" in p["concepts"] and "SellingGeneralAndAdministrativeExpense" in p["concepts"]

def test_eps_share_count_and_buyback_wording():
    p = R().plan("What happened to earnings per share and the share count, and are buybacks shrinking it?")
    for c in ("EarningsPerShareDiluted", "WeightedAverageNumberOfDilutedSharesOutstanding", "PaymentsForRepurchaseOfCommonStock"):
        assert c in p["concepts"], c

def test_eps_theme_does_not_fire_on_unrelated_words():
    p = R().plan("How did the steps taken on deposits affect operating margin?")
    assert "EarningsPerShareDiluted" not in p["concepts"]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
