# How much operating cash flow and free cash flow did Walmart generate, what did it spend on capex, and how much went to dividends and buybacks?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart generated $35.73B of operating cash flow in FY2024, up 23.9% YoY from $28.84B in FY2023 [F00317], and $15.12B of free cash flow, up 26.2% YoY from $11.98B [F01262]. Free cash flow is defined by management as operating cash flow minus payments for property and equipment [T00443], which reconciles: $35.73B - $20.61B capex = $15.12B. Capex rose 22.2% YoY to $20.61B [F00320], the largest cash outflow. Shareholder returns totaled $8.92B in FY2024, down 44.4% YoY [F01892], driven by buybacks falling 72.0% to $2.78B [F00353] while dividends held stable at $6.14B [F00350]. The payout of FCF to shareholders fell to 59.0% in FY2024 from 133.8% in FY2023 [F01895].

**Status:** positive

## Key numbers
- Operating cash flow (FY2024) (FY2024): **$35.73B**  [F00317]
- Free cash flow (FY2024) (FY2024): **$15.12B**  [F01262]
- Capex (FY2024) (FY2024): **$20.61B**  [F00320]
- Dividends (FY2024) (FY2024): **$6.14B**  [F00350]
- Buybacks (FY2024) (FY2024): **$2.78B**  [F00353]
- Total shareholder returns (FY2024) (FY2024): **$8.92B**  [F01892]
- Shareholder returns as % of FCF (FY2024) (FY2024): **59.0%**  [F01895]

## Drivers
- Free cash flow growth of +26.2% YoY was driven by operating cash flow growth of +23.9% [F00317] outpacing capex growth of +22.2% [F00320].
- The 44.4% YoY decline in total shareholder returns [F01892] was driven by buybacks falling 72.0% YoY to $2.78B [F00353], while dividends were stable at +0.4% [F00350].
- Capex increased strongly, +57% over the FY2022-FY2024 window [F00320], reflecting continued investment in stores and supply chain.

## Risks and red flags
- Buybacks dropped 72.0% YoY in FY2024 ($9.92B -> $2.78B) [F00353], a strong decreasing trend (-46.7% CAGR FY2022-FY2024).
- Shareholder returns as a percentage of FCF fell sharply from 133.8% in FY2023 to 59.0% in FY2024 (-7481 bps) [F01895], indicating a material shift in capital allocation.
- Capex is rising strongly (+22.2% YoY in FY2024) [F00320], which pressures free cash flow if operating cash flow growth slows.
- Free cash flow is a non-GAAP measure that does not deduct debt service, business acquisitions, or other contractual obligations [T00444].

## Data quality
- 5 accounting identities passed, 0 failed for the numbers above.
- 1 duplicate fact with conflicting values was set aside during parsing (the primary-statement value was kept).
- Dividend figures are XBRL-tagged outflows shown as magnitudes [F00350-F00352].

## Outlook
- Actuals: Positive: operating cash flow and free cash flow both grew strongly in FY2024, with FCF up 26.2% YoY to $15.12B [F01262] and CFO up 23.9% YoY to $35.73B [F00317].
- Guidance: No forward-looking management guidance on cash flow, capex, dividends, or buybacks is present in the retrieved evidence; all FY#### values are actuals.

## Follow-up checks
- Verify whether the 72% buyback reduction is a one-time timing effect or a strategic shift in capital allocation.
- Check the Liquidity and Capital Resources section for capex attribution by segment or business type.
- Confirm whether any business acquisitions or debt service payments are excluded from the FCF definition [T00444].
- Compare Walmart's FCF definition against peer companies, as management notes methods may differ [T00445].

## Sources (where each cited number came from)
- **F00317** $35.73B NetCashProvidedByUsedInOperatingActivities FY2024 - *XBRL*: inline XBRL tag us-gaap:NetCashProvidedByUsedInOperatingActivities
    - also shown in table #31 "Free Cash Flow", row "Net cash provided by operating activities", column "2024"
    - also shown in table #36 "Net Cash Provided by Operating Activities", row "Net cash provided by operating activities", column "2024"
    - also shown in table #54 "Consolidated Statements of Cash Flows", row "Net cash provided by operating activities", column "2024"
- **F01262** $15.12B FreeCashFlow FY2024 - *table*: table #31 "Free Cash Flow", row "Free cash flow", column "2024"
- **T00443**  - *prose*: paragraph in the filing: "We define free cash flow as net cash provided by operating activities in a period minus payments for property and equipment made in that period. We had net cash"
- **F00320** $20.61B PaymentsToAcquirePropertyPlantAndEquipment FY2024 - *XBRL*: inline XBRL tag us-gaap:PaymentsToAcquirePropertyPlantAndEquipment
    - also shown in table #30 "Strategic Capital Allocation", row "Total capital expenditures", column "2024"
- **F01892** $8.92B ShareholderReturns FY2024 - *computed*: Dividends + Repurchases
    - computed from F00350, F00353
- **F00353** $2.78B PaymentsForRepurchaseOfCommonStock FY2024 - *XBRL*: inline XBRL tag us-gaap:PaymentsForRepurchaseOfCommonStock
- **F00350** $6.14B PaymentsOfDividends FY2024 - *XBRL*: inline XBRL tag us-gaap:PaymentsOfDividendsCommonStock
    - also shown in table #54 "Consolidated Statements of Cash Flows", row "Dividends paid", column "2024"
- **F01895** 59.0% PayoutOfFcfPct FY2024 - *computed*: Returns / FCF x 100
    - computed from F01892, F01262
- **T00444**  - *prose*: paragraph in the filing: "Walmart's definition of free cash flow is limited in that it does not represent residual cash flows available for discretionary expenditures due to the fact tha"
- **F00352** $6.15B PaymentsOfDividends FY2022 - *XBRL*: inline XBRL tag us-gaap:PaymentsOfDividendsCommonStock
    - also shown in table #54 "Consolidated Statements of Cash Flows", row "Dividends paid", column "2022"
- **T00445**  - *prose*: paragraph in the filing: "Although other companies report their free cash flow, numerous methods may exist for calculating a company's free cash flow. As a result, the method used by man"
