"""Retrieval benchmark (no LLM). For each question: is an answer-bearing source in the reranked top-10, in the final
evidence set the model would get, and anywhere in the full context pack?

  python eval/retrieval_bench/run_bench.py --tag new  [--pkg <dir containing an old tenk_graphrag>] [--graph co=path ...]
  -> eval/retrieval_bench/results_<tag>.jsonl  and a summary table on stdout

With --pkg pointing at an OLD snapshot (no bm25_rerank mode) the old pipeline is emulated: BM25 top-50 -> the same
cross-encoder -> old final-stage selection.
"""
import argparse, json, logging, os, re, sys, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_GRAPHS = {"aapl": "eval/aapl_2023.json", "wmt": "eval/wmt.json", "jpm": "eval/jpm.json", "xom": "eval/xom.json", "pfe": "eval/pfe.json"}

# ------------------------------------------------------------------ answer matching
_NUM = re.compile(r"(?<![\w.])\(?-?\$?\s?\(?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\)?\s*(%|percent|trillion|billion|million|thousand|bn|mm)?", re.I)
_SCALE = {"trillion": 1e12, "billion": 1e9, "bn": 1e9, "million": 1e6, "mm": 1e6, "thousand": 1e3}
norm = lambda s: re.sub(r"\s+", " ", str(s).replace("’", "'").replace("“", '"').replace("”", '"')).lower()

def _numbers(text):
    for m in _NUM.finditer(text):
        raw, unit = m.group(1), (m.group(2) or "").lower()
        try: n = float(raw.replace(",", ""))
        except ValueError: continue
        digits = len(re.sub(r"\D", "", raw.split(".")[0]))
        dec = len(raw.split(".")[1]) if "." in raw else 0
        yield n, unit, digits, dec, raw

def contains_value(text, v, kind):
    v = abs(v)
    for n, unit, digits, dec, raw in _numbers(text):
        if kind == "percent":
            if abs(n - v) <= 0.051 + 0.5 * 10 ** -max(dec, 0) * (dec == 0): return True
            continue
        if kind == "per_share":
            if dec >= 1 and abs(n - v) <= 0.0051: return True
            continue
        if unit in _SCALE:
            x = n * _SCALE[unit]
            if abs(x - v) <= max(0.5 * 10 ** -dec * _SCALE[unit], 0.002 * v): return True
            continue
        if unit == "%" or (digits == 4 and dec == 0 and "," not in raw and 1990 <= n <= 2035):
            continue                                                # a percent or a year, not an amount
        if digits + dec < 3:
            continue
        for s in (1, 1e3, 1e6, 1e9):                                 # table cells shown in units/thousands/millions/billions
            x = n * s
            if abs(x - v) <= max(0.5 * 10 ** -dec * s, 1e-9 * v) and x > 0:
                return True
    return False

def matches(text, key):
    if "phrases" in key:
        t = norm(text)
        return any(norm(p) in t for p in key["phrases"])
    return contains_value(text, key["value"], key["kind"])

def first_hit(texts, keys):
    for i, t in enumerate(texts, 1):
        if any(matches(t, k) for k in keys):
            return i
    return None

# ------------------------------------------------------------------ runners
def load_pkg(pkg):
    if pkg:
        sys.path.insert(0, pkg)
    sys.path.insert(1, ROOT)
    import tenk_graphrag.retrieval as R
    from tenk_graphrag.graph_builder import FilingGraph
    return R, FilingGraph

def cache_scores(reranker):
    """Persist cross-encoder scores per (question, document text): each pair is scored once, ever. Pure speed-up; the
    scores are exactly what the model returns."""
    import hashlib, sqlite3
    reranker._load()
    model = reranker._model
    if model is None:
        return
    db = sqlite3.connect(os.path.join(HERE, ".rerank_cache.sqlite"))
    db.execute("CREATE TABLE IF NOT EXISTS s (k TEXT PRIMARY KEY, v REAL)")
    orig = model.predict
    tag = f"{reranker.model_name}|{getattr(model, 'max_seq_length', '') or getattr(model, 'max_length', '')}"
    def predict(pairs, **kw):
        keys = [hashlib.sha1((f"{tag}\x00{q}\x00{t}").encode("utf-8")).hexdigest() for q, t in pairs]
        have = {}
        for i in range(0, len(keys), 500):
            chunk = keys[i:i + 500]
            have.update(db.execute(f"SELECT k, v FROM s WHERE k IN ({','.join('?' * len(chunk))})", chunk).fetchall())
        todo = [i for i, k in enumerate(keys) if k not in have]
        if todo:
            new = orig([pairs[i] for i in todo], **kw)
            db.executemany("INSERT OR REPLACE INTO s VALUES (?, ?)", [(keys[i], float(v)) for i, v in zip(todo, new)])
            db.commit()
            have.update({keys[i]: float(v) for i, v in zip(todo, new)})
        return [have[k] for k in keys]
    model.predict = predict

def make_retriever(R, fg, path, reranker):
    if "bm25_rerank" in R.RETRIEVAL_MODES:                           # new code
        r = R.Retriever(fg, retrieval_mode="bm25_rerank", reranker=reranker)
        return r, (lambda q: [(h["document_id"], h["text"]) for h in r.search(q, top_k=10)])
    r = R.Retriever(fg, retrieval_mode="hybrid_rerank", index_path=path + ".dense", reranker=reranker)
    bm_rr = lambda q, top_k=10: r.reranker.rerank(q, r._bm25_hits(q, 50), top_k=top_k)
    r.search = lambda query, top_k=10, mode=None, top_k_candidates=50: bm_rr(query, top_k)    # old final stage on BM25+rerank hits
    return r, (lambda q: [(h["document_id"], h["text"]) for h in bm_rr(q)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True); ap.add_argument("--pkg"); ap.add_argument("--graph", action="append", default=[])
    ap.add_argument("--companies", default="aapl,wmt,jpm,xom,pfe"); ap.add_argument("--split", default="all")
    ap.add_argument("--no-context", action="store_true")
    a = ap.parse_args()
    logging.disable(logging.WARNING)
    os.chdir(ROOT)
    R, FilingGraph = load_pkg(a.pkg)
    graphs = dict(DEFAULT_GRAPHS); graphs.update(dict(g.split("=", 1) for g in a.graph))
    reranker = R.BGEReranker()
    cache_scores(reranker)
    out = open(os.path.join(HERE, f"results_{a.tag}.jsonl"), "w", encoding="utf-8")
    summ = defaultdict(lambda: [0, 0, 0, 0])
    t0 = time.time()
    for co in a.companies.split(","):
        qs = json.load(open(os.path.join(HERE, f"questions_{co}.json"), encoding="utf-8"))
        if a.split != "all":
            qs = [q for q in qs if q["split"] == a.split]
        fg = FilingGraph.load(graphs[co])
        r, top10 = make_retriever(R, fg, graphs[co], reranker)
        for q in qs:
            t10 = top10(q["q"])
            ev = r.retrieve(r.plan(q["q"]))
            fin = [(nv["id"], nv["text"]) for nv in ev["narrative"]]
            ctx = "" if a.no_context else r.build_context(ev)
            h10, hf = first_hit([t for _, t in t10], q["keys"]), first_hit([t for _, t in fin], q["keys"])
            rec = dict(id=q["id"], co=co, group=q["group"], split=q["split"], q=q["q"],
                       hit10=h10, hitfinal=hf, hitctx=bool(ctx) and any(matches(ctx, k) for k in q["keys"]), nfinal=len(fin),
                       hit10_doc=t10[h10 - 1][0] if h10 else None, hit10_text=t10[h10 - 1][1][:300] if h10 else None,
                       top3=[t[:160] for _, t in t10[:3]])
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
            for key in (co, f"{co}:{q['split']}", f"ALL:{q['split']}", f"group:{q['group']}", "ALL"):
                s = summ[key]; s[0] += 1; s[1] += rec["hit10"] is not None; s[2] += rec["hitfinal"] is not None; s[3] += rec["hitctx"]
        print(f"{co} done ({time.time() - t0:.0f}s)", flush=True)
    print(f"\n{'slice':<16}{'n':>5}{'hit@10':>9}{'final':>9}{'context':>9}")
    for k in sorted(summ):
        n, h, f, c = summ[k]
        print(f"{k:<16}{n:>5}{h / n:>9.1%}{f / n:>9.1%}{c / n:>9.1%}")

if __name__ == "__main__":
    main()

