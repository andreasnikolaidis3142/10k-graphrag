# What are Walmart's lease obligations (operating and finance) and how big are they relative to total assets?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's operating lease liability as of January 31, 2024 was $14.43B [F00788], comprising $1.49B current [F00131] and $12.94B noncurrent [F00139]. Finance lease liability was $6.43B [F00789], comprising $725.00M current [F00133] and $5.71B noncurrent [F00141]. Total assets were $252.40B [F00119]. The corresponding right-of-use assets were $13.67B for operating leases [F00111] (5.4% of total assets) and $5.86B for finance leases [F00113] (2.3% of total assets). The evidence does not provide a pre-computed ratio of total lease liabilities to total assets, so the combined lease obligation figure is not stated. Operating lease liability of $14.43B [F00788] exceeds finance lease liability of $6.43B [F00789].

**Status:** neutral

## Key numbers
- Operating lease liability (total) (FY2024 (Jan 31, 2024)): **$14.43B**  [F00788]
- Finance lease liability (total) (FY2024 (Jan 31, 2024)): **$6.43B**  [F00789]
- Total assets (FY2024 (Jan 31, 2024)): **$252.40B**  [F00119]
- Operating lease liability (current) (FY2024 (Jan 31, 2024)): **$1.49B**  [F00131]
- Operating lease liability (noncurrent) (FY2024 (Jan 31, 2024)): **$12.94B**  [F00139]
- Finance lease liability (current) (FY2024 (Jan 31, 2024)): **$725.00M**  [F00133]
- Finance lease liability (noncurrent) (FY2024 (Jan 31, 2024)): **$5.71B**  [F00141]
- Operating lease right-of-use asset (FY2024 (Jan 31, 2024)): **$13.67B**  [F00111]
- Finance lease right-of-use asset (FY2024 (Jan 31, 2024)): **$5.86B**  [F00113]
- PropertyPlantAndEquipmentNet (FY2024 (Jan 31, 2024)): **$110.81B**  [F00109]
- Walmart US assets (FY2024 (Jan 31, 2024)): **$137.78B**  [F00966]

## Drivers
- PropertyPlantAndEquipmentNet was the largest contributor to the change in total assets: $110.81B = 43.9% of total [F00109], change $10.05B (+10.0%), a swing of $10.05B against a NET total change of only $9.20B (other components offset it; no percentage share is meaningful) <- LARGEST CONTRIBUTOR TO THE CHANGE [F00109].
- Walmart US was the largest contributor to the change in total assets by segment: $137.78B = 54.6% of total [F00966], change $7.12B (+5.5%), 77% of the total change <- LARGEST CONTRIBUTOR TO THE CHANGE [F00966].
- Finance lease obligations grew +17.9% YoY noncurrent ($4.84B -> $5.71B) [F00141] and +27.9% YoY current ($567.00M -> $725.00M) [F00133], far outpacing operating leases which were essentially flat (+0.9% noncurrent [F00139], +1.0% current [F00131]).
- Operating lease right-of-use assets grew +0.9% YoY to $13.67B [F00111], while finance lease right-of-use assets grew +19.0% YoY to $5.86B [F00113].

## Risks and red flags
- Finance lease obligations are growing at ~19% YoY (noncurrent +17.9% [F00141], current +27.9% [F00133]), far outpacing operating leases which were essentially flat (+0.9% [F00139], +1.0% [F00131]), which may signal increasing capital-intensive leasing commitments and higher fixed obligations.
- The $34.3B of unrecorded purchase obligations [T00528], of which $14.6B is due within one year, is a separate commitment that should not be conflated with lease obligations but adds to Walmart's overall off-balance-sheet-like commitments.
- Only FY2024 total lease liability figures are provided in the evidence; prior-year totals must be derived from the sum of current and noncurrent components [F00131][F00139][F00133][F00141].

## Data quality
- Only FY2024 total values for OperatingLeaseLiability ($14.43B [F00788]) and FinanceLeaseLiability ($6.43B [F00789]) are provided; FY2023 totals are derived from the sum of current and noncurrent components.
- 2 duplicate facts with conflicting values were set aside during parsing (the primary-statement value was kept).
- The ratio of lease obligations to total assets is not pre-computed in the evidence; only the right-of-use asset percentages of total assets are given (operating 5.4% [F00111], finance 2.3% [F00113]).

## Outlook
- Actuals: Lease obligations are stable for operating leases but growing for finance leases; no indication of deleveraging in the lease portfolio.
- Guidance: Not in the retrieved evidence - no management guidance on lease obligations was provided.

## Follow-up checks
- Obtain the lease maturity schedule from the notes to financial statements to see future minimum lease payments by year for both operating and finance leases.
- Verify whether the finance lease growth relates to specific acquisitions, distribution center build-outs, or real estate transactions.
- Confirm the composition of the $34.3B unrecorded purchase obligations [T00528] to ensure no overlap with lease commitments.

## Sources (where each cited number came from)
- **F00788** $14.43B OperatingLeaseLiability @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:OperatingLeaseLiability
- **F00131** $1.49B OperatingLeaseLiabilityCurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:OperatingLeaseLiabilityCurrent
- **F00139** $12.94B OperatingLeaseLiabilityNoncurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:OperatingLeaseLiabilityNoncurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Long-term operating lease obligations", column "2024"
- **F00789** $6.43B FinanceLeaseLiability @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiability
- **F00133** $725.00M FinanceLeaseLiabilityCurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiabilityCurrent
- **F00141** $5.71B FinanceLeaseLiabilityNoncurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseLiabilityNoncurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Long-term finance lease obligations", column "2024"
- **F00119** $252.40B Assets @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:Assets
    - also shown in table #52 "Consolidated Balance Sheets", row "Total assets", column "2024"
- **F00111** $13.67B OperatingLeaseRightOfUseAsset @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:OperatingLeaseRightOfUseAsset
    - also shown in table #52 "Consolidated Balance Sheets", row "Operating lease right-of-use assets", column "2024"
- **F00113** $5.86B FinanceLeaseRightOfUseAsset @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:FinanceLeaseRightOfUseAsset
    - also shown in table #52 "Consolidated Balance Sheets", row "Finance lease right-of-use assets, net", column "2024"
- **F00109** $110.81B PropertyPlantAndEquipmentNet @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:PropertyPlantAndEquipmentNet
    - also shown in table #52 "Consolidated Balance Sheets", row "Property and equipment, net", column "2024"
    - also shown in table #55 "Property and Equipment", row "Property and equipment, net", column "2024"
- **F00966** $137.78B Assets @2024-01-31 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:Assets
- **T00528**  - *prose*: paragraph in the filing: "As of January 31, 2024, the Company has $34.3 billion of unrecorded purchase obligations outstanding, of which $14.6 billion is due within one year. Purchase ob"
- **F00987** $130.66B Assets @2023-01-31 [StatementBusinessSegments=WalmartUS] (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:Assets
