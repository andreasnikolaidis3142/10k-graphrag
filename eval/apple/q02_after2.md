# Is Apple's balance sheet healthy? Look at liquidity, debt and net cash.

*model: inclusionai/ling-3.1-flash | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Apple's FY2023 balance sheet is liquid but leveraged: the current ratio improved to 0.99x from 0.88x yet remains below 1.0x, with current assets of $143.57B against current liabilities of $145.31B [F01421][F00103][F00125]. The company holds a net cash position of $51.01B (negative net debt), up from $49.04B, as total debt fell 7.5% to $111.09B while cash rose 26.7% to $29.96B and short-term investments rose 28.1% to $31.59B [F01425][F01423][F00091][F00093]. Leverage declined, with debt/equity down 24.6% to 1.79x from 2.37x [F01427]. Interest coverage remains high but dropped 28.7% to 29.06x in FY2023 from 40.75x in FY2022 [F01432]. Management states cash, cash equivalents and unrestricted marketable securities totaled $148.3B at September 30, 2023 [T00350]. Overall the position is strong on solvency but shows tightening liquidity and coverage trends.

**Status:** mixed

## Key numbers
- Current ratio (FY2023 (2023-09-30)): **0.99x**  [F01421]
- Current ratio (FY2022 (2022-09-24)): **0.88x**  [F01420]
- Cash and cash equivalents (FY2023): **$29.96B**  [F00091]
- Short-term investments (marketable securities current) (FY2023): **$31.59B**  [F00093]
- Marketable securities, noncurrent (FY2023): **$100.54B**  [F00105]
- Total debt (derived) (FY2023): **$111.09B**  [F01423]
- Net debt (negative = net cash) (FY2023): **-$51.01B (net cash of $51.01B)**  [F01425]
- Debt / equity (FY2023): **1.79x**  [F01427]
- Interest coverage (EBIT / interest) (FY2023): **29.06x**  [F01432]
- Current assets (FY2023): **$143.57B**  [F00103]
- Current liabilities (FY2023): **$145.31B**  [F00125]
- Cash + unrestricted marketable securities (MD&A) (FY2023): **$148.3B**  [T00350]

## Drivers
- Liquidity improvement: current ratio rose 12.4% to 0.99x as current assets grew 6.0% to $143.57B while current liabilities fell 5.6% to $145.31B [F01421][F00103][F00125]; the ratio still sits below 1.0x, flagged MEDIUM in the red-flag screen [F01421].
- Net cash position: net cash of $51.01B (net debt of -$51.01B) vs $49.04B a year earlier [F01425][F01424]; the build reflects total debt down 7.5% to $111.09B [F01423], cash up 26.7% to $29.96B [F00091] and short-term investments up 28.1% to $31.59B [F00093], partly offset by noncurrent marketable securities down 16.8% to $100.54B [F00105].
- Debt composition: long-term debt noncurrent fell 3.7% to $95.28B [F00127] and current portion of long-term debt fell 11.7% to $9.82B [F00123]; the LongTermDebt (total) tag shows $105.10B vs $110.09B [F00765][F00766].
- Leverage: debt/equity fell 24.6% to 1.79x from 2.37x [F01427], the clearest deleveraging signal in the evidence.
- Coverage: interest coverage fell 28.7% to 29.06x in FY2023 from 40.75x in FY2022 (41.19x in FY2021), a flagged inflection [F01432][F01431][F01430]; coverage remains high in absolute terms.

## Risks and red flags
- Liquidity: current ratio below 1.0x in both FY2022 (0.88x) and FY2023 (0.99x) [F01420][F01421] - MEDIUM flag; the retrieved evidence does not explain the structural cause (e.g., deferred revenue or commercial paper).
- Inventory build: FY2023 inventory grew 28% while cost of revenue fell 4% - MEDIUM collection/build-up risk [F00099][F00022].
- Cash generation: operating cash flow fell 9.5% to $110.54B from $122.15B in FY2023 [F00224] - MEDIUM flag.
- Capital returns: FY2023 dividends plus buybacks of $92.58B were 93% of free cash flow of $99.58B (FY2022: $104.24B vs $111.44B, 94%) - LOW flag, little room to absorb a downturn [F01448][F01389][F01447][F01388].
- Earnings pressure: FY2023 revenue fell 2.8% to $383.29B [F00013] and operating income fell 4.3% to $114.30B [F00037], coinciding with the coverage decline.
- Investment portfolio: the company is exposed to credit risk and fluctuations in the values of its investment portfolio [T00225].

## Data quality
- 0 accounting identities passed and 0 failed for the numbers above; no text-vs-table conflicts reported.
- 5 duplicate facts with conflicting values were set aside during parsing (primary-statement value kept); the specific items are not identified in the retrieved evidence.
- The 'Cash' financial-instrument slice ($28.36B [F00301]) is a component of the consolidated cash total ($29.96B [F00091]), not the company total; likewise the $0.00 'Cash' slices for marketable securities [F00302][F00303] are instrument-level tags.
- Net debt pre-computed finding labels the change '+4.0% YoY' while the trend line says '-4% over the window' [F01425]; the magnitude of net cash grew from $49.04B to $51.01B, so the sign convention reflects a larger net cash balance, not deterioration.
- MD&A statement that cash and unrestricted marketable securities totaled $148.3B [T00350] is marked 'number checks: unchecked' and does not tie directly to the tagged lines in the retrieved evidence ($29.96B cash + $31.59B short-term + $100.54B noncurrent = components shown; the $148.3B figure itself is not independently verified here).

## Outlook
- Actuals: FY2023 actuals show a solvent, deleveraging balance sheet: net cash of $51.01B [F01425], total debt down 7.5% to $111.09B [F01423], debt/equity down to 1.79x [F01427], and interest coverage of 29.06x [F01432]. Offsetting this, the current ratio remains below 1.0x at 0.99x [F01421], operating cash flow fell 9.5% [F00224], and capital returns consumed 93% of free cash flow [F01448][F01389].
- Guidance: Management (forward-looking, not an actual) believes its $148.3B of cash, cash equivalents and unrestricted marketable securities at September 30, 2023, together with cash from operations and continued access to debt markets, will be sufficient to meet cash requirements and its capital return program over the next 12 months and beyond [T00350].

## Follow-up checks
- Reconcile the MD&A's $148.3B cash and unrestricted marketable securities figure [T00350] to the tagged balance-sheet lines ($29.96B cash [F00091], $31.59B short-term investments [F00093], $100.54B noncurrent marketable securities [F00105]) and identify any restricted securities excluded.
- Obtain the debt maturity schedule and commercial paper balance to assess refinancing risk behind the $111.09B total debt [F01423] and the sub-1.0x current ratio [F01421].
- Verify the composition of current liabilities ($145.31B [F00125]) - e.g., deferred revenue and accounts payable - to determine whether the current ratio below 1.0x is structural.
- Investigate the 28% inventory build against a 4% cost-of-revenue decline [F00099][F00022] for obsolescence or channel-stocking risk.
- Confirm the drivers of the interest coverage drop to 29.06x [F01432] - lower operating income [F00037] versus higher interest expense - and check the 5 duplicate facts that were set aside during parsing.
- Track whether the 93% payout of free cash flow [F01448][F01389] is sustained if operating cash flow keeps declining [F00224].

## Sources (where each cited number came from)
- **F01421** 0.99x CurrentRatio @2023-09-30 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00103, F00125
- **F00103** $143.57B AssetsCurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:AssetsCurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Total current assets", column "September 30, 2023"
- **F00125** $145.31B LiabilitiesCurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:LiabilitiesCurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Total current liabilities", column "September 30, 2023"
- **F01425** -$51.01B NetDebt @2023-09-30 - *computed*: TotalDebt - Cash - ShortTermInvestments - NonCurrentMarketableSecurities
    - computed from F01423, F00091, F00093, F00105
- **F01423** $111.09B TotalDebt @2023-09-30 - *computed*: LT debt + current debt + commercial paper
    - computed from F00127, F00123, F00121
- **F00091** $29.96B CashAndCashEquivalentsAtCarryingValue @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:CashAndCashEquivalentsAtCarryingValue
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Cash and cash equivalents", column "September 30, 2023"
- **F00093** $31.59B ShortTermInvestments @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:MarketableSecuritiesCurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Marketable securities", column "September 30, 2023"
- **F01427** 1.79x DebtToEquity @2023-09-30 - *computed*: TotalDebt / Equity
    - computed from F01423, F00149
- **F01432** 29.06x InterestCoverage FY2023 - *computed*: OperatingIncome / InterestExpense
    - computed from F00037, F00548
- **T00350**  - *prose*: paragraph in Item 7 MD&A: "The Company believes its balances of cash, cash equivalents and unrestricted marketable securities, which totaled $148.3 billion as of September 30, 2023, along"
- **F01420** 0.88x CurrentRatio @2022-09-24 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00104, F00126
- **F00105** $100.54B MarketableSecuritiesNoncurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:MarketableSecuritiesNoncurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Marketable securities", column "September 30, 2023"
- **F01424** -$49.04B NetDebt @2022-09-24 - *computed*: TotalDebt - Cash - ShortTermInvestments - NonCurrentMarketableSecurities
    - computed from F01422, F00092, F00094, F00106
- **F00127** $95.28B LongTermDebtNoncurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:LongTermDebtNoncurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Term debt", column "September 30, 2023"
- **F00123** $9.82B LongTermDebtCurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:LongTermDebtCurrent
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Term debt", column "September 30, 2023"
- **F00765** $105.10B LongTermDebtNoncurrent @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:LongTermDebt
- **F00766** $110.09B LongTermDebtNoncurrent @2022-09-24 - *XBRL*: inline XBRL tag us-gaap:LongTermDebt
- **F01431** 40.75x InterestCoverage FY2022 - *computed*: OperatingIncome / InterestExpense
    - computed from F00038, F00549
- **F01430** 41.19x InterestCoverage FY2021 - *computed*: OperatingIncome / InterestExpense
    - computed from F00039, F00550
- **F00099** $6.33B InventoryNet @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:InventoryNet
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Inventories", column "September 30, 2023"
- **F00022** $214.14B CostOfRevenue FY2023 - *XBRL*: inline XBRL tag us-gaap:CostOfGoodsAndServicesSold
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total cost of sales", column "September 30, 2023"
- **F00224** $110.54B NetCashProvidedByUsedInOperatingActivities FY2023 - *XBRL*: inline XBRL tag us-gaap:NetCashProvidedByUsedInOperatingActivities
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Cash generated by operating activities", column "September 30, 2023"
- **F01448** $92.58B ShareholderReturns FY2023 - *computed*: Dividends + Repurchases
    - computed from F00248, F00251
- **F01389** $99.58B FreeCashFlow FY2023 - *computed*: CFO - Capex
    - computed from F00224, F00236
- **F01447** $104.24B ShareholderReturns FY2022 - *computed*: Dividends + Repurchases
    - computed from F00249, F00252
- **F01388** $111.44B FreeCashFlow FY2022 - *computed*: CFO - Capex
    - computed from F00225, F00237
- **F00013** $383.29B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total net sales", column "September 30, 2023"
- **F00037** $114.30B OperatingIncomeLoss FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Operating income", column "September 30, 2023"
    - also shown in table #47 "untitled", row "Total operating income", column "2023"
- **T00225**  - *prose*: paragraph in Item 1A Risk Factors: "The Company is exposed to credit risk and fluctuations in the values of its investment portfolio."
- **F00301** $28.36B CashAndCashEquivalentsAtCarryingValue @2023-09-30 [FinancialInstrument=Cash] - *XBRL*: inline XBRL tag us-gaap:CashAndCashEquivalentsAtCarryingValue
- **F00302** $0.00 ShortTermInvestments @2023-09-30 [FinancialInstrument=Cash] - *XBRL*: inline XBRL tag us-gaap:MarketableSecuritiesCurrent
- **F00303** $0.00 MarketableSecuritiesNoncurrent @2023-09-30 [FinancialInstrument=Cash] - *XBRL*: inline XBRL tag us-gaap:MarketableSecuritiesNoncurrent
