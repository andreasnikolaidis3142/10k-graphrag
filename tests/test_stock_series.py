"""A balance (stock) series must show point-in-time values only: a note/table row of a stock concept that was read with a
fiscal-year (flow) period must not be mixed into it (Apple: 'Total term debt' $105B shown next to non-current debt $95B)."""
from tenk_graphrag.models import Fact
from tenk_graphrag.retrieval import Retriever, Embedder
from tests.test_balance_sheet import build

def _with_debt_note_row():
    fg = build()                       # XBRL balance sheet: non-current term debt $95,281M / $98,959M
    flow = fg.add_fact(Fact(concept="LongTermDebtNoncurrent", label="Total term debt", value=105_103e6, unit="USD", precision=1e6,
                            ptype="duration", period="FY2023", end="2023-09-30", months=12, fy=2023, source="table", stmt="DEBT",
                            location="table#40", is_total=True))
    return fg, flow

def test_stock_series_excludes_flow_labelled_facts_of_a_stock_concept():
    fg, flow = _with_debt_note_row()
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    items = [n for _, n in r._facts_for("LongTermDebtNoncurrent", None)]
    assert flow not in items
    assert [fg.F(n)["period"] for n in items] == ["@2022-09-24", "@2023-09-30"]

def test_context_shows_the_balance_sheet_yoy_not_the_note_total():
    fg, flow = _with_debt_note_row()
    r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    ctx = r.build_context(r.retrieve(r.plan("Is the balance sheet healthy? Look at liquidity and debt.")))
    assert f"[{flow}]" not in ctx and "$105.10B" not in ctx

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
