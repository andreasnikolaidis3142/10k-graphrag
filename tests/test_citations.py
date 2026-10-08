"""Pseudo-citations like [ATTRIBUTION] must be repaired, and facts named in the answer must still get a source."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag.answer import uncited_claims, mentioned_slice_ids, build_sources, ask
from tenk_graphrag import llm

HERE = os.path.dirname(__file__)
FG = build_graph(os.path.join(HERE, "apple_like.htm"))
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

def _ev(q="Which segment drove the change in revenue?"):
    r = Retriever(FG, embedder=OFFLINE()); return r, r.retrieve(r.plan(q))

def _top(ev, axis):
    a = next(a for a in ev["attribution"] if a["axis"] == axis); c = a["children"][0]; return c["id"], c["prior"]["id"]

def test_numbers_without_ids_and_section_name_citations_are_flagged():
    bad = {"drivers": ["Mac fell 26.9% [ATTRIBUTION]", "Americas fell 4.2%"], "risks_and_red_flags": ["Current ratio below 1 [DATA QUALITY]"]}
    assert len(uncited_claims(bad)) == 3
    good = {"drivers": ["Mac fell 26.9% [F00016][F00017]", "Services grew, which is a positive signal"], "risks_and_red_flags": ["Check T00455 [T00455]"]}
    assert uncited_claims(good) == []

def test_a_name_in_the_answer_finds_its_facts_unless_they_are_already_cited():
    _, ev = _ev()
    mac, mac_prior = _top(ev, "product")
    assert set(mentioned_slice_ids(ev, {"drivers": ["Mac fell a lot"]})) == {mac, mac_prior}
    assert not mentioned_slice_ids(ev, {"drivers": [f"Mac fell a lot [{mac}][{mac_prior}]"]})
    assert "Americas" not in str(mentioned_slice_ids(ev, {"drivers": ["Mac fell a lot"]}))

def test_sources_include_named_but_uncited_facts_with_a_note():
    _, ev = _ev()
    mac, _ = _top(ev, "product")
    src = build_sources(FG, {"drivers": ["Mac fell"]}, extra_ids=mentioned_slice_ids(ev, {"drivers": ["Mac fell"]}))
    assert mac in src and "not cited" in src[mac]["note"] and src[mac]["slice"] == "product=Mac"
    prior = next(i for i in src if i != mac and src[i].get("slice") == "product=Mac")
    assert src[prior]["note"].startswith("prior-year")

def test_ask_repairs_pseudo_citations_and_reports_what_is_left():
    r, ev = _ev(); mac, mp = _top(ev, "product"); am, ap = _top(ev, "segment")
    first = {"drivers": ["Mac fell 26.9% [ATTRIBUTION]", "Americas fell 4.2% [ATTRIBUTION]"]}
    second = {"drivers": [f"Mac fell 26.9% [{mac}][{mp}]", f"Americas fell 4.2% [{am}][{ap}]"]}
    seen, original = [], llm.chat_json
    answers = [first, second]
    llm.chat_json = lambda m, **k: (seen.append(m[-1]["content"]), (answers[len(seen) - 1], "mock"))[1]
    try:
        res = ask(FG, "Which segment drove the change in revenue?", retriever=Retriever(FG, embedder=OFFLINE()))
    finally:
        llm.chat_json = original
    assert len(seen) == 2 and "not fact ids" in seen[1] and res["uncited_claims"] == []
    assert mac in res["answer"]["sources"] and "note" not in res["answer"]["sources"][mac]

def test_if_the_model_never_fixes_it_sources_still_appear_by_name():
    first = {"drivers": ["Mac fell 26.9% [ATTRIBUTION]", "Americas fell 4.2% [ATTRIBUTION]"]}
    original = llm.chat_json
    llm.chat_json = lambda m, **k: (first, "mock")
    try:
        res = ask(FG, "Which segment drove the change in revenue?", retriever=Retriever(FG, embedder=OFFLINE()))
    finally:
        llm.chat_json = original
    assert len(res["uncited_claims"]) == 2
    assert [s for s in res["answer"]["sources"].values() if s.get("slice") == "product=Mac" and "note" in s]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
