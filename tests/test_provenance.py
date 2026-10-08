"""Provenance (where did each number come from?) and XBRL-first behaviour."""
import os
from tenk_graphrag.graph_builder import build_graph, FilingGraph
from tenk_graphrag.answer import build_sources
from tenk_graphrag.retrieval import Retriever, Embedder
from tenk_graphrag.models import Fact

HERE = os.path.dirname(__file__)
TAGGED = os.path.join(HERE, "ixbrl_tagged.htm")
SAMPLE = os.path.join(HERE, "sample_10k.htm")

def _one(fg, **kw):
    return next((n, d) for n, d in fg.facts(lambda d: all(d.get(k) == v for k, v in kw.items())))

def test_table_numbers_know_their_table_title_row_and_column():
    fg = build_graph(SAMPLE)
    n, d = _one(fg, concept="Revenues", period="FY2023", source="table", dims={})
    assert d["table_no"] >= 1 and d["table_title"] == "CONSOLIDATED STATEMENTS OF OPERATIONS" and d["column"] == "2023"
    s = build_sources(fg, f"[{n}]")[n]
    assert s["source"] == "table" and 'table #' in s["where"] and "CONSOLIDATED STATEMENTS OF OPERATIONS" in s["where"] and 'row "Net sales"' in s["where"]

def test_same_number_in_two_tables_is_one_node_that_remembers_both():
    fg = build_graph(SAMPLE)
    n, d = _one(fg, concept="Revenues", period="FY2023", source="table", dims={})
    assert any("table #" in x for x in d.get("also_in", []))

def test_prose_and_computed_numbers_say_so():
    fg = build_graph(SAMPLE)
    t, _ = _one(fg, source="text", concept="Revenues", role="level")
    g, _ = _one(fg, concept="GrossMarginPct", period="FY2023", source="derived")
    src = build_sources(fg, f"{t} {g}")
    assert src[t]["source"] == "prose" and "Net sales increased" in src[t]["where"]
    assert src[g]["source"] == "computed" and src[g]["inputs"] and "table #" in str(src[g]["input_sources"])

def test_xbrl_first_is_on_for_tagged_filings_and_off_for_untagged():
    assert build_graph(TAGGED, xbrl_min_facts=1).meta["xbrl_first"] is True
    assert build_graph(SAMPLE).meta["xbrl_first"] is False

def test_tagged_table_numbers_become_the_xbrl_fact_not_a_duplicate():
    fg = build_graph(TAGGED, xbrl_min_facts=1)
    dup = [1 for _, d in fg.facts(lambda d: d["concept"] == "Revenues" and d["value"] == 383_285e6 and d["source"] == "table")]
    assert not dup
    n, d = _one(fg, concept="Revenues", period="FY2023", source="ixbrl", dims={})
    titles = {a["table_title"] for a in d["appears_in"]}
    assert {"CONSOLIDATED STATEMENTS OF OPERATIONS", "Segment Information"} <= titles

def test_segment_members_are_xbrl_facts_with_their_table_recorded_and_roll_up():
    fg = build_graph(TAGGED, xbrl_min_facts=1)
    am = next(n for n, d in fg.facts(lambda d: d["source"] == "ixbrl" and d["period"] == "FY2023" and "Americas" in d["dims"].values()))
    assert any(a["table_title"] == "Segment Information" for a in fg.F(am)["appears_in"])
    tot, _ = _one(fg, concept="Revenues", period="FY2023", source="ixbrl", dims={})
    assert am in [u for u, _, k in fg.G.in_edges(tot, keys=True) if k == "ROLLS_UP_TO"]

def test_rollup_component_edges_use_resolved_fact_concepts():
    fg = FilingGraph()
    rows = []
    for group_concept, fact_concept, value, is_total in (
        ("custom:current", "CurrentRevenue", 2, False),
        ("custom:deferred", "DeferredRevenue", 3, False),
        ("custom:total", "TotalRevenue", 5, True),
    ):
        fact = Fact(concept=fact_concept, label=fact_concept, value=value, precision=1, period="FY2023")
        fact.id = fg.add_fact(fact)
        rows.append({"concept": group_concept, "facts": {"FY2023": fact}, "is_total": is_total, "dims": {}})

    fg.infer_rollups(rows)

    assert fg.G.has_edge("c:CurrentRevenue", "c:TotalRevenue", key="COMPONENT_OF")
    assert fg.G.has_edge("c:DeferredRevenue", "c:TotalRevenue", key="COMPONENT_OF")
    assert all("type" in data for _, data in fg.G.nodes(data=True))

def test_untagged_mdna_table_cannot_override_xbrl():
    fg = build_graph(TAGGED, xbrl_min_facts=1)
    live = [d for _, d in fg.facts(lambda d: d["concept"] == "OperatingIncomeLoss" and d["period"] == "FY2022" and not d["dims"] and d["role"] == "level")]
    assert len(live) == 1 and live[0]["source"] == "ixbrl" and live[0]["value"] == 119_437e6
    assert [1 for _, d in fg.facts(lambda d: d["source"] == "table" and d["role"] == "shadowed")]

def test_xbrl_sources_name_the_tag_and_every_table_that_shows_it():
    fg = build_graph(TAGGED, xbrl_min_facts=1)
    n, _ = _one(fg, concept="Revenues", period="FY2023", source="ixbrl", dims={})
    s = build_sources(fg, f"[{n}]")[n]
    assert s["source"] == "XBRL" and "us-gaap:Revenues" in s["where"] and any("table #" in x for x in s["also_displayed_in"])

def test_printed_sign_survives_xbrl_adoption():
    fg = build_graph(TAGGED, xbrl_min_facts=1)
    _, d = _one(fg, concept="PaymentsToAcquirePropertyPlantAndEquipment", period="FY2023", source="ixbrl")
    assert d["value"] == 300e6 and d["parens_negative"] is True

def test_evidence_lines_show_the_table_for_table_facts():
    fg = build_graph(SAMPLE); r = Retriever(fg, embedder=Embedder(model_name="definitely/not-a-model"))
    ctx = r.build_context(r.retrieve(r.plan("revenue trend")))
    assert '(table 1: CONSOLIDATED STATEMENTS OF OPERATIONS)' in ctx

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
