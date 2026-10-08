# Unit tests check logic, not model quality: use the lexical reranker unless a real model is requested explicitly.
import os
os.environ.setdefault("TENK_RERANK_MODEL", "lexical")
