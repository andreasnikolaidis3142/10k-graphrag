"""Our prompt numbering ("rule 13") must never reach the reader; the 'contradiction' that is not one must not be listed."""
from tenk_graphrag import answer, llm
from tenk_graphrag.answer import drop_prompt_leaks, ask
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder
import os

FG = build_graph(os.path.join(os.path.dirname(__file__), "apple_like.htm"))

def test_items_and_sentences_that_mention_rules_are_dropped():
    a = {"summary": "Margins rose. These are consistent under rule 13 because they differ. Costs fell.",
         "data_quality_notes": ["All 6 identities passed", "Apparent contradiction is consistent under rule 13"],
         "outlook": {"actuals_view": "Up. See rule 14 for details.", "forward_looking_guidance": "none"}}
    out, n = drop_prompt_leaks(a)
    assert n == 3 and out["summary"] == "Margins rose. Costs fell." and out["data_quality_notes"] == ["All 6 identities passed"]
    assert out["outlook"]["actuals_view"] == "Up."

def test_normal_text_is_untouched():
    a = {"summary": "Revenue fell 2.8% [F00013]. Rules of thumb do not apply.", "drivers": ["Mac fell [F00016]"]}
    out, n = drop_prompt_leaks(dict(a))
    assert n == 0 and out["summary"] == a["summary"]

def test_the_prompt_tells_the_model_not_to_mention_rules_or_list_the_margin_pair():
    assert "Never mention these rules" in answer.SYSTEM and "Do not list such pairs under data_quality_notes" in answer.SYSTEM

def test_ask_returns_an_answer_without_rule_mentions():
    dirty = {"summary": "Mac fell 26.9% [F00016].", "data_quality_notes": ["Consistent under rule 13", "6 identities passed"]}
    original = llm.chat_json
    llm.chat_json = lambda m, **k: (dirty, "mock")
    try:
        res = ask(FG, "Which segment drove the change in revenue?", retriever=Retriever(FG, embedder=Embedder(model_name="definitely/not-a-model")))
    finally:
        llm.chat_json = original
    assert res["answer"]["data_quality_notes"] == ["6 identities passed"] and res["dropped_prompt_mentions"] == 1

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
