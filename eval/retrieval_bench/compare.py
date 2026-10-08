"""Compare two benchmark runs.  python eval/retrieval_bench/compare.py old new [--top 20] [--md out.md]"""
import argparse, json, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

def load(tag):
    return {r["id"]: r for r in map(json.loads, open(os.path.join(HERE, f"results_{tag}.jsonl"), encoding="utf-8"))}

def rate(rows, key):
    rows = list(rows)
    return sum(r[key] not in (None, False) for r in rows) / len(rows) if rows else 0.0

def doc_kind(doc_id):
    if not doc_id:
        return "-"
    return {"T": "paragraph", "R": "table-row card", "X": "XBRL series card"}.get(doc_id[0], doc_id)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("old"); ap.add_argument("new")
    ap.add_argument("--top", type=int, default=20); ap.add_argument("--md")
    a = ap.parse_args()
    old, new = load(a.old), load(a.new)
    ids = [i for i in new if i in old]
    lines = []
    def p(s=""):
        lines.append(s); print(s)
    p(f"| slice | n | hit@10 old -> new | final set old -> new | full context old -> new |")
    p("|---|---|---|---|---|")
    slices = defaultdict(list)
    for i in ids:
        o, n = old[i], new[i]
        for k in ("ALL", f"split:{n['split']}", f"company:{n['co']}", f"type:{n['group']}"):
            slices[k].append(i)
    for k in sorted(slices, key=lambda s: (s != "ALL", s)):
        rows = slices[k]
        cells = [f"{rate([old[i] for i in rows], m):.0%} -> {rate([new[i] for i in rows], m):.0%}" for m in ("hit10", "hitfinal", "hitctx")]
        p(f"| {k} | {len(rows)} | " + " | ".join(cells) + " |")
    gained = [i for i in ids if old[i]["hitfinal"] is None and new[i]["hitfinal"] is not None]
    lost = [i for i in ids if old[i]["hitfinal"] is not None and new[i]["hitfinal"] is None]
    p(f"\nFinal-set transitions: {len(gained)} fixed, {len(lost)} lost, "
      f"{sum(old[i]['hitfinal'] is not None and new[i]['hitfinal'] is not None for i in ids)} kept, "
      f"{sum(old[i]['hitfinal'] is None and new[i]['hitfinal'] is None for i in ids)} still missing")
    kinds = defaultdict(int)
    for i in gained:
        kinds[doc_kind(new[i].get("hit10_doc"))] += 1
    p("Fixed questions by the document type that now answers them: " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))
    # most-improved: previously not even in the top-10, now in the final set, earliest rank first; spread over companies
    cand = sorted([i for i in gained if old[i]["hit10"] is None], key=lambda i: (new[i]["hitfinal"], i))
    per_co, pick = defaultdict(int), []
    for i in cand:
        if per_co[new[i]["co"]] < (a.top + 4) // 5:
            pick.append(i); per_co[new[i]["co"]] += 1
    for i in cand:
        if len(pick) >= a.top: break
        if i not in pick: pick.append(i)
    p(f"\n### {len(pick[:a.top])} questions that failed before and are answered now\n")
    for i in pick[:a.top]:
        n = new[i]
        p(f"- **{i}** ({n['split']}) {n['q']}")
        p(f"  - before: not in the top 10 (top hit: \"{old[i]['top3'][0][:110] if old[i]['top3'] else '-'}\")")
        p(f"  - now: rank {n['hit10'] or '-'} in top 10, in final set at {n['hitfinal']}, via {doc_kind(n.get('hit10_doc'))}: \"{(n.get('hit10_text') or '')[:200]}\"")
    if lost:
        p(f"\n### Lost ({len(lost)})\n")
        for i in lost:
            p(f"- {i} {new[i]['q']}  (old final rank {old[i]['hitfinal']}; new top: \"{new[i]['top3'][0][:110]}\")")
    if a.md:
        open(a.md, "w", encoding="utf-8").write("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
