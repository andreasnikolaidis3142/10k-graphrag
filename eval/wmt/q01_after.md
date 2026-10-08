# How did total revenue, operating income and operating margin change over the last three fiscal years?

*model: inclusionai/ling-3.1-flash | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Over FY2022-FY2024, Walmart's revenue grew each year: net sales rose from $567.76B in FY2022 to $605.88B in FY2023 (+6.7% YoY) and $642.64B in FY2024 (+6.1% YoY), a 6.4% CAGR [F00005][F00004][F00003]; the total Revenues line shows the same pattern at $572.75B, $611.29B and $648.12B [F00011][F00010][F00009]. Operating income was volatile: it fell 21.3% YoY from $25.94B in FY2022 to $20.43B in FY2023, then rebounded 32.2% to $27.01B in FY2024, ending only 4% above FY2022 (2.0% CAGR) [F00020][F00019][F00018]. Operating margin moved from 4.6% in FY2022 to 3.4% in FY2023 (-120 bps) and recovered to 4.2% in FY2024 (+83 bps), still 40 bps below FY2022 [F01836][F01837][F01838]; management text confirms the 83 bps increase and 120 bps decrease [T00425]. The FY2024 revenue increase was led by Walmart US ($21.26B, 58% of the $36.76B change) and Walmart International ($13.66B, 37%), while the operating income rebound was driven mainly by the Corporate and Support loss narrowing by $2.88B (44% of the $6.58B change) and International operating income rising $1.94B (30%) [F00958][F00959][F00965][F00963].

**Status:** mixed

## Key numbers
- Net sales (RevenueFromContractWithCustomerExcludingAssessedTax) (FY2022): **$567.76B**  [F00005]
- Net sales (FY2023): **$605.88B (+6.7% YoY)**  [F00004]
- Net sales (FY2024): **$642.64B (+6.1% YoY)**  [F00003]
- Total Revenues (us-gaap:Revenues) (FY2022-FY2024): **$572.75B / $611.29B / $648.12B**  [F00011]
- Operating income (FY2022): **$25.94B**  [F00020]
- Operating income (FY2023): **$20.43B (-21.3% YoY)**  [F00019]
- Operating income (FY2024): **$27.01B (+32.2% YoY)**  [F00018]
- Operating margin % (FY2022): **4.6%**  [F01836]
- Operating margin % (FY2023): **3.4% (-120 bps)**  [F01837]
- Operating margin % (FY2024): **4.2% (+83 bps)**  [F01838]

## Drivers
- FY2024 revenue change of +$36.76B (+6.1%): Walmart US was the LARGEST CONTRIBUTOR TO THE CHANGE at +$21.26B (+5.1%), 58% of the total change, on $441.82B of sales (68.8% of total) [F00958]; Walmart International added +$13.66B (+13.5%), 37% of the change, on $114.64B (17.8%) [F00959]; Sam's Club contributed +$1.83B (+2.2%), 5% of the change [F00960].
- FY2024 operating income change of +$6.58B (+32.2%): Corporate and Support was the LARGEST CONTRIBUTOR TO THE CHANGE as its loss narrowed from -$5.12B to -$2.24B (+$2.88B, -56.2%), 44% of the total change [F00965]; Walmart International operating income rose +$1.94B (+65.6%) to $4.91B, 30% of the change [F00963]; Walmart US rose +$1.53B (+7.4%) to $22.15B (82.0% of total operating income), 23% of the change [F00962]; Sam's Club added +$228.00M (+11.6%), 3% [F00964].
- FY2023 operating income decline of -21.3% ($25.94B to $20.43B) coincided with SG&A growing +7.9% YoY to $127.14B, faster than the +6.7% revenue growth, and gross margin falling 98 bps to 23.5% [F00019][F00016][F01834].
- Management narrative attributes the margin moves to the factors described in the filing: operating income as a percentage of net sales increased 83 bps in FY2024 and decreased 120 bps in FY2023 [T00425].

## Risks and red flags
- FY2023 was a clear profit trough: operating income fell 21.3% to $20.43B and operating margin dropped 120 bps to 3.4%, the lowest of the three years [F00019][F01837].
- Despite the FY2024 rebound, operating margin of 4.2% remains 40 bps below the FY2022 level of 4.6%, and operating income CAGR of 2.0% lags the 6.4% revenue CAGR, indicating margin compression over the window [F01838][F01836][F00018][F00003].
- SG&A expense rose from $117.81B to $130.97B over the window (+11%), outpacing revenue growth in FY2023 (+7.9% vs +6.7%) [F00017][F00015][F00016].
- The Corporate and Support segment remains a loss of -$2.24B in FY2024; the operating income rebound depends heavily on this loss narrowing rather than on core segment expansion [F00965].
- Two different revenue definitions exist in the filing (net sales $642.64B vs total revenues $648.12B in FY2024); the ~$5.5B gap (e.g., membership/other income) should be reconciled when comparing to peers [F00003][F00009].

## Data quality
- 3 accounting identities passed, 0 failed for the numbers above.
- 19 duplicate facts with conflicting values were set aside during parsing; the primary-statement value was kept.
- Narrative facts T00425, T00474, T00483 and T00467 carry 'unchecked' number-check flags, so their figures are reported as management text, not independently verified [T00425].
- Operating margin is a derived ratio (OperatingIncome / Revenues); its bps changes are percentage-point differences, not percent changes [F01836][F01837][F01838].
- Segment attribution shares are of the total change and can exceed 100% or be negative when components offset; Corporate and Support's 44% share reflects a loss narrowing, not a profit increase [F00965].

## Outlook
- Actuals: FY2022-FY2024 actuals show steady top-line growth (revenue +13% over the window) with a V-shaped profit path: a 21.3% operating income decline in FY2023 followed by a 32.2% rebound in FY2024 to a record $27.01B, though margin (4.2%) has not fully recovered to the FY2022 4.6% level [F00003][F00018][F01838].
- Guidance: not in the retrieved evidence - no management guidance figures were provided in the evidence for FY2025 or beyond.

## Follow-up checks
- Reconcile the two revenue lines (net sales $642.64B vs total revenues $648.12B) and confirm which the company uses as its headline 'total revenue' [F00003][F00009].
- Verify the 19 duplicate facts that were set aside during parsing to ensure the primary-statement values are the correct ones.
- Confirm the drivers behind the Corporate and Support loss narrowing (-$5.12B to -$2.24B), since it accounts for 44% of the FY2024 operating income change [F00965].
- Check whether the FY2024 operating margin recovery (+83 bps) is sustained in subsequent filings, given it remains below FY2022's 4.6% [F01838][F01836].
- Obtain the underlying causes cited in the filing text for the FY2023 margin decline (the narrative references 'factors described above' which are not in the retrieved evidence) [T00425].

## Sources (where each cited number came from)
- **F00005** $567.76B Revenues FY2022 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #32 "Consolidated Results of Operations", row "Net sales", column "2022"
    - also shown in table #50 "Consolidated Statements of Income", row "Net sales", column "2022"
- **F00004** $605.88B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #27 "untitled", row "Net sales", column "2023"
    - also shown in table #32 "Consolidated Results of Operations", row "Net sales", column "2023"
    - also shown in table #50 "Consolidated Statements of Income", row "Net sales", column "2023"
- **F00003** $642.64B Revenues FY2024 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #27 "untitled", row "Net sales", column "2024"
    - also shown in table #32 "Consolidated Results of Operations", row "Net sales", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Net sales", column "2024"
- **F00011** $572.75B Revenues FY2022 - *XBRL*: inline XBRL tag us-gaap:Revenues
    - also shown in table #32 "Consolidated Results of Operations", row "Total revenues", column "2022"
    - also shown in table #50 "Consolidated Statements of Income", row "Total revenues", column "2022"
    - also shown in table #86 "untitled", row "Total revenues", column "2022"
- **F00010** $611.29B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:Revenues
    - also shown in table #32 "Consolidated Results of Operations", row "Total revenues", column "2023"
    - also shown in table #50 "Consolidated Statements of Income", row "Total revenues", column "2023"
    - also shown in table #86 "untitled", row "Total revenues", column "2023"
- **F00009** $648.12B Revenues FY2024 - *XBRL*: inline XBRL tag us-gaap:Revenues
    - also shown in table #32 "Consolidated Results of Operations", row "Total revenues", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Total revenues", column "2024"
    - also shown in table #86 "untitled", row "Total revenues", column "2024"
- **F00020** $25.94B OperatingIncomeLoss FY2022 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #32 "Consolidated Results of Operations", row "Operating income", column "2022"
    - also shown in table #50 "Consolidated Statements of Income", row "Operating income", column "2022"
- **F00019** $20.43B OperatingIncomeLoss FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #27 "untitled", row "Operating income", column "2023"
    - also shown in table #28 "Return on Assets and Return on Investment", row "Operating income", column "2023"
    - also shown in table #32 "Consolidated Results of Operations", row "Operating income", column "2023"
- **F00018** $27.01B OperatingIncomeLoss FY2024 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #27 "untitled", row "Operating income", column "2024"
    - also shown in table #28 "Return on Assets and Return on Investment", row "Operating income", column "2024"
    - also shown in table #32 "Consolidated Results of Operations", row "Operating income", column "2024"
- **F01836** 4.6% OperatingMarginPct FY2022 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00020, F00005
- **F01837** 3.4% OperatingMarginPct FY2023 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00019, F00004
- **F01838** 4.2% OperatingMarginPct FY2024 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00018, F00003
- **T00425**  - *prose*: paragraph in the filing: "Operating income as a percentage of net sales increased 83 basis points and decreased 120 basis points for fiscal 2024 and 2023, respectively, due to the factor"
- **F00958** $441.82B Revenues FY2024 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00959** $114.64B Revenues FY2024 [StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00965** -$2.24B OperatingIncomeLoss FY2024 [StatementBusinessSegments=CorporateAndSupport] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00963** $4.91B OperatingIncomeLoss FY2024 [StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00960** $86.18B Revenues FY2024 [StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #35 "Sam's Club Segment", row "Net sales", column "2024"
- **F00962** $22.15B OperatingIncomeLoss FY2024 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00964** $2.19B OperatingIncomeLoss FY2024 [StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #35 "Sam's Club Segment", row "Operating income", column "2024"
- **F00016** $127.14B SellingGeneralAndAdministrativeExpense FY2023 - *XBRL*: inline XBRL tag us-gaap:SellingGeneralAndAdministrativeExpense
    - also shown in table #50 "Consolidated Statements of Income", row "Operating, selling, general and administrative expenses", column "2023"
- **F01834** 23.5% GrossMarginPct FY2023 - *computed*: GrossProfit / Revenues x 100
    - computed from F01828, F00004
- **F00017** $117.81B SellingGeneralAndAdministrativeExpense FY2022 - *XBRL*: inline XBRL tag us-gaap:SellingGeneralAndAdministrativeExpense
    - also shown in table #50 "Consolidated Statements of Income", row "Operating, selling, general and administrative expenses", column "2022"
- **F00015** $130.97B SellingGeneralAndAdministrativeExpense FY2024 - *XBRL*: inline XBRL tag us-gaap:SellingGeneralAndAdministrativeExpense
    - also shown in table #50 "Consolidated Statements of Income", row "Operating, selling, general and administrative expenses", column "2024"
- **T00474**  - *prose*: paragraph in the filing: "As a result of the factors discussed above, segment operating income increased $1.9 billion and decreased $0.8 billion for fiscal 2024 and 2023, respectively, w"
- **T00483**  - *prose*: paragraph in the filing: "As a result of the factors discussed above, segment operating income increased $0.2 billion and decreased $0.3 billion for fiscal 2024 and 2023, respectively, w"
- **T00467**  - *prose*: paragraph in the filing: "As a result of the factors discussed above, segment operating income increased $1.5 billion and decreased $1.0 billion for fiscal 2024 and 2023, respectively, w"
- **F00979** $420.55B Revenues FY2023 [StatementBusinessSegments=WalmartUS] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00980** $100.98B Revenues FY2023 [StatementBusinessSegments=WalmartInternational] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00961** $0.00 Revenues FY2024 [StatementBusinessSegments=CorporateAndSupport] (not cited by the answer; included because its name appears in the text) - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00982** $0.00 Revenues FY2023 [StatementBusinessSegments=CorporateAndSupport] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00986** -$5.12B OperatingIncomeLoss FY2023 [StatementBusinessSegments=CorporateAndSupport] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00984** $2.96B OperatingIncomeLoss FY2023 [StatementBusinessSegments=WalmartInternational] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00983** $20.62B OperatingIncomeLoss FY2023 [StatementBusinessSegments=WalmartUS] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
