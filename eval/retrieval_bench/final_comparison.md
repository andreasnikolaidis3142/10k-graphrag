| slice | n | hit@10 old -> new | final set old -> new | full context old -> new |
|---|---|---|---|---|
| ALL | 373 | 34% -> 96% | 30% -> 94% | 72% -> 96% |
| company:aapl | 82 | 16% -> 98% | 13% -> 95% | 77% -> 96% |
| company:jpm | 72 | 29% -> 93% | 19% -> 93% | 51% -> 94% |
| company:pfe | 78 | 37% -> 95% | 35% -> 92% | 74% -> 97% |
| company:wmt | 76 | 42% -> 100% | 42% -> 97% | 83% -> 97% |
| company:xom | 65 | 49% -> 95% | 42% -> 94% | 72% -> 95% |
| split:dev | 300 | 33% -> 96% | 29% -> 94% | 72% -> 96% |
| split:holdout | 73 | 40% -> 97% | 34% -> 95% | 73% -> 97% |
| type:numeric | 265 | 21% -> 95% | 17% -> 93% | 72% -> 95% |
| type:segment | 23 | 13% -> 100% | 13% -> 100% | 83% -> 100% |
| type:text | 85 | 81% -> 98% | 73% -> 98% | 69% -> 98% |

Final-set transitions: 243 fixed, 2 lost, 109 kept, 19 still missing
Fixed questions by the document type that now answers them: table-row card 164, XBRL series card 52, paragraph 27

### 20 questions that failed before and are answered now

- **aapl-005** (holdout) How much was spent on research and development in 2023?
  - before: not in the top 10 (top hit: "Depreciation expense on property, plant and equipment was $ 8.5 billion, $ 8.7 billion and $ 9.5 billion durin")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 13 – Segment Information and Geographic Data | in millions || Research and development expense: 2023: ( 29,915 ) (-$29.9 billion); 2022: ( 26,251 ) (-$26.3 billion); 2021: ( 21,914 ) (-$21.9 bill"
- **aapl-006** (dev) What was R&D spending in 2022?
  - before: not in the top 10 (top hit: "The Company issues unsecured short-term promissory notes pursuant to a commercial paper program. The Company u")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Research and Development Expense (us-gaap:ResearchAndDevelopmentExpense): FY2023: 29,915,000,000 dollars ($29.9 billion); FY2022: 26,251,000,000 dollars ($26.3 billion); FY2021: 21,914,"
- **aapl-007** (dev) What were selling, general and administrative costs in 2023?
  - before: not in the top 10 (top hit: "The Company is subject to an increasing number of federal, state and international laws relating to the collec")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Item 6. [Reserved] > Operating Expenses | Operating expenses for 2023, 2022 and 2021 were as follows (dollars in millions): | dollars in millions || Selling, general and administrative: 2023: $24,932 "
- **aapl-010** (holdout) What was income before taxes in 2023?
  - before: not in the top 10 (top hit: "Total net sales include $ 8.2 billion of revenue recognized in 2023 that was included in deferred revenue as o")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "CONSOLIDATED STATEMENTS OF OPERATIONS | Years ended Net sales: | In millions || Operating expenses — Income before provision for income taxes: September 30, 2023: 113,736 ($113.7 billion); September 2"
- **jpm-004** (dev) What was income before taxes in 2023?
  - before: not in the top 10 (top hit: "Net revenue was $19.8 billion, up 12%. Net interest income was $6.3 billion, up 20%. Noninterest revenue was $")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 25 – Income taxes > Results from U.S. and non-U.S. earnings | The following table presents the U.S. and non-U.S. components of income before income tax expense. | in millions || Income before inc"
- **jpm-005** (holdout) What was the income tax charge for 2023?
  - before: not in the top 10 (top hit: "Total income tax expense includes $ 68 million of tax benefits in 2023, $ 331 million of tax benefits in 2022,")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 25 – Income taxes > Effective tax rate and expense | Income tax expense/(benefit) Current income tax expense/(benefit) | in millions || Deferred income tax expense/(benefit) — Total income tax ex"
- **jpm-006** (dev) What was the effective tax rate in 2023?
  - before: not in the top 10 (top hit: "(a) Excludes excise tax and commissions. As part of the Inflation Reduction Act of 2022, a 1% excise tax was i")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 25 – Income taxes > Effective tax rate and expense | Effective tax rate || Increase/(decrease) in tax rate resulting from — Effective tax rate: 2023: 19.6%; 2022: 18.4%; 2021: 18.9%"
- **jpm-007** (dev) What tax rate did the company effectively pay in 2022?
  - before: not in the top 10 (top hit: "(a) Excludes excise tax and commissions. As part of the Inflation Reduction Act of 2022, a 1% excise tax was i")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Effective Income Tax Rate Continuing Operations (us-gaap:EffectiveIncomeTaxRateContinuingOperations): FY2023: 19.6%; FY2022: 18.4%; FY2021: 18.9% | shown in: Effective tax rate and expe"
- **pfe-002** (dev) What was the top line in fiscal 2022?
  - before: not in the top 10 (top hit: "The favorable period-over-period change of $1.1 billion was primarily driven by net gains on equity securities")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 17. Segment, Geographic and Other Revenue Information > Significant Revenues by Product | The following provides detailed revenue information for several of our major products: || TOTAL REVENUES:"
- **pfe-003** (dev) How much did it cost to produce the goods and services sold in 2023?
  - before: not in the top 10 (top hit: "As of December 31, 2023, we had commitments totaling $ 5.2 billion that are legally binding and enforceable. T")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Cost of Goods and Services Sold (us-gaap:CostOfGoodsAndServicesSold): FY2023: 24,954,000,000 dollars ($25.0 billion); FY2022: 34,344,000,000 dollars ($34.3 billion); FY2021: 30,821,000,"
- **pfe-005** (holdout) What was R&D spending in 2022?
  - before: not in the top 10 (top hit: "Revenues from operations outside the U.S. of $31.4 billion accounted for 54% of Total revenues in 2023. Revenu")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Research and Development Expense Excluding Acquired in Process Cost (us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost): FY2023: 10,679,000,000 dollars ($10.7 billion)"
- **pfe-014** (dev) What were diluted earnings per share for 2023?
  - before: not in the top 10 (top hit: "(a) Vested and non-vested shares outstanding, but not paid as of December 31, 2023 were 35.8 million.")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "NEW ACCOUNTING STANDARDS > Pfizer Inc. and Subsidiary Companies | Year Ended December 31, Revenues: | EXCEPT PER SHARE || Earnings per common share––diluted  — Net income attributable to Pfizer Inc. c"
- **wmt-003** (dev) How much did it cost to produce the goods and services sold in 2024?
  - before: not in the top 10 (top hit: "During fiscal 2024, our Walmart International operations generated approximately 18% of our consolidated net s")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "PART II > Consolidated Statements of Income | Fiscal Years Ended January 31, Revenues: | Amounts in millions || Costs and expenses — Cost of sales: 2024: 490,142 ($490.1 billion); 2023: 463,721 ($463."
- **wmt-004** (dev) What were selling, general and administrative costs in 2024?
  - before: not in the top 10 (top hit: "Advertising costs are expensed as incurred, and consist primarily of digital, television and print advertiseme")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Selling General and Administrative Expense (us-gaap:SellingGeneralAndAdministrativeExpense): FY2024: 130,971,000,000 dollars ($131.0 billion); FY2023: 127,140,000,000 dollars ($127.1 bi"
- **wmt-007** (dev) What was income before taxes in 2024?
  - before: not in the top 10 (top hit: "As of January 31, 2024, we have $2.1 billion of syndicated and fronted letters of credit available, of which $")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "PART II > Consolidated Statements of Income | Fiscal Years Ended January 31, Revenues: | Amounts in millions || Interest — Income before income taxes: 2024: 21,848 ($21.8 billion); 2023: 17,016 ($17.0"
- **wmt-008** (dev) What was the income tax charge for 2024?
  - before: not in the top 10 (top hit: "As of January 31, 2024 and 2023, the amount of gross unrecognized tax benefits related to continuing operation")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "Note 9. Taxes | A summary of the provision for income taxes is as follows: | Fiscal Years Ended January 31, Current: | Amounts in millions || Deferred — Total provision for income taxes: 2024: $5,578 "
- **xom-002** (dev) What was the top line in fiscal 2022?
  - before: not in the top 10 (top hit: "Cash provided by operating activities totaled $76.8 billion in 2022, $28.7 billion higher than 2021. The major")
  - now: rank 1 in top 10, in final set at 1, via XBRL series card: "Company total: Revenues (us-gaap:Revenues): FY2023: 344,582,000,000 dollars ($344.6 billion); FY2022: 413,680,000,000 dollars ($413.7 billion); FY2021: 285,640,000,000 dollars ($285.6 billion); change"
- **xom-005** (holdout) What were selling, general and administrative costs in 2023?
  - before: not in the top 10 (top hit: "Crude oil, products, and merchandise inventories are carried at the lower of current market value or cost (gen")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "CONSOLIDATED STATEMENT OF INCOME | Revenues and other income || Costs and other deductions — Selling, general and administrative expenses: 2023: 9,919; 2022: 10,095; 2021: 9,574; 2023 vs 2022: -1.7%"
- **xom-007** (dev) What was income before taxes in 2023?
  - before: not in the top 10 (top hit: "• increases in taxes, duties, or government royalty rates (including retroactive claims or punitive taxes on o")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "CONSOLIDATED STATEMENT OF INCOME | Revenues and other income || Costs and other deductions — Income (loss) before income taxes: 2023: 52,783; 2022: 77,753; 2021: 31,234; 2023 vs 2022: -32.1%"
- **xom-012** (dev) What was the bottom line in 2022?
  - before: not in the top 10 (top hit: "Cash provided by operating activities totaled $76.8 billion in 2022, $28.7 billion higher than 2021. The major")
  - now: rank 1 in top 10, in final set at 1, via table-row card: "FINANCIAL INFORMATION | except where || Net income (loss) attributable to ExxonMobil: 2023: 36,010; 2022: 55,740; 2021: 23,040; 2023 vs 2022: -35.4%"

### Lost (2)

- pfe-030 How large was the balance sheet, i.e. total assets, at the end of 2023?  (old final rank 1; new top: "Note 15. Leases > Pfizer Inc. and Subsidiary Companies | For operating leases, the ROU assets and liabilities ")
- pfe-051 How much new long-term debt was raised in 2023?  (old final rank 3; new top: "Note 7. Financial Instruments > D. Long-Term Debt | The following outlines our senior unsecured long-term debt")
