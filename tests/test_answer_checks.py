"""Regression tests for the second Apple answer: multi-year sentences, fact-id false positives, mismatch severity."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.narrative import extract_numbers
from tenk_graphrag.answer import numbers_in, check_grounding, unknown_citations
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag.signals import red_flags

DOC = dict(fy=2023, fy_end_month=9, fy_end_day=30)
SAMPLE = os.path.join(os.path.dirname(__file__), "sample_10k.htm")


def test_respectively_aligns_each_amount_to_its_year():
    s = "Depreciation expense on property, plant and equipment was $8.7 billion, $8.5 billion and $9.5 billion during 2023, 2022 and 2021, respectively."
    got = {f.label: f.period for f in extract_numbers(s, DOC, "Item 8", 0)}
    assert got == {"$8.7 billion": "FY2023", "$8.5 billion": "FY2022", "$9.5 billion": "FY2021"}


def test_list_of_amounts_is_not_a_range_but_between_is():
    lst = extract_numbers("It was $8.5 billion and $9.5 billion.", DOC, "x", 0)
    assert lst and not any("guidance_range" in f.flags for f in lst)
    rng = extract_numbers("We expect costs between $5 and $7 million.", DOC, "x", 0)
    assert sum("guidance_range" in f.flags for f in rng) == 2


def test_fact_ids_are_not_numbers():
    assert numbers_in('{"fact_id": "F00862", "note": "see [F01005] and T00004"}') == []


def test_invented_citation_is_reported():
    fg = build_graph(SAMPLE); r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    ctx = r.build_context(r.retrieve(r.plan("revenue trend")))
    assert unknown_citations(ctx, "see [F99999]") == ["F99999"]
    assert "unknown-id:F99999" in check_grounding(fg, ctx, "Revenue was $4.62B [F99999]")
    assert check_grounding(fg, ctx, {"fact_id": "F00013", "value": "$4.62B"}) == []


def test_level_mismatch_is_low_severity_change_mismatch_stays_medium():
    fg = build_graph(SAMPLE)
    for f in extract_numbers("Net income was $999 million in 2023.", dict(fy=2023, fy_end_month=12, fy_end_day=31), "x", 99):
        fg.add_fact(f)
    fg.reconcile_narrative()
    codes = {(x["code"], x["severity"]) for x in red_flags(fg)}
    assert ("NARRATIVE_DIFFERS", "low") in codes          # level in prose vs statement line: may be a narrower item
    assert ("NARRATIVE_MISMATCH", "medium") in codes      # the planted '150 basis points' change claim


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
