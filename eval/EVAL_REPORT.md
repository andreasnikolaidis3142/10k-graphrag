# tenk_graphrag evaluation report (Apple FY2023, Walmart FY2024, JPMorgan FY2023)

Date: 2026-10-06. Detailed per-question notes, ground truth and diagnoses: `eval/EVAL_LOG.md`.
Answers: `eval/<set>/qNN.json|md` (before), `qNN_after.*` (after fixes), `qNN_context.txt` (exact evidence via `--no-llm`).

**Status: Phases A and B as of 2026-10-06; Phase C (JPMorgan) rated 2026-10-07.** The OpenRouter free tier hit its daily cap (`free-models-per-day`, 50
requests; reset 2026-10-07 00:00 UTC = 03:00 local). Phase A is complete. Phase B is complete except two re-runs
(Q9, Q10). Phase C (JPMorgan) was not rated: the graph is built and inspected, ground truth is extracted, and the
10 questions are ready in `eval/jpm_questions.txt`.

Rubric: Numeric 4, Grounding 2, Completeness 2, Honesty 1, Analyst 1. Ground truth came from a separate
inline-XBRL extractor that reads the filing HTML directly, plus the filing text. It was not taken from the tool's own graph.

## 1. Apple FY2023: before / after

| Q | Topic | Before | After | What changed | Fault layer |
|---|---|---|---|---|---|
| 1 | Margins + drivers | 8.5 | 8.75 | Driver paragraphs (T00330/31/33/34) now reach the model (F4); model still explains arithmetically | RETRIEVAL, then MODEL |
| 2 | Balance sheet | 7.5 | 9.25 | Non-current debt now -3.7% (was -13.4% from a mixed series) (F1) | RETRIEVAL (mislabelled data) |
| 3 | Cash and returns | 9.25 | 9.25 | Regression check, unchanged | NONE |
| 4 | Red flags | 9.25 | 9.25 | Fragment replies fixed (F5, F6); all fix-22 flags correct and labelled | PROMPT/LLM (fragments) |
| 5 | R&D and SG&A | 3.5 | 8.5 | "R&D"/"SG&A" now map to concepts (F2); intensities still not stated | RETRIEVAL |
| 6 | EPS and share count | 4.0 | 9.0 | EPS/share-count wording now planned (F3) | RETRIEVAL |
| 7 | Supply chain / FX risks | 6.75 | 8.25 | On-topic risk paragraphs (F4); single-source supply risk still missing | RETRIEVAL |
| 8 | Tax rate | 9.5 | 9.25 | Regression check; 21% paragraph dropped from the top 4 (-0.25, under the 1-pt threshold) | NONE |
| 9 | China | 9.5 | 9.5 | Re-run, unchanged | NONE |
| 10 | Units / guidance trap | 9.0 | 9.0 | Re-run, unchanged; trap passed both times | NONE |
| | **Average** | **7.68** | **9.00** | | |

A second regression check after the Phase B fixes gave Apple Q2 = 9.25 (no regression; the new twin display shows
`us-gaap:LongTermDebt` as its own labelled series). Apple Q7 and Q8 second checks could not complete (rate limits,
then the daily cap). The Apple graph was rebuilt with the final code into a scratch file, and it is fact-for-fact
identical to `eval/aapl_2023.json`. So no Apple re-run was needed for the DATA-layer changes.

## 2. Walmart FY2024 (year ended 2024-01-31; built with `--year 2024`, because `--year` matches the period-end year)

| Q | Topic | Before | Fault layer | Fix | After |
|---|---|---|---|---|---|
| 1 | Revenue / OI / margin | 6.0 (capped) | DATA twin, hidden by RETRIEVAL | W3 | 9.5 |
| 2 | Segments, fastest growth, highest margin | 6.5 | RETRIEVAL (+ DATA pseudo-segments) | W2 | 9.25 |
| 3 | Current ratio, inventory build-up | 2.0 | RETRIEVAL ("current" read as a year; latest FY = 2029) | W1 | 9.5 |
| 4 | OCF / FCF / capex / payouts | 9.75 | NONE | none (regression check) | 9.5 |
| 5 | Debt, net debt, coverage | 3.75 | DATA (ShortTermBorrowings alias; InterestExpenseDebt unmapped) | W7 + F6 | 8.5 |
| 6 | Lease obligations vs assets | 7.5 | RETRIEVAL (lease-liability elements unreachable) | W4 | 8.75 |
| 7 | Tax rate vs statutory | 7.75 | RETRIEVAL (reconciliation unreachable) | W4 | 8.5 (sign error on credits, open) |
| 8 | eCommerce, membership | 7.25 | RETRIEVAL + DATA (`MembershipFeesMember` became `shipFees`) | W4, W5, W6 | 9.25 |
| 9 | Tariff / supply / FX / intl risks | 7.25 | RETRIEVAL (4 slots for a 4-topic question; semantic mapper) | W8, W8b | **not re-rated** (empty reply from a music model, then the daily cap) |
| 10 | Capex guidance / store-count trap | 9.5 | NONE (exact "$20 billion to $24 billion"; store count correctly not disclosed) | none (regression check) | **not re-rated** (same) |
| | **Average** | **6.73** (all 10) | | | **9.09** (8 re-rated; same 8 before: 6.31) |

## 3. JPMorgan FY2023: rated 2026-10-07 (held-out eval set, rate only, no fixes)

Graph built with the final code (13,512 facts). Model on every call: apodex-1.1-mini or ling-3.1-flash; no transport failures.

| Q | Topic | Score | Fault layer | What was wrong (concise) | Proposed fix (not applied) |
|---|---|---|---|---|---|
| 1 | Net revenue, NI, ROE | 6.0 (capped) | DATA | Revenue and NI exact; headline ROE 16.4/12.8/16.0% is derived on total equity, the filing says 19/14/17% (common); flags garbage "quarterly NI" from the misparsed summary table | Bank ROE on common equity (or prefer the reported ROE); stop reading multi-year summary tables as instants |
| 2 | NII and NIM | 8.5 | RETRIEVAL | NII $89.3B (+34%) and drivers exact; says NIM not in evidence, but the filing has it (2.70% vs 2.00%) | Theme for "net interest margin"/"net yield" text and the table row |
| 3 | ACL and provision vs loans | 6.0 | RETRIEVAL + MODEL | Provision $9.3B, NCOs $6.2B, +$3.1B build right; ACL $22.4B and loans $1.32T (1.69%) never reached it; segment provisions presented as "quarterly" | Credit theme (FinancingReceivableAllowance..., loans) using standard us-gaap names |
| 4 | CET1 and capital ratios | 9.0 | RETRIEVAL (minor) | CET1 15.0% vs 11.4% requirement correct with buffer breakdown; Tier 1 16.6%, Total 18.5%, leverage 7.2%, SLR 6.1% honestly reported missing | Retrieve the selected-metrics capital rows |
| 5 | Loans, deposits, LDR | 3.25 | RETRIEVAL | Loans $1.32T, deposits $2.40T, LDR 55% all missing (honest); padded with PPP loans and "total debt" | Deposits/loans theme; bank-aware derived LDR |
| 6 | Segment revenue | 1.25 | DATA + RETRIEVAL | All segment numbers wrong: the 2024 allocated-EQUITY table (CIB $102B, CCB $54.5B ...) was read as "FY2024 revenue". Truth: CCB $70.15B, CIB $48.81B, CB $15.55B, AWM $19.83B | Use the two-axis XBRL segment slices (segment x consolidation item); reject table periods beyond the filing year |
| 7 | Noninterest expense, overhead, comp | 6.0 | RETRIEVAL + MODEL | Expense $87.2B (+14%) and drivers right; gives share-based comp $3.12B instead of compensation $46.47B; overhead ratio 55% vs 59% missing; "may outpace revenue" is false (revenue +23%) | Map LaborAndRelatedExpense; overhead-ratio theme |
| 8 | Credit, market, liquidity risks | 6.0 | SIGNALS + RETRIEVAL | Credit and liquidity risk text cited correctly; market risk barely covered; forces industrial flags on a bank ("OCF fell 87.9%", "OCF 0.26x NI", "total debt +27.8%") | Bank-aware red-flag screen (suppress cash-conversion/OCF/total-debt flags for banks); 8 paragraphs for risk questions |
| 9 | Shareholder returns, shares, EPS | 8.75 | MODEL (minor) | All numbers exact (dividends $13.46B, buybacks $9.82B, EPS $16.23 +34.2%, diluted shares -0.9%); attributes EPS growth to share count instead of NI +32%; omits period-end shares -2.0%; OCF noise | Same bank-aware screen |
| 10 | Guidance / market-share trap | 8.0 | MODEL | Trap passed: NII ~$90B (~$88B ex-Markets) quoted exactly; no NI guidance and no market share correctly stated; but calls "$18.73B" the FY2023 NII base (actual $89.27B) | none needed beyond the NII series in context |
| | **Average** | **6.28** | | | |

Pattern: the numbers that reach the model are almost always right, and honesty is good (no invented market share, no
invented NI guidance). Failures come from bank concepts that aren't reachable (deposits, loans, allowance,
compensation, NIM, overhead), one table misread (allocated equity as revenue), and an industrial red-flag screen
that isn't bank-aware.
## 4. Code changes

| ID | File / function | Reason (one line) | Test | Rebuild? |
|---|---|---|---|---|
| fix 22 | signals.py `red_flags`, retrieval.py, tests | Applied exactly as specified (labels, PAYOUT low, declines, coverage drop) | tests/test_redflags.py, test_balance_sheet.py | No |
| F0 | table_parser.py `parse_header_periods` | `int("Three")` was evaluated eagerly, so any "Three Months Ended" header crashed the build | tests/test_header_periods.py | Only filings that crashed (JPM) |
| F1 | retrieval.py `_facts_for` | A stock-concept series shows instants only (no FY-labelled note rows or cash-flow changes) | tests/test_stock_series.py | No |
| F2 | retrieval.py `plan` | "&" expanded to "and" before concept matching ("R&D", "SG&A") | tests/test_question_planning.py | No |
| F3 | retrieval.py `THEMES` | EPS / share-count / buyback wording | tests/test_question_planning.py | No |
| F4 | retrieval.py `retrieve` | Graph-link boost only for named concepts, once per paragraph | tests/test_narrative_ranking.py | No |
| F5 | answer.py `ask` | A fragment reply never replaces the answer; first-reply fragment is re-asked | tests/test_answer_fragments.py | No |
| F6 | llm.py `extract_json` | Never salvage a nested item of a truncated object (this also skipped the bigger-budget retry) | tests/test_llm.py | No |
| F7 | llm.py `list_free_models` | Skip free models that output anything but text (music/image generators) | tests/test_llm.py | No |
| F8 | answer.py `ask` | No parsable answer raises instead of returning an empty answer | tests/test_answer_fragments.py | No |
| W1 | retrieval.py `plan` | "current ratio" is not a time word; "latest" = the filing's FY | tests/test_plan_and_slices.py | No |
| W2 | retrieval.py `plan`/`retrieve` | Empty member never matches; ratio inputs get slices; XBRL slices beat table pseudo-segments | tests/test_plan_and_slices.py | No |
| W3 | retrieval.py `_xbrl_twins` | Equally-trusted XBRL twins shown as separate labelled series | tests/test_plan_and_slices.py | No |
| W4 | retrieval.py `THEMES` | Lease liabilities, statutory-rate reconciliation, membership/other income (standard us-gaap names) | tests/test_plan_and_slices.py | No |
| W5 | retrieval.py `plan`/`_sub_slices` | Hyphen-insensitive members; two-axis slices (eCommerce x segment) | tests/test_plan_and_slices.py | No |
| W6 | loader.py `parse_ixbrl` | Strip only a trailing "Member"/"Axis" | tests/test_plan_and_slices.py | Yes (WMT; AAPL/JPM unaffected) |
| W7 | taxonomy.py, derived.py `TotalDebt` | `ShortTermBorrowings` is its own concept, counted in TotalDebt; `InterestExpenseDebt` is mapped to InterestExpense | tests/test_debt_and_interest_mapping.py | Yes (done: WMT, JPM) |
| W8/W8b | retrieval.py `retrieve` | 8 narrative paragraphs when no metric is named (overview or semantic plan) | tests/test_narrative_ranking.py | No |

No company names, tickers or filing numbers appear in any fix. `requirements.txt` is unchanged: scikit-learn 1.8.0
imports cleanly, and the real BGE embedder plus reranker is in use (not the BM25 fallback).

## 5. Regression results

| After fix | Question re-run | Before | After |
|---|---|---|---|
| F1–F5 (retrieval / answer) | Apple Q3 | 9.25 | 9.25 |
| F1–F5 | Apple Q8 | 9.5 | 9.25 (-0.25, OK) |
| Phase B fixes | Walmart Q4 | 9.75 | 9.5 (-0.25, OK) |
| Phase B fixes | Apple Q2 | 9.25 | 9.25 |
| Phase B fixes | Walmart Q10, Apple Q7, Apple Q8 | — | not completed (empty model replies, then the daily cap) |

No regression of 1 point or more anywhere.

## 6. Unresolved defects, ranked by impact

1. **Free-model quota and quality (MODEL/infra).** 50 requests a day, frequent 429s, non-JSON or fragment replies, and
   one model that wasn't a chat model (now filtered). This alone stopped the run.
2. **Tax-reconciliation sign convention (DATA).** `...TaxCredits` (and similar reduction items) are reported positive
   but mean a reduction. Walmart Q7 said credits *add* 1.5 pp. Needs element-specific sign rules plus a rebuild.
3. **Equally-trusted XBRL twins are resolved by insertion order (DATA).** `ProfitLoss` vs `NetIncomeLoss` (Walmart net
   margin / ROE use NI incl. NCI) and `LongTermDebt` vs `LongTermDebtNoncurrent`. W3 makes both visible, but derived
   ratios still use the first one.
4. **JPMorgan table parsing (DATA).** Summary tables read as instants, share counts mapped as EPS, pseudo-segments.
   The bank phase will show how much of this reaches answers.
5. **Prompt over-caution (PROMPT/MODEL).** The model refuses to compute an asked-for ratio of two evidence numbers
   (Walmart Q6: leases / assets), and doesn't sum finance leases into "total debt incl. leases" (Walmart Q5).
6. **Overview padding for text questions (RETRIEVAL).** Apple Q7: numeric overview series are still added to pure risk
   questions, and the model echoes them.
7. **Interest coverage uses debt interest only (DATA definition).** Walmart: 11.96x vs 10.1x including finance-lease
   interest. Should be labelled or extended.
8. **Pre-existing stale test.** `test_retrieval::test_auto_mode_resolves_offline_to_bm25` expects `auto` -> `hybrid`;
   the code and its docstring say `hybrid_rerank`. Your call whether the test or the code is right; I left it.

MODEL-only issues (not code): Apple Q1 ignoring the provided driver paragraphs; the antidilutive-RSU misreading
(Apple Q6); "highest OI, therefore highest margin" (Walmart Q2); "materially affected cash" for $69M (Walmart Q9, first pass).

## 7. Generalization verdict

- **Calendar/September-year tech company (Apple):** strong after fixes (9.0 average). The numbers are almost always
  exact; the remaining gaps are model interpretation.
- **January-year retailer (Walmart):** fiscal-year naming and period ids were correct from the start. The weaknesses
  were standard us-gaap elements outside the taxonomy, alias twins, two-axis XBRL slices, and "current" read as a
  year. With fixes, the 8 re-rated answers average 9.09 (from 6.31).
- **Bank (JPMorgan):** 6.28 on the held-out set. Numbers that reach the model are right and honesty is good (the guidance/market-share trap was passed), but bank concepts (deposits, loans, allowance, compensation, NIM, overhead) are mostly unreachable, one table misread produced wrong segment revenue, and the red-flag screen pushes industrial flags (OCF, cash conversion, total debt) onto a bank.

**Next three improvements:**
1. Prefer the exact-name XBRL element over an alias twin in `Lookup` / derived metrics, and carry a sign convention
   for reduction-type elements. This removes the remaining DATA ambiguity.
2. Replace the hand-made theme lists with a generic mapping from question words to *any* us-gaap element present in
   the filing (its standard label), so unmapped standard elements are always reachable.
3. Make the LLM layer quota-aware: count requests, back off on `free-models-per-day`, and let the prompt allow
   simple ratios/sums of evidence numbers that the question explicitly asks for.

## How to finish (after the quota reset, 2026-10-07 03:00 local)

```powershell
.\eval\run_set.ps1 -Graph eval/wmt.json -Set wmt -Questions eval/wmt_questions.txt -Only 9,10 -Suffix _after
.\eval\run_set.ps1 -Graph eval/aapl_2023.json -Set apple -Questions eval/apple_questions.txt -Only 7,8 -Suffix _after2
.\eval\run_set.ps1 -Graph eval/jpm.json -Set jpm -Questions eval/jpm_questions.txt
```

About 15–35 requests in total, which fits within one day's 50-request quota.

Final test run: **149 passed, 1 failed** (the pre-existing `test_retrieval::test_auto_mode_resolves_offline_to_bm25`).
