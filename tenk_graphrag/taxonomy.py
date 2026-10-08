"""
Canonical concept taxonomy (keys follow us-gaap element local names so that inline-XBRL tags
map 1:1) + label matching + accounting identities.

This is "Layer 1: semantic data understanding" from the Reddit post: every number must know
- what it is (concept), its statement, whether it is a flow (duration) or a stock (instant),
- its natural unit, and how it relates to other numbers (identities / roll-ups).
"""
import re
import difflib

# key: (label, statement, period_type, unit, synonyms, flags)
# flags: abs=True -> store magnitude (cash outflows are printed in parentheses but are "payments")
def _c(label, stmt, ptype, unit, syn, alias=(), abs_=False, neg_loss=False):
    return dict(label=label, stmt=stmt, ptype=ptype, unit=unit, syn=list(syn),
                alias=list(alias), abs=abs_, neg_loss=neg_loss)

CONCEPTS = {
    # ---------------- Income statement ----------------
    "Revenues": _c("Total revenue", "IS", "duration", "USD",
        ["total revenue", "total revenues", "revenue", "revenues", "net sales", "total net sales",
         "net revenue", "net revenues", "total net revenue", "sales", "total sales"],
        ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
         "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet"]),
    "CostOfRevenue": _c("Cost of revenue", "IS", "duration", "USD",
        ["cost of revenue", "cost of revenues", "cost of sales", "cost of goods sold", "total cost of sales",
         "cost of products sold", "total cost of revenue", "cost of services"],
        ["CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"]),
    "GrossProfit": _c("Gross profit", "IS", "duration", "USD", ["gross profit", "gross margin", "gross income"]),
    "ResearchAndDevelopmentExpense": _c("R&D expense", "IS", "duration", "USD",
        ["research and development", "research and development expense", "research development", "r&d"]),
    "SellingAndMarketingExpense": _c("Sales & marketing", "IS", "duration", "USD",
        ["sales and marketing", "selling and marketing", "marketing and sales"]),
    "GeneralAndAdministrativeExpense": _c("G&A", "IS", "duration", "USD",
        ["general and administrative", "general administrative"]),
    "SellingGeneralAndAdministrativeExpense": _c("SG&A", "IS", "duration", "USD",
        ["selling general and administrative", "selling general administrative", "sg&a",
         "selling general and administrative expenses"]),
    "OperatingExpenses": _c("Total operating expenses", "IS", "duration", "USD",
        ["total operating expenses", "operating expenses", "total opex"]),
    "CostsAndExpenses": _c("Total costs and expenses", "IS", "duration", "USD",
        ["total costs and expenses", "total expenses", "costs and expenses"]),
    "OperatingIncomeLoss": _c("Operating income", "IS", "duration", "USD",
        ["operating income", "income from operations", "operating profit", "operating loss",
         "loss from operations", "operating income loss", "income loss from operations",
         "operating earnings"], neg_loss=True),
    "InterestExpense": _c("Interest expense", "IS", "duration", "USD",
        ["interest expense", "interest expense net", "interest and debt expense"], ["InterestExpenseNonoperating", "InterestExpenseDebt"], abs_=True),
    "InvestmentIncomeInterest": _c("Interest income", "IS", "duration", "USD",
        ["interest income", "investment income", "interest and other income", "interest and dividend income"]),
    "OtherNonoperatingIncomeExpense": _c("Other income (expense), net", "IS", "duration", "USD",
        ["other income expense net", "other income net", "other expense net", "other net",
         "total other income expense net", "total other income net", "nonoperating income expense"],
        ["NonoperatingIncomeExpense"]),
    "IncomeLossBeforeIncomeTaxes": _c("Income before income taxes", "IS", "duration", "USD",
        ["income before income taxes", "income before provision for income taxes", "earnings before income taxes",
         "income before taxes", "pretax earnings", "pretax income", "loss before income taxes", "income loss before income taxes",
         "income before provision for taxes", "income before income tax expense"],
        ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
         "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
        neg_loss=True),
    "IncomeTaxExpenseBenefit": _c("Income tax expense", "IS", "duration", "USD",
        ["provision for income taxes", "income tax expense", "income taxes", "provision for benefit from income taxes",
         "income tax provision", "provision for taxes", "income tax expense benefit", "benefit from income taxes"]),
    "NetIncomeLoss": _c("Net income", "IS", "duration", "USD",
        ["net income", "net earnings", "net loss", "net income loss", "net loss income", "net earnings loss",
         "net income attributable to common stockholders", "net income attributable to shareholders"],
        ["ProfitLoss"], neg_loss=True),
    "EarningsPerShareBasic": _c("EPS basic", "IS", "duration", "USD/share",
        ["basic", "earnings per share basic", "basic earnings per share", "net income per share basic",
         "basic net income per share", "net income loss per share basic", "basic eps"]),
    "EarningsPerShareDiluted": _c("EPS diluted", "IS", "duration", "USD/share",
        ["diluted", "earnings per share diluted", "diluted earnings per share", "net income per share diluted",
         "diluted net income per share", "net income loss per share diluted", "diluted eps"]),
    "WeightedAverageNumberOfSharesOutstandingBasic": _c("Wtd avg shares basic", "IS", "duration", "shares",
        ["weighted average shares basic", "shares used in computing basic", "weighted average basic shares outstanding",
         "weighted average number of shares basic", "basic shares", "weighted average shares outstanding basic",
         "shares used in computing basic eps", "shares used in computing basic earnings per share", "basic weighted average shares"]),
    "WeightedAverageNumberOfDilutedSharesOutstanding": _c("Wtd avg shares diluted", "IS", "duration", "shares",
        ["weighted average shares diluted", "shares used in computing diluted", "weighted average diluted shares outstanding",
         "weighted average number of shares diluted", "diluted shares", "weighted average shares outstanding diluted",
         "shares used in computing diluted eps", "shares used in computing diluted earnings per share", "shares used in computing diluted net income per share", "diluted weighted average shares"]),
    "CommonStockDividendsPerShareDeclared": _c("Dividends per share", "IS", "duration", "USD/share",
        ["dividends declared per share", "dividends per share", "cash dividends declared per share", "dividends declared per common share"]),
    # ---------------- Balance sheet ----------------
    "CashAndCashEquivalentsAtCarryingValue": _c("Cash & equivalents", "BS", "instant", "USD",
        ["cash and cash equivalents", "cash and equivalents", "cash"]),
    "ShortTermInvestments": _c("Short-term investments", "BS", "instant", "USD",
        ["short term investments", "marketable securities", "marketable securities current", "short term marketable securities"],
        ["MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"]),
    "AccountsReceivableNetCurrent": _c("Accounts receivable", "BS", "instant", "USD",
        ["accounts receivable", "accounts receivable net", "receivables net", "trade receivables", "accounts receivable net of allowance"]),
    "InventoryNet": _c("Inventory", "BS", "instant", "USD", ["inventories", "inventory", "inventory net", "inventories net"]),
    "PrepaidExpenseAndOtherAssetsCurrent": _c("Prepaids & other current", "BS", "instant", "USD",
        ["prepaid expenses and other current assets", "prepaid expenses", "other current assets", "vendor non trade receivables"],
        ["OtherAssetsCurrent", "PrepaidExpenseCurrent"]),
    "AssetsCurrent": _c("Total current assets", "BS", "instant", "USD", ["total current assets", "current assets"]),
    "PropertyPlantAndEquipmentNet": _c("PP&E, net", "BS", "instant", "USD",
        ["property plant and equipment net", "property and equipment net", "property plant equipment net",
         "property and equipment", "net property plant and equipment"]),
    "OperatingLeaseRightOfUseAsset": _c("Operating lease ROU asset", "BS", "instant", "USD",
        ["operating lease right of use assets", "right of use assets", "operating lease assets"]),
    "Goodwill": _c("Goodwill", "BS", "instant", "USD", ["goodwill"]),
    "IntangibleAssetsNetExcludingGoodwill": _c("Intangibles, net", "BS", "instant", "USD",
        ["intangible assets net", "intangible assets", "acquired intangible assets net", "intangibles net"]),
    "Assets": _c("Total assets", "BS", "instant", "USD", ["total assets"]),
    "AccountsPayableCurrent": _c("Accounts payable", "BS", "instant", "USD", ["accounts payable", "trade payables", "accounts payable trade"]),
    "AccruedLiabilitiesCurrent": _c("Accrued liabilities", "BS", "instant", "USD",
        ["accrued liabilities", "accrued expenses", "accrued expenses and other current liabilities", "other current liabilities",
         "accrued compensation"], ["OtherLiabilitiesCurrent"]),
    "ContractWithCustomerLiabilityCurrent": _c("Deferred revenue (current)", "BS", "instant", "USD",
        ["deferred revenue", "contract liabilities", "unearned revenue", "deferred revenue current", "customer deposits"],
        ["DeferredRevenueCurrent"]),
    "LongTermDebtCurrent": _c("Current debt", "BS", "instant", "USD",
        ["current portion of long term debt", "short term debt", "current maturities of long term debt",
         "current portion of debt", "term debt current"],
        ["DebtCurrent"]),
    "ShortTermBorrowings": _c("Short-term borrowings", "BS", "instant", "USD", ["short term borrowings"]),   # NOT current maturities of LT debt
    "LiabilitiesCurrent": _c("Total current liabilities", "BS", "instant", "USD", ["total current liabilities", "current liabilities"]),
    "LongTermDebtNoncurrent": _c("Long-term debt", "BS", "instant", "USD",
        ["long term debt", "long term debt net of current portion", "long term debt less current portion",
         "long term borrowings", "notes payable long term", "term debt", "long term debt net"], ["LongTermDebt"]),
    "OperatingLeaseLiabilityNoncurrent": _c("Operating lease liab. (non-current)", "BS", "instant", "USD",
        ["operating lease liabilities", "long term operating lease liabilities", "operating lease liabilities non current"]),
    "Liabilities": _c("Total liabilities", "BS", "instant", "USD", ["total liabilities"]),
    "StockholdersEquity": _c("Total stockholders' equity", "BS", "instant", "USD",
        ["total stockholders equity", "total shareholders equity", "total equity", "stockholders equity",
         "shareholders equity", "total stockholders equity deficit", "total shareholders equity deficit"],
        ["StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]),
    "LiabilitiesAndStockholdersEquity": _c("Total liabilities & equity", "BS", "instant", "USD",
        ["total liabilities and stockholders equity", "total liabilities and shareholders equity", "total liabilities and equity",
         "total liabilities and stockholders equity deficit", "total liabilities equity"]),
    "RetainedEarningsAccumulatedDeficit": _c("Retained earnings", "BS", "instant", "USD",
        ["retained earnings", "accumulated deficit", "retained earnings accumulated deficit", "retained earnings deficit"]),
    "AdditionalPaidInCapital": _c("APIC", "BS", "instant", "USD", ["additional paid in capital", "additional paid in capital common stock"]),
    "TreasuryStockValue": _c("Treasury stock", "BS", "instant", "USD", ["treasury stock", "treasury stock at cost"], abs_=True),
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax": _c("AOCI", "BS", "instant", "USD",
        ["accumulated other comprehensive income loss", "accumulated other comprehensive loss", "accumulated other comprehensive income"]),
    # ---------------- Cash flow ----------------
    "DepreciationDepletionAndAmortization": _c("D&A", "CF", "duration", "USD",
        ["depreciation and amortization", "depreciation amortization and accretion", "depreciation depletion and amortization"],
        ["DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"]),
    "ShareBasedCompensation": _c("Stock-based compensation", "CF", "duration", "USD",
        ["stock based compensation", "share based compensation", "stock based compensation expense", "share based compensation expense"],
        ["AllocatedShareBasedCompensationExpense"]),
    "NetCashProvidedByUsedInOperatingActivities": _c("Cash from operations", "CF", "duration", "USD",
        ["net cash provided by operating activities", "net cash from operating activities", "cash generated by operating activities",
         "net cash provided by used in operating activities", "net cash used in provided by operating activities",
         "net cash provided by operations", "cash flows from operating activities", "net cash used in operating activities",
         "net cash flows from operating activities"]),
    "NetCashProvidedByUsedInInvestingActivities": _c("Cash from investing", "CF", "duration", "USD",
        ["net cash used in investing activities", "net cash provided by investing activities", "net cash from investing activities",
         "net cash provided by used in investing activities", "net cash used in provided by investing activities",
         "cash generated by used in investing activities", "cash flows from investing activities"]),
    "NetCashProvidedByUsedInFinancingActivities": _c("Cash from financing", "CF", "duration", "USD",
        ["net cash used in financing activities", "net cash provided by financing activities", "net cash from financing activities",
         "net cash provided by used in financing activities", "net cash used in provided by financing activities",
         "cash used in financing activities", "cash flows from financing activities"]),
    "PaymentsToAcquirePropertyPlantAndEquipment": _c("Capex", "CF", "duration", "USD",
        ["purchases of property and equipment", "capital expenditures", "purchases of property plant and equipment",
         "additions to property and equipment", "payments for acquisition of property plant and equipment",
         "purchase of property and equipment", "purchases of property equipment"], abs_=True),
    "PaymentsForRepurchaseOfCommonStock": _c("Share repurchases", "CF", "duration", "USD",
        ["repurchases of common stock", "purchase of treasury stock", "share repurchases", "repurchases of common stock and related costs",
         "payments for repurchase of common stock", "common stock repurchased"], abs_=True),
    "PaymentsOfDividends": _c("Dividends paid", "CF", "duration", "USD",
        ["dividends paid", "payments of dividends", "cash dividends paid", "payments for dividends", "dividends and dividend equivalents paid"],
        ["PaymentsOfDividendsCommonStock"], abs_=True),
    "RepaymentsOfDebt": _c("Debt repayments", "CF", "duration", "USD",
        ["repayments of debt", "repayments of long term debt", "repayments of term debt", "payments on debt", "repayment of borrowings"],
        ["RepaymentsOfLongTermDebt"], abs_=True),
    "ProceedsFromIssuanceOfDebt": _c("Debt issuance", "CF", "duration", "USD",
        ["proceeds from issuance of debt", "proceeds from issuance of long term debt", "proceeds from issuance of term debt",
         "proceeds from borrowings", "proceeds from long term debt"], ["ProceedsFromIssuanceOfLongTermDebt"]),
    "EffectOfExchangeRateOnCash": _c("FX effect on cash", "CF", "duration", "USD",
        ["effect of exchange rate changes on cash", "effect of foreign exchange rate changes on cash",
         "effect of exchange rate on cash and cash equivalents"],
        ["EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]),
    "CashPeriodIncrease": _c("Net change in cash", "CF", "duration", "USD",
        ["net increase decrease in cash and cash equivalents", "net change in cash and cash equivalents",
         "increase decrease in cash cash equivalents and restricted cash", "net increase in cash and cash equivalents",
         "net decrease in cash and cash equivalents", "change in cash and cash equivalents"],
        ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
         "CashAndCashEquivalentsPeriodIncreaseDecrease"]),
    "Depreciation": _c("Depreciation expense (PP&E only)", "NOTE", "duration", "USD", ["depreciation expense", "depreciation"]),
    "CommercialPaper": _c("Commercial paper", "BS", "instant", "USD", ["commercial paper", "commercial paper outstanding"]),
    "OtherAssetsNoncurrent": _c("Other non-current assets", "BS", "instant", "USD", ["other non current assets", "other assets noncurrent", "other assets"]),
    "MarketableSecuritiesNoncurrent": _c("Non-current marketable securities", "BS", "instant", "USD",
        ["non current marketable securities", "long term marketable securities", "marketable securities non current"]),
    "OtherLiabilitiesNoncurrent": _c("Other non-current liabilities", "BS", "instant", "USD", ["other non current liabilities", "other liabilities noncurrent"]),
    # ---------------- Non-GAAP / KPIs ----------------
    "Ebitda": _c("EBITDA (non-GAAP)", "NONGAAP", "duration", "USD", ["ebitda"]),
    "AdjustedEbitda": _c("Adjusted EBITDA (non-GAAP)", "NONGAAP", "duration", "USD", ["adjusted ebitda"]),
    "FreeCashFlow": _c("Free cash flow (non-GAAP)", "NONGAAP", "duration", "USD", ["free cash flow"]),
    "EffectiveIncomeTaxRate": _c("Effective tax rate", "TAX", "duration", "percent",
        ["effective tax rate", "effective income tax rate"], ["EffectiveIncomeTaxRateContinuingOperations"]),
    "NumberOfEmployees": _c("Employees", "KPI", "instant", "count", ["employees", "full time employees", "number of employees"]),
}

# canonical key for any alias / xbrl name
ALIAS = {}
for k, v in CONCEPTS.items():
    ALIAS[k.lower()] = k
    for a in v["alias"]:
        ALIAS[a.lower()] = k

# percent/ratio twins when a % is printed on a currency row ("Gross margin 43%")
PCT_TWIN = {"GrossProfit": "GrossMarginPct", "OperatingIncomeLoss": "OperatingMarginPct", "NetIncomeLoss": "NetMarginPct"}
AGG_CONCEPTS = {"AssetsCurrent", "Assets", "LiabilitiesCurrent", "Liabilities", "StockholdersEquity",
                "LiabilitiesAndStockholdersEquity", "OperatingExpenses", "CostsAndExpenses", "GrossProfit",
                "OperatingIncomeLoss", "NetCashProvidedByUsedInOperatingActivities",
                "NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInFinancingActivities", "CashPeriodIncrease"}

# Accounting identities: target = sum(sign*term) [required]  (+ optional terms if present)
# (target, [(concept, sign)], [optional (concept, sign)], name)
IDENTITIES = [
    ("GrossProfit", [("Revenues", 1), ("CostOfRevenue", -1)], [], "Gross profit = Revenue - COGS"),
    ("OperatingIncomeLoss", [("GrossProfit", 1), ("OperatingExpenses", -1)], [], "Operating income = Gross profit - Opex"),
    ("OperatingIncomeLoss", [("Revenues", 1), ("CostsAndExpenses", -1)], [], "Operating income = Revenue - Total costs"),
    ("NetIncomeLoss", [("IncomeLossBeforeIncomeTaxes", 1), ("IncomeTaxExpenseBenefit", -1)], [], "Net income = Pre-tax income - Taxes"),
    ("LiabilitiesAndStockholdersEquity", [("Assets", 1)], [], "Total L&E = Total assets"),
    ("Assets", [("Liabilities", 1), ("StockholdersEquity", 1)], [], "Assets = Liabilities + Equity"),
    ("CashPeriodIncrease", [("NetCashProvidedByUsedInOperatingActivities", 1),
                            ("NetCashProvidedByUsedInInvestingActivities", 1),
                            ("NetCashProvidedByUsedInFinancingActivities", 1)],
     [("EffectOfExchangeRateOnCash", 1)], "Net change in cash = CFO + CFI + CFF (+FX)"),
]

_STOP = {"the", "of", "and", "for", "to", "in", "on", "a", "an"}
# a fuzzy match must not drop or add one of these ("other NON-CURRENT assets" is not "other current assets")
_DISCRIMINATORS = {"non", "noncurrent", "long", "short", "deferred", "accrued", "restricted", "unrestricted"}

def norm(label: str) -> str:
    s = label.lower().replace("&", " and ").replace("’", "'").replace("'", "")
    s = re.sub(r"\(\s*\d\s*\)$", "", s)                 # trailing footnote (1)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _tokset(s):
    return {t for t in s.split() if t not in _STOP}

_SYN_INDEX = {}
for k, v in CONCEPTS.items():
    for s in v["syn"]:
        _SYN_INDEX.setdefault(norm(s), k)

def match_concept(label: str, stmt_hint=None, threshold=0.86):
    """label -> (concept_key | None, score). Exact > exact-without 'total' > token-set > fuzzy."""
    n = norm(label)
    if not n:
        return None, 0.0
    if n in _SYN_INDEX:
        key = _SYN_INDEX[n]
        if key == "Depreciation" and stmt_hint == "CF":          # a bare "Depreciation" row in a cash-flow statement is D&A
            key = "DepreciationDepletionAndAmortization"
        return key, 1.0
    n2 = re.sub(r"^(total|net)\s+", "", n)
    if n2 != n and n2 in _SYN_INDEX:
        return _SYN_INDEX[n2], 0.95
    n3 = re.sub(r"\b(loss|income expense|expense benefit)\b", "", n).strip()
    best, score = None, 0.0
    ts = _tokset(n)
    for syn, key in _SYN_INDEX.items():
        if stmt_hint and CONCEPTS[key]["stmt"] not in (stmt_hint, "NONGAAP", "KPI") and stmt_hint in ("IS", "BS", "CF"):
            continue
        tt = _tokset(syn)
        if not tt or not ts or (ts ^ tt) & _DISCRIMINATORS:
            continue
        jac = len(ts & tt) / len(ts | tt)
        sm = difflib.SequenceMatcher(None, n, syn).ratio()
        sc = max(jac if jac >= 0.8 else 0, sm)
        if sc > score:
            best, score = key, sc
    return (best, score) if score >= threshold else (None, score)

_PHRASES = sorted(((s, k) for s, k in _SYN_INDEX.items() if len(s) >= 5), key=lambda x: -len(x[0]))

def find_concepts_in_text(text: str):
    """All (start, end, concept, phrase) synonym hits in free text (positions refer to the ORIGINAL text),
    longest phrase wins, non-overlapping."""
    chars, idx = [" "], [0]
    for i, ch in enumerate(text):
        if ch in "'’":
            continue                                   # drop apostrophes (stockholders' -> stockholders)
        chars.append(ch.lower() if ch.isalnum() or ch == "&" else " "); idx.append(i)
    chars.append(" "); idx.append(len(text))
    low = "".join(chars)
    taken, hits = [], []
    for phrase, key in _PHRASES:
        for m in re.finditer(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", low):
            if any(not (m.end() <= a or m.start() >= b) for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            hits.append((idx[m.start()], idx[min(m.end(), len(idx) - 1)], key, phrase))
    return sorted(hits)

def canonical(name: str):
    """XBRL element (with or without prefix) -> canonical key or None."""
    local = name.split(":")[-1]
    return ALIAS.get(local.lower())
