"""Narrative ranking: graph links (EXPLAINS) may boost a paragraph only for concepts the QUESTION named, and only once.
Overview fallback metrics (a pure text question such as 'what risks...') must not drag in paragraphs the search never found."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)

def _r():
    return Retriever(build_graph(os.path.join(HERE, "apple_like.htm")), embedder=Embedder(model_name="definitely/not-a-model"))

def test_overview_fallback_does_not_boost_unsearched_paragraphs():
    r = _r()
    p = r.plan("What are the main risks the company describes about its suppliers?")
    assert p["concept_source"] == "overview"
    hits = {h["document_id"] for h in r.search(p["question"], top_k=10)}
    for nv in r.retrieve(p)["narrative"]:
        assert nv["id"] in hits, nv["text"][:80]

def test_llm_gets_the_retriever_top_10_in_order():
    fg = build_graph(os.path.join(HERE, "apple_like.htm"))
    for i in range(12):
        fg.add_chunk(f"Risk factor {i}: the company depends on suppliers and outsourcing partners for components; supplier disruption "
                     f"number {i} could adversely affect results, margins and the timing of product shipments.", "Item 1A Risk Factors", 900 + i, [])
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    for q in ("What are the main risks the company describes about its suppliers?", "What were net sales?"):
        p = r.plan(q)
        top10 = [h["document_id"] for h in r.search(p["question"], top_k=10)]
        assert len(top10) == 10
        assert [nv["id"] for nv in r.retrieve(p)["narrative"]] == top10    # no second selection stage (was 6 / 8 slots)

def test_named_concept_still_gets_its_linked_paragraph():
    r = _r()
    p = r.plan("Why did net sales change?")
    linked = {u for u, _, k in r.G.in_edges("c:Revenues", keys=True) if k == "EXPLAINS"}
    assert linked and linked & {nv["id"] for nv in r.retrieve(p)["narrative"]}

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
