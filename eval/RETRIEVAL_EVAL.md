# Narrative retrieval rating: JPMorgan FY2023 (held-out set)

No LLM calls and nothing re-run end to end. The existing graph `eval/jpm.json` was loaded and each stage was dumped
per question:
- Raw dumps: `eval/jpm/retrieval_dump.txt` (reranker top-10, hybrid final set, BM25 final set) and
  `eval/jpm/retrieval_bm25_rerank.txt` (BM25 top-50 -> same reranker).
- Setup: BGE-large embedder, hybrid = BM25 + dense fused with RRF over 50 candidates, then a cross-encoder reranker.

Scope: these are the narrative paragraphs only. The XBRL/table numbers reach the model through a separate path and
are not rated here.

**Per-passage relevance:**
- 2 = contains the answer or a key fact.
- 1 = on topic but partial (definition, methodology, a segment-level sub-figure, a heading).
- 0 = off topic.

**Grade (0–10):** my judgement of how well the set lets a model answer the question; mainly key-fact recall, then noise.

"Final" means what the model actually received: the top 4, or 8 when the plan came from the semantic mapper.

## Results per question

| Q | Topic | Reranker top-10: rel sum / 20, P@10 | Grade | Hybrid final (as used) | Grade | BM25 final | Grade |
|---|---|---|---|---|---|---|---|
| 1 | Revenue, NI, ROE | 5, 0.3 | 5 | 3 / 8 | 3 | 2 / 8 | 2 |
| 2 | NII and NIM | 8, 0.6 | 6 | 3 / 8 | 5 | 4 / 8 | 5 |
| 3 | ACL and provision vs loans | 9, 0.6 | 8 | 7 / 16 (8 slots) | 6 | 4 / 16 | 4 |
| 4 | Capital ratios | 12, 0.9 | 8 | 11 / 16 (8 slots) | 8 | 9 / 16 | 7 |
| 5 | Loans, deposits, LDR | 1, 0.1 | 2 | 1 / 16 (8 slots) | 1 | 1 / 16 | 1 |
| 6 | Segment revenue | 5, 0.5 | 2 | 3 / 8 | 2 | 4 / 8 | 3 |
| 7 | Expense, overhead, comp | 8, 0.7 | 6 | 5 / 16 (8 slots) | 5 | 2 / 16 | 2 |
| 8 | Credit, market, liquidity risk | 12, 0.8 | 9 | 6 / 8 | 7 | 5 / 8 | 6 |
| 9 | Returns, share count, EPS | 3, 0.3 | 2 | 1 / 8 | 1 | 1 / 8 | 1 |
| 10 | Guidance / market-share trap | 5, 0.3 | 9 | 5 / 8 | 9 | 0 / 8 | 0 |
| | **Average grade** | P@10 0.51 | **5.7** | | **4.7** | | **3.1** |

For comparison, simply taking the reranker's own top 4 (top 8 where 8 slots apply) instead of the final fused set
grades **4.9**.

## Short notes per question

- **Q1.** The reranker found net revenue (T00959, R4) and ROE (T04463, R3) but not the NI/ROE headline paragraph
  (T00958). The final stage then dropped T00959 for footnotes that have graph links to `Revenues`.
  BM25 final: only the ROE footnote.
- **Q2.** NII headline (T00960) and drivers (T01068) are in the top 10. The final kept T00960 but swapped T01068
  for an off-topic hedge footnote. The plan mapped "net interest margin" to industrial margin concepts (gross /
  operating / EBITDA), whose graph links pull in junk. No prose paragraph states NIM; it lives in a table.
- **Q3.** The top 10 includes the key allowance paragraph (T00968: ACL $24.8B, coverage 1.75% vs 1.81%). The final
  set lost it: the semantic mapper guessed `ShortTermBorrowings` and `AOCI`, and their links added 3 junk
  paragraphs in its place. BM25 also missed it.
- **Q4.** Strong at every stage: CET1 15.0%, requirement 11.4%, buffer breakdown. The other ratio values live only
  in tables. BM25 missed the 11.4% sentence.
- **Q5.** Nothing to retrieve: loans, deposits and the ratio are only in a table. Every method surfaces the table's
  caption (T01897) and noise.
- **Q6.** Only organisational descriptions, three near-duplicates. Each segment's "Net revenue was $X billion"
  MD&A sentence exists (e.g. AWM T01455) but was never ranked, because the question names the segments but not
  "net revenue".
- **Q7.** Top 10: firm-wide expense (T00962), segment expenses, overhead definition, compensation heading. Final:
  4 of 8 slots taken by link-junk (`ShareBasedCompensation` / `Depreciation` from the semantic mapper). BM25 final
  lost the firm-wide $87.2B sentence.
- **Q8.** The best top 10: credit, market and liquidity risk factors all present. With only 4 final slots, the market
  and credit risk-factor bullets (T00142, T00143) were cut. The plan mapped "liquidity" to an industrial theme
  (current ratio...), so this question didn't get the 8-slot text rule.
- **Q9.** Weak everywhere: company intros, preferred-stock boilerplate. Buyback and dividend amounts are in
  capital-actions tables, not in a retrieved sentence.
- **Q10.** Hybrid is exactly right: both guidance sentences (T01008 ~$90B, T01009 ~$88B ex-Markets) plus the NI
  context. **BM25 final retrieved neither guidance sentence (0/8).** That is the single largest
  hybrid-vs-BM25 gap, on the honesty-critical question.

## BM25 top-50 -> same reranker (no dense model)

- Overlap with hybrid -> reranker top 10: 8, 9, 8, 9, 7, 6, 10, 7, 7, 7 (**average 7.8 / 10**).
- Every key paragraph found by hybrid is also found by BM25 + rerank, at similar ranks:
  - T00959 (revenue) B3;
  - T00968 (ACL coverage) B10;
  - T00962 (expense) B1;
  - T00142 / T00143 (market / credit risks) B5 / B7;
  - T01637 (11.4%) B8;
  - T01008 / T01009 (guidance) B2 / B4.
- The paragraphs that differ are mostly low value on both sides. One exception favours BM25 + rerank: in Q10 it adds
  the actual-NII sentence T00960, which would have prevented the model's "$18.73B" error.
- My grade for the BM25 + rerank top 10: about **5.8**, i.e. the same as hybrid (5.7).

## Opinion: is hybrid worth it?

- **The reranker is worth it. The dense half of "hybrid" barely is, on this filing.**
  - Pure BM25 final sets grade 3.1 vs 4.7 for the hybrid-reranked pipeline. Most of that gain comes from the
    cross-encoder. Feeding the reranker BM25's 50 candidates gives practically the same top 10 (7.8 / 10 overlap,
    every key paragraph kept).
  - 10-K prose is jargon-dense and repeats the question's own terms ("provision for credit losses", "net interest
    income"), which suits lexical recall. The reranker then fixes BM25's ordering.
  - Cost of the dense half: a 1.3 GB BGE-large model, an index build per filing, and about a minute of model load
    per CLI call on CPU. Cheap to drop, for roughly no measured loss here.
  - Caveat: 10 questions, one filing. Dense recall should matter more for paraphrased questions ("how dependent
    on China" vs "Greater China"). I'd keep it switchable and measure on the Apple and Walmart sets before
    removing it.
- **The biggest retrieval problem isn't BM25 vs dense; it's the final fusion step.** It *lowers* quality (5.7 top-10 →
  4.7 final; even the plain reranker top 4 / 8 grades 4.9). The +1 graph-link bonus is applied to whatever concepts
  the plan guessed, and on a bank those guesses are wrong (industrial margin themes, semantic-mapper guesses like
  `ShortTermBorrowings`, `AOCI`, `AdditionalPaidInCapital`). That pushes key paragraphs out:
  - T00959 in Q1;
  - T00968 in Q3;
  - T01068 in Q2;
  - the overhead definition in Q7.
- Suggested next steps (not applied):
  1. Make the reranker order authoritative; use graph links only as a tie-breaker or for keyword-matched concepts,
     never for semantic-mapper guesses.
  2. For multi-part questions, give 6–8 slots based on the number of asked topics, not only when no metric is named.
  3. Questions whose answers live in tables (Q5, Q6, Q9) can't be fixed by paragraph retrieval. They need
     bank-concept coverage on the structured side (deposits, loans, segment net revenue, capital actions).
