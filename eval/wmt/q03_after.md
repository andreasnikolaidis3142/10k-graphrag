# What are Walmart's current ratio, inventory level and inventory growth versus cost of sales growth, and is there any build-up risk?

*model: inclusionai/ling-3.1-flash | ungrounded numbers: none | missing contributors: none | uncited claims: 0*

## Summary
Walmart's current ratio was 0.83x at FY2024 (January 31, 2024), up from 0.82x at FY2023, a +1.4% YoY change [F01861], with the trend described as stable (weak), +1% over the window. Current liabilities of $92.42B [F00135] exceed current assets of $76.88B [F00107], and the filing text reports a working capital deficit of $15.5 billion at FY2024 [F01400] and $16.5 billion at FY2023 [F01401]. Inventory was $54.89B at FY2024 [F00103], down 3.0% YoY from $56.58B at FY2023 [F00104], while cost of sales rose +5.7% YoY to $490.14B in FY2024 [F00012]. Inventory contracting while cost of sales expands coincides with no inventory build-up in the reported period.

**Status:** mixed

## Key numbers
- Current ratio (@2024-01-31): **0.83x**  [F01861]
- Current ratio (@2023-01-31): **0.82x**  [F01860]
- Current ratio YoY change (@2024-01-31): **+1.4%**  [F01861]
- Inventory (InventoryNet) (@2024-01-31): **$54.89B**  [F00103]
- Inventory (InventoryNet) (@2023-01-31): **$56.58B**  [F00104]
- Inventory YoY change (@2024-01-31): **-3.0%**  [F00103]
- Cost of sales (FY2024): **$490.14B**  [F00012]
- Cost of sales YoY growth (FY2024): **+5.7%**  [F00012]
- Current assets (@2024-01-31): **$76.88B**  [F00107]
- Current liabilities (@2024-01-31): **$92.42B**  [F00135]
- Working capital deficit (text) (@2024-01-31): **$15.5 billion**  [F01400]

## Drivers
- Inventory declined -3.0% YoY to $54.89B [F00103], moving AGAINST any build-up concern; this coincides with cost of sales growth of +5.7% YoY to $490.14B [F00012], so inventory is contracting while the cost base expands.
- Current ratio rose +1.4% YoY to 0.83x [F01861], driven by current assets growing +1.6% YoY to $76.88B [F00107] while current liabilities grew only +0.2% YoY to $92.42B [F00135].
- The text-reported working capital deficit narrowed from $16.5 billion at FY2023 [F01401] to $15.5 billion at FY2024 [F01400]; these are narrower than total current liabilities of $92.20B [F00136] and $92.42B [F00135].

## Risks and red flags
- Current ratio of 0.83x [F01861] with current liabilities of $92.42B [F00135] exceeding current assets of $76.88B [F00107] reflects a working capital deficit of $15.5 billion [F01400], a liquidity consideration.
- Inventory is valued under the retail inventory method (RIM) using LIFO for Walmart U.S. [T00653], which can affect valuation and comparability of the -3.0% inventory change [F00103].
- Text/table scope difference: narrative text cites $15.5 billion [F01400] and $16.5 billion [F01401] for the working capital deficit, versus total current liabilities of $92.42B [F00135] and $92.20B [F00136]; verify scope before treating as an error.

## Data quality
- The '$15.5 billion' (FY2024) and '$16.5 billion' (FY2023) text figures [F01400][F01401] describe the working capital deficit (total current assets less total current liabilities), not total current liabilities of $92.42B [F00135] and $92.20B [F00136]; this is a scope difference, not a contradiction.
- Current ratio is a derived metric (CurrentAssets / CurrentLiabilities), reported as 0.83x at FY2024 [F01861] and not recomputed.
- Inventory is a stock (point-in-time) measure [F00103] and cost of sales is a flow (12-month) measure [F00012]; the -3.0% inventory change [F00103] and +5.7% cost of sales growth [F00012] are compared as rates, not summed.

## Outlook
- Actuals: FY2024 actuals show inventory down 3.0% YoY to $54.89B [F00103] while cost of sales rose 5.7% YoY to $490.14B [F00012], coinciding with no inventory build-up; liquidity remains tight with a 0.83x current ratio [F01861] and a $15.5 billion working capital deficit [F01400].
- Guidance: Not in the retrieved evidence - no management guidance figures were provided for inventory, cost of sales, or current ratio.

## Follow-up checks
- Verify the working capital deficit figures of $15.5 billion (FY2024) [F01400] and $16.5 billion (FY2023) [F01401] against the balance sheet to confirm they equal total current assets less total current liabilities.
- Check the LIFO reserve / inventory valuation disclosure for any material adjustment affecting the $54.89B inventory figure [F00103] given RIM/LIFO accounting [T00653].
- Review segment-level inventory (Walmart U.S. vs. International vs. Sam's Club) to confirm the -3.0% decline [F00103] is not concentrated in a single segment.
- Confirm whether markdown or obsolescence provisions changed materially in FY2024, given RIM records permanent markdowns immediately [T00653].

## Sources (where each cited number came from)
- **F01861** 0.83x CurrentRatio @2024-01-31 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00107, F00135
- **F00135** $92.42B LiabilitiesCurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:LiabilitiesCurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Total current liabilities", column "2024"
- **F00107** $76.88B AssetsCurrent @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:AssetsCurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Total current assets", column "2024"
- **F01400** $15.50B LiabilitiesCurrent @2024-01-31 - *prose*: sentence in the filing: "Our working capital deficit, defined as total current assets less total current liabilities, was $15.5 billion and $16.5 billion as of January 31, 2024 and 2023"
- **F01401** $16.50B LiabilitiesCurrent @2023-01-31 - *prose*: sentence in the filing: "Our working capital deficit, defined as total current assets less total current liabilities, was $15.5 billion and $16.5 billion as of January 31, 2024 and 2023"
- **F00103** $54.89B InventoryNet @2024-01-31 - *XBRL*: inline XBRL tag us-gaap:InventoryNet
    - also shown in table #52 "Consolidated Balance Sheets", row "Inventories", column "2024"
- **F00104** $56.58B InventoryNet @2023-01-31 - *XBRL*: inline XBRL tag us-gaap:InventoryNet
    - also shown in table #52 "Consolidated Balance Sheets", row "Inventories", column "2023"
- **F00012** $490.14B CostOfRevenue FY2024 - *XBRL*: inline XBRL tag us-gaap:CostOfRevenue
    - also shown in table #50 "Consolidated Statements of Income", row "Cost of sales", column "2024"
- **F01860** 0.82x CurrentRatio @2023-01-31 - *computed*: CurrentAssets / CurrentLiabilities
    - computed from F00108, F00136
- **F00136** $92.20B LiabilitiesCurrent @2023-01-31 - *XBRL*: inline XBRL tag us-gaap:LiabilitiesCurrent
    - also shown in table #52 "Consolidated Balance Sheets", row "Total current liabilities", column "2023"
- **T00653**  - *prose*: paragraph in the filing: "• Walmart U.S. Segment - Inventories are primarily accounted for under the retail inventory method of accounting ("RIM") to determine inventory cost, using the "
