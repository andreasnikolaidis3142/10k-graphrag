"""Markdown rows for hand-picked before/after examples.  python eval/retrieval_bench/showcase.py old final"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PICK = [  # (question id, mechanism that fixed it)
    ("jpm-060", "short sentence now indexed + heading context (CONSUMER & COMMUNITY BANKING)"),
    ("jpm-061", "short sentence now indexed + heading context"),
    ("jpm-053", "finance vocabulary: net interest margin -> net yield"),
    ("jpm-059", "table-row card (loans-to-deposits table)"),
    ("jpm-030", "table-row card (Note 17 deposits)"),
    ("jpm-019", "table-row card + jargon gloss (compensation expense)"),
    ("jpm-020", "table-row card + vocabulary (set aside -> provision for credit losses)"),
    ("jpm-049", "table-row card with multi-level segment header expanded"),
    ("jpm-070", "short definition no longer filtered out + vocabulary (efficiency -> overhead)"),
    ("jpm-026", "stopwords + subject field boost (card was BM25 rank 743)"),
    ("jpm-039", "cash-flow statement row card"),
    ("aapl-060", "segment table-row card"),
    ("aapl-006", "XBRL series card + '&' / R&D vocabulary"),
    ("aapl-075", "heading context (European Commission State Aid Decision)"),
    ("wmt-061", "segment table-row card under its segment heading"),
    ("xom-002", "jargon gloss (top line) + company-total XBRL card"),
    ("xom-012", "jargon gloss (bottom line) + table-row card"),
    ("pfe-059", "segment table-row card + scope prior (product slices demoted)"),
    ("pfe-063", "vocabulary + heading context (PRICING AND REIMBURSEMENT)"),
    ("pfe-003", "XBRL series card (cost of goods sold)"),
]
old, new = (dict((r["id"], r) for r in map(json.loads, open(os.path.join(HERE, f"results_{t}.jsonl"), encoding="utf-8")))
            for t in sys.argv[1:3])
clean = lambda s: (s or "").replace("|", "/").replace("\n", " ")
print("| # | Question (split) | Before: top hit | Now: answering source (rank in final set) | What fixed it |")
print("|---|---|---|---|---|")
for k, (i, why) in enumerate(PICK, 1):
    o, n = old[i], new[i]
    before = clean(o["top3"][0][:120]) if o["top3"] else "-"
    print(f"| {k} | {i}: {clean(n['q'])} ({n['split']}) | {before} | {clean((n.get('hit10_text') or '')[:170])} ({n['hitfinal']}) | {why} |")
