import argparse, json, logging, sys
from .graph_builder import build_graph, FilingGraph
from .retrieval import Retriever, RETRIEVAL_MODES, DEFAULT_MODE
from .signals import red_flags, fmt
from . import answer, llm, scenarios as sc
from . import edgar

def provenance(fg, fid, depth=0, seen=None):
    seen = seen or set(); d = fg.F(fid); pad = "  " * depth
    print(f"{pad}{fid} {d['concept']} {d['period']} = {fmt(d['value'], d['unit'])}  [{d['source']}; {d['location']}] flags={d['flags']}")
    if fid in seen or depth > 3: return
    seen.add(fid)
    for _, t, k in fg.G.out_edges(fid, keys=True):
        if k in ("DERIVED_FROM", "ROLLS_UP_TO", "VERIFIES", "CONTRADICTS") or (k == "PRIOR_PERIOD" and depth == 0) and fg.G.nodes[t].get("type") == "Fact":
            print(f"{pad} --{k}-->"); provenance(fg, t, depth + 1, seen)
    for u, _, k in fg.G.in_edges(fid, keys=True):
        if k == "ROLLS_UP_TO" and depth == 0:
            print(f"{pad} <--component: {fg.F(u)['dims']} {fmt(fg.F(u)['value'], fg.F(u)['unit'])} [{u}]")

def main(argv=None):
    ap = argparse.ArgumentParser(prog="tenk-graphrag")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("filing", nargs="?"); b.add_argument("--out", default="graph.json"); b.add_argument("--company")
    b.add_argument("--year", type=int); b.add_argument("--out-dir"); b.add_argument("--refresh", action="store_true")
    b.add_argument("--by-filing-year", action="store_true"); b.add_argument("--include-amendments", action="store_true")
    b.add_argument("--include-variants", action="store_true")
    b.add_argument("--dense", action="store_true", help="also build the dense (BGE) index; only needed for dense/hybrid modes")
    fch = sub.add_parser("fetch"); fch.add_argument("--company", required=True); fch.add_argument("--year", required=True, type=int)
    fch.add_argument("--out-dir"); fch.add_argument("--refresh", action="store_true")
    fch.add_argument("--by-filing-year", action="store_true"); fch.add_argument("--include-amendments", action="store_true")
    fch.add_argument("--include-variants", action="store_true")
    a = sub.add_parser("ask"); a.add_argument("graph"); a.add_argument("question"); a.add_argument("--no-llm", action="store_true", help="print the evidence pack only"); a.add_argument("-v", action="store_true"); a.add_argument("--retrieval", choices=RETRIEVAL_MODES, default=DEFAULT_MODE, help="evidence retrieval mode (default: BM25 + cross-encoder rerank)")
    f = sub.add_parser("flags"); f.add_argument("graph")
    e = sub.add_parser("explain"); e.add_argument("graph"); e.add_argument("fact_id")
    s = sub.add_parser("scenarios"); s.add_argument("graph"); s.add_argument("spec", help='JSON: {"Bear":{"revenue_growth":0.0,"gross_margin":0.40}, ...}'); s.add_argument("--no-llm", action="store_true")
    sub.add_parser("models")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    if args.cmd == "build":
        filing, company = args.filing, args.company
        if filing is None:
            if not args.company or args.year is None:
                ap.error("build requires a filing path, or both --company and --year to download a 10-K")
            try:
                company_info = {}
                filing = str(edgar.download_10k(
                    args.company, args.year, out_dir=args.out_dir, refresh=args.refresh,
                    by_filing_year=args.by_filing_year,
                    include_amendments=args.include_amendments,
                    include_variants=args.include_variants,
                    company_info=company_info,
                ))
            except (ValueError, RuntimeError) as exc:
                ap.error(str(exc))
            company = company_info.get("title") or None
        fg = build_graph(filing, company); fg.save(args.out)
        from collections import Counter
        c = Counter(d["type"] for _, d in fg.G.nodes(data=True)); nf = sum(1 for _ in fg.facts(lambda d: d["source"] != "derived"))
        bad = [d for _, d in fg.G.nodes(data=True) if d.get("type") == "Validation" and d["status"] == "fail"]
        print(f"{fg.meta['company']} FY{fg.meta['fy']}: {nf} typed facts, {c['Validation']} identity checks ({len(bad)} failed) -> {args.out}")
        n_cards = sum(1 for _, d in fg.G.nodes(data=True) if d.get("type") == "Card")
        print(f"retrieval index: {sum(1 for _, d in fg.G.nodes(data=True) if d.get('type') == 'Chunk')} paragraphs + {n_cards} number cards")
        if args.dense:                                             # only the dense/hybrid modes need embeddings
            r = Retriever(fg, retrieval_mode="hybrid_rerank", index_path=args.out + ".dense")
            if r.embedder.is_real:
                r.ensure_dense(); print(f"dense index ({r.embedder.name}) -> {args.out}.dense.npy")
            else:
                print("no embedding model available: dense/hybrid modes will fall back to BM25")
    elif args.cmd == "fetch":
        try:
            path = edgar.download_10k(
                args.company, args.year, out_dir=args.out_dir, refresh=args.refresh,
                by_filing_year=args.by_filing_year,
                include_amendments=args.include_amendments,
                include_variants=args.include_variants,
            )
        except (ValueError, RuntimeError) as exc:
            ap.error(str(exc))
        print(path)
    elif args.cmd == "ask":
        fg = FilingGraph.load(args.graph)
        retr = Retriever(fg, retrieval_mode=args.retrieval, index_path=args.graph + ".dense")
        r = answer.ask(fg, args.question, use_llm=not args.no_llm, verbose=args.v, retriever=retr)
        if args.no_llm: print(r["context"]); return
        print(json.dumps(r["answer"], indent=2, ensure_ascii=False))
        print(f"\n[model: {r['model']}]  ungrounded numbers: {r['ungrounded'] or 'none'}")
    elif args.cmd == "flags":
        for x in red_flags(FilingGraph.load(args.graph)): print(f"[{x['severity'].upper():6}] {x['code']:18} {x['text']}")
    elif args.cmd == "explain":
        provenance(FilingGraph.load(args.graph), args.fact_id)
    elif args.cmd == "scenarios":
        fg = FilingGraph.load(args.graph); out = sc.run_scenarios(fg, json.loads(args.spec))
        print(sc.scenario_prompt(out))
        if not args.no_llm: print(json.dumps(sc.explain_scenarios(out), indent=2))
    elif args.cmd == "models":
        print("\n".join(llm.list_free_models(refresh=True)))

if __name__ == "__main__":
    main()
