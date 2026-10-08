# Retrieval-optimised build: what changed and what it bought

**Scope:** retrieval only (BM25 + cross-encoder), no LLM calls. 5 companies, 373 questions. Answer keys come from an independent iXBRL parse of each filing (not from this system), so the benchmark can't inherit the system's own parsing bugs. Every 5th question was held out and never inspected while tuning.

## Result

| | answer in reranked top 10 | in the final evidence set the LLM gets | anywhere in the full context |
| --- | --- | --- | --- |
| **Before** (old index, same BM25 + reranker, old 4-slot final stage) | 34% | 30% | 72% |
| After, with the 6/8-slot final stage (*removed*) | 96% | 94% | 96% |
| **Now: LLM gets the retriever top 10** | **96%** | **96%** | **98%** |
| held-out only (73 q) | 40% -> **97%** | 34% -> **95%** | 73% -> **97%** |
| numeric (265) / segment (23) / text (85) | 21->95% / 13->100% / 81->98% | 17->93% / 13->100% / 73->98% | |

Per company (final set, old -> 6/8-slot stage -> top 10 now): Apple 13% -> 95% -> 98%, Walmart 42% -> 97% -> 100%, JPMorgan 19% -> 93% -> 93%, ExxonMobil 42% -> 94% -> 95%, Pfizer 35% -> 92% -> 95%.

Transitions: **243 questions fixed, 2 lost** with the 6/8-slot stage; **248 fixed, 0 lost** after removing it (top 10). The documents that now answer them: 164 table-row cards, 52 XBRL series cards, 27 paragraphs.

## Problems grouped, and the mechanism built for each

| Problem class (seen across companies) | Mechanism | Where |
| --- | --- | --- |
| Numbers live in tables, which were not searchable | **Table-row cards.** Every table row becomes a sentence: context path + title + scale + row label + every column (multi-level headers expanded, footnote markers removed), values verbalised (`,148 ($70.1 billion)`) plus the YoY change | `cards.table_cards` |
| Numbers with no taxonomy entry or table caption (bank concepts, multi-axis segment facts) | **XBRL series cards.** Every element and dimension series, named in words (`Financing Receivable Allowance For Credit Loss...`), marked company total or slice | `cards.xbrl_cards` |
| Paragraphs lose the heading that says what they are about | **Heading context**, from ALL-CAPS/Item/Note headings, one-cell layout-table headings and bullet lead-ins, prepended to each paragraph | `cards.HeadingContext` |
| One-line results (`Net revenue was $70.1 billion, up 28%.`) were dropped at build | Short numeric paragraphs indexed; prose inside one-cell layout tables indexed | `graph_builder.build_graph` |
| Analyst vs filing vocabulary (NIM/net yield, buybacks/repurchases, ROE, top/bottom line, capex) | Finance vocabulary added to the BM25 query; plain-English gloss of jargon for the reranker; light stemming | `cards.expand_query`, `cards.gloss_query`, `BM25._stem` |
| Long paragraphs out-scored short, exact number cards (`Company total: Liabilities` was BM25 rank 743) | Stop/question words removed; a card's subject is repeated in its index text, and long digit strings are dropped from it | `BM25.STOP`, `retrieval.index_text` |
| Company-wide questions answered with a segment/product slice | **Scope prior:** slices are demoted unless the question names a segment, product or region of that filing | `cards.member_words/card_scope`, `Retriever.search` |
| The final stage re-ordered good hits and dropped short ones | ~~Reranker order is final; no length filter; graph links only fill empty slots; 6 slots (8 for text questions)~~ **Removed (see "Final selection stage removed" below):** the LLM now gets the retriever top 10 as ranked (`TENK_NARRATIVE_K`, default 10) | `Retriever.retrieve` |

Default mode is now `bm25_rerank` (CLI and API; `auto` maps to it). No embedding model is loaded, and `build` only makes a dense index with `--dense`.

## 20 questions that were failures and are answered now

| # | Question (split) | Before: top hit | Now: answering source (rank in final set) | What fixed it |
| --- | --- | --- | --- | --- |
| 1 | jpm-060: How did Consumer & Community Banking net revenue change? (holdout) | Net revenue was $8.0 billion, compared with $80 million in the prior year, predominantly driven by higher net interest i | [CONSUMER & COMMUNITY BANKING > 2023 compared with 2022] Net revenue was $70.1 billion, up 28%. (1) | short sentence now indexed + heading context (CONSUMER & COMMUNITY BANKING) |
| 2 | jpm-061: How did Corporate & Investment Bank net revenue change? (dev) | Net revenue was $19.8 billion, up 12%. Net interest income was $6.3 billion, up 20%. Noninterest revenue was $13.6 billi | [CORPORATE & INVESTMENT BANK > 2023 compared with 2022] Net revenue was $48.8 billion, up 1%. (2) | short sentence now indexed + heading context |
| 3 | jpm-053: What was the net interest margin (net yield) and how did it change? (dev) | Changes in net interest income, volume and rate analysis | [CONSOLIDATED RESULTS OF OPERATIONS > partially offset by] The Firm’s average interest-earning assets were $3.3 trillion, down $23 billion, and the yield was 5.14%, up 23 (5) | finance vocabulary: net interest margin -> net yield |
| 4 | jpm-059: What is the loans-to-deposits ratio? (dev) | All banking institutions are currently required to have a minimum CET1 capital ratio of 4.5% of risk-weighted assets. | NSFR > Management’s discussion and analysis / As of December 31, (in billions except ratios) / in billions // Loans-to-deposits ratio: 2023: 55%; 2022: 49% (1) | table-row card (loans-to-deposits table) |
| 5 | jpm-030: How much in customer deposits did the company hold at the end of 2023? (holdout) | (d) Excludes $ 2.8 billion and $ 2.5 billion of accrued interest receivable at December 31, 2023 and 2022, respectively, | Note 17 – Deposits / As of December 31, 2023 and 2022, noninterest-bearing and interest-bearing deposits were as follows. / U.S. offices / in millions // Non-U.S. offices (2) | table-row card (Note 17 deposits) |
| 6 | jpm-019: How much did employee compensation cost in 2023? (dev) | At December 31, 2023, approximately $ 1.0 billion (pretax) of compensation expense related to unvested awards had not ye | CONSOLIDATED RESULTS OF OPERATIONS > 2023 compared with 2022 / Noninterest expense Year ended December 31, / in millions // Compensation expense: 2023: $46,465 ($46.5 bil (1) | table-row card + jargon gloss (compensation expense) |
| 7 | jpm-020: How much was set aside for expected credit losses in 2023? (holdout) | The allowance for credit losses as of December 31, 2023 was $24.8 billion, reflecting a net addition of $3.1 billion fro | CONSOLIDATED RESULTS OF OPERATIONS > partially offset by / Provision for credit losses Year ended December 31, / in millions // Total provision for credit losses: 2023: $ (1) | table-row card + vocabulary (set aside -> provision for credit losses) |
| 8 | jpm-049: How much revenue did the Asset and Wealth Management segment report in 2023? (dev) | Revenue from Asset Management was $9.1 billion, up 4%, driven by: | BUSINESS SEGMENT RESULTS > Segment Results – Managed Basis / in millions // Total net revenue: Asset & Wealth Management 2023: $19,827 ($19.8 billion); Asset & Wealth Man (1) | table-row card with multi-level segment header expanded |
| 9 | jpm-070: What is the overhead (efficiency) ratio? (holdout) | Overhead ratio: Noninterest expense as a percentage of total net revenue. | [Note 34 – Business combinations > OPEB: Other postretirement employee benefit] Overhead ratio: Noninterest expense as a percentage of total net revenue. (1) | short definition no longer filtered out + vocabulary (efficiency -> overhead) |
| 10 | jpm-026: What were total liabilities at the end of 2023? (dev) | (e) Total assets for the U.K. were approximately $ 352 billion, $ 357 billion and $ 365 billion at December 31, 2023, 20 | FORWARD-LOOKING STATEMENTS > Consolidated balance sheets / Assets / in millions // Liabilities — Total liabilities (a): 2023: 3,547,515 ($3.5 trillion); 2022: 3,373,411 ( (2) | stopwords + subject field boost (card was BM25 rank 743) |
| 11 | jpm-039: How much was paid out in dividends in 2023? (dev) | Investments classified in level 3 of the fair value hierarchy increased in 2023 to $ 3.1 billion, due to $ 400 million i | FORWARD-LOOKING STATEMENTS > Consolidated statements of cash flows / Operating activities / in millions // Net change in — Dividends paid: 2023: ( 13,463 ) (-$13.5 billio (1) | cash-flow statement row card |
| 12 | aapl-060: How much revenue did the Greater China segment report in 2023? (holdout) | As of September 30, 2023 and September 24, 2022, the Company had total deferred revenue of $ 12.1 billion and $ 12.4 bil | Note 13 – Segment Information and Geographic Data / Americas: / in millions // Greater China — Net sales: 2023: $72,559 ($72.6 billion); 2022: $74,200 ($74.2 billion); 20 (1) | segment table-row card |
| 13 | aapl-006: What was R&D spending in 2022? (dev) | The Company issues unsecured short-term promissory notes pursuant to a commercial paper program. The Company uses net pr | Company total: Research and Development Expense (us-gaap:ResearchAndDevelopmentExpense): FY2023: 29,915,000,000 dollars ($29.9 billion); FY2022: 26,251,000,000 dollars ($ (1) | XBRL series card + '&' / R&D vocabulary |
| 14 | aapl-075: What is the European Commission tax case about? (holdout) | The Company is subject to changes in tax rates, the adoption of new U.S. or international tax legislation and exposure t | [Note 7 – Income Taxes > European Commission State Aid Decision] On an annual basis, the Company may request approval from the Irish Minister for Finance to reduce the re (1) | heading context (European Commission State Aid Decision) |
| 15 | wmt-061: How much operating income did the Walmart US segment report in 2024? (dev) | In fiscal 2024, our Walmart U.S. and Sam's Club operating segments generated approximately 82% of our consolidated net s | PART II > Walmart U.S. Segment / Fiscal Years Ended January 31, / Amounts in millions // Operating income: 2024: $22,154 ($22.2 billion); 2023: $20,620 ($20.6 billion); 2 (1) | segment table-row card under its segment heading |
| 16 | xom-002: What was the top line in fiscal 2022? (dev) | Cash provided by operating activities totaled $76.8 billion in 2022, $28.7 billion higher than 2021. The major source of | Company total: Revenues (us-gaap:Revenues): FY2023: 344,582,000,000 dollars ($344.6 billion); FY2022: 413,680,000,000 dollars ($413.7 billion); FY2021: 285,640,000,000 do (1) | jargon gloss (top line) + company-total XBRL card |
| 17 | xom-012: What was the bottom line in 2022? (dev) | Cash provided by operating activities totaled $76.8 billion in 2022, $28.7 billion higher than 2021. The major source of | FINANCIAL INFORMATION / except where // Net income (loss) attributable to ExxonMobil: 2023: 36,010; 2022: 55,740; 2021: 23,040; 2023 vs 2022: -35.4% (1) | jargon gloss (bottom line) + table-row card |
| 18 | pfe-059: How much revenue did the Biopharma segment report in 2023? (dev) | (a) Primarily represents cost-reduction initiatives. Amounts associated with our Biopharma segment: $ 672 million for 20 | Note 17. Segment, Geographic and Other Revenue Information > Selected Income Statement Information / The following table provides selected income statement information by (3) | segment table-row card + scope prior (product slices demoted) |
| 19 | pfe-063: How could Medicare drug price negotiation affect revenues? (dev) | Payors may promote generic drugs and biosimilars more aggressively to generate savings and attempt to stimulate addition | [PRICING AND REIMBURSEMENT] In the U.S., pharmaceutical product pricing is subject to government and public scrutiny and calls for reform, and many of our products are su (1) | vocabulary + heading context (PRICING AND REIMBURSEMENT) |
| 20 | pfe-003: How much did it cost to produce the goods and services sold in 2023? (dev) | As of December 31, 2023, we had commitments totaling $ 5.2 billion that are legally binding and enforceable. These commi | Company total: Cost of Goods and Services Sold (us-gaap:CostOfGoodsAndServicesSold): FY2023: 24,954,000,000 dollars ($25.0 billion); FY2022: 34,344,000,000 dollars ($34.3 (1) | XBRL series card (cost of goods sold) |

## What is still missed (21 of 373 with the 6/8-slot stage; 14 now, with the top 10)

- **Near-identical debt lines (8):** long-term debt vs total term debt vs debt issued or repaid. The right row was usually rank 7-9, just below the old 6-slot cut. **The cut has since been removed** (the LLM now gets the full top 10), so these now reach the model.
- **Lease note tables (3):** liabilities vs undiscounted payments vs right-of-use assets.
- **Bank balance sheet totals (2):** JPMorgan's consolidated loans and allowance rows are buried among loan-portfolio note tables.
- **Key strictness (4):** for example, buybacks keyed to cash paid ($9,824M) while the retrieved table gives the purchase price including excise tax ($9,898M); the CET1 15.0% sentence keyed as a phrase while a table row with 15.0% was found.
- **Other (4):** Pfizer inventory, intangibles and AOCI rows; Pfizer loss-of-exclusivity (one sentence in the whole filing).

**Lost vs old (2, both Pfizer):** total assets (rank 10) and debt raised (rank 8), both just outside the 6-slot cut. **Both recovered once the cut was removed.**

## Final selection stage removed

The 6/8-slot final stage was removed: it re-cut the reranker's list and dropped right answers sitting at ranks 7-10. The evidence handed to the LLM is now the BM25 + reranker top 10, unchanged (`Retriever.retrieve`, `NARRATIVE_K`, env `TENK_NARRATIVE_K`, default 10). Measured on the same 373 questions: final set 94% -> 96%, **7 fixed, 0 lost**, namely Apple lease liabilities (rank 8) and debt raised (7), Walmart bottom line (9) and long-term borrowing (8), ExxonMobil debt raised (8), Pfizer total assets (10) and debt raised (8). Cost: up to 4 more documents in the prompt (each truncated at 900 characters).

## Honest notes

- **Question count.** The generator caps at 100 per company but only emits questions whose answer element exists in the filing, so the set is 65-82 per company (373 total), not 500.
- **Holdout.** Holdout questions share template families with dev questions (e.g. "What was R&D in 2023/2022?"), so they test generalisation across years and companies more than across phrasings. The 85 hand-written text questions are all distinct.
- **One key widened.** Walmart's FX question also accepts "fluctuations in currency exchange rates" (the answering paragraph uses that word order). The baseline was scored with the narrower key.
- **Speed.** The cross-encoder costs about 15-20 s per question on this CPU (50 candidates). `TENK_TOP_K_CANDIDATES` (default 50) and `TENK_RERANK_MAXLEN` (default 384) trade quality for speed. The benchmark caches scores in `eval/retrieval_bench/.rerank_cache.sqlite`.
- **ExxonMobil.** The SEC ticker map now points XOM at a new holding company with no FY2023 10-K, so it was fetched by CIK 34088.
- **Tests:** 162 passed, 0 failed. `test_retrieval`'s old auto->hybrid test and the 4-slot (later 6/8-slot) rule in `test_narrative_ranking` were updated (now: the narrative evidence equals the search top 10, in order) to the requested defaults; 12 new tests (tests/test_cards.py) cover cards, context, vocabulary, scope and the final stage.

Reproduce: `python eval/retrieval_bench/run_bench.py --tag mine` then `python eval/retrieval_bench/compare.py old mine`.

---

## Before vs after, one example per problem

**"Cards" are not charts or a separate graph.** A card is a short text document, one sentence-like line per table row or per XBRL series. Cards are stored as extra nodes (type `Card`) in the same graph file as the paragraphs, and the search engine indexes them next to the paragraphs. Examples below are from Apple's FY2023 10-K unless marked JPMorgan.

### 1. Numbers locked in tables -> table-row cards

**Before.** The table existed only as parsed numbers. The search index held 0 documents containing `29,915`. Raw rows as the loader sees them:

```text
['2023', 'Change', '2022', 'Change', '2021']
['Research and development', '$29,915', '14%', '$26,251', '20%', '$21,914']
['Selling, general and administrative', '$24,932', '(1)%', '$25,094', '14%', '$21,973']
```

**After.** Each row becomes one searchable card (`R00338_000`): where it sits, title, scale, row label, every column with its period, and values spelled out:

```text
Item 6. [Reserved] > Operating Expenses | Operating expenses for 2023, 2022 and 2021 were as follows (dollars in millions)
| dollars in millions || Research and development: 2023: $29,915 ($29.9 billion); Change: 14%; 2022: $26,251 ($26.3 billion);
Change: 20%; 2021: $21,914 ($21.9 billion)
```

### 2. XBRL numbers with no searchable text -> XBRL series cards

**Before.** Only a structured fact, reachable just when the question's wording mapped to that exact concept:

```text
F00028  ResearchAndDevelopmentExpense  FY2023  29915000000.0  ix:us-gaap:ResearchAndDevelopmentExpense
```

**After** (`X00353`). The element name is written in words, all periods are given, the change is computed, it says where the number is shown, and it is marked as the company total:

```text
Company total: Research and Development Expense (us-gaap:ResearchAndDevelopmentExpense): FY2023: 29,915,000,000 dollars
($29.9 billion); FY2022: 26,251,000,000 dollars ($26.3 billion); FY2021: 21,914,000,000 dollars ($21.9 billion);
change FY2022 -> FY2023: +14.0% | shown in: CONSOLIDATED STATEMENTS OF OPERATIONS: Research and development; ...
```

### 3. Paragraphs without their heading -> heading context

**Before** (`T00347`): `The Company's effective tax rate for 2023 and 2022 was lower than the statutory federal income tax rate due primarily to ...`

**After** (same paragraph): `[Item 6. [Reserved] > Provision for Income Taxes] The Company's effective tax rate for 2023 and 2022 was lower than ...`

### 4. One-line results dropped at build time (JPMorgan)

**Before.** No document at all: paragraphs of 40 characters or less were skipped.

**After** (`T01280`): `[CONSUMER & COMMUNITY BANKING > 2023 compared with 2022] Net revenue was $70.1 billion, up 28%.`

The heading also supplies the segment name, which the sentence itself never says.

### 5. Analyst wording vs filing wording -> vocabulary and gloss

Question: `What was capex in 2022?`

| | Before | After |
| --- | --- | --- |
| Search terms (BM25) | `what was capex in 2022` | `capex 2022 capital expenditur purchas payment property plant equipment` |
| What the reranker reads | `What was capex in 2022?` | `What was capex in 2022? (capital expenditures, payments for property, plant and equipment)` |

The filing never says "capex". It says "Payments for acquisition of property, plant and equipment".

### 6. Long paragraphs out-scoring short exact cards -> stopwords and subject boost (JPMorgan)

Question: `What were total liabilities at the end of 2023?`

| | Before | After |
| --- | --- | --- |
| Search terms | `what were total liabilities at the end of 2023` | `total liability 2023` |
| How the card is indexed | as displayed: `Company total: Liabilities (us-gaap:Liabilities): @2023-12-31: 3,547,515,000,000 dollars ($3.5 trillion) ...` | subject twice, long digit strings removed: `Liabilities Liabilities Company total: Liabilities (us-gaap:Liabilities): ... dollars ($ trillion) ...` |
| BM25 rank of that card | 743 (the reranker never saw it) | 27, and the balance-sheet "Total liabilities" row now ranks 2nd in the final set |

### 7. Segment slice answering a company-wide question -> scope prior

Table-row and XBRL cards are tagged with a scope, using that filing's own segment, product and region names:

```text
scope=slice | Note 13 - Segment Information and Geographic Data | Americas: | in millions || Operating income: 2023: $60,508 ($60.5 billion) ...
scope=(neutral) | Note 13 - Segment Information and Geographic Data | in millions || Total operating income: 2023: $114,301 ($114.3 billion) ...
```

**Before.** "What was operating profit in 2023?" could be answered with the Americas row; at ExxonMobil, "net PP&E" came back as the "Upstream equipment" slice.

**After.** When the question names no segment, product or region, slices are pushed down by a fixed amount. "How much operating income did the Americas segment report?" is unaffected.

### 8. The final step overruled the reranker -> reranker order is final -> step removed (JPMorgan)

**Before.** The reranker ranked `Total net revenue was $158.1 billion, up 23%, reflecting:` 4th for the revenue question. The final step then dropped it, because hits of 80 characters or less got no score (this one is 59), and filled the 4 slots with footnotes linked to a guessed concept.

**After (first version).** The final evidence was the reranker's top 6 (8 for pure text questions), with no length filter.

**Now (removed).** The 6/8 cut is gone. The LLM gets the retriever top 10 exactly as BM25 + reranker ranked them. Graph links only fill slots when the search returns fewer than 10 documents, which happens only on tiny test filings.

---

## Retrieval index statistics

Words per document, Apple FY2023 10-K. Paragraph text includes its heading path; cards as stored.

| Document type | Count | Mean words | Median | Std dev | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| Paragraphs, **before** | 386 | 60.3 | 45.0 | 53.9 | 5 | 305 |
| Paragraphs, after | 396 | 67.8 | 51.5 | 53.7 | 1 | 315 |
| Table-row cards (new) | 437 | 35.4 | 36.0 | 12.4 | 14 | 76 |
| XBRL series cards (new) | 414 | 33.0 | 33.0 | 10.6 | 10 | 63 |
| **All documents, after** | **1,247** | **44.9** | **37.0** | **35.4** | **1** | **315** |

Paragraphs grew by about 7 words on average (the heading path) and by 10 in number (short numeric sentences and one-cell layout-table prose). The 1-word minimum is a short numeric line, such as a lone date.

Searchable documents per 10-K, all five filings:

| Filing | Paragraphs | Table-row cards | XBRL cards | Total |
| --- | --- | --- | --- | --- |
| Apple FY2023 | 396 | 437 | 414 | 1,247 |
| Walmart FY2024 | 621 | 528 | 499 | 1,648 |
| JPMorgan FY2023 | 3,339 | 2,881 | 3,609 | 9,829 |
| ExxonMobil FY2023 | 688 | 1,489 | 943 | 3,120 |
| Pfizer FY2023 | 1,214 | 875 | 1,441 | 3,530 |
| **Average 10-K** | **1,252** | **1,242** | **1,381** | **3,875** |

The old index held only the paragraphs column, which is about a third of today's documents. The cards are short and uniform (about 33-35 words, low spread); paragraphs are longer and much more variable.
