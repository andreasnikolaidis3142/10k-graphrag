"""
Audit helper (no LLM, no network).

  python inspect_graph.py graph.json conflicts    # facts that were SET ASIDE as conflicting duplicates
  python inspect_graph.py graph.json differs      # prose numbers that differ from the tables (low-severity flags)
  python inspect_graph.py graph.json ambiguous    # equally-trusted facts with different values (kept, not discarded) - raw values shown
  python inspect_graph.py graph.json all
"""
import collections, sys
from tenk_graphrag.graph_builder import FilingGraph
from tenk_graphrag.signals import fmt


def _why(fg, loser, winner):
    a, b = fg._trust_rank(loser), fg._trust_rank(winner)
    names = ["not-XBRL", "scale-unknown", "statement-inferred", "statement-priority", "unmapped-label"]
    for i, nm in enumerate(names):
        if a[i] != b[i]:
            return nm
    return "TIE (kept the earlier fact id - verify this one by hand)"


def conflicts(fg, limit=25):
    rows = []
    for n, d in fg.facts(lambda d: d["role"] == "shadowed"):
        win = next((t for _, t, k in fg.G.out_edges(n, keys=True) if k == "SHADOWED_BY"), None)
        rows.append((n, d, win, fg.F(win) if win else None))
    if not rows:
        print("No facts were set aside."); return
    print(f"{len(rows)} facts set aside.\n\nBy source table:")
    for loc, c in collections.Counter(d["location"] for _, d, _, _ in rows).most_common(12):
        print(f"  {loc:<12} {c}")
    by_concept = collections.Counter(d["concept"] for _, d, _, _ in rows)
    custom = sum(c for k, c in by_concept.items() if k.startswith("custom:"))
    print(f"\nBy concept (top 10; {custom} of {len(rows)} are generic custom: rows such as 'Total'/'Other'):")
    for k, c in by_concept.most_common(10):
        print(f"  {c:>4}  {k}")
    why = collections.Counter(_why(fg, n, w) for n, _, w, _ in rows if w)
    print("\nWhy the losers lost:")
    for k, c in why.most_common():
        print(f"  {c:>4}  {k}")
    ties = [r for r in rows if r[2] and _why(fg, r[0], r[2]).startswith("TIE")]
    print(f"\nSample (the {limit} biggest disagreements, loser vs winner):")
    def rel(r):
        n, d, w, wd = r
        return abs(d["value"] - wd["value"]) / (abs(wd["value"]) or 1) if wd else 0
    for n, d, w, wd in sorted(rows, key=rel, reverse=True)[:limit]:
        print(f"  {d['concept']:<42} {d['period']:<8} loser {fmt(d['value'], d['unit']):>11} [{n}] {d['location']:<10}"
              f" vs kept {fmt(wd['value'], wd['unit']):>11} [{w}] {wd['location']:<10} -> {_why(fg, n, w)}")
    if ties:
        print(f"\n!! {len(ties)} conflicts were decided only by fact id (a tie). Check these first:")
        for n, d, w, wd in ties[:10]:
            print(f"   {d['concept']} {d['period']}: {fmt(d['value'], d['unit'])} [{n}, {d['location']}] vs {fmt(wd['value'], wd['unit'])} [{w}, {wd['location']}]")


def ambiguous(fg, limit=20):
    rows = [(n, d) for n, d in fg.facts(lambda d: "ambiguous_duplicate" in d["flags"])]
    print(f"{len(rows)} facts have an equally-trusted twin with a different value (both kept).\n")
    for k, c in collections.Counter(d["concept"] for _, d in rows).most_common(10):
        print(f"  {c:>4}  {k}")
    print("\nRaw values (repr) so tiny differences are visible:")
    for n, d in rows[:limit]:
        print(f"  {n} {d['concept']} {d['period']} value={d['value']!r} precision={d['precision']!r} dims={d['dims']} end={d['end']} {d['location']}")


def differs(fg, limit=40):
    rows = [(n, d) for n, d in fg.facts(lambda d: "narrative_mismatch" in d["flags"])]
    print(f"{len(rows)} prose numbers differ from the tables.\n")
    for n, d in rows[:limit]:
        tgt = next((t for _, t, k in fg.G.out_edges(n, keys=True) if k == "CONTRADICTS"), None)
        tv = fg.F(tgt) if tgt else None
        ratio = f"{d['value'] / tv['value']:.2f}x" if tv and tv["value"] else "n/a"
        print(f"[{n}] {d['concept']} {d['period']} role={d['role']}")
        print(f"   text : {fmt(d['value'], d['unit'])}   <- \"{d['context'][:170]}\"")
        if tv:
            print(f"   table: {fmt(tv['value'], tv['unit'])} [{tgt}, {tv['location']}, {tv['label'][:40]}]   text/table = {ratio}")
        print()
    print("Reading guide: text/table far from 1.00x usually means the sentence is about a NARROWER item "
          "(e.g. 'cash paid for income taxes' vs 'provision for income taxes') - not an error.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    g, mode = FilingGraph.load(sys.argv[1]), (sys.argv[2] if len(sys.argv) > 2 else "all")
    if mode in ("conflicts", "all"): conflicts(g)
    if mode in ("ambiguous", "all"):
        print("\n" + "=" * 80 + "\n"); ambiguous(g)
    if mode in ("differs", "all"):
        print("\n" + "=" * 80 + "\n"); differs(g)
