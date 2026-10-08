# What happened to e-commerce, membership and other income, and how does it compare with net sales growth?

*model: inclusionai/ling-3.1-flash | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's e-commerce sales accelerated sharply in FY2024: Walmart U.S. e-commerce rose 22.5% YoY to $65.40B [F01049], Walmart International e-commerce rose 22.2% to $24.80B [F01067], and Sam's Club e-commerce rose 17.9% to $9.90B [F01085], each well above net sales growth of 6.1% to $642.64B [F00003]. Each e-commerce slice shows an FY2024 inflection, spiking 28-29% versus the prior two-period average [F01049][F01067][F01085]. In contrast, membership and other income (us-gaap:OtherIncome) decelerated to +1.5% YoY at $5.49B in FY2024 [F00006], down from +8.3% in FY2023 [F00007], lagging net sales growth. Total revenues rose 6.0% to $648.12B in FY2024 [F00009], with management attributing the net sales increase primarily to positive comparable sales at Walmart U.S. and Sam's Club, driven by growth in transactions [T00454]. Walmart U.S. e-commerce is the largest of the three disclosed e-commerce slices at $65.40B [F01049].

**Status:** mixed

## Key numbers
- E-commerce revenues - Walmart U.S. (FY2024): **$65.40B, +22.5% YoY**  [F01049]
- E-commerce revenues - Walmart International (FY2024): **$24.80B, +22.2% YoY**  [F01067]
- E-commerce revenues - Sam's Club (FY2024): **$9.90B, +17.9% YoY**  [F01085]
- Membership and other income (us-gaap:OtherIncome) (FY2024): **$5.49B, +1.5% YoY**  [F00006]
- Net sales (RevenueFromContractWithCustomerExcludingAssessedTax) (FY2024): **$642.64B, +6.1% YoY**  [F00003]
- Total revenues (us-gaap:Revenues) (FY2024): **$648.12B, +6.0% YoY**  [F00009]
- E-commerce CAGR FY2022-FY2024 - Walmart U.S. (FY2022-FY2024): **17.0%**  [F01049]
- E-commerce CAGR FY2022-FY2024 - Walmart International (FY2022-FY2024): **15.8%**  [F01067]
- E-commerce CAGR FY2022-FY2024 - Sam's Club (FY2022-FY2024): **19.8%**  [F01085]
- Net sales CAGR FY2022-FY2024 (FY2022-FY2024): **6.4%**  [F00003]

## Drivers
- E-commerce was the standout growth driver in FY2024, with all three disclosed slices growing at 17.9%-22.5% YoY [F01049][F01067][F01085] versus net sales growth of 6.1% [F00003]; each slice shows an FY2024 inflection spike of 28-29% vs the prior-2-period average [F01049][F01067][F01085].
- Walmart U.S. e-commerce is the largest disclosed e-commerce component at $65.40B in FY2024 [F01049], followed by Walmart International at $24.80B [F01067] and Sam's Club at $9.90B [F01085]; these are MAJORCUSTOMERS slices, components of the consolidated total, not company totals.
- Management states the FY2024 net sales increase was primarily due to positive comparable sales for the Walmart U.S. and Sam's Club segments, driven by growth in transactions [T00454].
- Membership and other income moved against the e-commerce momentum: growth decelerated to +1.5% in FY2024 [F00006] from +8.3% in FY2023 [F00007], a stable/weak trend of +10% over the FY2022-FY2024 window [F00006], below the 6.1% net sales growth [F00003].

## Risks and red flags
- Security-related events could materially adversely affect reputation and harm Walmart's competitive position particularly with respect to its eCommerce operations [T00252].
- Failure to meet or delay in meeting market expectations, including eCommerce growth rates and advertising and other higher-margin initiatives, could cause the market price of Walmart's stock to decline [T00269].
- Risk factors cite the amount, number, growth or decrease in measures including eCommerce sales as items that could affect results [T00058].

## Data quality
- 0 accounting identities passed and 0 failed for the numbers above; 10 duplicate facts with conflicting values were set aside during parsing, with the primary-statement value kept.
- The e-commerce figures are MAJORCUSTOMERS statement-segment slices (components of the consolidated total), not the company total; they should not be summed or treated as standalone company results.
- The membership and other income series is XBRL-tagged us-gaap:OtherIncome; narrative [T00454] refers to 'membership and other income' as a component of total revenues alongside net sales.
- Narrative [T00454] dollar figures ($36.8B / 6.0% / 6.1% / $38.5B / 6.7% / $38.1B) are marked 'unchecked' in the machine-check status, so they are unverified against the tables even though the XBRL-tagged series corroborate the 6.0% and 6.1% growth rates [F00009][F00003].

## Outlook
- Actuals: FY2024 actuals show e-commerce growing 17.9%-22.5% across the three segments [F01049][F01067][F01085], above the 6.1% net sales growth [F00003], while membership and other income slowed to +1.5% [F00006].
- Guidance: No numeric guidance is in the retrieved evidence; management's forward-looking statement is that advertising and other higher-margin initiatives are expected to help drive operating income growth at a rate faster than net sales over the long term [T00269] - this is management expectation, not an actual.

## Follow-up checks
- Verify what drove the membership and other income deceleration to +1.5% in FY2024 [F00006] - e.g., membership fee income vs other components - since the filing text does not break it down in the retrieved evidence.
- Confirm e-commerce penetration as a percentage of net sales; the evidence provides e-commerce dollars [F01049][F01067][F01085] and net sales [F00003] but no disclosed penetration ratio.
- Check whether the e-commerce acceleration coincided with margin expansion or dilution, using segment operating income not present in the retrieved evidence.
- Reconcile the 10 duplicate facts with conflicting values that were set aside during parsing to confirm the primary-statement values were correctly retained.
- Obtain the full text of [T00454] (truncated) to confirm the transaction-growth driver detail and the unchecked narrative figures.

## Sources (where each cited number came from)
- **F01049** $65.40B Revenues FY2024 [MajorCustomers=ECommerce, StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F01067** $24.80B Revenues FY2024 [MajorCustomers=ECommerce, StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F01085** $9.90B Revenues FY2024 [MajorCustomers=ECommerce, StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00003** $642.64B Revenues FY2024 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #27 "untitled", row "Net sales", column "2024"
    - also shown in table #32 "Consolidated Results of Operations", row "Net sales", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Net sales", column "2024"
- **F00006** $5.49B OtherIncome FY2024 - *XBRL*: inline XBRL tag us-gaap:OtherIncome
    - also shown in table #50 "Consolidated Statements of Income", row "Membership and other income", column "2024"
- **F00007** $5.41B OtherIncome FY2023 - *XBRL*: inline XBRL tag us-gaap:OtherIncome
    - also shown in table #50 "Consolidated Statements of Income", row "Membership and other income", column "2023"
- **F00009** $648.12B Revenues FY2024 - *XBRL*: inline XBRL tag us-gaap:Revenues
    - also shown in table #32 "Consolidated Results of Operations", row "Total revenues", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Total revenues", column "2024"
    - also shown in table #86 "untitled", row "Total revenues", column "2024"
- **T00454**  - *prose*: paragraph in the filing: "Our total revenues, which includes net sales and membership and other income, increased $36.8 billion or 6.0% and $38.5 billion or 6.7% for fiscal 2024 and 2023"
- **T00252**  - *prose*: paragraph in the filing: "Our reputation with our customers and members is important to the success of our enterprise strategy, which combines traditional retail, membership models, mark"
- **T00269**  - *prose*: paragraph in the filing: "We believe that the price of our stock generally reflects high market expectations for our future operating results. Any failure to meet or delay in meeting the"
- **T00058**  - *prose*: paragraph in the filing: "• the amount, number, growth, increase, reduction or decrease in or over certain periods, of or in certain financial items or measures or operating measures, in"
