# What is Walmart's total debt (short and long term, including finance leases) and its net debt or net cash, and how are interest expense and interest coverage trending?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's total debt was $40.46B as of January 31, 2024, up 3.2% from $39.21B a year earlier [F01863][F01862]. Net debt was $30.59B at both FY2023 and FY2024, meaning the company carries net debt (not net cash) and it remained flat YoY [F01864][F01865]. Interest expense rose sharply to $2.26B in FY2024, up 26.4% YoY from $1.79B [F00021][F00022], following a 6.8% increase in FY2023 [F00022]. Interest coverage declined from 15.50x in FY2022 to 11.43x in FY2023 (-26.2%), then improved modestly to 11.96x in FY2024 (+4.6%) [F01870][F01871][F01872]. Debt-to-equity improved to 0.48x from 0.51x [F01866][F01867], while finance lease liabilities grew 17.9-27.9% YoY to $6.43B total [F00789][F00141][F00133].

**Status:** mixed

## Key numbers
- Total debt (@2024-01-31): **$40.46B**  [[F01863]]
- Total debt (@2023-01-31): **$39.21B**  [[F01862]]
- Net debt (@2024-01-31): **$30.59B**  [[F01865]]
- Interest expense (FY2024): **$2.26B**  [[F00021]]
- Interest expense (FY2023): **$1.79B**  [[F00022]]
- Interest coverage (FY2024): **11.96x**  [[F01872]]
- Interest coverage (FY2022): **15.50x**  [[F01870]]
- Finance lease liability (@2024-01-31): **$6.43B**  [[F00789]]
- Debt-to-equity (@2024-01-31): **0.48x**  [[F01867]]

## Drivers
- Interest expense growth of 26.4% in FY2024, with short-term borrowings' weighted-average interest rate rising from 6.6% to 7.7% [T00510]
- Net debt flat at $30.59B as total debt growth was offset by cash and investments [F01865]
- Interest coverage improved +4.6% in FY2024 after a -26.2% decline in FY2023 [F01872][F01871]
- Debt-to-equity improved -5.6% YoY to 0.48x as equity grew faster than debt [F01867]

## Risks and red flags
- Interest expense spiked 26.4% YoY in FY2024 to $2.26B, a 31% inflection vs the prior-2-period average [F00021]
- Interest coverage down 23% over the FY2022-FY2024 window, from 15.50x to 11.96x [F01870][F01872]
- Finance lease liabilities growing 17.9-27.9% YoY, with noncurrent rising from $4.84B to $5.71B [F00141][F00133]
- Short-term borrowings doubled from $0.4B to $0.9B, with the weighted-average rate climbing from 6.6% to 7.7% [T00510]

## Data quality
- Net debt is positive $30.59B, so it represents net debt rather than net cash [F01865]
- 0 accounting identities passed or failed for the numbers above

## Outlook
- Actuals: Debt and net debt are stable while interest expense is rising sharply, compressing coverage; leverage ratio (debt-to-equity) improved modestly
- Guidance: not in the retrieved evidence

## Follow-up checks
- Verify the composition of total debt (commercial paper, long-term debt, short-term borrowings) and whether finance leases are included in the $40.46B figure
- Check cash, short-term investments and non-current marketable securities balances to understand the net debt derivation
- Confirm whether the FY2024 interest expense increase is driven by higher rates versus increased borrowing volume
- Review undrawn committed credit lines of $15.0B for liquidity coverage [T00510]

## Sources (where each cited number came from)
- **F01863** $40.46B TotalDebt @2024-01-31 - *computed*: LT debt + current debt + short-term borrowings + commercial paper
    - computed from F00137, F00129, F00121
- **F01862** $39.21B TotalDebt @2023-01-31 - *computed*: LT debt + current debt + short-term borrowings + commercial paper
    - computed from F00138, F00130, F00122
- **F01864** $30.59B NetDebt @2023-01-31 - *computed*: TotalDebt - Cash - ShortTermInvestments - NonCurrentMarketableSecurities
    - computed from F01862, F00100
- **F01865** $30.59B NetDebt @2024-01-31 - *computed*: TotalDebt - Cash - ShortTermInvestments - NonCurrentMarketableSecurities
    - computed from F01863, F00099
- **F00021** $2.26B InterestExpense FY2024 - *XBRL*: inline XBRL tag us-gaap:InterestExpenseDebt
    - also shown in table #50 "Consolidated Statements of Income", row "Debt", column "2024"
- **F00022** $1.79B InterestExpense FY2023 - *XBRL*: inline XBRL tag us-gaap:InterestExpenseDebt
    - also shown in table #50 "Consolidated Statements of Income", row "Debt", column "2023"
- **F01870** 15.50x InterestCoverage FY2022 - *computed*: OperatingIncome / InterestExpense
    - computed from F00020, F00023
- **F01871** 11.43x InterestCoverage FY2023 - *computed*: OperatingIncome / InterestExpense
    - computed from F00019, F00022
- **F01872** 11.96x InterestCoverage FY2024 - *computed*: OperatingIncome / InterestExpense
    - computed from F00018, F00021
- **F01866** 0.51x DebtToEquity @2023-01-31 - *computed*: TotalDebt / Equity
    - computed from F01862, F00156
- **F01867** 0.48x DebtToEquity @2024-01-31 - *computed*: TotalDebt / Equity
    - computed from F01863, F00155
- **F00789** $6.43B FinanceLeaseLiability @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiability
- **F00141** $5.71B FinanceLeaseLiabilityNoncurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiabilityNoncurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Long-term finance lease obligations", column "2024"
- **F00133** $725.00M FinanceLeaseLiabilityCurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiabilityCurrent
- **T00510**  - *prose*: paragraph in the filing: "Short-term borrowings as of January 31, 2024 and 2023 were $0.9 billion and $0.4 billion, respectively, with weighted-average interest rates of 7.7% and 6.6%, r"
