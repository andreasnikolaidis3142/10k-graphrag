"""
Graph retrieval + context assembly.

Query -> plan (concepts, years, dims, intent) -> graph walk (series, roll-up children, derived, narrative, validations)
-> a context pack in which every number carries its semantics (Layers 1-6 of the Reddit post), pre-computed findings
and fact ids for citation.

TWO KINDS OF RETRIEVAL LIVE HERE
  * NUMBERS  : exact graph lookups (series, roll-ups, derived, validations). Never similarity search.
  * NARRATIVE: paragraphs of management text, found with BM25 / dense (BGE) / hybrid (RRF) / hybrid + cross-encoder rerank.

Design rules for the narrative side
  1. ONE embedder instance encodes both documents and queries (a dim mismatch is impossible by construction).
  2. A fallback embedder is never silent: it is logged and every hit says which backend produced it.
  3. A saved dense index is only trusted if its fingerprint (embedder + chunk ids + chunk text) matches.
  4. BM25, dense and hybrid all index the SAME ordered id list, so ids can never drift apart.
"""
import hashlib, json, logging, math, os, re
from collections import Counter, defaultdict

import numpy as np

from .taxonomy import CONCEPTS, find_concepts_in_text
from .cards import expand_query, gloss_query, asks_for_slice
from .signals import series_findings, red_flags, fmt
from .derived import DERIVED

log = logging.getLogger("tenk_graphrag.retrieval")

# ------------------------------------------------------------------ config
EMBED_MODEL = os.getenv("TENK_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
RERANK_MODEL = os.getenv("TENK_RERANK_MODEL", "BAAI/bge-reranker-base")      # -large is very slow on CPU
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
SEMANTIC_MIN_SCORE = float(os.getenv("TENK_SEMANTIC_MIN", "0.55"))            # tune on your own questions
RERANK_MAXLEN = int(os.getenv("TENK_RERANK_MAXLEN", "384"))
RRF_K = 60
TOP_K_CANDIDATES = int(os.getenv("TENK_TOP_K_CANDIDATES", "50"))
NARRATIVE_K = int(os.getenv("TENK_NARRATIVE_K", "10"))       # documents handed to the LLM: the retriever top 10
RETRIEVAL_MODES = ("auto", "bm25", "bm25_rerank", "dense", "hybrid", "hybrid_rerank")
DEFAULT_MODE = os.getenv("TENK_RETRIEVAL_MODE", "bm25_rerank")       # measured: as good as hybrid, no embedding model needed
DENSE_MODES = ("dense", "hybrid", "hybrid_rerank")
SCOPE_PRIOR = float(os.getenv("TENK_SCOPE_PRIOR", "2.0"))           # reranker-logit penalty for slices on company-wide questions

# natural-language aliases for derived metrics / themes
THEMES = {
    "margin": ["GrossMarginPct", "OperatingMarginPct", "NetMarginPct", "EbitdaMarginPct", "GrossProfit",
               "ResearchAndDevelopmentExpense", "SellingGeneralAndAdministrativeExpense", "OperatingExpenses"],     # the cost lines explain WHY margins moved
    "profitab": ["GrossMarginPct", "OperatingMarginPct", "NetMarginPct", "RoePct", "RoaPct",
                 "ResearchAndDevelopmentExpense", "SellingGeneralAndAdministrativeExpense", "OperatingExpenses"],
    "liquidity": ["CurrentRatio", "CashAndCashEquivalentsAtCarryingValue", "NetDebt"],
    "leverage": ["DebtToEquity", "NetDebtToEbitda", "InterestCoverage", "TotalDebt"],
    "debt": ["TotalDebt", "NetDebt", "DebtToEquity", "InterestCoverage"],
    "cash flow": ["NetCashProvidedByUsedInOperatingActivities", "FreeCashFlow", "CashConversion"],
    "working capital": ["DSO", "DIO", "DPO", "CurrentRatio"],
    "quality of earnings": ["CashConversion", "DSO", "NetMarginPct", "SbcIntensityPct"],
    "return on": ["RoePct", "RoaPct", "AssetTurnover"],              # "return on equity/assets"; NOT "how did it return cash to shareholders"
    "growth": ["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"],
    "shareholder": ["ShareholderReturns", "PayoutOfFcfPct", "PaymentsForRepurchaseOfCommonStock"],
    "tax": ["EffectiveTaxRatePct", "IncomeTaxExpenseBenefit"],
    "per share": ["EarningsPerShareDiluted", "EarningsPerShareBasic", "WeightedAverageNumberOfDilutedSharesOutstanding",
                  "WeightedAverageNumberOfSharesOutstandingBasic"],
    # standard us-gaap elements that have no taxonomy entry (an untagged-in-taxonomy XBRL fact keeps its local name as concept)
    " lease": ["OperatingLeaseLiability", "FinanceLeaseLiability", "OperatingLeaseLiabilityCurrent", "OperatingLeaseLiabilityNoncurrent",
               "FinanceLeaseLiabilityCurrent", "FinanceLeaseLiabilityNoncurrent", "OperatingLeaseRightOfUseAsset", "FinanceLeaseRightOfUseAsset", "Assets"],
    "statutory": ["EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate", "EffectiveIncomeTaxRateReconciliationStateAndLocalIncomeTaxes",
                  "EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential", "EffectiveIncomeTaxRateReconciliationTaxCredits",
                  "EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance", "EffectiveIncomeTaxRateReconciliationOtherAdjustments"],
    "membership": ["OtherIncome"],
}
THEME_ALIASES = {"cash flow": ["cash generat", "generate cash", "generated cash", "cash from operat", "operating cash", "cash burn"],   # "how much cash did X generate"
                 "per share": [" eps", "share count", "shares outstanding", "dilution"],
                 "shareholder": ["buyback", "repurchas"],
                 " lease": [" leases", "lease obligation", "lease liabilit"], "statutory": ["rate reconciliation"], "membership": ["other income"]}
DERIVED_ALIAS = {"gross margin": "GrossMarginPct", "operating margin": "OperatingMarginPct", "net margin": "NetMarginPct",
                 "ebitda": "Ebitda", "free cash flow": "FreeCashFlow", "fcf": "FreeCashFlow", "current ratio": "CurrentRatio",
                 "net debt": "NetDebt", "debt to equity": "DebtToEquity", "leverage": "NetDebtToEbitda", "interest coverage": "InterestCoverage",
                 "roe": "RoePct", "roa": "RoaPct", "dso": "DSO", "dio": "DIO", "dpo": "DPO", "days sales": "DSO",
                 "cash conversion": "CashConversion", "effective tax": "EffectiveTaxRatePct", "r&d intensity": "RdIntensityPct"}
OVERVIEW = ["Revenues", "GrossMarginPct", "OperatingIncomeLoss", "OperatingMarginPct", "NetIncomeLoss", "FreeCashFlow", "TotalDebt", "NetDebtToEbitda", "CurrentRatio"]


def _pretty_member(m):
    s = re.sub(r"(Segment|Member)$", "", str(m))
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s).strip() or str(m)


def slice_label(d):
    """Human name of a slice: the table row/group that names it ('iPhone', 'Americas'), else a tidied XBRL member."""
    from .taxonomy import match_concept
    for a in d.get("appears_in", []):
        for cand in (a.get("group"), a.get("row")):
            c = re.sub(r"\s*\(\d{1,2}\)\s*$", "", cand or "").strip()
            if c and not match_concept(c)[0]:
                return c
    vals = list(d["dims"].values())
    if d.get("source") == "table" and vals:
        return ", ".join(str(v) for v in vals)
    return ", ".join(_pretty_member(v) for v in vals) or d["label"]


# ================================================================== BM25 (pure python, deterministic)
class BM25:
    """Okapi BM25 with Lucene-style IDF (always positive).
    Deliberately NOT swapped for `rank_bm25`: its IDF can go negative on small corpora, and results then depend on
    which packages happen to be installed."""

    def __init__(self, docs, k1=1.2, b=0.75):
        self.k1, self.b = k1, b
        self.corpus = list(docs)
        self.docs = [self._tok(d) for d in self.corpus]
        self.tfs = [Counter(d) for d in self.docs]
        self.df = Counter(t for d in self.docs for t in set(d))
        self.avg = sum(map(len, self.docs)) / max(1, len(self.docs))
        self.post = defaultdict(list)                     # inverted index: term -> [doc index]; tens of thousands of cards
        for i, tf in enumerate(self.tfs):
            for t in tf:
                self.post[t].append(i)

    @staticmethod
    def _stem(t):
        """Tiny suffix stemmer so 'repurchases'/'repurchased', 'loans'/'loan' meet. Numbers are left alone."""
        if t.isdigit() or len(t) <= 3:
            return t
        if t.endswith("ies") and len(t) > 5:
            t = t[:-3] + "y"
        elif t.endswith("ing") and len(t) > 6:
            t = t[:-3]
        elif t.endswith("ed") and len(t) > 5:
            t = t[:-2]
        elif t.endswith("s") and not t.endswith("ss") and len(t) > 4:
            t = t[:-1]
        return t[:-1] if t.endswith("e") and len(t) > 3 else t

    STOP = frozenset("a an the of in on at to for by from with and or as is are was were be been being what which who whom how "
                     "much many did does do has have had it its this that these those there their they company s end".split())

    @classmethod
    def _tok(cls, t):
        """Lower-case words, light stemming, no stop/question words (they made long paragraphs outscore short cards)."""
        return [cls._stem(w) for w in re.findall(r"[a-z0-9]+", str(t).lower()) if w not in cls.STOP]

    def _q(self, q):
        return self._tok(q) if isinstance(q, str) else list(q)

    def score(self, q, i):
        tf, n, s = self.tfs[i], len(self.docs), 0.0
        dl = len(self.docs[i])
        for t in self._q(q):
            f = tf.get(t)
            if f:
                idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / (self.avg or 1)))
        return s

    def get_scores(self, q):
        qt, n = self._q(q), len(self.docs)
        scores = [0.0] * n
        for t in qt:                                      # same Okapi formula as score(), only over docs containing t
            if t not in self.post:
                continue
            idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            for i in self.post[t]:
                f, dl = self.tfs[i][t], len(self.docs[i])
                scores[i] += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / (self.avg or 1)))
        return scores

    def top(self, q, k=4):
        """Indices of the k best documents (score > 0), best first."""
        sc = sorted(((s, i) for i, s in enumerate(self.get_scores(q))), key=lambda x: (-x[0], x[1]))
        return [i for s, i in sc[:k] if s > 0]

    def get_top_n(self, q, n=10):
        return [self.corpus[i] for i in self.top(q, n)]


BM25Okapi = BM25


def index_text(text, node):
    """What BM25 indexes for a document. For a number card the SUBJECT (row label / XBRL element name) is what it is
    about, so it is repeated (a field boost), and long digit strings are dropped (they only dilute the card; years stay)."""
    if node.get("type") != "Card":
        return text
    if node.get("kind") == "xbrl":
        subject = text.split("(us-gaap:")[0].split("(", 1)[0].replace("Company total:", "")
    else:
        subject = text.partition(" || ")[2].split(":")[0]
    body = re.sub(r"\b(?!(?:19|20)\d{2}\b)\d[\d,.]*\b", " ", text)
    return f"{subject} {subject} {body}"


# ================================================================== embeddings
def _hash_encode(texts, dim=64):
    """Lexical bag-of-words hashing. NOT semantic. Exists only so the code runs offline; always logged."""
    out = np.zeros((len(texts), dim), dtype=np.float32)
    for r, text in enumerate(texts):
        for tok in re.findall(r"[a-z0-9]+", str(text).lower()):
            out[r, int.from_bytes(hashlib.md5(tok.encode()).digest()[:8], "big") % dim] += 1.0
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.where(norms == 0, 1.0, norms)


class Embedder:
    """The ONLY thing allowed to turn text into vectors. Documents and queries share one instance, so they always
    live in the same vector space. Loads lazily; falls back to hashing if the model is unavailable (and says so)."""

    def __init__(self, model_name=EMBED_MODEL, allow_fallback=True):
        self.model_name, self.allow_fallback = model_name, allow_fallback
        self.query_prefix = BGE_QUERY_PREFIX if "bge" in model_name.lower() else ""
        self._model, self._loaded = None, False

    def _load(self):
        if self._loaded:
            return
        self._loaded = True
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            if not self.allow_fallback:
                raise
            log.info("Embedding model %r unavailable (%s: %s); using hash-fallback.", self.model_name, type(e).__name__, e)

    @property
    def is_real(self):
        self._load()
        return self._model is not None

    @property
    def backend(self):
        return "sentence-transformers" if self.is_real else "hash-fallback"

    @property
    def name(self):
        return f"sentence-transformers:{self.model_name}" if self.is_real else "hash-fallback:64"

    def encode(self, texts, is_query=False):
        texts = [str(t) for t in texts]
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        self._load()
        if self._model is None:
            return _hash_encode(texts)
        if is_query and self.query_prefix:
            texts = [self.query_prefix + t for t in texts]
        arr = self._model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        return np.asarray(arr, dtype=np.float32).reshape(len(texts), -1)


class DenseIndexMismatch(RuntimeError):
    pass


class DenseRetriever:
    """Exact cosine search over normalised embeddings (brute-force matmul is exact and instantaneous for the few
    hundred paragraphs in a 10-K; no FAISS needed). The on-disk index carries a fingerprint and is rebuilt if stale."""

    def __init__(self, ids, texts, embedder, index_path=None, metas=None):
        self.ids, self.texts, self.embedder = list(ids), list(texts), embedder
        self.metas = list(metas) if metas is not None else [{} for _ in self.ids]
        self.index_path = index_path
        self.fingerprint = self._fingerprint()
        self.loaded_from_disk = bool(index_path) and self._load()
        if not self.loaded_from_disk:
            self.emb = embedder.encode(self.texts)
            if index_path and embedder.is_real:          # never persist a fake (hash) index
                self.save()

    def _fingerprint(self):
        h = hashlib.sha256()
        h.update(self.embedder.name.encode())
        for i, t in zip(self.ids, self.texts):
            h.update(b"\x00" + str(i).encode() + b"\x01" + str(t).encode())
        return h.hexdigest()

    def save(self, path=None):
        path = path or self.index_path
        if path is None:
            return
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        np.save(path + ".npy", self.emb.astype(np.float32))
        with open(path + ".json", "w", encoding="utf-8") as fh:
            json.dump({"fingerprint": self.fingerprint, "embedder": self.embedder.name,
                       "n": len(self.ids), "dim": int(self.emb.shape[1]) if self.emb.size else 0}, fh)

    def _load(self):
        p = self.index_path
        if p is None:
            return False
        if not (os.path.exists(p + ".npy") and os.path.exists(p + ".json")):
            return False
        try:
            meta = json.load(open(p + ".json", encoding="utf-8"))
            if meta.get("fingerprint") != self.fingerprint:
                log.info("Dense index at %s is stale (chunks or embedder changed); rebuilding.", p)
                return False
            emb = np.load(p + ".npy").astype(np.float32)
            if emb.shape[0] != len(self.ids):
                return False
            self.emb = emb
            return True
        except Exception as e:
            log.warning("Could not read dense index %s (%s); rebuilding.", p, e)
            return False

    def search(self, query, top_k=10):
        if not self.ids:
            return []
        qv = self.embedder.encode([query], is_query=True)[0]
        if qv.shape[0] != self.emb.shape[1]:
            raise DenseIndexMismatch(f"query vector dim {qv.shape[0]} != index dim {self.emb.shape[1]} "
                                     f"(index built with a different embedder; rebuild it)")
        scores = self.emb @ qv
        order = np.argsort(-scores, kind="stable")[:top_k]
        return [dict(document_id=self.ids[i], text=self.texts[i], metadata=self.metas[i], score=float(scores[i]),
                     retrieval_method="dense", backend=self.embedder.backend) for i in order]


# ================================================================== fusion + rerank
def reciprocal_rank_fusion(ranked_lists, k=RRF_K):
    """[[idA, idB, ...], [idB, idC, ...]] -> [(id, score)] best first. Score = sum 1/(k + rank)."""
    scores = defaultdict(float)
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], str(kv[0])))


class HybridRetriever:
    """BM25 + dense fused with RRF. Works on ids only, so BM25 and dense can't disagree about which chunk is which."""

    def __init__(self, ids, bm25, dense, records, rrf_k=RRF_K):
        self.ids, self.bm25, self.dense, self.records, self.rrf_k = list(ids), bm25, dense, records, rrf_k
        assert self.dense.ids == self.ids, "BM25 and dense indexes must cover the same ids in the same order"

    def search(self, query, top_k=10, depth=TOP_K_CANDIDATES):
        bm_ids = [self.ids[i] for i in self.bm25.top(query, k=depth)]
        dn_ids = [h["document_id"] for h in self.dense.search(query, top_k=depth)]
        bm_rank = {d: r for r, d in enumerate(bm_ids, 1)}
        dn_rank = {d: r for r, d in enumerate(dn_ids, 1)}
        out = []
        for doc_id, score in reciprocal_rank_fusion([bm_ids, dn_ids], k=self.rrf_k)[:top_k]:
            rec = self.records[doc_id]
            out.append(dict(document_id=doc_id, text=rec["text"], metadata=rec["metadata"], score=score, rrf_score=score,
                            bm25_rank=bm_rank.get(doc_id), dense_rank=dn_rank.get(doc_id),
                            retrieval_method="hybrid", backend=self.dense.embedder.backend))
        return out


class BGEReranker:
    """Cross-encoder reranker. Falls back to lexical overlap (logged) if the model is unavailable."""

    def __init__(self, model_name=RERANK_MODEL):
        self.model_name, self._model, self._loaded = model_name, None, False

    def _load(self):
        if self._loaded:
            return
        self._loaded = True
        if str(self.model_name).lower() in ("", "none", "lexical"):      # explicit opt-out (tests, no-model environments)
            log.info("Reranker disabled (TENK_RERANK_MODEL=%r); using lexical-overlap ordering.", self.model_name)
            return
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name, max_length=RERANK_MAXLEN)
        except Exception as e:
            log.warning("Reranker %r unavailable (%s: %s); using lexical-overlap fallback.", self.model_name, type(e).__name__, e)

    @property
    def is_real(self):
        self._load()
        return self._model is not None

    def rerank(self, query, candidates, top_k=10):
        if not candidates:
            return []
        self._load()
        model = self._model
        if model is not None:
            scores = [float(s) for s in model.predict([(query, c["text"]) for c in candidates])]
            method = "hybrid_rerank"
        else:
            q = set(re.findall(r"[a-z0-9]+", query.lower()))
            scores = [float(len(q & set(re.findall(r"[a-z0-9]+", str(c["text"]).lower())))) for c in candidates]
            method = "hybrid_rerank(lexical-fallback)"
        ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])[:top_k]
        return [dict(c, reranker_score=s, score=s, retrieval_method=method) for c, s in ranked]


# ================================================================== optional semantic query planning
class ConceptMapper:
    """Maps a question with NO keyword hit ("top line", "how much cash did they burn") to taxonomy concepts by
    embedding similarity. One vector per concept (label + synonyms). Only used when a real embedder is present."""

    def __init__(self, embedder, present):
        self.embedder, self.present = embedder, set(present)
        keys, texts = [], []
        for k, v in CONCEPTS.items():
            keys.append(k); texts.append(f"{v['label']}: " + ", ".join(v["syn"][:8]))
        inv = defaultdict(list)
        for alias, key in DERIVED_ALIAS.items():
            inv[key].append(alias)
        for spec in DERIVED:
            if spec["name"] not in CONCEPTS:
                keys.append(spec["name"]); texts.append(f"{spec['label']}: {spec['formula']}, " + ", ".join(inv.get(spec["name"], [])))
        self.keys = keys
        self.emb = embedder.encode(texts)

    def top(self, question, k=2, min_score=SEMANTIC_MIN_SCORE):
        qv = self.embedder.encode([question], is_query=True)[0]
        if qv.shape[0] != self.emb.shape[1]:
            return []
        sims = self.emb @ qv
        out = []
        for i in np.argsort(-sims, kind="stable"):
            if sims[i] < min_score or len(out) >= k:
                break
            if self.keys[i] in self.present:
                out.append((self.keys[i], float(sims[i])))
        return out


# ================================================================== the retriever
class Retriever:
    VALID_MODES = set(RETRIEVAL_MODES)

    def __init__(self, fg, retrieval_mode=DEFAULT_MODE, index_path=None, embedder=None, reranker=None, semantic_planning=None):
        """
        retrieval_mode: bm25_rerank (default: BM25 top-50 -> cross-encoder) | auto (= bm25_rerank) | bm25 | dense | hybrid
                        | hybrid_rerank. The embedding model is only loaded by the dense modes.
        index_path    : where to persist the dense index (fingerprinted; rebuilt automatically when stale)
        semantic_planning: None = on only in a dense mode with a real embedder; True/False to force
        Documents: paragraphs (T..., with their heading context), table-row cards (R...) and XBRL series cards (X...).
        """
        self.fg, self.G = fg, fg.G
        self.chunks = [(n, d) for n, d in self.G.nodes(data=True) if d.get("type") in ("Chunk", "Card")]
        self.ids = [n for n, _ in self.chunks]                      # THE single source of ordering
        def shown(d):                                               # heading context travels with the paragraph
            return (f"[{d['ctx']}] " if d.get("ctx") else "") + d.get("text", "")
        self.records = {n: {"document_id": n, "text": shown(d),
                            "metadata": {k: v for k, v in d.items() if k not in ("type", "text")} | {"doc_type": d.get("type")}}
                        for n, d in self.chunks}
        self.bm25 = BM25([index_text(self.records[n]["text"], self.G.nodes[n]) for n in self.ids]) if self.chunks else None
        self.embedder = embedder or Embedder()
        self.reranker = reranker or BGEReranker()
        self.index_path = index_path
        self.semantic_planning = semantic_planning
        self._dense = self._hybrid = self._mapper = None
        self._warned_fallback = False
        self._rerank_cache = {}
        self.set_retrieval_mode(retrieval_mode)
        self.fys = sorted({d["fy"] for _, d in fg.facts(lambda d: d["source"] != "text")})
        self.dims = defaultdict(set)
        for n, d in self.G.nodes(data=True):
            if d.get("type") == "Dim":
                self.dims[d["axis"]].add(d["member"])
        self.present_concepts = {d["key"] for _, d in self.G.nodes(data=True) if d.get("type") == "Concept"}

    # ---------------------------------------------------------------- narrative retrieval
    def set_retrieval_mode(self, mode):
        mode = str(mode).lower()
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unsupported retrieval mode: {mode!r}. Supported: {sorted(self.VALID_MODES)}")
        self.retrieval_mode = mode
        return self

    def _resolve_mode(self, mode=None):
        mode = self.retrieval_mode if mode is None else str(mode).lower()
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unsupported retrieval mode: {mode!r}. Supported: {sorted(self.VALID_MODES)}")
        if mode == "auto":
            return "bm25_rerank"
        return mode

    def _members(self):
        """Dimension members in words ('Walmart International', 'Greater China') to detect slice questions."""
        if not hasattr(self, "_member_words"):
            self._member_words = {_pretty_member(m) for ms in self.dims.values() for m in ms if m}
        return self._member_words

    @property
    def dense(self):
        if self._dense is None:
            texts = [self.records[i]["text"] for i in self.ids]
            self._dense = DenseRetriever(self.ids, texts, self.embedder, self.index_path,
                                         metas=[self.records[i]["metadata"] for i in self.ids])
        return self._dense

    @property
    def hybrid(self):
        if self._hybrid is None:
            self._hybrid = HybridRetriever(self.ids, self.bm25, self.dense, self.records)
        return self._hybrid

    def ensure_dense(self):
        """Build (and persist, if index_path is set) the dense index now. Call once at build time."""
        return self.dense if self.chunks else None

    def _bm25_hits(self, query, top_k):
        if self.bm25 is None:
            return []
        out = []
        for i in self.bm25.top(query, k=top_k):
            rec = self.records[self.ids[i]]
            out.append(dict(document_id=self.ids[i], text=rec["text"], metadata=rec["metadata"],
                            score=float(self.bm25.score(query, i)), retrieval_method="bm25", backend="lexical"))
        return out

    def search(self, query, top_k=10, mode=None, top_k_candidates=TOP_K_CANDIDATES):
        """-> list of hit dicts {document_id, text, metadata, score, retrieval_method, backend, ...}, best first."""
        if not self.chunks:
            return []
        mode = self._resolve_mode(mode)
        lex = expand_query(query)                                   # filing-side vocabulary for the LEXICAL side only
        if mode == "bm25":
            return self._bm25_hits(lex, top_k)
        if mode == "bm25_rerank":
            depth = max(top_k_candidates, top_k)
            rq = gloss_query(query)                                 # the cross-encoder reads plain words, not jargon
            key = (rq, depth)
            if key not in self._rerank_cache:                       # rerank all candidates once; any top_k is a slice
                cands = self._bm25_hits(lex, depth)
                try:
                    hits = [dict(h, retrieval_method="bm25_rerank") for h in self.reranker.rerank(rq, cands, top_k=depth)]
                except Exception as e:
                    log.warning("Reranking failed (%s: %s); returning BM25 order.", type(e).__name__, e)
                    return cands[:top_k]
                if SCOPE_PRIOR and not asks_for_slice(query, self._members()):
                    # a company-wide question: demote segment / product / region slices (no bonus for totals: a bonus
                    # lifted irrelevant company-total cards above the right table row or paragraph)
                    bonus = {"slice": -SCOPE_PRIOR}
                    hits.sort(key=lambda h: -(h["score"] + bonus.get(h["metadata"].get("scope"), 0.0)))
                self._rerank_cache[key] = hits
                if len(self._rerank_cache) > 256:
                    self._rerank_cache.pop(next(iter(self._rerank_cache)))
            return self._rerank_cache[key][:top_k]
        if not self.embedder.is_real and not self._warned_fallback:
            log.warning("Mode %r is running on the hash-fallback embedder: lexical, NOT semantic. "
                        "Install sentence-transformers (and allow the model download) for real dense retrieval.", mode)
            self._warned_fallback = True
        try:
            if mode == "dense":
                return self.dense.search(query, top_k=top_k)
            depth = max(top_k_candidates, TOP_K_CANDIDATES)
            if mode == "hybrid":
                return self.hybrid.search(query, top_k=top_k, depth=depth)
            cands = self.hybrid.search(query, top_k=max(top_k_candidates, top_k), depth=depth)      # hybrid_rerank
            try:
                return self.reranker.rerank(query, cands, top_k=top_k)
            except Exception as e:
                log.warning("Reranking failed (%s: %s); returning hybrid order.", type(e).__name__, e)
                return cands[:top_k]
        except DenseIndexMismatch as e:
            log.warning("%s -> falling back to BM25.", e)
            return self._bm25_hits(query, top_k)

    # ---------------------------------------------------------------- plan
    def _semantic_on(self):
        if self.semantic_planning is not None:
            return bool(self.semantic_planning)
        return self._resolve_mode() in DENSE_MODES and self.embedder.is_real     # never load an embedder for BM25 modes

    @property
    def mapper(self):
        if self._mapper is None:
            self._mapper = ConceptMapper(self.embedder, self.present_concepts)
        return self._mapper

    @staticmethod
    def _with_inputs(concepts, cap=12):
        """For a derived ratio (InterestCoverage, CurrentRatio, DebtToEquity ...) also retrieve the series it is computed from,
        so the model can explain WHY it moved (interest expense up) instead of guessing from the ratio alone."""
        spec = {}
        for d in DERIVED:
            inputs = d.get("inputs") or []
            if isinstance(inputs, (list, tuple)):
                spec[d["name"]] = [c for _, c, _, _ in inputs]
        out, i = list(concepts), 0
        while i < len(out) and len(out) < cap:
            for inp in spec.get(out[i], []):
                if inp not in out and len(out) < cap:
                    out.append(inp)
            i += 1
        return out

    def plan(self, q):
        ql = " " + q.lower()
        concepts, source = [], "keyword"
        for _, _, key, phrase in find_concepts_in_text(re.sub(r"\s*&\s*", " and ", q)):      # "R&D" -> "R and D", as taxonomy.norm spells synonyms
            if key not in concepts: concepts.append(key)
        for alias, key in DERIVED_ALIAS.items():
            if alias in ql and key not in concepts: concepts.append(key)
        for theme, keys in THEMES.items():
            if (theme in ql or any(a in ql for a in THEME_ALIASES.get(theme, ()))) and not (theme == "growth" and concepts):      # "revenue growth" is about revenue, not net income / operating income too
                concepts += [k for k in keys if k not in concepts]
        if not concepts and self._semantic_on():
            concepts = [k for k, _ in self.mapper.top(q)]
            source = "semantic" if concepts else source
        yrs = sorted({int(y) for y in re.findall(r"\b(?:fy\s?|fiscal\s+)?((?:19|20)\d{2})\b", ql)} |
                     {2000 + int(y) for y in re.findall(r"\bfy\s?'?(\d{2})\b", ql)})
        latest = self.fg.meta.get("fy") or (self.fys[-1] if self.fys else None)      # the filing's year, not a far-future maturity bucket
        if re.search(r"\b(latest|this year|most recent)\b|\bcurrent\b(?!\s+(?:ratio|assets?|liabilit|portion|debt|maturit|investments?|tax))",
                     ql) and latest: yrs.append(latest)                              # "current ratio" is not a time word
        if re.search(r"\b(last year|prior year|previous year)\b", ql) and latest: yrs.append(latest - 1)
        trend = bool(re.search(r"\b(trend|over time|history|since|growth|grew|cagr|trajectory|evolv|change)\b", ql))
        intent = ("screen" if re.search(r"red flag|risk|concern|health|quality|overview|summar|analy[sz]e|assess|how is|how are", ql) else
                  "attribution" if re.search(r"\bwhy\b|driver|cause|explain|attribut|what drove|contribut|mix|segment", ql) else
                  "compare" if re.search(r"\bvs\b|versus|compare|compared", ql) else "lookup")
        qn = ql.replace("-", "")                                                      # "e-commerce" finds member "ECommerce"
        dims = {ax: [m for m in mem if m and (m.lower() in ql or m.lower() in qn)] for ax, mem in self.dims.items()}
        dims = {a: m for a, m in dims.items() if m}
        if not concepts and intent in ("screen", "attribution"):
            concepts, source = list(OVERVIEW), "overview"
        primary = list(concepts)                               # what the question is ABOUT (before adding the inputs of derived ratios)
        concepts = self._with_inputs(concepts)
        return dict(concepts=concepts, primary=primary, concept_source=source, years=sorted(set(yrs)), trend=trend or not yrs,
                    intent=intent, dims=dims, question=q)

    # ---------------------------------------------------------------- graph walk
    def _facts_for(self, concept, years, dims=None):
        out = []
        stock = CONCEPTS.get(concept, {}).get("ptype") == "instant"     # a balance: a fiscal-YEAR fact of it is a misread note row or a cash-flow change
        for n, d in self.fg.facts(lambda d: d["concept"] == concept and d["source"] != "text" and d["role"] in ("level", "derived") and
                                  d["dims"] == (dims or {}) and (d["ptype"] == "instant" or (d["months"] in (12, 13) and not stock))):
            if not years or d["fy"] in years: out.append((d["end"], n, d["period"]))
        out.sort()
        seen, res = set(), []
        for e, n, per in out:                            # one fact per PERIOD (end dates can differ by a few days between tables)
            if per not in seen: seen.add(per); res.append((e, n))
        return res

    @staticmethod
    def _one_per_period(rows):
        rows.sort(); seen, res = set(), []
        for e, n, per in rows:
            if per not in seen: seen.add(per); res.append((e, n))
        return res

    def _xbrl_twins(self, concept, years, shown):
        """Equally-trusted XBRL twins: two different elements mapped to one concept (total revenues vs net sales, net income incl.
        vs excl. noncontrolling interests). The one-per-period series hides one of them; return each hidden element as its own series."""
        groups = defaultdict(list)
        for n, d in self.fg.facts(lambda d: d["concept"] == concept and d["source"] == "ixbrl" and not d["dims"] and d["role"] == "level"
                                  and "ambiguous_duplicate" in d["flags"] and (d["ptype"] == "instant" or d["months"] in (12, 13))):
            if n not in shown and (not years or d["fy"] in years):
                groups[d["location"]].append((d["end"], n, d["period"]))
        return [self._one_per_period(g) for g in groups.values()]

    def _sub_slices(self, concept, years, ax, m):
        """A member tagged only together with one more axis (e-commerce x segment): one series per combination."""
        groups = defaultdict(list)
        for n, d in self.fg.facts(lambda d: d["concept"] == concept and d["source"] != "text" and d["role"] in ("level", "derived")
                                  and len(d["dims"]) == 2 and d["dims"].get(ax) == m and (d["ptype"] == "instant" or d["months"] in (12, 13))):
            if not years or d["fy"] in years:
                groups[tuple(sorted(d["dims"].items()))].append((d["end"], n, d["period"]))
        return [dict(concept=concept, dims=dict(k), items=self._one_per_period(g)) for k, g in groups.items()]

    def _prior(self, fid):
        """Same series one year earlier: {id, value, delta, pct} or None (follows the PRIOR_PERIOD edge)."""
        for _, t, k, e in self.G.out_edges(fid, keys=True, data=True):
            if k == "PRIOR_PERIOD":
                return dict(id=t, value=self.fg.F(t)["value"], delta=e.get("delta"), pct=e.get("pct"))

    def children(self, fid):
        return [(u, self.fg.F(u)) for u, _, k in self.G.in_edges(fid, keys=True)
                if k == "ROLLS_UP_TO" and self.fg.F(u)["role"] != "shadowed"]

    def retrieve(self, plan):
        ev = dict(series=[], attribution=[], narrative=[], flags=[], validations=[], mismatches=[], plan=plan)
        primary = plan.get("primary") or plan["concepts"]
        want_years = set(plan["years"])
        if want_years and plan["trend"]:                 # include prior year for YoY context
            want_years |= {y - 1 for y in want_years}
        for c in plan["concepts"][:12]:
            s = self._facts_for(c, want_years if want_years else None)
            if s: ev["series"].append(dict(concept=c, dims={}, items=s))
            for tw in self._xbrl_twins(c, want_years or None, {n for _, n in s}):
                ev["series"].append(dict(concept=c, dims={}, items=tw))
            for ax, mems in plan["dims"].items():
                for m in mems:
                    s2 = self._facts_for(c, want_years or None, {ax: m})
                    if s2: ev["series"].append(dict(concept=c, dims={ax: m}, items=s2))
                    else: ev["series"] += self._sub_slices(c, want_years or None, ax, m)
            if c in primary and plan["intent"] in ("attribution", "screen", "lookup") and s:      # inputs of a ratio get a series, not a breakdown
                last = s[-1][1]
                kids = self.children(last)
                if any(d["source"] == "ixbrl" for _, d in kids):          # XBRL slices are authoritative; table rows only duplicate them or are
                    kids = [(k, d) for k, d in kids if d["source"] == "ixbrl"]       # pseudo-segments ("Unit counts at period end")
                if kids:
                    tot = self.fg.F(last)["value"]
                    by_axis = defaultdict(list)                  # product / segment / geography breakdowns are separate views of the SAME total
                    for k, d in kids:
                        by_axis[next(iter(d["dims"]), "component")].append((k, d))
                    for axis, group in by_axis.items():
                        rows = [dict(id=k, d=d, pct=d["value"] / tot * 100 if tot else None, prior=self._prior(k)) for k, d in group]
                        # biggest MOVER first (by size of the change vs prior year), not biggest component
                        def row_sort_key(r):
                            prior = r.get("prior")
                            if prior and prior.get("delta") is not None:
                                return -abs(prior["delta"])
                            return -abs(r["d"]["value"])
                        rows.sort(key=row_sort_key)
                        ev["attribution"].append(dict(parent=last, concept=c, axis=axis, parent_prior=self._prior(last), children=rows))
        if plan["intent"] == "attribution":              # segment/geo breakdown even if not asked by name
            sliced = []
            for c in primary[:4]:                        # a ratio has no slices: slice its inputs (operating margin -> operating income)
                sliced += [x for x in self._with_inputs([c]) if x not in sliced]
            for c in sliced:
                xbrl_sliced = any(True for _ in self.fg.facts(lambda d: d["concept"] == c and d["dims"] and d["source"] == "ixbrl"))
                for dk, mems in self.dims.items():
                    for m in sorted(mems):
                        s2 = self._facts_for(c, want_years or None, {dk: m})
                        if xbrl_sliced and s2 and all(self.fg.F(n)["source"] != "ixbrl" for _, n in s2):
                            continue                     # a table-row pseudo-segment next to real XBRL slices
                        if s2 and not any(x["concept"] == c and x["dims"] == {dk: m} for x in ev["series"]):
                            ev["series"].append(dict(concept=c, dims={dk: m}, items=s2))
        # evidence documents = the search top NARRATIVE_K as ranked (no second selection stage: the old 6/8-slot cut
        # dropped right answers ranked 7-10). Graph links (EXPLAINS of concepts the question NAMED) only fill slots the
        # search left empty (tiny filings) - they used to outrank better hits when the concept guess was wrong.
        k_narr = NARRATIVE_K
        picked = [h["document_id"] for h in self.search(plan["question"], top_k=k_narr)] if self.chunks else []
        named = [] if plan.get("concept_source") in ("overview", "semantic") else primary
        for u in sorted({u for c in named if ("c:" + c) in self.G for u, _, k in self.G.in_edges("c:" + c, keys=True) if k == "EXPLAINS"}):
            if len(picked) >= k_narr:
                break
            if u not in picked:
                picked.append(u)
        for cid in picked:
            mentioned = [t for _, t, k in self.G.out_edges(cid, keys=True) if k == "MENTIONS"]
            ev["narrative"].append(dict(id=cid, text=self.records[cid]["text"] if cid in self.records else self.G.nodes[cid]["text"],
                                        section=self.G.nodes[cid].get("section", ""), facts=mentioned))
        shown = {n for s in ev["series"] for _, n in s["items"]}
        for n, d in self.G.nodes(data=True):
            if d.get("type") == "Validation" and any(t in shown for _, t, k in self.G.out_edges(n, keys=True) if k in ("VALIDATES", "USES")):
                ev["validations"].append(d | {"id": n})
        ev["mismatches"] = [(n, d) for n, d in self.fg.facts(lambda d: "narrative_mismatch" in d["flags"])]
        if plan["intent"] == "screen":
            shown_concepts = {sr["concept"] for sr in ev["series"]}
            ev["flags"] = [f for f in red_flags(self.fg)
                           if f["code"] != "NARRATIVE_DIFFERS" or (f["facts"] and self.fg.F(f["facts"][0])["concept"] in shown_concepts)]
        return ev

    # ---------------------------------------------------------------- context pack
    def render_series(self, s):
        fg = self.fg
        facts = [(e, n, fg.F(n)) for e, n in s["items"]]
        d0 = facts[0][2]
        kind = "STOCK (point-in-time balance; do NOT sum across dates)" if d0["ptype"] == "instant" else \
               f"FLOW ({d0['months']}-month period; do NOT add annual values together)"
        if d0["source"] == "derived": kind = f"DERIVED ratio/metric = {d0['formula']} (already computed; do not recompute)"
        if d0["unit"] == "percent": kind += "; unit is PERCENT - differences are percentage points, not %"
        lines = [f"SERIES {s['concept']}{' ' + str(s['dims']) if s['dims'] else ''} - {d0['label'][:60]}",
                 f"  VIEW: {kind}",
                 f"  UNIT: {d0['unit']} (filing displayed in {({1e3: 'thousands', 1e6: 'millions', 1e9: 'billions'}).get(d0['scale'], 'units')}; values below are normalised to base units)"]
        if any(g[2]["is_total"] for g in facts) and not s["dims"]:
            lines.append("  CONTEXT: this is a TOTAL line; its components (if listed under ATTRIBUTION) already roll up into it.")
        if s["dims"]:
            lines.append(f"  CONTEXT: this is a {list(s['dims'])[0].upper()} slice, one component of the consolidated total - not the company total.")
        for e, n, d in facts:
            tags = []
            if "rollup_failed" in d["flags"] or any(f.startswith("identity_fail") for f in d["flags"]): tags.append("CHECK-FAILED")
            elif "rollup_verified" in d["flags"] or any(f.startswith("identity_pass") for f in d["flags"]): tags.append("verified")
            if d["source"] == "ixbrl": tags.append("XBRL-tagged")
            elif d["source"] == "table" and d.get("table_no"): tags.append(f'(table {d["table_no"]}: {(d.get("table_title") or d["stmt"])[:40]})')
            if d["parens_negative"] and d["concept"] in CONCEPTS and CONCEPTS[d["concept"]]["abs"]: tags.append("outflow shown as magnitude")
            lines.append(f"  {d['period']:<12} {fmt(d['value'], d['unit']):>14}  [{n}] {' '.join(tags)}")
        sf = series_findings(fg, s["items"])
        if sf and len(facts) > 1:
            lines.append("  PRE-COMPUTED FINDINGS (treat as facts):")
            lines += [f"   - {x}" for x in sf[:8]]
        return "\n".join(lines)

    def build_context(self, ev):
        fg, out = self.fg, []
        meta = fg.meta
        out.append(f"COMPANY: {meta.get('company')} | Fiscal year end: month {meta.get('fy_end_month')} day {meta.get('fy_end_day')} | Latest fiscal year in filing: FY{meta.get('fy')}")
        out.append("TIME CONTEXT: periods named FY#### are ACTUALS reported in this 10-K. Text facts with role 'guidance' are FORWARD-LOOKING management estimates, not actuals.")
        out.append("")
        for s in ev["series"]:
            out.append(self.render_series(s)); out.append("")
        for a in ev["attribution"]:
            p, pp = fg.F(a["parent"]), a.get("parent_prior")
            head = f"ATTRIBUTION of {a['concept']} {p['period']} BY {a.get('axis', 'component').upper()}, total {fmt(p['value'], p['unit'])} [{a['parent']}]"
            if pp and pp["delta"] is not None and pp["pct"] is not None:
                head += f"; change vs prior year {fmt(pp['delta'], p['unit'])} ({pp['pct']:+.1f}%) [{pp['id']}]"
            has_change = bool(pp and pp["delta"])
            out.append(head + (" (components sorted by size of their CHANGE vs prior year, biggest mover first):" if has_change
                               else " (components sorted by size, largest first):"))
            for i, r in enumerate(a["children"]):
                d, pct, pr = r["d"], r["pct"], r["prior"]
                label = slice_label(d)
                line = f"  - {label}: {fmt(d['value'], d['unit'])}" + (f" = {pct:.1f}% of total" if pct is not None else "") + f" [{r['id']}]"
                if pr and pr["delta"] is not None:
                    line += f"; prior year {fmt(pr['value'], d['unit'])} [{pr['id']}], change {fmt(pr['delta'], d['unit'])}" + (f" ({pr['pct']:+.1f}%)" if pr["pct"] is not None else "")
                    if pp and pp["delta"]:
                        share = pr["delta"] / pp["delta"] * 100
                        if abs(share) > 100:        # tiny net change: a percentage share would be meaningless (and misleading)
                            line += (f", a swing of {fmt(pr['delta'], d['unit'])} against a NET total change of only {fmt(pp['delta'], p['unit'])}"
                                     " (other components offset it; no percentage share is meaningful)")
                        elif share >= 0:
                            line += f", {share:.0f}% of the total change"
                        else:
                            line += f", moves AGAINST the total change (offsets {abs(share):.0f}% of it)"
                        if i == 0:
                            line += "  <- LARGEST CONTRIBUTOR TO THE CHANGE"
                out.append(line)
            if pp and pp["delta"]:
                out.append("  (A component's share of the total change can exceed 100% or be negative when other components offset it.)")
            out.append("")
        if ev["narrative"]:
            out.append("NARRATIVE EVIDENCE (management text [T..., with its heading path], table rows [R...] and XBRL series [X...] "
                       "written out as sentences; numbers in text were machine-checked against the tables):")
            for nv in ev["narrative"]:
                st = []
                for fid in nv["facts"]:
                    d = fg.F(fid)
                    st.append("OK" if "verified_by_table" in d["flags"] or "verified_other_period" in d["flags"] else "MISMATCH" if "narrative_mismatch" in d["flags"] else "unchecked")
                out.append(f"  [{nv['id']}] ({nv['section'] or 'n/a'}; number checks: {', '.join(st) or 'none'}) {nv['text'][:900]}")
            out.append("")
        if ev["flags"]:
            out.append("RED-FLAG SCREEN (pre-computed across statements; MUST be considered):")
            for f in sorted(ev["flags"], key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f["severity"], 3))[:14]:
                out.append(f"  - [{f['severity'].upper()}] {f.get('label', f['code'])}: {f['text']} {' '.join('[' + x + ']' for x in f['facts'][:3])}")
            out.append("")
        bad = [v for v in ev["validations"] if v["status"] == "fail"]
        out.append(f"DATA QUALITY: {len(ev['validations']) - len(bad)} accounting identities passed, {len(bad)} failed for the numbers above."
                   + (" Failed: " + "; ".join(f"{v['name']} {v['period']} (off by {fmt(v['diff'], 'USD')})" for v in bad) if bad else ""))
        shown = {s["concept"] for s in ev["series"]}                  # only mention conflicts that touch the metrics above
        n_shadow = sum(1 for _ in fg.facts(lambda d: d["role"] == "shadowed" and d["concept"] in shown))
        if n_shadow:
            out.append(f"NOTE: for the metrics above, {n_shadow} duplicate facts with conflicting values were set aside during parsing (the primary-statement value was kept).")
        if ev["mismatches"]:
            out.append("TEXT-vs-TABLE CONFLICTS: " + "; ".join(                f"'{d['label']}' says {fmt(d['value'], d['unit'])} but tables imply {d['computed_from_tables']:.1f} [{n}]"
                for n, d in ev["mismatches"][:4] if d.get("computed_from_tables") is not None))
        return "\n".join(out)


# ================================================================== measure, don't guess
def evaluate_modes(retriever, qa, modes=("bm25", "dense", "hybrid", "hybrid_rerank"), k=5):
    """qa = [(question, {gold_chunk_id, ...}), ...]  ->  {mode: {"recall@k": x, "mrr": y, "backend": ...}}.
    Check the 'backend' field first: if it says hash-fallback you are NOT measuring a semantic model."""
    res = {}
    for m in modes:
        hit = rr = 0.0
        backend = "lexical"
        for q, gold in qa:
            hits = retriever.search(q, top_k=k, mode=m)
            ids = [h["document_id"] for h in hits]
            backend = hits[0]["backend"] if hits else backend
            hit += bool(set(ids) & set(gold))
            rr += next((1.0 / (i + 1) for i, d in enumerate(ids) if d in gold), 0.0)
        res[m] = {f"recall@{k}": hit / len(qa), "mrr": rr / len(qa), "backend": backend}
    return res
