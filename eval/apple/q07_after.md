# What are the main risks Apple describes about its supply chain and foreign exchange?

*model: inclusionai/ling-3.1-flash | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Apple's Item 1A Risk Factors identify foreign exchange and supply chain as primary exposures. FX exposure centers on non-U.S. dollar-denominated sales, cost of sales and operating expenses worldwide, with gross margins on foreign products and products using foreign-sourced components vulnerable to FX fluctuations [T00221]. The value of the U.S. dollar relative to local currencies also affects financial performance [T00220]. Supply chain risks include credit exposure on trade receivables, vendor non-trade receivables and prepayments tied to long-term supply agreements, heightened during economic downturns [T00228]. Broader business interruption risks from political events, trade disputes, war, natural disasters and public health issues could disrupt suppliers, contract manufacturers, logistics providers and channel partners [T00123]. These risks coincided with FY2023 revenue declining 2.8% to $383.29B [F00013], where Mac was the largest contributor to the product-level decline at -$10.82B (-26.9%), 98% of the total change [F00282] [F00283], partly offset by Services growth of $7.07B (+9.1%) [F00010] [F00011].

**Status:** mixed

## Key numbers
- FY2023 revenue (FY2023): **$383.29B**  [[F00013]]
- FY2023 Mac revenue (largest contributor to change) (FY2023): **$29.36B (7.7% of total); change -$10.82B (-26.9%), 98% of total change**  [[F00282] [F00283]]
- FY2023 Services revenue (offset) (FY2023): **$85.20B (22.2% of total); change +$7.07B (+9.1%), offsets 64% of total change**  [[F00010] [F00011]]
- FY2023 iPhone revenue (FY2023): **$200.58B (52.3% of total); change -$4.91B (-2.4%), 44% of total change**  [[F00279] [F00280]]
- FY2023 operating income (FY2023): **$114.30B**  [[F00037]]
- FY2023 operating cash flow (FY2023): **$110.54B**  [[F00224]]
- FY2023 gross margin (FY2023): **44.1%**  [[F01392]]
- FY2023 current ratio (@2023-09-30): **0.99x**  [[F01421]]
- FY2023 inventory growth vs CostOfRevenue (FY2023): **inventory +28% vs CostOfRevenue -4%**  [[F00099] [F00022]]

## Drivers
- Foreign exchange exposure on non-USD sales, cost of sales and operating expenses is the primary FX driver [T00221]
- Gross margin vulnerability from FX on products with foreign components is a secondary FX driver [T00221]
- Credit risk on receivables and supply-agreement prepayments is the primary supply chain credit driver [T00228]
- Geopolitical and natural disruption risk across the full supplier-to-channel partner chain is the primary supply chain operational driver [T00123]
- FY2023 revenue decline of 2.8%: Mac was the LARGEST CONTRIBUTOR TO THE CHANGE by ProductOrService at -$10.82B (-26.9%), 98% of the total change [F00282] [F00283]; iPhone contributed -$4.91B (-2.4%), 44% of the total change [F00279] [F00280]; Services moved AGAINST the total change, +$7.07B (+9.1%), offsetting 64% of it [F00010] [F00011]
- By geography, the US was the largest contributor to the revenue decline at -$9.29B (-6.3%), 84% of the total change [F00877] [F00878], and Americas -$7.10B (-4.2%), 64% of the total change [F00838] [F00839]

## Risks and red flags
- FX exposure on non-U.S. dollar-denominated sales, cost of sales and operating expenses [T00221]
- Gross margins on foreign products and products with foreign-sourced components could be materially adversely affected by FX fluctuations [T00221]
- USD strength relative to local currencies affects financial performance [T00220]
- Credit risk on trade receivables, vendor non-trade receivables and prepayments under long-term supply agreements, heightened in economic downturns [T00228]
- Business interruption from political events, trade disputes, war, terrorism, natural disasters and public health issues affecting suppliers, contract manufacturers, logistics providers and channel partners [T00123]
- FY2023 inventory grew 28% while CostOfRevenue fell 4%, indicating collection/build-up risk [F00099] [F00022]
- Current ratio below 1 in both FY2022 (0.88x) and FY2023 (0.99x) [F01420] [F01421]
- FY2023 operating cash flow fell 9.5% to $110.54B [F00224]

## Data quality
- Text-vs-table conflict: text references '$8.2 billion' for a narrower revenue item while the statement line shows $383.29B; may describe a narrower item, verify before treating as error [F01111] [F00013]
- 4 duplicate facts with conflicting values were set aside during parsing; the primary-statement value was kept

## Outlook
- Actuals: FY2023 revenue declined 2.8% to $383.29B [F00013], led by Mac at -$10.82B (-26.9%), 98% of the total change [F00282] [F00283], partly offset by Services +$7.07B (+9.1%) [F00010] [F00011]; operating income fell 4.3% to $114.30B [F00037], though gross margin improved to 44.1% [F01392] and operating cash flow remained $110.54B [F00224].
- Guidance: not in the retrieved evidence

## Follow-up checks
- Verify the $8.2B text item against the revenue table to confirm it describes a narrower item [F01111]
- Review FX hedging program disclosures and sensitivity analysis for non-USD exposure [T00221]
- Assess Mac's -26.9% decline [F00282] [F00283] for supply constraints vs demand, and whether Services growth [F00010] [F00011] continues to offset product weakness
- Assess inventory turnover trends and whether the 28% inventory build-up is channel-related [F00099] [F00022]
- Check supplier concentration and geographic concentration of contract manufacturers [T00123]
- Confirm whether any forward-looking guidance exists outside the retrieved evidence

## Sources (where each cited number came from)
- **T00221**  - *prose*: paragraph in Item 1A Risk Factors: "The Company’s primary exposure to movements in foreign exchange rates relates to non–U.S. dollar–denominated sales, cost of sales and operating expenses worldwi"
- **T00220**  - *prose*: paragraph in Item 1A Risk Factors: "The Company’s financial performance is subject to risks associated with changes in the value of the U.S. dollar relative to local currencies."
- **T00228**  - *prose*: paragraph in Item 1A Risk Factors: "The Company is exposed to credit risk on its trade accounts receivable, vendor non-trade receivables and prepayments related to long-term supply agreements, and"
- **T00123**  - *prose*: paragraph in Item 1A Risk Factors: "Political events, trade and other international disputes, war, terrorism, natural disasters, public health issues, industrial accidents and other business inter"
- **F00013** $383.29B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total net sales", column "September 30, 2023"
- **F00282** $29.36B Revenues FY2023 [ProductOrService=Mac] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Mac (1)", column "2023"
    - also shown in table #20 "untitled", row "Mac (1)", column "2023"
- **F00283** $40.18B Revenues FY2022 [ProductOrService=Mac] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Mac (1)", column "2022"
    - also shown in table #20 "untitled", row "Mac (1)", column "2022"
- **F00010** $85.20B Revenues FY2023 [ProductOrService=Service] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Services (2)", column "2023"
    - also shown in table #20 "untitled", row "Services (2)", column "2023"
- **F00011** $78.13B Revenues FY2022 [ProductOrService=Service] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Services (2)", column "2022"
    - also shown in table #20 "untitled", row "Services (2)", column "2022"
- **F00279** $200.58B Revenues FY2023 [ProductOrService=IPhone] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "iPhone (1)", column "2023"
    - also shown in table #20 "untitled", row "iPhone (1)", column "2023"
- **F00280** $205.49B Revenues FY2022 [ProductOrService=IPhone] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "iPhone (1)", column "2022"
    - also shown in table #20 "untitled", row "iPhone (1)", column "2022"
- **F00037** $114.30B OperatingIncomeLoss FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Operating income", column "September 30, 2023"
    - also shown in table #47 "untitled", row "Total operating income", column "2023"
- **F00224** $110.54B NetCashProvidedByUsedInOperatingActivities FY2023 - *XBRL*: inline XBRL tag us-gaap:NetCashProvidedByUsedInOperatingActivities
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Cash generated by operating activities", column "September 30, 2023"
- **F01392** 44.1% GrossMarginPct FY2023 - *computed*: GrossProfit / Revenues x 100
    - computed from F00025, F00013
- **F01421** 0.99x CurrentRatio @2023-09-30 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00103, F00125
- **F00099** $6.33B InventoryNet @2023-09-30 - *XBRL*: inline XBRL tag us-gaap:InventoryNet
    - also shown in table #17 "CONSOLIDATED BALANCE SHEETS", row "Inventories", column "September 30, 2023"
- **F00022** $214.14B CostOfRevenue FY2023 - *XBRL*: inline XBRL tag us-gaap:CostOfGoodsAndServicesSold
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total cost of sales", column "September 30, 2023"
- **F00877** $138.57B Revenues FY2023 [StatementGeographical=US] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00878** $147.86B Revenues FY2022 [StatementGeographical=US] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00838** $162.56B Revenues FY2023 [StatementBusinessSegments=AmericasSegment] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Americas", column "2023"
    - also shown in table #46 "Note 13 – Segment Information and Geographic Data", row "Net sales", column "2023"
- **F00839** $169.66B Revenues FY2022 [StatementBusinessSegments=AmericasSegment] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Americas", column "2022"
    - also shown in table #46 "Note 13 – Segment Information and Geographic Data", row "Net sales", column "2022"
- **F01420** 0.88x CurrentRatio @2022-09-24 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00104, F00126
- **F01111** $8.20B Revenues FY2023 - *prose*: sentence in Item 8 Financial Statements: "Total net sales include $ 8.2 billion of revenue recognized in 2023 that was included in deferred revenue as of September 24, 2022, $ 7.5 billion of revenue rec"
