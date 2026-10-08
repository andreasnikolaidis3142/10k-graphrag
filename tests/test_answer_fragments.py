"""A model reply that is only a fragment (one key_numbers item) must never replace or become the answer."""
import os
from tenk_graphrag import llm
from tenk_graphrag.answer import ask
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

FG = build_graph(os.path.join(os.path.dirname(__file__), "apple_like.htm"))
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")
FRAGMENT = {"metric": "Current ratio", "period": "FY2022", "value": "0.88", "fact_id": "F00001"}

def _ask(answers):
    seen, original = [], llm.chat_json
    llm.chat_json = lambda m, **k: (seen.append(m[-1]["content"]), (answers[min(len(seen), len(answers)) - 1], "mock"))[1]
    try:
        return ask(FG, "Are there any red flags?", retriever=Retriever(FG, embedder=OFFLINE())), seen
    finally:
        llm.chat_json = original

def test_repair_reply_that_is_a_fragment_does_not_replace_the_answer():
    full = {"summary": "Revenue fell 3% [ATTRIBUTION].", "drivers": ["Revenue fell 3% [ATTRIBUTION]"]}   # uncited -> repair pass
    res, seen = _ask([full, FRAGMENT, FRAGMENT])
    assert len(seen) >= 2 and res["answer"].get("summary", "").startswith("Revenue fell")

def test_first_reply_that_is_a_fragment_is_asked_again_for_the_full_object():
    full = {"summary": "No material red flags.", "drivers": []}
    res, seen = _ask([FRAGMENT, full])
    assert "COMPLETE" in seen[1] and res["answer"]["summary"] == "No material red flags."

def test_no_parsable_answer_is_an_error_not_an_empty_answer():
    original = llm.chat_json
    llm.chat_json = lambda m, **k: (None, "mock")
    try:
        ask(FG, "Are there any red flags?", retriever=Retriever(FG, embedder=OFFLINE())); assert False, "should raise"
    except RuntimeError:
        pass
    finally:
        llm.chat_json = original

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
