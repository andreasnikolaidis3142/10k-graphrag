# Evaluation log: tenk_graphrag

Judge: evaluation agent. Rubric: Numeric 4 / Grounding 2 / Completeness 2 / Honesty 1 / Analyst 1.
Ground truth: an independent inline-XBRL extractor (scratch script that parses ix:nonFraction + contexts directly from the
downloaded filing HTML, not through tenk_graphrag) plus the filing's plain text for narrative claims.

## Setup (2026-10-06)

- Python 3.13.14 in `.venv` (note: bare `python` on PATH is the WindowsApps interpreter, so all commands use `.venv\Scripts\python.exe`).
- Packages: networkx 3.7, numpy 2.5.3, beautifulsoup4 4.15.0, lxml 6.1.3, requests 2.34.2, python-dotenv 1.2.4,
  sentence-transformers 6.1.0, scikit-learn 1.8.0 (imports cleanly; no pin change needed), torch 2.14.1.
- Embedder: real (`BAAI/bge-large-en-v1.5`), so narrative retrieval runs in `hybrid_rerank`, not the BM25 fallback.
- LLM: `.env` sets `FREE_MODELS=apodex-1.1-mini:free`; auto-discovered free models are fallbacks.
- **Baseline tests: 20/21 suites pass. Pre-existing failure:** `test_retrieval::test_auto_mode_resolves_offline_to_bm25`
  asserts `auto -> "hybrid"` with a real embedder, but `Retriever._resolve_mode` (and its docstring, retrieval.py:364)
  returns `"hybrid_rerank"`. The test is stale relative to the documented design; it is unrelated to every evaluated layer.
  Left untouched (changing a test's expectation is the owner's call). Still failing at the end for the same reason.

## Fix 22 (applied exactly as specified)

All anchors found exactly once. Edits 2a-2g applied verbatim (signals.py FLAG_LABELS + label field + PAYOUT low branch +
REVENUE/OPINC/OCF_DECLINE + COVERAGE_DROP; retrieval.py label in red-flag line; test_balance_sheet strings; new
tests/test_redflags.py). Result: test_redflags 3 passed, test_balance_sheet 5 passed, test_cash_questions 4 passed (fix 21
present). All other suites unchanged (only the pre-existing test_retrieval failure).

## Phase A: Apple FY2023

Build: `build --company AAPL --year 2023 --out eval/aapl_2023.json` -> accession 0000320193-23-000106, period end
2023-09-30, 1383 typed facts, 16 identity checks, 0 failed.

inspect_graph findings:
- 33 table facts set aside, all losing to XBRL (note sub-tables such as the term-debt maturity table, RSU tables). Benign.
- 18 "equally-trusted twins": `us-gaap:LongTermDebt` ($105.10B, includes current portion) is mapped to the same concept as
  `us-gaap:LongTermDebtNoncurrent` ($95.28B); `us-gaap:NonoperatingIncomeExpense` (-$565M) shares the slot of
  `OtherNonoperatingIncomeExpense` (-$382M); 4 RPO percentages. Watch: debt questions (Q2).
- 3 prose numbers differ from tables (interest expense on term debt $3.7B vs total interest expense $3.93B; deferred
  revenue recognised). All narrower items, correctly classified as "differs", not errors.

Ground truth (from XBRL, FY2021 / FY2022 / FY2023):
- Revenue 365.817 / 394.328 / 383.285 B (FY23 -2.80%). COGS 212.981 / 223.546 / 214.137 (FY23 -4.21%).
- GP 152.836 / 170.782 / 169.148 -> GM 41.78 / 43.31 / 44.13%. OI 108.949 / 119.437 / 114.301 -> OM 29.78 / 30.29 / 29.82%.
- R&D 21.914 / 26.251 / 29.915 (5.99 / 6.66 / 7.80% of rev). SG&A 21.973 / 25.094 / 24.932 (6.01 / 6.36 / 6.50%).
- Current assets 143.566, current liabilities 145.308 -> CR 0.988 (FY22 0.879).
- Debt FY23: CP 5.985 + term debt current 9.822 + non-current 95.281 = 111.088 B.
  Cash 29.965 + current mkt sec 31.590 + non-current mkt sec 100.544 = 162.099 B -> net cash 51.0 B.
- OCF 110.543 (FY22 122.151, -9.5%), capex 10.959, FCF 99.584; buybacks 77.550, dividends 15.025 (total 92.575 = 93% of FCF).
- Inventory 4.946 -> 6.331 (+28.0%) vs COGS -4.2%. AR 28.184 -> 29.508 (+4.7%) vs revenue -2.8%.
- Interest expense 2.645 / 2.931 / 3.933; EBIT/interest 41.2x / 40.7x / 29.1x.
- EPS diluted 5.61 / 6.11 / 6.13; diluted WASO 16.865 / 16.326 / 15.813 B (FY23 -3.1%); basic 15.744 B; shares outstanding
  at year end 15.550 B (FY22 15.943 B).
- ETR 13.3 / 16.2 / 14.7% vs 21% statutory. Reason (MD&A): "lower effective tax rate on foreign earnings, the impact of the
  U.S. federal R&D credit, and tax benefits from share-based compensation, partially offset by state income taxes."
- Greater China 68.366 / 74.200 / 72.559 B (FY23 -2.2%, 18.9% of revenue); OI 30.328 B. iPhone net sales 200.583 B (-2.4%).
- MD&A margin drivers: Products GM% up on cost savings and mix, offset by FX and decreased leverage (T00331); Services GM%
  down on higher Services costs and FX, offset by mix (T00334).

### Apple first pass ("before" column)

Each answer: `eval/apple/qNN.json|md`; exact evidence the model got: `eval/apple/qNN_context.txt` (`--no-llm`).
Model on every call: `apodex/apodex-1.1-mini:free` (no transport failures, no retries needed).

**Q1 margins: 8.5** (Num 4 / Ground 2 / Compl 1 / Hon 1 / Analyst 0.5). Fault: RETRIEVAL.
All numbers right (GM 41.8/43.3/44.1%, +153/+82 bps; OM 29.8/30.3/29.8%, +51/-47 bps; Products GM $108.80B vs $114.73B,
Services $60.34B vs $56.05B). Defect: the MD&A sentences that explain the margin *percentages* (T00331 Products GM%
up on cost savings + mix, offset by FX + decreased leverage; T00334 Services GM% down) were not in the context; it got
T00333 (Services GM *dollars*) plus an off-topic segment paragraph and a seasonality risk factor. The answer therefore
explains the GM% move only arithmetically. Diagnosis: hybrid search ranks T00330/T00331 #1/#2, but the graph `EXPLAINS`
bonus is added once per linked concept across all 12 planned concepts (incl. ratio inputs Revenues/CostOfRevenue
that the question never named), so a generic segment paragraph (4 links, no search hit) scores 4.0 and wins the top-4.
Decision: 8-8.9 accept; candidate cheap fix noted (see Fixes).

**Q2 balance sheet: 7.5** (Num 3 / Ground 1.5 / Compl 1.5 / Hon 1 / Analyst 0.5). Fault: RETRIEVAL (series mixes
mislabelled DATA).
Right: net cash $51.01B (FY22 $49.04B), total debt $111.09B (-7.5%), D/E 1.79x vs 2.37x, CR 0.99 vs 0.88, coverage 29.06x,
cash +26.7%, current securities +28.1%, non-current securities -16.8%, $148.3B unrestricted (T00350).
Wrong: "long-term debt noncurrent down 13.4% to $95.28B" -> truth -3.7% (95.281 vs 98.959). 13.4% = 95.281/110.087, the
FY22 *total* term debt from the debt note. The `LongTermDebtNoncurrent` series in the context mixed the balance-sheet
instants (@2022-09-24 $98.96B, @2023-09-30 $95.28B) with the note's "Total term debt" read with *flow* periods
(FY2022 $110.09B, FY2023 $105.10B). Also: "net cash of -$51.01B" (sign confusion in prose), data-quality section padded with
cash-slice noise. Below 8 -> fix (see Fixes).

**Q3 cash generation and returns: 9.25** (4 / 1.75 / 1.75 / 1 / 0.75). Fault: NONE.
OCF $110.54B, capex $10.96B, FCF $99.58B, buybacks $77.55B, dividends $15.03B, total $92.58B = 93.0% of FCF, all exact.
Minor: "relies on continued access to debt markets" overstates T00350 (management "believes ... will be sufficient");
omits the 9.5% OCF decline; one off-topic net-sales line. Accept.

**Q4 red flags:** the first-pass answer process started about 1 s after I briefly applied (and then reverted) a
retrieval edit, so it may have run on modified code. Its evidence pack was produced on clean code. To keep the before
column honest, Q4 was re-run on clean code after the batch; that run is the "before" score (see below).
Evidence pack red-flag screen (clean code) matches ground truth exactly: CR<1 FY22/FY23 (medium), inventory +28% vs
COGS -4% (medium), OCF -9.5% (medium), payout 94%/93% of FCF (low), revenue -2.8% and OI -4.3% (low), coverage
40.7x -> 29.1x (low). Labels readable. Cosmetic: an empty "TEXT-vs-TABLE CONFLICTS:" line is printed when no
mismatch has a computed value; the inventory flag text says "collection / build-up risk" (collection belongs to AR).

**Q5 R&D and SG&A: 3.5** (Num 1 / Ground 1.5 / Compl 0 / Hon 1 / Analyst 0). Fault: RETRIEVAL.
Truth: R&D $29.915B (7.80% of rev; FY22 6.66%, FY21 5.99%; +14.0%), SG&A $24.932B (6.50%; FY22 6.36%; -0.6%).
The answer says R&D and SG&A are "not in the retrieved evidence" (true for the context, so it was honest) and pads with
revenue attribution (whose numbers are correct). Diagnosis: `plan()` mapped the question to `['Revenues']` only. The
taxonomy synonyms `r&d` / `sg&a` are normalised by `norm()` to `r and d` / `sg and a`, but `find_concepts_in_text`
keeps `&` as a literal character, so an abbreviation with `&` in a question can never match. General bug (any
"R&D", "SG&A", "D&A" question). Below 8 -> fix.

**Q6 EPS and share count: 4.0** (Num 1 / Ground 1.5 / Compl 0.25 / Hon 1 / Analyst 0.25). Fault: RETRIEVAL.
Truth: diluted EPS $6.13 vs $6.11 (+0.3%) vs $5.61; diluted WASO 15.813B vs 16.326B (-3.1%); basic 15.744B; buybacks
$77.55B (-13.3%). The context had no EPS and no share-count series; the answer correctly reports buyback/dividend
changes and honestly says EPS/share counts are missing. Diagnosis: the question's words ("earnings per share",
"share count", "buybacks") match no taxonomy synonym (only "diluted earnings per share", "weighted average shares
diluted", "share repurchases"...); the series shown came from the semantic mapper. Model: inclusionai/ling-3.1-flash
(fallback; apodex unavailable for that call). Below 8 -> fix.

**Q7 supply chain and FX risks: 6.75** (Num 3.5 / Ground 1.5 / Compl 0.5 / Hon 1 / Analyst 0.25). Fault: RETRIEVAL.
FX risk (T00221) described correctly; no supply-chain risk factor at all ("no dedicated supply chain risk factor" -
false for the filing: outsourcing partners, single/limited-source components, IT systems of the supply chain).
Off-topic revenue attribution fills the answer (numbers correct). Diagnosis: "risks" -> intent `screen` with no named
concept -> OVERVIEW fallback (9 metrics + inputs); their EXPLAINS links give +1/+2 to paragraphs with no search hit
(T00274 net-sales sentence, T00333, T00593) and push out search hits (T00220 FX, T00123 trade/political, T00177
supply-chain IT). Same mechanism as Q1. Below 8 -> fix.

**Q8 effective tax rate: 9.5** (4 / 2 / 1.75 / 1 / 0.75). Fault: NONE. ETR 14.7 / 16.2 / 13.3%, 21% statutory, the
four reasons quoted faithfully from T00347; tax $16.74B on pre-tax $113.74B; UTB $19.5B / $9.5B verified in the text.
Minor: data-quality padding. Accept.

**Q9 China: 9.5** (4 / 2 / 1.75 / 1 / 0.75). Fault: NONE. Greater China $72.56B vs $74.20B (-2.2%), 18.9% of sales;
U.S./China the only >10% countries (T00600); Americas segment vs U.S. geography kept distinct; Japan, Europe, RoAP and
product moves all exact. Minor: verbose product breakdown. Accept.

**Q10 honesty trap: 9.0** (4 / 2 / 1.5 / 0.75 / 0.75). Fault: NONE. No unit count, ASP or guidance invented; iPhone
$200.58B (-2.4%), 52.3% of revenue. Minor: off-topic Americas/Mac drivers; a follow-up suggests units might be in
"Note 13", which they are not. Accept.

## Phase B: Walmart (fiscal year ended 2024-01-31)

`--year` is matched against the calendar year of the filing's period-end date (`reportDate`), so the 10-K for the
fiscal year ended January 2024 is `--year 2024`. Build: `build --company WMT --year 2024 --out eval/wmt.json` ->
accession 0000104169-24-000056, period end 2024-01-31, 1826 typed facts, 7 identity checks, 0 failed.
Fiscal-year labelling: periods are `FY2024` / `FY2023` / `FY2022` with ends 2024-01-31 etc., matching Walmart's own
"fiscal 2024" naming. Correct.

inspect_graph findings:
- 25 table facts set aside, all losing to XBRL. Notably the segment tables (tables 463/470/919: Walmart U.S. $441.8B,
  International $114.6B, Sam's Club $86.2B rows read as company-wide `Revenues`/`OperatingIncomeLoss`) were caught by
  conflict resolution and shadowed. Correct behaviour.
- 81 equally-trusted XBRL twins (both kept, `Lookup` picks by insertion order). Three matter:
  1. `Revenues` = both `us-gaap:Revenues` (total revenues $648.1B, incl. membership & other income) and
     `RevenueFromContractWithCustomer...` (net sales $642.6B).
  2. `NetIncomeLoss` = both `us-gaap:ProfitLoss` (consolidated $16.27B, incl. noncontrolling interest) and
     `us-gaap:NetIncomeLoss` (attributable to Walmart $15.51B). Taxonomy alias collapses two different items.
  3. `LongTermDebtCurrent` = both `us-gaap:ShortTermBorrowings` ($0.878B) and `us-gaap:LongTermDebtCurrent`
     ($3.447B). Two different items; derived TotalDebt can only include one of them.
- 0 prose/table mismatches.

Ground truth (XBRL; FY2022 / FY2023 / FY2024):
- Total revenues 572.754 / 611.289 / 648.125 B (+6.7%, +6.0%); net sales 567.762 / 605.881 / 642.637 (+6.7%, +6.1%).
- Membership & other income (revenues - net sales) 4.992 / 5.408 / 5.488 (+1.5% FY24). Membership fee revenue
  (OtherIncome, MembershipFeesMember) 2.2 / 2.6 / 3.1 B. eCommerce net sales FY24: U.S. 65.4 (+22%), Intl 24.8 (+22%),
  Sam's 9.9 (+18%) -> total 100.1 B vs 82.1 (+22%).
- Operating income 25.942 / 20.428 / 27.012 (-21.3%, +32.2%); OM on total revenues 4.53 / 3.34 / 4.17%
  (on net sales 4.57 / 3.37 / 4.20%).
- Segments FY24 (FY23): U.S. 441.817 (420.553) +5.1%, OI 22.154 -> 5.0%; International 114.641 (100.983) +13.5%, OI
  4.909 -> 4.3%; Sam's Club 86.179 (84.345) +2.2%, OI 2.192 -> 2.5%. Fastest growth: International; highest OM: U.S.
- Current assets 76.877 / current liabilities 92.415 -> CR 0.83 (FY23 0.82). Inventory 56.576 -> 54.892 (-3.0%) vs
  COGS 463.721 -> 490.142 (+5.7%): inventory fell while sales grew, i.e. no build-up.
- OCF 24.181 / 28.841 / 35.726 (+23.9%); capex 13.106 / 16.857 / 20.606; FCF 11.075 / 11.984 / 15.120; dividends 6.140,
  buybacks 2.779 (FY23 9.920) -> 8.919 = 59% of FCF.
- Debt FY24: ST borrowings 0.878 + LTD due within one year 3.447 + LTD 36.132 = 40.457 B; + finance lease liabilities
  0.725 + 5.709 = 46.891 B incl. finance leases. Cash 9.867 -> net debt 30.59 B (37.02 B incl. finance leases).
- Interest: debt 2.259 + finance lease 0.424 = 2.683 B gross (FY23 2.128, FY22 1.994); net of interest income 2.137.
  EBIT/gross interest 13.0x / 9.6x / 10.1x.
- Leases FY24: operating lease liabilities 1.487 + 12.943 = 14.430 B; finance 0.725 + 5.709 = 6.434 B; total 20.864 B
  = 8.3% of total assets 252.399 B. ROU assets: operating 13.673, finance 5.855.
- ETR 25.4 / 33.6 / 25.5% vs 21%. FY24 reconciliation (printed table): state & local +3.0 pp, valuation allowance +1.2,
  other +1.5, contingencies +0.6, foreign +0.1, repatriation (0.4), federal tax credits (1.5); sums to 25.5. (Corrected:
  repatriation was first logged as +0.4 from the unsigned XBRL value; the printed table shows a reduction.) FY23 spike: PhonePe.
- Fiscal 2025 capex guidance (MD&A, liquidity): "approximately $20 billion to $24 billion". No count of new stores to be
  opened is disclosed (only period-end unit counts). FY25 annual dividend $0.83/share (vs $0.76) is disclosed.

### Fixes applied in Phase A (all general; none names a company, ticker or filing number)

| # | Layer | File / function | Change | Test | Rebuild? |
|---|---|---|---|---|---|
| F0 | DATA (crash) | table_parser.py `parse_header_periods` | `_N.get(n.lower(), int(n))` evaluated `int("Three")` eagerly, so any table header "Three Months Ended" crashed the whole build (found when building JPM). Default is now evaluated only for digits. | tests/test_header_periods.py (2) | Only for filings that crashed before; Apple/WMT graphs cannot change (they never reached that path without crashing). |
| F1 | RETRIEVAL | retrieval.py `Retriever._facts_for` | A series for a stock (balance) concept keeps instants only; a fiscal-year-labelled fact of a stock concept is a misread note row or a cash-flow change and is no longer mixed in. (Q2) | tests/test_stock_series.py (2) | No |
| F2 | RETRIEVAL | retrieval.py `Retriever.plan` | Expand "&" to " and " before concept matching (taxonomy stores `r and d`, `sg and a`). (Q5) | tests/test_question_planning.py | No |
| F3 | RETRIEVAL | retrieval.py `THEMES` / `THEME_ALIASES` | New "per share" theme (diluted/basic EPS + diluted/basic share counts; aliases " eps", "share count", "shares outstanding", "dilution"); "buyback"/"repurchas" aliases for the shareholder theme. (Q6) | tests/test_question_planning.py (3 total, incl. a negative test) | No |
| F4 | RETRIEVAL | retrieval.py `Retriever.retrieve` (narrative) | EXPLAINS graph links boost a paragraph only for concepts the question named (not the OVERVIEW fallback, not ratio inputs) and only once per paragraph. (Q1, Q7) | tests/test_narrative_ranking.py (2) | No |
| F5 | PROMPT/VERIFIER | answer.py `ask` (+ `_is_answer`) | A reply with none of the answer-schema keys (e.g. a lone key_numbers item) no longer replaces the answer during repair, and a fragment first reply triggers one "return the COMPLETE object" re-ask. Q4 came back as a fragment in 2 of 4 runs (two different models). | tests/test_answer_fragments.py (2) | No |

Discarded alternative for Q2: forcing every stock-concept table fact to an instant period in table_parser (DATA layer).
Checked against both graphs before applying: it would turn cash-flow-statement change rows (e.g. "Inventories
-$2,642M" FY2021, a change) into balance-sheet values where no XBRL twin exists to shadow them, corrupting the
inventory-vs-COGS screen. Rejected in favour of F1 (display-only, derived ratios already use instants only).

Process note: while the first pass was running in the background I briefly applied F1 to check a test, then reverted
it within ~30 s. Only Q4's answer process could have started inside that window; Q4 was therefore re-run on clean code
for the before column (first clean retry returned a malformed fragment = MODEL failure, not rated; second retry rated).
After applying F5, the background "after" batch for Q5-Q8 picked up answer.py mid-run; F5 only acts on fragment
replies, which did not occur in those runs.

### Apple after-fix re-runs (`eval/apple/qNN_after.*`)

- **Q1 after 8.75** (4 / 1.5 / 1.5 / 1 / 0.75). Context now holds T00330/T00331/T00333/T00334 (all four margin-driver
  paragraphs). The model still explains GM% arithmetically and adds an uncited "mix shift toward Services"; it cites the
  driver paragraphs only for the FX risk. Remaining gap = MODEL.
- **Q2 after 9.25** (4 / 2 / 1.5 / 1 / 0.75). Non-current term debt now -3.7% (correct); net cash phrased correctly
  ("$51.01B (negative net debt)"). Remaining: cash-slice noise in data-quality, off-topic revenue line.
- **Q3 after 9.25** (regression check, retrieval layer): unchanged score; adds CP $6.0B at 5.28% vs $10.0B at 2.31%
  (verified in the filing).
- **Q4 after 9.25**: first after-run returned a fragment (answer blank) -> led to F5; re-run after F5 complete and
  correct, readable labels, severities now in the prose. Still no net-cash context for CR < 1 (analyst -0.5).
- **Q5 after 8.5** (4 / 2 / 1 / 1 / 0.5). R&D $29.91B (+14.0%), SG&A $24.93B (-0.6%), revenue -2.8%, all exact.
  Does not state the intensities (7.8% vs 6.7%; 6.5% vs 6.4%); off-topic revenue attribution. Possible next step:
  pull `RdIntensityPct` (exists) when R&D is asked and add an SG&A-intensity derived metric (not done: 8-8.9 band).
- **Q6 after 9.0** (4 / 1.75 / 1.75 / 1 / 0.5). EPS $6.13 vs $6.11, +8.9% FY22; diluted shares 15,812,547,000 (-3.1%),
  -3.2% FY22; buybacks -13.3%. Misses that net income fell 2.8% (why EPS barely rose); wrongly says antidilutive RSUs
  mean diluted EPS "understates potential dilution" (MODEL).
- **Q7 after 8.25** (3.5 / 2 / 1.25 / 1 / 0.5). Four on-topic risk-factor paragraphs (FX x2, supplier credit/prepayments,
  trade/political/natural disruption of suppliers and logistics). Still missing the outsourcing / single-source
  component factors (search rank) and padded with overview numbers (OVERVIEW fallback still adds series for a
  pure-text risk question).
- **Q8 after 9.25** (regression check, retrieval layer) vs 9.5 before: adds the FY23-vs-FY22 reasons (T00348, correct)
  but the reconciliation paragraph with 21% dropped out of the top-4, so 21% is not stated (honestly flagged).
  -0.25 < 1 point: not a regression under the policy.
- **Q9 after 9.5**, **Q10 after 9.0**: re-run for an honest after column (narrative ranking changed for all questions);
  same content quality, same scores. Q10's follow-up again suggests units "may appear in Note 13" (MODEL).

Apple averages: before 7.68 (76.75/10), after 9.00 (90.0/10). No DATA-layer change affected the Apple graph (F0 only
changes filings that crashed), so no rebuild was needed and the after column is on the same graph.

### Walmart first pass (`eval/wmt/qNN.*`)

**Q1 revenue / OI / margin: 6.0** (raw 2.5 / 1.75 / 1.75 / 0.75 / 0.75 = 7.5, capped at 6: wrong headline number).
Fault: DATA twin surfacing through RETRIEVAL. "Total revenue" reported as $567.76B / $605.88B / $642.64B; those are
NET SALES. Total revenues are $572.75B / $611.29B / $648.13B (us-gaap:Revenues, incl. membership & other income). The
two XBRL tags map to one concept; the series keeps one fact per period, so the total-revenues twin is never shown.
Correct: OI $25.94B / $20.43B / $27.01B (-21.3%, +32.2%), OM 4.6 / 3.4 / 4.2% (on net sales, Walmart's convention),
-120 / +83 bps, segment contributions to sales and OI change (U.S. 58%, Intl 37%, Sam's 5%; corporate -$5.12B ->
-$2.24B), SG&A +7.9% FY23. Also "net income $16.27B" = consolidated incl. NCI (attributable $15.51B; second twin
defect, not asked); "may reflect one-off items" is uncited speculation.

**Q2 segments: 6.5** (Num 3 / Ground 1.5 / Compl 1 / Hon 0.5 / Analyst 0.5). Fault: RETRIEVAL (+ DATA junk).
Net sales by segment, shares and growth all exact (U.S. $441.82B 68.8% +5.1%; Intl $114.64B +13.5% fastest; Sam's
$86.18B +2.2%; Sam's FY23 +14.7%). Says segment operating margin "cannot be answered from this filing" - false
(segment OI is XBRL-tagged; U.S. 5.0% highest, Intl 4.3%, Sam's 2.5%). "Walmart U.S. unit counts ... 4.62B" is a
scale error (4,615 stores). Diagnoses: (1) attribution slices are pulled only for primary[:4]; `OperatingMarginPct`
is a ratio with no slices and its input `OperatingIncomeLoss` is not primary, so segment OI never reaches the
context. (2) A Dim node with an EMPTY member exists and `'' in question` is always true -> spurious
`{'segment': ''}` series in every Walmart question. (3) Table parser turns segment-table rows ("Unit counts at period
end", "Interest, net", "Fiscal Year Ended January 31, 2022", ...) into fake `segment` members of Revenues, shown next
to the authoritative XBRL segment slices.

**Q3 current ratio / inventory: 2.0** (0 / 1 / 0 / 1 / 0). Fault: RETRIEVAL. Context had zero series; the model
honestly said so. Diagnosis: `plan()` treats the word "current" as "latest year", so "current ratio" adds a year
filter, and "latest" = max FY of ANY fact = 2029 (debt/lease maturity schedules). Every series filtered to FY2029 ->
empty. Truth: CR 0.83 (FY23 0.82); inventory $54.89B (-3.0%) vs COGS +5.7%: no build-up.

**Q4 cash flow and returns: 9.75** (4 / 2 / 2 / 1 / 0.75). Fault: NONE. OCF $35.73B (+23.9%), FCF $15.12B (+26.2%),
capex $20.61B (+22.2%, +57% over window), dividends $6.14B, buybacks $2.78B (-72.0%), total $8.92B = 59.0% of FCF vs
133.8% FY23, buyback CAGR -46.7%: all exact; FCF caveat (T00444) cited correctly. Minor: a 74.8-pt payout change
written as "-7481 bps". Accept.

**Q5 debt: not rated (transport/model failure).** Answer object came back as a lone key_numbers item ("Total debt
$37.01B"), although F5 was active. Root cause found in `llm.extract_json`: when the outer JSON object is unbalanced
(truncated) or invalid, it continues the scan INSIDE that object and returns the first complete nested item. Because
`chat()` uses `extract_json(...) is None` to decide whether a truncated reply needs a bigger budget, the truncated
answer was not retried and its first key_numbers entry became the "answer". This also explains the Apple Q4
fragments. Fix (F6) prepared with tests; applied only after the Walmart first pass finished, to keep Q6-Q10 clean.
Note: the evidence pack shows TotalDebt = $37.01B = LTD 36.13 + ShortTermBorrowings 0.88 (the `LongTermDebtCurrent`
twin picked ShortTermBorrowings; current maturities $3.45B and finance leases $6.43B missing).

**Q5 debt (clean retry): 3.75** (Num 1 / Ground 1 / Compl 0.75 / Hon 0.5 / Analyst 0.5). Fault: DATA.
"Total debt (short and long term, including finance leases) $37.01B" - truth $40.46B excl. leases ($46.89B incl.
finance leases); it is LTD 36.13 + ShortTermBorrowings 0.88 only, because `ShortTermBorrowings` was an alias of
`LongTermDebtCurrent` and won the twin slot over the $3.45B current maturities; finance leases are not in TotalDebt
and the label "including finance leases" is false. Net debt $27.14B (truth $30.59B excl. leases), D/E 0.44x inherit
it. Interest expense/coverage "not in the evidence": Walmart tags `InterestExpenseDebt`, which was not mapped to
`InterestExpense`, so InterestCoverage was never derived.

**Q6 leases: 7.5** (Num 3 / Ground 2 / Compl 0.75 / Hon 1 / Analyst 0.75). Fault: RETRIEVAL. ROU assets $13.67B
(5.4%) and $5.86B (2.3%) and segment assets correct; correctly refuses to treat ROU assets as obligations; but lease
LIABILITIES ($14.43B operating + $6.43B finance = $20.86B, 8.3% of assets) never reached the context: the standard
us-gaap lease-liability elements have no taxonomy entry, so no wording maps to them.

**Q7 tax rate: 7.75** (Num 4 / Ground 2 / Compl 0.5 / Hon 0.75 / Analyst 0.5). Fault: RETRIEVAL. ETR 25.5 / 33.6 /
25.4%, tax $5.58B on $21.85B, FY23 PhonePe spike all correct; never answers "what drove the difference from the
statutory rate" (21%; state +3.0, valuation allowance +1.2, other +1.5, credits -1.5): the rate-reconciliation
elements are XBRL-tagged but unreachable (same class as Q6).

**Q8 e-commerce / membership: 7.25** (Num 4 / Ground 2 / Compl 0.5 / Hon 0.25 / Analyst 0.5). Fault: RETRIEVAL +
DATA. Total revenues (+6.0% / +6.7%) and net sales (+6.1% / +6.7%) quoted correctly from T00454; asserts that
membership & other income is "not separately disclosed" and no e-commerce figure exists - both false (OtherIncome
$5.49B on the income statement; membership fees $3.1B; eCommerce net sales U.S. $65.4B, Intl $24.8B, Sam's $9.9B).
Diagnoses: no wording maps to `us-gaap:OtherIncome`; e-commerce exists only as TWO-axis slices (eCommerce x
segment) and retrieval fetched single-axis slices only; "e-commerce" (hyphen) never matched member "ECommerce";
loader stripped "Member" anywhere in a member name (`MembershipFeesMember` -> `shipFees`).

**Q9 risks: 7.25** (Num 3 / Ground 1.5 / Compl 1.25 / Hon 1 / Analyst 0.5). Fault: RETRIEVAL (+ MODEL wording).
Tariff/sourcing (T00284), international (T00277) and trade-restriction (T00280) risks cited correctly; no FX
risk-factor text and little supply-chain text (4 paragraph slots for a 4-topic question; one slot went to Walmart
Health); "foreign currency fluctuations materially affected cash" for a +$69M effect and "-194.5% YoY" for a sign
flip are analyst errors.

**Q10 honesty trap: 9.5** (4 / 2 / 1.75 / 1 / 0.75). Fault: NONE. Quotes the filing exactly ("approximately $20
billion to $24 billion" for fiscal 2025 capex, T00499), labels it guidance, and states that no store-opening count is
given. Accept (no rerun needed; rerun only as regression check).

Walmart before average: (6.0 + 6.5 + 2.0 + 9.75 + 3.75 + 7.5 + 7.75 + 7.25 + 7.25 + 9.5) / 10 = 6.73.

### Fixes applied in Phase B (all general)

| # | Layer | File / function | Change | Test | Rebuild? |
|---|---|---|---|---|---|
| F6 | PROMPT/LLM | llm.py `extract_json` | Never salvage a nested item of a truncated/invalid outer object; skip past it. Restores the bigger-budget retry for truncated answers. (WMT Q5, Apple Q4) | tests/test_llm.py (+2) | No |
| W1 | RETRIEVAL | retrieval.py `plan` | "latest" = filing FY (`meta['fy']`), not max FY of any fact (2029 maturity bucket); "current" before ratio/assets/liabilities/portion/debt/maturities/investments/tax is not a time word. (Q3) | test_plan_and_slices.py | No |
| W2 | RETRIEVAL | retrieval.py `plan` / `retrieve` | Empty dimension member never matches; attribution slices also cover the inputs of a ratio (operating margin -> operating income); when XBRL slices exist, table-row pseudo-segments are dropped (both in the dimension loop and in roll-up children). (Q2) | test_plan_and_slices.py | No |
| W3 | RETRIEVAL | retrieval.py `_xbrl_twins` | Equally-trusted XBRL twins (two elements, one concept) are shown as their own labelled series instead of being hidden by the one-per-period rule. (Q1) | test_plan_and_slices.py | No |
| W4 | RETRIEVAL | retrieval.py `THEMES` | Themes for lease liabilities (" lease", "lease obligation", "lease liabilit"; not "release"), statutory-rate reconciliation ("statutory", "rate reconciliation") and membership/other income, using standard us-gaap element names. (Q6, Q7, Q8) | test_plan_and_slices.py | No |
| W5 | RETRIEVAL | retrieval.py `plan` / `_sub_slices` | Member matching is hyphen-insensitive; a member tagged only with a second axis (eCommerce x segment) is returned as two-axis series. (Q8) | test_plan_and_slices.py | No |
| W6 | DATA | loader.py `parse_ixbrl` | Strip only a trailing "Member"/"Axis" (was: every occurrence). (Q8) | test_plan_and_slices.py | Yes (WMT only; AAPL/JPM have no such names) |
| W7 | DATA | taxonomy.py + derived.py `TotalDebt` | `ShortTermBorrowings` is its own concept (was an alias of current LTD) and an optional TotalDebt term; `InterestExpenseDebt` is an alias of `InterestExpense`. (Q5) | tests/test_debt_and_interest_mapping.py (3) | Yes |
| W8 | RETRIEVAL | retrieval.py `retrieve` | A question that names no metric (overview fallback = text question) gets 8 narrative paragraphs instead of 4. (Q9, also Apple Q7) | covered by test_narrative_ranking (unchanged) | No |

Rebuild check: eval/wmt.json rebuilt (1826 facts, 0 failed identities). A scratch rebuild of the Apple filing with the
final code is fact-for-fact identical to eval/aapl_2023.json (0 facts differ), so the Apple results stand without a
rebuild. Walmart diff limited to the intended concepts (ShortTermBorrowings split out, InterestExpense/Coverage
present, debt ratios, MembershipFees member). New derived values match ground truth: TotalDebt $40.457B (FY23
$39.212B), NetDebt $30.59B, D/E 0.48x; InterestCoverage 11.96x is on debt interest only (10.1x incl. finance-lease
interest) - caveat.

### Walmart after-fix re-runs (`eval/wmt/qNN_after.*`, rebuilt graph)

- **Q1 after 9.5** (4 / 2 / 1.75 / 1 / 0.75): net sales AND total revenues ($572.75B / $611.29B / $648.12B) both shown and
  labelled; OI, OM, bps, contributions unchanged and correct. Minor: margin basis (net sales) not stated.
- **Q2 after 9.25** (4 / 2 / 1.75 / 1 / 0.5): segment OI now present ($22.15B / $4.91B / $2.19B), U.S. correctly the
  highest margin; pseudo-segment "unit counts" gone. Margins not computed (5.0 / 4.3 / 2.5%) and the reasoning
  "highest operating income, so highest margin" is a logical slip with a correct conclusion (MODEL).
- **Q3 after 9.5** (4 / 2 / 1.75 / 1 / 0.75): CR 0.83 vs 0.82, CA +1.6% / CL +0.2%, WC deficit $15.5B vs $16.5B,
  inventory -3.0% vs COGS +5.7% -> no build-up. Noise: a "text/table scope" flag because the narrative extractor
  maps "working capital deficit" to LiabilitiesCurrent (minor DATA, not fixed).
- **Q4 after 9.5** (regression check) vs 9.75: same numbers; adds one uncited causal phrase ("investment in stores and
  supply chain"). -0.25: not a regression.
- **Q5 after 8.5** (4 / 2 / 1.25 / 0.75 / 0.5): total debt $40.46B (+3.2%), net debt $30.59B, interest $2.26B (+26.4%),
  coverage 15.50 -> 11.43 -> 11.96x, D/E 0.48x, finance-lease liabilities $6.43B - all correct. Does not add finance
  leases ($46.89B) or say that $40.46B excludes them; does not say coverage uses debt interest only.
- **Q6 after 8.75** (4 / 2 / 1.25 / 1 / 0.5): operating $14.43B ($1.49B + $12.94B), finance $6.43B ($0.725B + $5.71B),
  assets $252.40B - all correct; refuses to compute the asked ratio (20.86 / 252.40 = 8.3%) citing "no pre-computed
  ratio" - prompt-induced over-caution (PROMPT/MODEL, not fixed).
- **Q7 after 8.5** (3 / 2 / 1.75 / 1 / 0.75): 25.5% vs 21.0% statutory; state +3.0, valuation allowance +1.2 (4.4 ->
  1.7 -> 1.2), foreign +0.1, PhonePe for FY23 - correct. Wrong sign: "tax credits contributed +1.5%" (the printed table
  shows (1.5)%, a reduction). Root cause DATA semantics: `EffectiveIncomeTaxRateReconciliationTaxCredits` is reported
  as a positive value meaning a reduction, and the context renders it as +1.5% with no convention note. Not fixed
  (needs element-specific sign rules + rebuild); recorded as an open defect.
- **Q8 after 9.25** (4 / 2 / 1.5 / 1 / 0.75): eCommerce U.S. $65.4B (+22.5%), Intl $24.8B (+22.2%), Sam's $9.9B (+17.9%)
  vs net sales +6.1%; membership & other income $5.49B (+1.5%, from +8.3%); CAGRs correct. Misses the separately
  disclosed membership fee revenue ($3.1B, +19%).
- **Q9 after: not rated** - empty answer from `google/lyria-3-pro-preview` (a music model). Also: its context still had
  4 paragraphs because "foreign currency" was mapped by the SEMANTIC mapper to EffectOfExchangeRateOnCash, so
  `concept_source` was "semantic", not "overview" -> W8 extended (W8b): semantic-mapper plans also get 8 paragraphs
  (test_narrative_ranking +1 test). Re-run below.
- **Q10 after: not rated** - empty answer from the same music model. Led to two LLM-layer fixes:
  - **F7** llm.py `list_free_models`: keep only models whose `architecture.output_modalities` includes "text"
    (models without the field are kept). Test: test_llm.py +1.
  - **F8** answer.py `ask`: no parsable JSON answer -> RuntimeError instead of a silently empty answer (so callers/
    the runner retry). Test: test_answer_fragments.py +1.
  Re-run below.

### Stop (2026-10-06 23:30 local)

- F7 tightened: Lyria reports output_modalities = text,audio, so "includes text" was not enough; now text-only.
- Apple Q2 after2 (regression check after Phase B fixes): 9.25, no regression; twin `us-gaap:LongTermDebt` shown as its
  own labelled series and kept apart by the model.
- Apple Q7/Q8 after2, Walmart Q9/Q10 after: not completed. Sequence: 429s, non-JSON replies (now loud via F8), then
  OpenRouter `free-models-per-day` (limit 50, remaining 0, reset 2026-10-07 00:00 UTC).
- Stopped at the user's request. Phase C (JPMorgan) not rated; graph built with final code, inspected, truth recorded
  in EVAL_REPORT.md section 3.
- Final tests: 149 passed, 1 failed (pre-existing test_retrieval::test_auto_mode_resolves_offline_to_bm25).

## Phase C: JPMorgan (rated 2026-10-07, rate only)

Quota reset confirmed (HTTP 200). All 10 answered on the first attempt (`eval/jpm/qNN.*`). Scores: Q1 6.0 (capped,
ROE definition), Q2 8.5, Q3 6.0, Q4 9.0, Q5 3.25, Q6 1.25, Q7 6.0, Q8 6.0, Q9 8.75, Q10 8.0 -> average 6.28.
Per-question diagnosis and proposed (not applied) fixes: EVAL_REPORT.md section 3.
Additional truth used: segment net revenue FY23 (FY22) CCB 70.148 (54.814), CIB 48.807 (48.102), CB 15.546 (11.533),
AWM 19.827 (17.748); ROE 17/14/19%, ROTCE 21/18/23%, overhead 55/59/59%, LDR 55/49/44%, CET1 15.0/13.2/13.1%,
Tier 1 16.6%, Total 18.5%, Tier 1 leverage 7.2%, SLR 6.1%; NIM (managed) 2.70/2.00/1.64%; period-end shares 2,876.6M
vs 2,934.2M; compensation $46.465B (+11.6%).
