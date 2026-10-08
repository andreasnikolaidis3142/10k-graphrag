"""'revenue growth' must not pull in net income / operating income; section-name citations in ANY text are flagged and stripped."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag.answer import uncited_claims, strip_pseudo_citations, ask
from tenk_graphrag import llm

HERE = os.path.dirname(__file__)
FG = build_graph(os.path.join(HERE, "apple_like.htm"))
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

def _plan(q):
    return Retriever(FG, embedder=OFFLINE()).plan(q)["concepts"]

def test_growth_only_expands_to_a_theme_when_no_metric_is_named():
    assert _plan("Which segment drove revenue growth?") == ["Revenues"]
    assert _plan("net income growth") == ["NetIncomeLoss"]
    assert _plan("growth") == ["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"]

def test_section_name_citations_are_flagged_in_summary_and_outlook_too():
    assert len(uncited_claims({"summary": "Mac was 98% of the change [ATTRIBUTION]."})) == 1
    assert len(uncited_claims({"outlook": {"actuals_view": "Down [DATA QUALITY]", "forward_looking_guidance": "none"}})) == 1
    assert uncited_claims({"summary": "Mac fell [F00016] and see [T00455].", "drivers": ["Mac fell 26.9% [F00016]"]}) == []

def test_stripping_removes_section_names_everywhere_but_keeps_real_ids():
    cleaned, n = strip_pseudo_citations({"summary": "Offsets 64% [ATTRIBUTION] of it [F00010].", "drivers": ["Mac [DATA QUALITY] fell [F00016]"],
                                         "outlook": {"actuals_view": "ok [ATTRIBUTION]"}})
    assert n == 3 and cleaned["summary"] == "Offsets 64% of it [F00010]." and cleaned["drivers"] == ["Mac fell [F00016]"]
    assert cleaned["outlook"]["actuals_view"] == "ok"

def test_ask_returns_a_clean_answer_even_if_the_model_never_stops_using_fake_citations():
    dirty = {"summary": "Mac fell 26.9% [ATTRIBUTION]", "drivers": ["Americas fell 4.2% [ATTRIBUTION]"]}
    original = llm.chat_json
    llm.chat_json = lambda m, **k: (dirty, "mock")
    try:
        res = ask(FG, "Which segment drove the change in revenue?", retriever=Retriever(FG, embedder=OFFLINE()))
    finally:
        llm.chat_json = original
    assert "[ATTRIBUTION]" not in str(res["answer"]) and res["stripped_pseudo_citations"] == 2
    assert res["answer"]["sources"] and len(res["uncited_claims"]) == 1       # the driver still has a number without an id

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
