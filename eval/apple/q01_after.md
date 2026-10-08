# How have gross margin and operating margin changed over the last three years, and what drove the change?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Gross margin expanded over the three-year window, rising from 41.8% in FY2021 [F01390] to 43.3% in FY2022 [F01391] (+153 bps) and 44.1% in FY2023 [F01392] (+82 bps), even as gross profit dollars peaked at $170.78B in FY2022 [F00026] before declining 1.0% to $169.15B in FY2023 [F00025]. Operating margin followed a similar but flatter path, improving from 29.8% in FY2021 [F01393] to 30.3% in FY2022 [F01394] (+51 bps) then retreating to 29.8% in FY2023 [F01395] (-47 bps), returning to the FY2021 level. The gross margin expansion was driven by cost of revenue growing only +5.0% in FY2022 [F00023] versus revenue +7.8% [F00014] and declining -4.2% in FY2023 [F00022] versus revenue -2.8% [F00013], alongside a mix shift toward higher-margin Services. Operating margin compression in FY2023 coincides with operating expenses rising +6.8% to $54.85B [F00034], led by R&D up +14.0% to $29.91B [F00028], while operating income fell -4.3% to $114.30B [F00037].

**Status:** mixed

## Key numbers
- Gross margin % (FY2021): **41.8%**  [F01390]
- Gross margin % (FY2022): **43.3%**  [F01391]
- Gross margin % (FY2023): **44.1%**  [F01392]
- Operating margin % (FY2021): **29.8%**  [F01393]
- Operating margin % (FY2022): **30.3%**  [F01394]
- Operating margin % (FY2023): **29.8%**  [F01395]
- Gross profit (FY2023): **$169.15B**  [F00025]
- Operating income (FY2023): **$114.30B**  [F00037]
- Revenue (FY2023): **$383.29B**  [F00013]
- Cost of revenue (FY2023): **$214.14B**  [F00022]
- Operating expenses (FY2023): **$54.85B**  [F00034]
- R&D expense (FY2023): **$29.91B**  [F00028]
- SG&A expense (FY2023): **$24.93B**  [F00031]
- Products gross profit (FY2023): **$108.80B**  [F01002]
- Services gross profit (FY2023): **$60.34B**  [F01005]

## Drivers
- FY2022 gross margin +153 bps: cost of revenue +5.0% [F00023] grew slower than revenue +7.8% [F00014]
- FY2023 gross margin +82 bps: cost of revenue -4.2% [F00022] declined faster than revenue -2.8% [F00013], plus mix shift toward Services (+7.7% [F01005]) offsetting Products (-5.2% [F01003])
- FY2022 operating margin +51 bps: operating income +9.6% [F00038] grew faster than revenue +7.8% [F00014]
- FY2023 operating margin -47 bps: operating expenses +6.8% [F00034] outpaced revenue decline, with R&D +14.0% [F00028] the largest contributor to the $3.50B expense increase
- FY2023 gross profit -$1.63B net change: Products -$5.92B [F01003] was the largest contributor, partially offset by Services +$4.29B [F01006]

## Risks and red flags
- Operating margin declined -47 bps in FY2023 [F01395], erasing the entire FY2022 improvement of +51 bps [F01394]
- R&D expense grew +14.0% [F00028] while revenue declined -2.8% [F00013], indicating rising cost base amid top-line weakness
- Products gross profit fell -5.2% [F01003] in FY2023, the largest contributor to the gross profit decline
- Foreign currency weakness relative to the U.S. dollar is cited as a recurring headwind to both Products and Services margins [T00330][T00331][T00333][T00334]
- Operating income declined -4.3% [F00037] in FY2023, the first annual decline in the three-year window

## Data quality
- 4 duplicate facts with conflicting values were set aside during parsing; the primary-statement value was kept
- Same pattern for Services: T00333 reports gross margin increased while T00334 reports gross margin percentage decreased, consistent with dollars vs ratio distinction
- No forward-looking guidance facts present in the retrieved evidence

## Outlook
- Actuals: Margins peaked in FY2022 (gross 43.3% [F01391], operating 30.3% [F01394]) and FY2023 shows compression in operating margin (-47 bps [F01395]) despite continued gross margin expansion (+82 bps [F01392]), as operating expense growth outpaced revenue
- Guidance: not in the retrieved evidence - no management guidance facts were present in the filing evidence provided

## Follow-up checks
- Confirm whether FY2024 or FY2025 guidance exists in subsequent filings or earnings releases
- Analyze segment-level gross margin percentage trends for Products vs Services to isolate mix effects
- Quantify the foreign currency impact magnitude on gross margin from the MD&A
- Assess R&D productivity given +14.0% expense growth [F00028] against -2.8% revenue decline [F00013]
- Verify whether the FY2023 operating margin decline is one-off (currency, mix) or structural (cost base)

## Sources (where each cited number came from)
- **F01390** 41.8% GrossMarginPct FY2021 - *computed*: GrossProfit / Revenues x 100
    - computed from F00027, F00015
- **F01391** 43.3% GrossMarginPct FY2022 - *computed*: GrossProfit / Revenues x 100
    - computed from F00026, F00014
- **F01392** 44.1% GrossMarginPct FY2023 - *computed*: GrossProfit / Revenues x 100
    - computed from F00025, F00013
- **F00026** $170.78B GrossProfit FY2022 - *XBRL*: inline XBRL tag us-gaap:GrossProfit
    - also shown in table #9 "Gross Margin", row "Total gross margin", column "2022"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Gross margin", column "September 24, 2022"
- **F00025** $169.15B GrossProfit FY2023 - *XBRL*: inline XBRL tag us-gaap:GrossProfit
    - also shown in table #9 "Gross Margin", row "Total gross margin", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Gross margin", column "September 30, 2023"
- **F01393** 29.8% OperatingMarginPct FY2021 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00039, F00015
- **F01394** 30.3% OperatingMarginPct FY2022 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00038, F00014
- **F01395** 29.8% OperatingMarginPct FY2023 - *computed*: OperatingIncome / Revenues x 100
    - computed from F00037, F00013
- **F00023** $223.55B CostOfRevenue FY2022 - *XBRL*: inline XBRL tag us-gaap:CostOfGoodsAndServicesSold
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total cost of sales", column "September 24, 2022"
- **F00014** $394.33B Revenues FY2022 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2022"
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2022"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total net sales", column "September 24, 2022"
- **F00022** $214.14B CostOfRevenue FY2023 - *XBRL*: inline XBRL tag us-gaap:CostOfGoodsAndServicesSold
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total cost of sales", column "September 30, 2023"
- **F00013** $383.29B Revenues FY2023 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #7 "The following table shows net sales by reportable segment for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #8 "The following table shows net sales by category for 2023, 2022 and 2021 (dollars in millions):", row "Total net sales", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total net sales", column "September 30, 2023"
- **F00034** $54.85B OperatingExpenses FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingExpenses
    - also shown in table #11 "Operating expenses for 2023, 2022 and 2021 were as follows (dollars in millions):", row "Total operating expenses", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Total operating expenses", column "September 30, 2023"
- **F00028** $29.91B ResearchAndDevelopmentExpense FY2023 - *XBRL*: inline XBRL tag us-gaap:ResearchAndDevelopmentExpense
    - also shown in table #11 "Operating expenses for 2023, 2022 and 2021 were as follows (dollars in millions):", row "Research and development", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Research and development", column "September 30, 2023"
    - also shown in table #47 "untitled", row "Research and development expense", column "2023"
- **F00037** $114.30B OperatingIncomeLoss FY2023 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Operating income", column "September 30, 2023"
    - also shown in table #47 "untitled", row "Total operating income", column "2023"
- **F00031** $24.93B SellingGeneralAndAdministrativeExpense FY2023 - *XBRL*: inline XBRL tag us-gaap:SellingGeneralAndAdministrativeExpense
    - also shown in table #11 "Operating expenses for 2023, 2022 and 2021 were as follows (dollars in millions):", row "Selling, general and administrative", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Selling, general and administrative", column "September 30, 2023"
- **F01002** $108.80B custom:products FY2023 - *table*: table #9 "Gross Margin", row "Products", column "2023"
- **F01005** $60.34B custom:services FY2023 - *table*: table #9 "Gross Margin", row "Services", column "2023"
- **F01003** $114.73B custom:products FY2022 - *table*: table #9 "Gross Margin", row "Products", column "2022"
- **F00038** $119.44B OperatingIncomeLoss FY2022 - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Operating income", column "September 24, 2022"
    - also shown in table #47 "untitled", row "Total operating income", column "2022"
- **F01006** $56.05B custom:services FY2022 - *table*: table #9 "Gross Margin", row "Services", column "2022"
- **T00330**  - *prose*: paragraph in Item 7 MD&A: "Products gross margin decreased during 2023 compared to 2022 due to the weakness in foreign currencies relative to the U.S. dollar and lower Products volume, pa"
- **T00331**  - *prose*: paragraph in Item 7 MD&A: "Products gross margin percentage increased during 2023 compared to 2022 due to cost savings and a different Products mix, partially offset by the weakness in fo"
- **T00333**  - *prose*: paragraph in Item 7 MD&A: "Services gross margin increased during 2023 compared to 2022 due primarily to higher Services net sales, partially offset by the weakness in foreign currencies "
- **T00334**  - *prose*: paragraph in Item 7 MD&A: "Services gross margin percentage decreased during 2023 compared to 2022 due to higher Services costs and the weakness in foreign currencies relative to the U.S."
