# What narrative retrieval is missing: JPMorgan weak questions, BM25 + reranker only

## Method

Only the 7 weak questions were analysed (Q1, Q2, Q3, Q5, Q6, Q7, Q9).

1. **Ideal set.** I searched all 3,317 indexed chunks and the raw filing text myself for every passage that answers
   (part of) each question.
2. **Trace.** Each ideal chunk was traced through BM25 (its rank over all chunks) → BM25 top-50 → cross-encoder
   reranker → top 10.
3. **Denominator.** The answers that are not in any chunk (tables, dropped sentences) are listed separately, so the
   recall figure has a reference.
4. **Caveat.** The ideal set is hand-made from keyword searches, so it is a lower bound: there may be a few more
   relevant chunks.

Raw trace: `eval/jpm/retrieval_oracle_trace.txt`.

## Recall against the ideal set

| Q | Ideal chunks | In reranked top 10 | Missed by BM25 (not in top 50) | In top 50 but reranked out | Answer only in a table or a dropped sentence |
|---|---|---|---|---|---|
| 1 Revenue / NI / ROE | 3 | 2 | 1 | 0 | 3-year revenue / NI / ROE table; 2022 NI ($37.7B) is in no prose at all |
| 2 NII / NIM | 7 | 2 | 3 | 2 | NIM history (2.70 / 2.00 / 1.64%) is in a table |
| 3 ACL / provision vs loans | 5 | 3 | 2 | 0 | ACL and loans by portfolio: table |
| 5 Loans / deposits / LDR | 5 | 1 | 4 | 0 | Period-end loans $1.32T, deposits $2.40T, LDR 55%: tables only |
| 6 Segment revenue | 3 (+3 dropped) | 2 (descriptions only) | 1 | 0 | CCB $70.1B, CIB $48.8B, CB $15.5B sentences exist in the filing but were never indexed |
| 7 Expense / overhead / comp | 9 | 4 | 4 | 1 | Compensation $46.5B and overhead 55% / 59%: tables only |
| 9 Returns / shares / EPS | 7 | 2 | 5 | 0 | Buyback $9.8B, dividends, share count: tables only |
| **Total** | **39** | **16 (41%)** | **20** | **3** | |

**Where the losses happen.** Of the 23 ideal chunks missed:
- 20 never entered BM25's top 50, so the reranker never saw them.
- Only 3 were demoted by the reranker.

The reranker is not the bottleneck: candidate recall is.

## What is missing, by cause (biggest first)

1. **Tables are not retrievable text.**
   - Most hard numbers live only in tables. That covers the three-year history, period-end loans and deposits,
     LDR, NIM history, segment revenue, compensation, the overhead ratio, buybacks and dividends.
   - Tables are not chunked. They reach the model only as structured facts, and only when the concept mapping
     works, which for bank concepts it mostly doesn't.
   - What the retriever can find is the caption ("The table below shows the loan and deposit balances…",
     T01897, BM25 #1), and that carries no numbers.
   - This alone explains Q5 and Q9, and most of Q6.
2. **Short paragraphs are dropped at build time.**
   - `graph_builder.py:493` indexes only paragraphs longer than 40 characters, and doesn't extract numbers from
     shorter ones either.
   - JPMorgan's segment results are one-liners: "Net revenue was $70.1 billion, up 28%." (38 characters). So CCB, CIB
     and CB revenue never entered the index.
3. **Vocabulary mismatch: BM25 has no synonyms, abbreviations or stemming across words.**
   - Q2: the question says "net interest margin", the filing says "net yield" (T01069 "net yield … 2.70%,
     an increase of 70 bps" is BM25 #79).
   - Q9: "buybacks" vs "repurchase(s)" (all repurchase paragraphs are BM25 #83–138).
   - Q1: "return on equity" vs "ROE" (T00958 "net income of $49.6 billion … ROE of 17%" is BM25 #139).
   - Q5: "total loans / total deposits" vs "Firmwide average loans of $1.2 trillion" (#780) and "average
     deposits" (#386, #489).
   - Note: the hybrid (dense) top 10 did not recover T01069 or the repurchase paragraphs either. This gap needs
     query expansion with finance synonyms, not just embeddings.
4. **Chunks lose their context when split.**
   - Bullet lists become separate chunks, and the heading isn't attached to them.
   - "Compensation expense increased driven by:" (T01088) is retrieved, but its content bullet "• an increase in
     employees, primarily in technology and front office, as well as wage inflation" (T01089) doesn't contain the
     word "compensation" and ranks #2,862.
   - Segment sentences ("Net revenue was $19.8 billion…", T01455 = AWM) don't name the segment, because the name
     is in the section heading. So a question naming the segment can't match it (#438).
5. **The final stage throws away short hits.**
   - `retrieval.py` gives a search hit no score if its text is 80 characters or less.
   - Correctly retrieved, dense answers are lost that way: T00959 "Total net revenue was $158.1 billion, up 23%"
     (59 characters, reranked #3 for Q1), T00972 average deposits $2.4T, T04668 overhead-ratio definition,
     T01088 / T01092 expense headings.
   - Combined with the graph-link bonus from wrongly mapped concepts (see RETRIEVAL_EVAL.md), these are why the
     final set is worse than the reranker's own top 10.
6. **The reranker itself (minor).** It demoted three useful candidates, all short headings or definitions:
   T01198 (#22), T04655 (#39), T01093 (#40, the FDIC $2.9B special-assessment bullet).

## What would recover the most (proposals, not applied)

| Fix | Recovers | Layer / rebuild? |
|---|---|---|
| Index tables as text chunks (caption + header + rows, linearised) next to the facts | Q5, Q6, Q9 and the 3-year histories in Q1, Q2, Q7, i.e. most of the missing numbers | DATA, rebuild |
| Prepend the nearest heading / parent sentence to each chunk (bullets, segment sections) | Q6 segment sentences, Q7 compensation bullets | DATA, rebuild |
| Lower the 40-character build threshold (e.g. index sentences with a number) | CCB / CIB / CB revenue lines | DATA, rebuild |
| Drop or lower the 80-character final filter | Q1 revenue, Q5 deposits, Q7 headings / overhead definition | RETRIEVAL, no rebuild |
| Finance synonym expansion for the BM25 query (NIM ↔ net yield, buyback ↔ repurchase, ROE ↔ return on equity, total loans ↔ loans retained / average loans) | Q1, Q2, Q5, Q9 | RETRIEVAL, no rebuild |
| Make the reranker order authoritative in the final stage | Q1, Q3, Q7 (see RETRIEVAL_EVAL.md) | RETRIEVAL, no rebuild |
