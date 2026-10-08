"""Tests for the corrected retrieval layer. Each test targets one bug from the review."""
import os, tempfile, logging
import numpy as np
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag import retrieval as R
from tenk_graphrag.retrieval import (Retriever, Embedder, DenseRetriever, BM25, reciprocal_rank_fusion,
                                     evaluate_modes, DenseIndexMismatch)

HERE = os.path.dirname(__file__)
FG = build_graph(os.path.join(HERE, "sample_10k.htm"))

class FakeEmbedder:
    """Stands in for BGE: real=True, 32-dim lexical hashing, so we can test the dense/hybrid code paths offline."""
    is_real, backend, model_name = True, "fake", "fake"
    name = "fake:32"
    def __init__(self, dim=32, query_dim=None): self.dim, self.query_dim = dim, query_dim or dim
    def encode(self, texts, is_query=False):
        d = self.query_dim if is_query else self.dim
        v = R._hash_encode(list(texts), dim=d); return v

class SemanticFake(FakeEmbedder):
    """'top line' and 'revenue' land on the same axis, so semantic planning can be exercised."""
    def encode(self, texts, is_query=False):
        out = np.zeros((len(texts), 8), dtype=np.float32)
        for i, t in enumerate(texts):
            tl = t.lower()
            if "revenue" in tl or "top line" in tl: out[i, 0] = 1.0
            else: out[i, 1 + (sum(map(ord, tl)) % 7)] = 1.0
        return out

def test_bm25_is_deterministic_and_positive():
    b = BM25(["net sales grew", "the cat sat", "net sales net sales"])
    assert b.top("net sales", 3)[0] == 2 and all(s >= 0 for s in b.get_scores("net sales"))

def test_rrf_prefers_docs_in_both_lists():
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "d"]])
    assert fused[0][0] == "b"

def test_bug1_retrieve_uses_configured_search_mode():
    r = Retriever(FG, retrieval_mode="bm25"); calls = []
    orig = r.search
    r.search = lambda q, top_k=10, mode=None, **kw: (calls.append((q, top_k)), orig(q, top_k=top_k, mode=mode, **kw))[1]
    r.retrieve(r.plan("Why did net sales grow?"))
    assert calls and calls[0][0] == "Why did net sales grow?"

def test_bug2_docs_and_queries_share_one_embedder():
    r = Retriever(FG, retrieval_mode="dense", embedder=FakeEmbedder())
    hits = r.search("net sales increased to billion", top_k=3)
    assert hits and hits[0]["retrieval_method"] == "dense" and hits[0]["backend"] == "fake"
    assert r.dense.emb.shape[1] == 32                         # docs encoded by the SAME embedder as queries

def test_bug2_dim_mismatch_degrades_to_bm25_not_crash():
    r = Retriever(FG, retrieval_mode="hybrid", embedder=FakeEmbedder(dim=32, query_dim=16))
    hits = r.search("net sales", top_k=3)
    assert hits and all(h["retrieval_method"] == "bm25" for h in hits)

def test_bug2_fallback_is_labelled_not_silent():
    r = Retriever(FG, retrieval_mode="dense", embedder=Embedder(model_name="definitely/not-a-model"))
    hits = r.search("net sales", top_k=2)
    assert hits and hits[0]["backend"] == "hash-fallback"

def test_hybrid_reports_both_ranks_and_order_alignment():
    r = Retriever(FG, retrieval_mode="hybrid", embedder=FakeEmbedder())
    h = r.search("gross margin basis points", top_k=3)
    assert h and h[0]["retrieval_method"] == "hybrid" and "bm25_rank" in h[0] and "dense_rank" in h[0]
    assert r.hybrid.dense.ids == r.ids

def test_rerank_respects_top_k_and_falls_back_lexically():
    r = Retriever(FG, retrieval_mode="hybrid_rerank", embedder=FakeEmbedder())
    h = r.search("employees segments", top_k=2)
    assert len(h) <= 2 and h[0]["retrieval_method"].startswith("hybrid_rerank")

def test_bug3_index_persists_and_stale_index_is_rejected():
    d = tempfile.mkdtemp(); path = os.path.join(d, "idx")
    ids, texts, emb = ["T1", "T2"], ["net sales rose", "gross margin fell"], FakeEmbedder()
    a = DenseRetriever(ids, texts, emb, index_path=path); assert not a.loaded_from_disk and os.path.exists(path + ".npy")
    b = DenseRetriever(ids, texts, emb, index_path=path); assert b.loaded_from_disk
    c = DenseRetriever(ids, ["net sales rose", "TEXT CHANGED"], emb, index_path=path); assert not c.loaded_from_disk
    d2 = DenseRetriever(ids, texts, FakeEmbedder(dim=16), index_path=path)         # different embedder => different fingerprint
    assert not d2.loaded_from_disk

def test_hash_fallback_index_is_never_persisted():
    d = tempfile.mkdtemp(); path = os.path.join(d, "idx")
    DenseRetriever(["T1"], ["net sales rose"], Embedder(model_name="definitely/not-a-model"), index_path=path)
    assert not os.path.exists(path + ".npy")

def test_auto_mode_resolves_to_bm25_rerank_without_loading_an_embedder():
    # default changed on request: BM25 top-50 -> cross-encoder measured as good as hybrid, with no embedding model
    e = Embedder(model_name="definitely/not-a-model")
    r = Retriever(FG, embedder=e)
    assert r.retrieval_mode == "bm25_rerank" and r._resolve_mode("auto") == "bm25_rerank"
    r.retrieve(r.plan("How many employees does the company have?"))
    assert not e._loaded                                     # the BM25 modes never touch the embedding model
    r2 = Retriever(FG, embedder=FakeEmbedder(), retrieval_mode="auto"); assert r2._resolve_mode() == "bm25_rerank"

def test_invalid_mode_raises():
    try: Retriever(FG, retrieval_mode="nope"); assert False
    except ValueError: pass

def test_semantic_planning_maps_question_without_keywords():
    r = Retriever(FG, embedder=SemanticFake(), semantic_planning=True)
    p = r.plan("how is the top line looking")
    assert p["concept_source"] == "semantic" and "Revenues" in p["concepts"]
    p2 = Retriever(FG, embedder=SemanticFake(), semantic_planning=False).plan("top line")
    assert p2["concept_source"] != "semantic"

def test_evaluate_modes_reports_backend():
    r = Retriever(FG, embedder=FakeEmbedder())
    gold = {n for n, d in r.chunks if "employ" in d["text"].lower()}
    out = evaluate_modes(r, [("how many employees", gold)], modes=("bm25", "hybrid"), k=3)
    assert out["bm25"]["recall@3"] == 1.0 and out["hybrid"]["backend"] == "fake"


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
