# What happened to earnings per share and the share count, and are buybacks shrinking it?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Diluted EPS rose to $6.13 in FY2023, up 0.3% YoY from $6.11 in FY2022 [F00055], after a stronger 8.9% gain in FY2022 [F00056]. The share count continued to shrink: diluted weighted-average shares fell 3.1% YoY to 15,812,547,000 in FY2023 [F00061], following a 3.2% decline in FY2022 [F00062]. Buybacks did slow materially — repurchases of common stock dropped 13.3% YoY to $77.55B in FY2023 [F00251], down from $89.40B in FY2022 [F00252] and $85.97B in FY2021 [F00253]. Despite the slower buyback pace, the share count still declined, so buybacks continued to shrink the denominator, just at a reduced rate. Dividends kept growing (+1.2% YoY to $15.03B) [F00248], so total shareholder returns fell 11.2% YoY to $92.58B in FY2023 [F01448].

**Status:** positive

## Key numbers
- Diluted EPS (FY2023): **$6.13**  [F00055]
- Diluted EPS growth (FY2023 YoY): **+0.3%**  [F00055]
- Diluted weighted-average shares outstanding (FY2023): **15,812,547,000**  [F00061]
- Diluted share count change (FY2023 YoY): **-3.1%**  [F00061]
- Payments for repurchase of common stock (FY2023): **$77.55B**  [F00251]
- Repurchase change (FY2023 YoY): **-13.3%**  [F00251]
- Payments of dividends (FY2023): **$15.03B**  [F00248]
- Total shareholder returns (FY2023): **$92.58B**  [F01448]

## Drivers
- Share count reduction (buybacks) is the primary driver of EPS growth: diluted shares declined 3.1% in FY2023 [F00061] while EPS rose 0.3% [F00055].
- Buyback pace decelerated: repurchases fell 13.3% YoY in FY2023 to $77.55B [F00251], the largest single drag on total shareholder returns.
- Dividends offset part of the buyback decline, growing 1.2% YoY to $15.03B [F00248], but not enough to prevent total returns from falling 11.2% YoY [F01448].

## Risks and red flags
- Buyback activity is shrinking: repurchases down 13.3% YoY in FY2023 [F00251], and total shareholder returns down 11.2% YoY [F01448], which could slow future EPS accretion.
- EPS growth nearly stalled in FY2023 at +0.3% [F00055], coincides with the buyback slowdown.
- Approximately 24 million RSUs were excluded from diluted EPS in FY2023 as antidilutive [T00460], meaning reported diluted EPS understates potential dilution if those shares were included.

## Data quality
- 9 duplicate facts with conflicting values were set aside during parsing; the primary-statement value was kept.
- 3 accounting identities passed, 0 failed for the numbers above.
- Repurchase figures are XBRL-tagged outflows shown as magnitudes [F00251][F00252][F00253].

## Outlook
- Actuals: EPS growth decelerated sharply to +0.3% in FY2023 [F00055] as buybacks slowed 13.3% [F00251]; share count still declined 3.1% [F00061].
- Guidance: Not in the retrieved evidence — no management guidance facts were provided in this filing extract.

## Follow-up checks
- Verify remaining share repurchase authorization and whether the FY2023 buyback reduction reflects a deliberate pace change or cash allocation shift.
- Check whether the FY2023 share count decline of 3.1% [F00061] is on track to continue in subsequent quarters.
- Confirm whether the 24 million antidilutive RSUs [T00460] could become dilutive in future periods if EPS rises.
- Compare buyback reduction against free cash flow decline of 10.6% YoY to $99.58B [F01389] to assess funding capacity.

## Sources (where each cited number came from)
- **F00055** $6.13 EarningsPerShareDiluted FY2023 - *XBRL*: inline XBRL tag us-gaap:EarningsPerShareDiluted
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Diluted", column "September 30, 2023"
    - also shown in table #21 "Note 3 – Earnings Per Share", row "Diluted earnings per share", column "2023"
- **F00056** $6.11 EarningsPerShareDiluted FY2022 - *XBRL*: inline XBRL tag us-gaap:EarningsPerShareDiluted
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Diluted", column "September 24, 2022"
    - also shown in table #21 "Note 3 – Earnings Per Share", row "Diluted earnings per share", column "2022"
- **F00061** 15,812,547,000 WeightedAverageNumberOfDilutedSharesOutstanding FY2023 - *XBRL*: inline XBRL tag us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Diluted", column "September 30, 2023"
    - also shown in table #21 "Note 3 – Earnings Per Share", row "Weighted-average diluted shares", column "2023"
- **F00062** 16,325,819,000 WeightedAverageNumberOfDilutedSharesOutstanding FY2022 - *XBRL*: inline XBRL tag us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Diluted", column "September 24, 2022"
    - also shown in table #21 "Note 3 – Earnings Per Share", row "Weighted-average diluted shares", column "2022"
- **F00251** $77.55B PaymentsForRepurchaseOfCommonStock FY2023 - *XBRL*: inline XBRL tag us-gaap:PaymentsForRepurchaseOfCommonStock
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Repurchases of common stock", column "September 30, 2023"
- **F00252** $89.40B PaymentsForRepurchaseOfCommonStock FY2022 - *XBRL*: inline XBRL tag us-gaap:PaymentsForRepurchaseOfCommonStock
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Repurchases of common stock", column "September 24, 2022"
- **F00253** $85.97B PaymentsForRepurchaseOfCommonStock FY2021 - *XBRL*: inline XBRL tag us-gaap:PaymentsForRepurchaseOfCommonStock
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Repurchases of common stock", column "September 25, 2021"
- **F00248** $15.03B PaymentsOfDividends FY2023 - *XBRL*: inline XBRL tag us-gaap:PaymentsOfDividends
    - also shown in table #19 "CONSOLIDATED STATEMENTS OF CASH FLOWS", row "Payments for dividends and dividend equivalents", column "September 30, 2023"
- **F01448** $92.58B ShareholderReturns FY2023 - *computed*: Dividends + Repurchases
    - computed from F00248, F00251
- **T00460**  - *prose*: paragraph in Item 8 Financial Statements: "Approximately 24 million restricted stock units (“RSUs”) were excluded from the computation of diluted earnings per share for 2023 because their effect would ha"
- **F01389** $99.58B FreeCashFlow FY2023 - *computed*: CFO - Capex
    - computed from F00224, F00236
