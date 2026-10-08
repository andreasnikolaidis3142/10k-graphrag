# What was the effective tax rate, and what drove the difference from the U.S. statutory rate?

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's effective income tax rate on continuing operations was 25.5% in FY2024 [F00872], above the 21.0% U.S. federal statutory rate [F00845]. The rate spiked to 33.6% in FY2023 [F00873] before returning to 25.4% in FY2022 [F00874]. Management attributes the FY2023 spike primarily to the tax impact of the business reorganization resulting in the full separation of PhonePe from Flipkart [T00460]. Income tax expense was $5.58B in FY2024 [F00042] on pre-tax income of $21.85B [F00039].

**Status:** neutral

## Key numbers
- Effective income tax rate FY2024 (FY2024): **25.5%**  [F00872]
- U.S. federal statutory tax rate FY2024 (FY2024): **21.0%**  [F00845]
- Effective income tax rate FY2023 (FY2023): **33.6%**  [F00873]
- Effective income tax rate FY2022 (FY2022): **25.4%**  [F00874]
- Income tax expense FY2024 (FY2024): **$5.58B**  [F00042]
- Income before income taxes FY2024 (FY2024): **$21.85B**  [F00039]

## Drivers
- Total deferred tax expense (benefit) swung from $430.00M in FY2023 [F00843] to -$171.00M in FY2024 [F00842], a change of -$601.00M, the largest contributor to the total change in IncomeTaxExpenseBenefit of -$146.00M [F00043]; other components offset it so no percentage share is meaningful.
- Total current tax provision increased by $455.00M to $5.75B [F00830], offsetting the deferred tax swing against the net total change of -$146.00M [F00043].
- State and local income taxes added +3.0% to the FY2024 effective rate versus the 21.0% statutory rate [F00848], the largest positive reconciliation component.
- Tax credits contributed +1.5% [F00863] and other adjustments contributed +1.5% [F00869] to the FY2024 rate.
- Change in deferred tax assets valuation allowance added +1.2% [F00857] in FY2024, down from +1.7% in FY2023 [F00858].
- Foreign income tax rate differential was +0.1% in FY2024 [F00851], down from +1.1% in FY2023 [F00852].
- The FY2023 rate spike to 33.6% (vs 21.0% statutory) was primarily driven by the tax impact of the PhonePe/Flipkart separation [T00460]; coinciding with the foreign differential sign flip from -1.5% to +1.1% [F00852] and other adjustments sign flip from -0.6% to +1.8% [F00870].

## Risks and red flags
- Management flags that the effective tax rate may fluctuate due to changes in assessment of unrecognized tax benefits, valuation allowances, changes in tax law, outcomes of administrative audits, and discrete items [T00460].
- Realization of certain net deferred tax assets and effects of resolutions of tax-related matters could affect the effective tax rate for certain periods [T00067].
- FY2023 valuation allowance was unusually high at 4.4% [F00859] before normalizing to 1.7% [F00858] and 1.2% [F00857].

## Data quality
- 3 accounting identities passed, 0 failed for the numbers above.
- Narrative fact [T00460] has unchecked number checks; the effective rate figures it cites (25.5%, 33.6%, 25.4%) match the XBRL-tagged series [F00872][F00873][F00874].

## Outlook
- Actuals: FY2024 effective tax rate of 25.5% [F00872] represents a normalization from the FY2023 reorganization-driven spike of 33.6% [F00873], with the valuation allowance and foreign differential both declining [F00857][F00851].
- Guidance: Management cautions the effective tax rate may fluctuate due to unrecognized tax benefits, valuation allowances, tax law changes, audit outcomes, and discrete items [T00460]; no specific forward-looking rate guidance is provided in the retrieved evidence.

## Follow-up checks
- Verify the specific tax impact amount of the PhonePe/Flipkart separation in the FY2023 reconciliation table.
- Review the composition of 'other adjustments' (+1.5% in FY2024 [F00869]) for discrete items.
- Assess the sustainability of the +3.0% state and local tax contribution [F00848] versus prior years.

## Sources (where each cited number came from)
- **F00872** 25.5% EffectiveIncomeTaxRate FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Effective income tax rate", column "2024"
- **F00845** 21.0% EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "U.S. statutory tax rate", column "2024"
- **F00873** 33.6% EffectiveIncomeTaxRate FY2023 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Effective income tax rate", column "2023"
- **F00874** 25.4% EffectiveIncomeTaxRate FY2022 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateContinuingOperations
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Effective income tax rate", column "2022"
- **T00460**  - *prose*: paragraph in the filing: "Our effective income tax rate was 25.5%, 33.6%, and 25.4% for fiscal 2024, 2023 and 2022, respectively. The higher effective tax rate in fiscal 2023 as compared"
- **F00042** $5.58B IncomeTaxExpenseBenefit FY2024 - *XBRL*: inline XBRL tag us-gaap:IncomeTaxExpenseBenefit
    - also shown in table #50 "Consolidated Statements of Income", row "Provision for income taxes", column "2024"
    - also shown in table #79 "A summary of the provision for income taxes is as follows:", row "Total provision for income taxes", column "2024"
- **F00039** $21.85B IncomeLossBeforeIncomeTaxes FY2024 - *XBRL*: inline XBRL tag us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest
    - also shown in table #50 "Consolidated Statements of Income", row "Income before income taxes", column "2024"
    - also shown in table #78 "The components of income before income taxes are as follows:", row "Total income before income taxes", column "2024"
    - also shown in table #85 "Segments", row "Income before income taxes", column "Fiscal Year Ended January 31, 2024"
- **F00843** $430.00M DeferredIncomeTaxExpenseBenefit FY2023 - *XBRL*: inline XBRL tag us-gaap:DeferredIncomeTaxExpenseBenefit
- **F00842** -$171.00M DeferredIncomeTaxExpenseBenefit FY2024 - *XBRL*: inline XBRL tag us-gaap:DeferredIncomeTaxExpenseBenefit
    - also shown in table #79 "A summary of the provision for income taxes is as follows:", row "Total deferred tax expense (benefit)", column "2024"
- **F00043** $5.72B IncomeTaxExpenseBenefit FY2023 - *XBRL*: inline XBRL tag us-gaap:IncomeTaxExpenseBenefit
    - also shown in table #50 "Consolidated Statements of Income", row "Provision for income taxes", column "2023"
    - also shown in table #79 "A summary of the provision for income taxes is as follows:", row "Total provision for income taxes", column "2023"
- **F00830** $5.75B CurrentIncomeTaxExpenseBenefit FY2024 - *XBRL*: inline XBRL tag us-gaap:CurrentIncomeTaxExpenseBenefit
    - also shown in table #79 "A summary of the provision for income taxes is as follows:", row "Total current tax provision", column "2024"
- **F00848** 3.0% EffectiveIncomeTaxRateReconciliationStateAndLocalIncomeTaxes FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationStateAndLocalIncomeTaxes
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "U.S. state income taxes, net of federal income tax benefit", column "2024"
- **F00863** 1.5% EffectiveIncomeTaxRateReconciliationTaxCredits FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits
- **F00869** 1.5% EffectiveIncomeTaxRateReconciliationOtherAdjustments FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationOtherAdjustments
- **F00857** 1.2% EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Valuation allowance", column "2024"
- **F00858** 1.7% EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance FY2023 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Valuation allowance", column "2023"
- **F00851** 0.1% EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential FY2024 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential
- **F00852** 1.1% EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential FY2023 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Income taxed outside the U.S.", column "2023"
- **F00870** 1.8% EffectiveIncomeTaxRateReconciliationOtherAdjustments FY2023 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationOtherAdjustments
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Other, net", column "2023"
- **T00067**  - *prose*: paragraph in the filing: "• our effective tax rate for certain periods and the realization of certain net deferred tax assets and the effects of resolutions of tax-related matters;"
- **F00859** 4.4% EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance FY2022 - *XBRL*: inline XBRL tag us-gaap:EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance
    - also shown in table #80 "Effective Income Tax Rate Reconciliation", row "Valuation allowance", column "2022"
- **F00831** $5.29B CurrentIncomeTaxExpenseBenefit FY2023 (prior-year value behind the change shown) - *XBRL*: inline XBRL tag us-gaap:CurrentIncomeTaxExpenseBenefit
    - also shown in table #79 "A summary of the provision for income taxes is as follows:", row "Total current tax provision", column "2023"
