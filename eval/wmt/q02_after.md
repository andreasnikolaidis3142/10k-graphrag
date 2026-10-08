# Break down net sales by segment (Walmart U.S., Walmart International, Sam's Club) and say which segment grew fastest and which had the highest operating margin.

*model: apodex/apodex-1.1-mini:free | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's FY2024 consolidated net sales were $642.64B [F00003], up 6.1% YoY [F00003]. By segment, Walmart U.S. generated $441.82B (68.8% of total) [F00958], Walmart International $114.64B (17.8%) [F00959], and Sam's Club $86.18B (13.4%) [F00960]. Walmart International grew fastest in FY2024 at +13.5% YoY ($100.98B -> $114.64B) [F00959], versus Walmart U.S. at +5.1% [F00958] and Sam's Club at +2.2% [F00960]. Walmart U.S. had the highest operating income at $22.15B [F00962] on $441.82B of net sales [F00958], versus Walmart International at $4.91B [F00963] and Sam's Club at $2.19B [F00964], so Walmart U.S. had the highest operating margin. This is consistent with management's statement that Walmart U.S. has historically had the highest gross profit as a percentage of net sales [T00090].

**Status:** positive

## Key numbers
- Consolidated net sales FY2024 (FY2024): **$642.64B**  [F00003]
- Walmart U.S. net sales FY2024 (FY2024): **$441.82B (68.8% of total)**  [F00958]
- Walmart International net sales FY2024 (FY2024): **$114.64B (17.8% of total)**  [F00959]
- Sam's Club net sales FY2024 (FY2024): **$86.18B (13.4% of total)**  [F00960]
- Walmart International net sales growth FY2024 (FY2024): **+13.5% YoY**  [F00959]
- Walmart U.S. operating income FY2024 (FY2024): **$22.15B**  [F00962]
- Walmart International operating income FY2024 (FY2024): **$4.91B**  [F00963]
- Sam's Club operating income FY2024 (FY2024): **$2.19B**  [F00964]

## Drivers
- Walmart U.S. was the LARGEST CONTRIBUTOR TO THE CHANGE in FY2024 net sales, contributing $21.26B (+5.1%), 58% of the total change [F00958][F00979]
- Walmart International contributed $13.66B (+13.5%), 37% of the total change [F00959][F00980]
- Sam's Club contributed $1.83B (+2.2%), 5% of the total change [F00960][F00981]
- Corporate And Support contributed $0.00, 0% of the total change [F00961][F00982]

## Risks and red flags
- Sam's Club growth decelerated sharply to +2.2% in FY2024 from +14.7% in FY2023 [F00960], with lower fuel sales due to deflation partially offsetting growth [T00478]
- Walmart U.S. growth slowed to +5.1% in FY2024 from +6.9% in FY2023 [F00958]
- Corporate And Support posted a negative operating income of -$2.24B in FY2024, down 56.2% YoY from -$5.12B [F00965]
- Sam's Club has the lowest operating income ($2.19B) among the three reportable segments [F00964]

## Data quality
- 19 duplicate facts with conflicting values were set aside during parsing (primary-statement value kept)
- Two NetIncomeLoss series exist with different FY2024 values: $16.27B (ProfitLoss) [F00045] vs $15.51B (NetIncomeLoss) [F00051]
- Segment operating margins are derived from segment operating income and segment net sales (not pre-computed in the evidence)
- Segment slices are components of the consolidated total, not the company total

## Outlook
- Actuals: FY2024 consolidated net sales grew +6.1% YoY to $642.64B [F00003], with Walmart International the fastest-growing segment at +13.5% [F00959]
- Guidance: No management guidance facts are present in the retrieved evidence; guidance would be labeled forward-looking and kept separate from actuals

## Follow-up checks
- Verify the segment operating margins against the filing's segment note (operating income / net sales per segment)
- Reconcile the two NetIncomeLoss series ($16.27B ProfitLoss vs $15.51B NetIncomeLoss) to determine which is the correct consolidated figure
- Review the drivers of Corporate And Support's -$2.24B operating loss and its 56.2% YoY improvement [F00965]
- Check whether FY2025 segment-level guidance is available in the filing or subsequent 10-Qs

## Sources (where each cited number came from)
- **F00003** $642.64B Revenues FY2024 - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #27 "untitled", row "Net sales", column "2024"
    - also shown in table #32 "Consolidated Results of Operations", row "Net sales", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Net sales", column "2024"
- **F00958** $441.82B Revenues FY2024 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00959** $114.64B Revenues FY2024 [StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00960** $86.18B Revenues FY2024 [StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #35 "Sam's Club Segment", row "Net sales", column "2024"
- **F00962** $22.15B OperatingIncomeLoss FY2024 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00963** $4.91B OperatingIncomeLoss FY2024 [StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00964** $2.19B OperatingIncomeLoss FY2024 [StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
    - also shown in table #35 "Sam's Club Segment", row "Operating income", column "2024"
- **T00090**  - *prose*: paragraph in the filing: "Walmart U.S. is our largest segment and operates in the U.S., including in all 50 states, Washington D.C. and Puerto Rico. Walmart U.S. is a mass merchandiser o"
- **F00979** $420.55B Revenues FY2023 [StatementBusinessSegments=WalmartUS] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00980** $100.98B Revenues FY2023 [StatementBusinessSegments=WalmartInternational] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00981** $84.34B Revenues FY2023 [StatementBusinessSegments=SamsClub] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
    - also shown in table #35 "Sam's Club Segment", row "Net sales", column "2023"
- **F00961** $0.00 Revenues FY2024 [StatementBusinessSegments=CorporateAndSupport] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **F00982** $0.00 Revenues FY2023 [StatementBusinessSegments=CorporateAndSupport] - *XBRL*: inline XBRL tag us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax
- **T00478**  - *prose*: paragraph in the filing: "Net sales for the Sam's Club segment increased $1.8 billion or 2.2% and $10.8 billion or 14.7% for fiscal 2024 and 2023, respectively, when compared to the prev"
- **F00965** -$2.24B OperatingIncomeLoss FY2024 [StatementBusinessSegments=CorporateAndSupport] - *XBRL*: inline XBRL tag us-gaap:OperatingIncomeLoss
- **F00045** $16.27B NetIncomeLoss FY2024 - *XBRL*: inline XBRL tag us-gaap:ProfitLoss
    - also shown in table #28 "Return on Assets and Return on Investment", row "Consolidated net income", column "2024"
    - also shown in table #32 "Consolidated Results of Operations", row "Consolidated net income", column "2024"
    - also shown in table #50 "Consolidated Statements of Income", row "Consolidated net income", column "2024"
- **F00051** $15.51B NetIncomeLoss FY2024 - *XBRL*: inline XBRL tag us-gaap:NetIncomeLoss
    - also shown in table #50 "Consolidated Statements of Income", row "Consolidated net income attributable to Walmart", column "2024"
    - also shown in table #51 "Consolidated Statements of Comprehensive Income", row "Consolidated net income attributable to Walmart", column "2024"
    - also shown in table #57 "Note 2. Net Income Per Common Share", row "Consolidated net income attributable to Walmart", column "2024"
