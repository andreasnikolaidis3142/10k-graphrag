# Are there any red flags in Apple's financial statements?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Apple's FY2023 10-K (fiscal year ended September 30, 2023) carries several pre-computed red flags, although the auditor issued an unqualified opinion dated November 2, 2023 [T00627]. Operating cash flow fell 9.5% to $110.54B and free cash flow fell 10.6% to $99.58B, while capex rose 2.3% to $10.96B [F00224][F01389][F00236]. Liquidity is a medium-risk flag: the current ratio was below 1 in both FY2022 (0.88) and FY2023 (0.99) [F01420][F01421]. Inventory grew 28% in FY2023 while cost of revenue fell 4%, flagged as a collection/build-up risk [F00099][F00022]. Revenue fell 2.8% to $383.29B and operating income fell 4.3% to $114.30B, and interest coverage dropped 29% to 29.1x [F00013][F00037][F01432]. Shareholder payouts of $92.58B consumed 93% of free cash flow in FY2023, leaving little room to absorb a downturn [F01448][F01389].

**Status:** mixed

## Key numbers
- Operating cash flow (FY2023): **$110.54B (-9.5% YoY)**  [F00224]
- Free cash flow (derived: CFO - capex) (FY2023): **$99.58B (-10.6% YoY)**  [F01389]
- Capex (PaymentsToAcquirePropertyPlantAndEquipment) (FY2023): **$10.96B (+2.3% YoY)**  [F00236]
- Current ratio (FY2023): **0.99 (<1)**  [F01421]
- Current ratio (FY2022): **0.88 (<1)**  [F01420]
- Inventory growth vs cost of revenue (FY2023): **inventory +28% vs cost of revenue -4%**  [F00099]
- Revenue (FY2023): **$383.29B (-2.8% YoY)**  [F00013]
- Operating income (FY2023): **$114.30B (-4.3% YoY)**  [F00037]
- Interest coverage (FY2023): **29.1x (-29%, from 40.7x)**  [F01432]
- Dividends + buybacks as % of free cash flow (FY2023): **$92.58B = 93% of FCF**  [F01448]

## Drivers
- FY2023 free cash flow decline (-10.6%, $111.44B -> $99.58B) coincides with the 9.5% operating cash flow decline ($122.15B -> $110.54B); capex was roughly flat (+2.3%), so the cash-flow deterioration is on the operating side rather than investment [F01389][F00224][F00236].
- Inventory build-up is the medium-risk driver: FY2023 inventory grew 28% while cost of revenue fell 4%, a divergence the screen flags as collection/build-up risk [F00099][F00022].
- Shareholder payout is a low-risk but binding constraint: dividends+buybacks of $92.58B were 93% of FY2023 free cash flow (94% in FY2022 at $104.24B of $111.44B), leaving little buffer in a downturn [F01448][F01447][F01389][F01388].
- Liquidity improved but remains flagged: current ratio rose from 0.88 (FY2022) to 0.99 (FY2023), still below 1.0 in both years [F01420][F01421].

## Risks and red flags
-  Liquidity: FY2022 current ratio 0.88 (<1) [F01420].
-  Liquidity: FY2023 current ratio 0.99 (<1) [F01421].
-  Inventory vs cost of sales: FY2023 inventory grew 28% while cost of revenue fell 4% (collection/build-up risk) [F00099][F00022].
-  Operating cash flow decline: FY2023 OCF fell 9.5% ($122.15B -> $110.54B) [F00224].
-  Shareholder payout vs free cash flow: FY2022 dividends+buybacks ($104.24B) were 94% of FCF ($111.44B) [F01447][F01388].
-  Shareholder payout vs free cash flow: FY2023 dividends+buybacks ($92.58B) were 93% of FCF ($99.58B) [F01448][F01389].
-  Revenue decline: FY2023 revenue fell 2.8% ($394.33B -> $383.29B) [F00013].
-  Operating income decline: FY2023 operating income fell 4.3% ($119.44B -> $114.30B) [F00037].
-  Interest coverage drop: FY2023 interest coverage fell 29% (40.7x -> 29.1x) [F01432].

## Data quality
- 3 accounting identities passed, 0 failed for the screened numbers; no text-vs-table conflicts were reported.
- Free cash flow is a derived metric (CFO - capex) per the evidence view; operating cash flow and capex are XBRL-tagged [F00224][F00236][F01389].
- The current-ratio, payout-ratio and interest-coverage items are pre-computed screen outputs, not separately re-derived here.
- Audit opinion was unqualified (PCAOB standards), report dated November 2, 2023 [T00627].

## Outlook
- Actuals: FY2023 actuals show broad-based declines: revenue -2.8%, operating income -4.3%, operating cash flow -9.5%, free cash flow -10.6%, and interest coverage -29%, with the current ratio still below 1.0; the two-year FCF/OCF trend is characterized as 'stable (weak)' [F00013][F00037][F00224][F01389][F01432][F01421].
- Guidance: Not in the retrieved evidence - no management guidance figures were provided in the narrative evidence.

## Follow-up checks
- Inventory composition (finished goods vs components/raw materials) to determine whether the 28% FY2023 build is deliberate supply-chain positioning or demand softness [F00099].
- Current-ratio trajectory and short-term debt/commercial paper levels in FY2024 filings, given sub-1.0 ratios in FY2022 and FY2023 [F01420][F01421].
- Whether operating cash flow recovers in FY2024 quarterly filings after the 9.5% FY2023 decline [F00224].
- Sustainability of the ~93% payout ratio versus free cash flow and remaining buyback authorization [F01448][F01389].
- Drivers of the interest-coverage drop (interest expense versus operating income) behind the move from 40.7x to 29.1x [F01432].

## Sources (where each cited number came from)
- **T00627**  - *prose*: paragraph in Item 8 Financial Statements: "We also have audited, in accordance with the standards of the Public Company Accounting Oversight Board (United States) (the “PCAOB”), the consolidated balance "
- **F00224** $110.54B NetCashProvidedByUsedInOperatingActivities FY2023 - *XBRL*: inline XBRL tag us-gaap:NetCashProvidedByUsedInOperatingActivities
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Cash generated by operating activities", column "September 30, 2023"
- **F01389** $99.58B FreeCashFlow FY2023 - *computed*: CFO - Capex
    - computed from F00224, F00236
- **F00236** $10.96B PaymentsToAcquirePropertyPlantAndEquipment FY2023 - *XBRL*: inline XBRL tag us-gaap:PaymentsToAcquirePropertyPlantAndEquipment
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Payments for acquisition of property, plant and equipment", column "September 30, 2023"
- **F01420** 0.88x CurrentRatio @2022-09-24 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00104, F00126
- **F01421** 0.99x CurrentRatio @2023-09-30 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00103, F00125
- **F00099** $6.33B InventoryNet @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:InventoryNet
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Inventories", column "September 30, 2023"
- **F00022** $214.14B CostOfRevenue FY2023 - *XBRL*: inline XBRL tag us-gaap:CostOfGoodsAndServicesSold
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total cost of sales", column "September 30, 2023"
- **F00013** $383.29B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total net sales", column "September 30, 2023"
- **F00037** $114.30B OperatingIncomeLoss FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Operating income", column "September 30, 2023"
    - also shown in table #47 "untitled", row "Total operating income", column "2023"
- **F01432** 29.06x InterestCoverage FY2023 - *computed*: OperatingIncome / InterestExpense
    - computed from F00037, F00548
- **F01448** $92.58B ShareholderReturns FY2023 - *computed*: Dividends + Repurchases
    - computed from F00248, F00251
- **F01447** $104.24B ShareholderReturns FY2022 - *computed*: Dividends + Repurchases
    - computed from F00249, F00252
- **F01388** $111.44B FreeCashFlow FY2022 - *computed*: CFO - Capex
    - computed from F00225, F00237
