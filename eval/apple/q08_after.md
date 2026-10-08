# What was Apple's effective tax rate, and why was it below the US statutory rate?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Apple's effective tax rate for FY2023 was 14.7%, down 150 bps from 16.2% in FY2022 and up from 13.3% in FY2021 [F00608][F00609][F00610]. The rate was below the US federal statutory rate primarily because of a lower effective tax rate on foreign earnings, the US federal R&D credit, and tax benefits from share-based compensation, partially offset by state income taxes [T00347]. The FY2023 decline versus FY2022 was driven mainly by a lower effective tax rate on foreign earnings and the impact of US foreign tax credit regulations issued by the Treasury in 2022, partially offset by lower tax benefits from share-based compensation [T00348]. Income tax expense was $16.74B on pre-tax income of $113.74B in FY2023 [F00046][F00043]. The statutory federal rate itself is referenced in the filing's rate-reconciliation table but its numeric value is not in the retrieved evidence [T00345]. Gross unrecognized tax benefits were $19.5B as of September 30, 2023, of which $9.5B would impact the effective rate if recognized [T00527].

**Status:** neutral

## Key numbers
- Effective income tax rate (FY2023): **14.7%**  [F00608]
- Effective income tax rate (FY2022): **16.2%**  [F00609]
- Effective income tax rate (FY2021): **13.3%**  [F00610]
- Effective tax rate change YoY (FY2023 vs FY2022): **-150 bps**  [F00608]
- Income tax expense (FY2023): **$16.74B**  [F00046]
- Pre-tax income (FY2023): **$113.74B**  [F00043]
- Gross unrecognized tax benefits (As of September 30, 2023): **$19.5B ($9.5B would impact ETR)**  [T00527]

## Drivers
- Below-statutory rate in FY2023: lower effective tax rate on foreign earnings, US federal R&D credit, and tax benefits from share-based compensation, partially offset by state income taxes [T00347]
- FY2023 vs FY2022 decline of 150 bps: lower effective tax rate on foreign earnings and impact of 2022 US foreign tax credit regulations, partially offset by lower tax benefits from share-based compensation [T00348][F00608]

## Risks and red flags
- Gross unrecognized tax benefits rose to $19.5B (from $16.8B a year earlier), with $9.5B (vs $8.0B) that would impact the effective tax rate if recognized — a potential future rate volatility source [T00527]
- Reliance on foreign-earnings mix and R&D credits means the rate is sensitive to changes in foreign tax regulations and credit eligibility [T00347][T00348]

## Data quality
- The unrecognized-tax-benefit figures in [T00527] are marked unchecked against the tables; verify against the income tax footnote before use
- The numeric statutory federal income tax rate is referenced in the rate-reconciliation table but is not present in the retrieved evidence [T00345]
- The two derived series show a 1 bp rounding difference for the FY2023 change (-150 bps [F00608] vs -149 bps [F01407]); both round to a ~1.5 pp decline

## Outlook
- Actuals: FY2023 effective tax rate of 14.7% on $113.74B pre-tax income, producing $16.74B of tax expense; the rate fell 150 bps from FY2022's 16.2% [F00608][F00046][F00043]
- Guidance: No forward-looking tax-rate guidance is in the retrieved evidence

## Follow-up checks
- Pull the full statutory-rate reconciliation table (referenced in Item 7 MD&A) to confirm the statutory rate and quantify each reconciling item in dollars [T00345]
- Verify the $19.5B / $9.5B unrecognized tax benefit figures against the income tax footnote, since they are currently unchecked [T00527]
- Track the foreign-earnings mix and any changes to US foreign tax credit regulations, the two named drivers of the FY2023 rate decline [T00348]

## Sources (where each cited number came from)
- **F00608** 14.7% EffectiveIncomeTaxRate FY2023 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #12 "Provision for Income Taxes", row "Effective tax rate", column "2023"
    - also shown in table #34 "untitled", row "Effective tax rate", column "2023"
- **F00609** 16.2% EffectiveIncomeTaxRate FY2022 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #12 "Provision for Income Taxes", row "Effective tax rate", column "2022"
    - also shown in table #34 "untitled", row "Effective tax rate", column "2022"
- **F00610** 13.3% EffectiveIncomeTaxRate FY2021 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #12 "Provision for Income Taxes", row "Effective tax rate", column "2021"
    - also shown in table #34 "untitled", row "Effective tax rate", column "2021"
- **T00347**  - *prose*: paragraph in Item 7 MD&A: "The Company’s effective tax rate for 2023 and 2022 was lower than the statutory federal income tax rate due primarily to a lower effective tax rate on foreign e"
- **T00348**  - *prose*: paragraph in Item 7 MD&A: "The Company’s effective tax rate for 2023 was lower compared to 2022 due primarily to a lower effective tax rate on foreign earnings and the impact of U.S. fore"
- **F00046** $16.74B IncomeTaxExpenseBenefit FY2023 - *XBRL*: inline XBRL tag us-gaap:IncomeTaxExpenseBenefit
    - also shown in table #12 "Provision for Income Taxes", row "Provision for income taxes", column "2023"
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Provision for income taxes", column "September 30, 2023"
    - also shown in table #33 "Provision for Income Taxes and Effective Tax Rate", row "Provision for income taxes", column "2023"
- **F00043** $113.74B IncomeLossBeforeIncomeTaxes FY2023 - *XBRL*: inline XBRL tag us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest
    - also shown in table #15 "CONSOLIDATED STATEMENTS OF OPERATIONS", row "Income before provision for income taxes", column "September 30, 2023"
- **T00345**  - *prose*: paragraph in Item 7 MD&A: "Provision for income taxes, effective tax rate and statutory federal income tax rate for 2023, 2022 and 2021 were as follows (dollars in millions):"
- **T00527**  - *prose*: paragraph in Item 8 Financial Statements: "As of September 30, 2023, the total amount of gross unrecognized tax benefits was $ 19.5 billion, of which $ 9.5 billion, if recognized, would impact the Compan"
- **F01407** 14.7% EffectiveTaxRatePct FY2023 - *computed*: IncomeTax / PreTaxIncome x 100
    - computed from F00046, F00043
