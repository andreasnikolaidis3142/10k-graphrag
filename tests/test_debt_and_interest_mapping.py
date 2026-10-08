"""Short-term borrowings and current maturities of long-term debt are different balance-sheet lines: both belong in total debt
(they used to collapse onto one concept, so total debt silently dropped one). Interest on debt tagged InterestExpenseDebt feeds
interest coverage."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.taxonomy import canonical
from tests.test_balance_sheet import nf, inst

DUR = ('<xbrli:context id="d"><xbrli:entity><xbrli:identifier scheme="x">1</xbrli:identifier></xbrli:entity><xbrli:period>'
       '<xbrli:startDate>2023-02-01</xbrli:startDate><xbrli:endDate>2024-01-31</xbrli:endDate></xbrli:period></xbrli:context>')

def _build():
    rows = [("Short-term borrowings", "ShortTermBorrowings", 878), ("Long-term debt due within one year", "LongTermDebtCurrent", 3447),
            ("Long-term debt", "LongTermDebtNoncurrent", 36132), ("Cash and cash equivalents", "CashAndCashEquivalentsAtCarryingValue", 9867),
            ("Total shareholders' equity", "StockholdersEquity", 83861)]
    body = "".join(f'<tr><td>{l}</td><td>{nf("us-gaap:" + n, "i", f"{v:,}")}</td></tr>' for l, n, v in rows)
    html = (f'<html><body><ix:header><ix:resources>{inst("i", "2024-01-31")}{DUR}<xbrli:unit id="usd"><xbrli:measure>iso4217:USD'
            f'</xbrli:measure></xbrli:unit></ix:resources></ix:header><p>CONSOLIDATED BALANCE SHEETS</p><p>(In millions)</p>'
            f'<table><tr><td></td><td>January 31, 2024</td></tr>{body}</table><p>CONSOLIDATED STATEMENTS OF INCOME</p>'
            f'<table><tr><td></td><td>2024</td></tr><tr><td>Operating income</td><td>{nf("us-gaap:OperatingIncomeLoss", "d", "27,012")}</td></tr>'
            f'<tr><td>Interest: Debt</td><td>{nf("us-gaap:InterestExpenseDebt", "d", "2,259")}</td></tr></table></body></html>')
    p = os.path.join(tempfile.mkdtemp(), "f.htm"); open(p, "w").write(html)
    return build_graph(p, xbrl_min_facts=1)

def _derived(fg, concept):
    return {d["period"]: d["value"] for _, d in fg.facts(lambda d: d["concept"] == concept and d["source"] == "derived")}

def test_short_term_borrowings_is_its_own_concept():
    assert canonical("us-gaap:ShortTermBorrowings") == "ShortTermBorrowings"
    assert canonical("us-gaap:LongTermDebtCurrent") == "LongTermDebtCurrent"

def test_total_debt_counts_borrowings_and_current_maturities():
    d = _derived(_build(), "TotalDebt")
    assert round(d["@2024-01-31"] / 1e6) == 878 + 3447 + 36132

def test_interest_expense_on_debt_feeds_coverage():
    assert canonical("us-gaap:InterestExpenseDebt") == "InterestExpense"
    cov = _derived(_build(), "InterestCoverage")
    assert round(cov["FY2024"], 1) == round(27012 / 2259, 1)

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
