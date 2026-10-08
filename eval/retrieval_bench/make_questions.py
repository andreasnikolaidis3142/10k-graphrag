"""Generate the retrieval benchmark: up to 100 questions per company with machine-checkable answer keys.

Answer values come from an INDEPENDENT inline-XBRL parse of the filing (not from tenk_graphrag's graph), so the
benchmark cannot inherit the system's own parsing bugs. Questions use analyst wording on purpose, not XBRL labels.

  python eval/retrieval_bench/make_questions.py            -> eval/retrieval_bench/questions_<co>.json

Every 5th question (by position) is marked split="holdout" and is never looked at while optimizing.
"""
import glob, json, os, re, sys, warnings
from datetime import date
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
COMPANIES = {"aapl": "AAPL_2023_*.htm", "wmt": "WMT_2024_*.htm", "jpm": "JPM_2023_*.htm", "xom": "34088_2023_*.htm", "pfe": "PFE_2023_*.htm"}
MAX_Q = 100

# ------------------------------------------------------------------ independent iXBRL truth
def ix_facts(path):
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="replace").read(), "lxml")
    ctx = {}
    for c in soup.find_all(re.compile(r"xbrli:context$", re.I)):
        per = c.find(re.compile(r"xbrli:period$", re.I))
        inst = per.find(re.compile(r"instant$", re.I)) if per else None
        if inst is not None:
            p = (None, inst.text.strip())
        else:
            s = per.find(re.compile(r"startdate$", re.I)); e = per.find(re.compile(r"enddate$", re.I))
            p = (s.text.strip(), e.text.strip()) if s is not None and e is not None else (None, None)
        dims = tuple(sorted((m.get("dimension").split(":")[-1], m.text.strip().split(":")[-1])
                            for m in c.find_all(re.compile(r"explicitmember$", re.I))))
        ctx[c.get("id")] = (p, dims)
    out = []
    for t in soup.find_all(re.compile(r"ix:nonfraction$", re.I)):
        txt = t.get_text().strip().replace(",", "")
        try:
            v = float(txt) if txt not in ("", "-", "—") else 0.0
        except ValueError:
            continue
        v *= 10 ** int(t.get("scale", "0") or 0)
        if t.get("sign") == "-":
            v = -v
        (start, end), dims = ctx.get(t.get("contextref"), ((None, None), ()))
        if end:
            out.append(dict(name=t.get("name").split(":")[-1], start=start, end=end, dims=dims, value=v,
                            unit=(t.get("unitref") or "").lower()))
    return out

def fiscal_ends(facts):
    ends = sorted({f["end"] for f in facts if f["start"] and not f["dims"] and
                   330 <= (date.fromisoformat(f["end"]) - date.fromisoformat(f["start"])).days <= 380}, reverse=True)
    return ends[:3]

def pick(facts, names, end, flow, dims=()):
    for n in names:
        for f in facts:
            if f["name"] != n or f["end"] != end or f["dims"] != dims or f["value"] == 0:
                continue
            if flow and not (f["start"] and 330 <= (date.fromisoformat(f["end"]) - date.fromisoformat(f["start"])).days <= 380):
                continue
            if not flow and f["start"]:
                continue
            return f
    return None

def kind_of(f, name):
    u = f["unit"]
    if "share" in u and ("usd" in u or "per" in u):
        return "per_share"
    if "rate" in name.lower() or "percent" in name.lower() or u in ("pure", "percent"):
        return "percent"
    if "shares" in u:
        return "shares"
    return "usd"

# ------------------------------------------------------------------ generic analyst-phrased templates
# (current-year wording, prior-year wording, flow?, candidate us-gaap elements)
T = [
    ("What was the company's total revenue for fiscal {Y}?", "What was the top line in fiscal {PY}?", True,
     ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenuesNetOfInterestExpense", "SalesRevenueNet"]),
    ("How much did it cost to produce the goods and services sold in {Y}?", None, True, ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"]),
    ("What gross profit did the company earn in {Y}?", None, True, ["GrossProfit"]),
    ("How much was spent on research and development in {Y}?", "What was R&D spending in {PY}?", True, ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]),
    ("What were selling, general and administrative costs in {Y}?", None, True, ["SellingGeneralAndAdministrativeExpense"]),
    ("What was operating profit in {Y}?", None, True, ["OperatingIncomeLoss"]),
    ("How much interest expense did the company incur on its borrowings in {Y}?", None, True, ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"]),
    ("What was income before taxes in {Y}?", None, True, ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"]),
    ("What was the income tax charge for {Y}?", None, True, ["IncomeTaxExpenseBenefit"]),
    ("What was the effective tax rate in {Y}?", "What tax rate did the company effectively pay in {PY}?", True, ["EffectiveIncomeTaxRateContinuingOperations"]),
    ("How much profit did the company make in {Y}?", "What was the bottom line in {PY}?", True, ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"]),
    ("What were diluted earnings per share for {Y}?", "What was diluted EPS in {PY}?", True, ["EarningsPerShareDiluted"]),
    ("How many diluted shares were used to compute EPS in {Y}?", None, True, ["WeightedAverageNumberOfDilutedSharesOutstanding"]),
    ("How much stock-based compensation was expensed in {Y}?", None, True, ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]),
    ("What were depreciation and amortization charges in {Y}?", None, True, ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAndAmortization"]),
    ("What was net interest income in {Y}?", "How much did net interest income come to in {PY}?", True, ["InterestIncomeExpenseNet"]),
    ("How much fee and other non-interest revenue was earned in {Y}?", None, True, ["NoninterestIncome"]),
    ("What were total non-interest expenses in {Y}?", None, True, ["NoninterestExpense"]),
    ("How much did employee compensation cost in {Y}?", None, True, ["LaborAndRelatedExpense"]),
    ("How much was set aside for expected credit losses in {Y}?", None, True, ["ProvisionForLoanLeaseAndOtherLosses", "ProvisionForLoanAndLeaseLosses"]),
    ("How large were asset impairment charges in {Y}?", None, True, ["AssetImpairmentCharges", "GoodwillImpairmentLoss", "ImpairmentOfLongLivedAssetsHeldForUse"]),
    ("How much were restructuring charges in {Y}?", None, True, ["RestructuringCharges"]),
    ("How much cash and cash equivalents did the company hold at the end of {Y}?", "What was the cash balance at the end of {PY}?", False, ["CashAndCashEquivalentsAtCarryingValue"]),
    ("What were trade receivables at the end of {Y}?", None, False, ["AccountsReceivableNetCurrent"]),
    ("How much inventory was on the balance sheet at the end of {Y}?", "What were inventories at the end of {PY}?", False, ["InventoryNet"]),
    ("What were total current assets at the end of {Y}?", None, False, ["AssetsCurrent"]),
    ("What was the net book value of property, plant and equipment at the end of {Y}?", None, False, ["PropertyPlantAndEquipmentNet"]),
    ("How much goodwill was carried on the balance sheet at the end of {Y}?", None, False, ["Goodwill"]),
    ("What were intangible assets other than goodwill at the end of {Y}?", None, False, ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet"]),
    ("How large was the balance sheet, i.e. total assets, at the end of {Y}?", None, False, ["Assets"]),
    ("How much did the company owe its suppliers at the end of {Y}?", None, False, ["AccountsPayableCurrent"]),
    ("What were total current liabilities at the end of {Y}?", None, False, ["LiabilitiesCurrent"]),
    ("How much long-term debt was outstanding at the end of {Y}?", "What was long-term borrowing at the end of {PY}?", False, ["LongTermDebtNoncurrent", "LongTermDebt"]),
    ("How much debt matures within the next year as of the end of {Y}?", None, False, ["LongTermDebtCurrent", "DebtCurrent"]),
    ("What short-term borrowings were outstanding at the end of {Y}?", None, False, ["ShortTermBorrowings", "CommercialPaper"]),
    ("What were operating lease liabilities at the end of {Y}?", None, False, ["OperatingLeaseLiability"]),
    ("What were total liabilities at the end of {Y}?", None, False, ["Liabilities"]),
    ("What was shareholders' equity at the end of {Y}?", "How much book equity did shareholders have at the end of {PY}?", False, ["StockholdersEquity"]),
    ("What were retained earnings at the end of {Y}?", None, False, ["RetainedEarningsAccumulatedDeficit"]),
    ("How much in customer deposits did the company hold at the end of {Y}?", "What were total deposits at the end of {PY}?", False, ["Deposits"]),
    ("How large was the loan book at the end of {Y}?", None, False, ["FinancingReceivableExcludingAccruedInterestBeforeAllowanceForCreditLoss", "LoansAndLeasesReceivableNetOfDeferredIncome", "FinancingReceivableExcludingAccruedInterestBeforeAllowanceForCreditLossNetOfDeferredIncome"]),
    ("What reserves were held against loan losses at the end of {Y}?", None, False, ["FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest", "AllowanceForLoanAndLeaseLosses"]),
    ("How many common shares were outstanding at the end of {Y}?", None, False, ["CommonStockSharesOutstanding"]),
    ("How much cash did operations generate in {Y}?", "What was operating cash flow in {PY}?", True, ["NetCashProvidedByUsedInOperatingActivities"]),
    ("How much was invested in capital expenditures in {Y}?", "What was capex in {PY}?", True, ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"]),
    ("How much did the company spend buying back its own stock in {Y}?", "What were share buybacks in {PY}?", True, ["PaymentsForRepurchaseOfCommonStock"]),
    ("How much was paid out in dividends in {Y}?", None, True, ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"]),
    ("What was net cash used in investing activities in {Y}?", None, True, ["NetCashProvidedByUsedInInvestingActivities"]),
    ("What was net cash from financing activities in {Y}?", None, True, ["NetCashProvidedByUsedInFinancingActivities"]),
    ("How much cash was spent on acquisitions in {Y}?", None, True, ["PaymentsToAcquireBusinessesNetOfCashAcquired"]),
    ("How much debt was repaid in {Y}?", None, True, ["RepaymentsOfLongTermDebt"]),
    ("How much new long-term debt was raised in {Y}?", None, True, ["ProceedsFromIssuanceOfLongTermDebt"]),
    ("How much cash was paid for income taxes in {Y}?", None, True, ["IncomeTaxesPaidNet", "IncomeTaxesPaid"]),
    ("What dividend per share was declared in {Y}?", None, True, ["CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid"]),
    ("How large were unrecognized tax benefits at the end of {Y}?", None, False, ["UnrecognizedTaxBenefits"]),
    ("What were total future operating lease payments as of the end of {Y}?", None, False, ["LesseeOperatingLeaseLiabilityPaymentsDue"]),
    ("How much deferred revenue was recorded at the end of {Y}?", None, False, ["ContractWithCustomerLiabilityCurrent", "ContractWithCustomerLiability", "DeferredRevenueCurrent"]),
    ("How much income came from equity-method investments in {Y}?", None, True, ["IncomeLossFromEquityMethodInvestments"]),
    ("What was accumulated other comprehensive income or loss at the end of {Y}?", None, False, ["AccumulatedOtherComprehensiveIncomeLossNetOfTax"]),
    ("What was the value of treasury stock at the end of {Y}?", None, False, ["TreasuryStockValue", "TreasuryStockCommonValue"]),
]
SEG_AXES = ("StatementBusinessSegmentsAxis",)
SEG_NAMES = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenuesNetOfInterestExpense", "OperatingIncomeLoss")

def pretty_member(m):
    m = re.sub(r"(Segment)?Member$", "", m)
    m = re.sub(r"(?<=[a-z])and(?=[A-Z])", "And", m)
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", m).replace(" And ", " and ")

def numeric_questions(facts):
    ends = fiscal_ends(facts)
    if not ends:
        return []
    Y, PY = date.fromisoformat(ends[0]).year, (date.fromisoformat(ends[1]).year if len(ends) > 1 else None)
    out = []
    for cur, prior, flow, names in T:
        for wording, end, yr in ((cur, ends[0], Y), (prior, ends[1] if len(ends) > 1 else None, PY)):
            if not wording or not end:
                continue
            f = pick(facts, names, end, flow)
            if f:
                k = kind_of(f, f["name"])
                v = f["value"] * (100 if k == "percent" and abs(f["value"]) < 1.5 else 1)
                out.append(dict(q=wording.format(Y=yr, PY=yr), group="numeric", keys=[dict(value=v, kind=k)],
                                source=f"{f['name']} {f['end']}"))
    # segments: revenue / operating income per reportable segment (latest year)
    segs = {}
    for f in facts:
        seg = [m for a, m in f["dims"] if a in SEG_AXES]
        others = [(a, m) for a, m in f["dims"] if a not in SEG_AXES]
        plain = not others or others == [("ConsolidationItemsAxis", "OperatingSegmentsMember")]
        if f["end"] == ends[0] and f["name"] in SEG_NAMES and len(seg) == 1 and plain and f["value"] and f["start"]:
            segs.setdefault((f["name"] == "OperatingIncomeLoss", seg[0]), f)
    for (is_oi, mem), f in sorted(segs.items())[:10]:
        what = "operating income" if is_oi else "revenue"
        out.append(dict(q=f"How much {what} did the {pretty_member(mem)} segment report in {Y}?", group="segment",
                        keys=[dict(value=f["value"], kind="usd")], source=f"{f['name']} {mem} {f['end']}"))
    return out

def build(co, extra):
    path = sorted(glob.glob(os.path.join(ROOT, ".tenk_cache", "edgar", COMPANIES[co])))
    if not path:
        print(f"{co}: filing not downloaded yet"); return None
    facts = ix_facts(path[-1])
    qs = numeric_questions(facts)
    qs = [q for q in qs if q["keys"][0]["value"]]
    text_q = [dict(q=q, group="text", keys=[dict(phrases=p)], source="text") for q, p in extra]
    num_budget = MAX_Q - len(text_q)
    qs = qs[:num_budget] + text_q
    for i, q in enumerate(qs):
        q["id"] = f"{co}-{i + 1:03d}"
        q["split"] = "holdout" if (i + 1) % 5 == 0 else "dev"
    json.dump(qs, open(os.path.join(HERE, f"questions_{co}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{co}: {len(qs)} questions ({sum(q['group']=='numeric' for q in qs)} numeric, {sum(q['group']=='segment' for q in qs)} segment, {len(text_q)} text)")
    return qs

if __name__ == "__main__":
    from text_questions import TEXT_Q
    for co in (sys.argv[1:] or COMPANIES):
        build(co, TEXT_Q.get(co, []))


