"""Regression tests for the problems found in a real Apple 10-K answer."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder

FG = build_graph(os.path.join(os.path.dirname(__file__), "apple_like.htm"))

def val(concept, period, dims=None):
    return next((d["value"] for _, d in FG.facts(lambda d: d["concept"] == concept and d["period"] == period
                                                  and d["dims"] == (dims or {}) and d["source"] == "table")), None)

def test_segment_name_as_subheader_gets_dims_not_consolidated():
    assert val("Revenues", "FY2023") == 383_285e6                                   # true total untouched
    assert val("Revenues", "FY2023", {"segment": "Americas"}) == 162_560e6
    assert val("OperatingIncomeLoss", "FY2022", {"segment": "Rest of Asia Pacific"}) == 10_417e6
    assert val("OperatingIncomeLoss", "FY2022") == 119_437e6                        # the "$10.42B anomaly" is gone

def test_no_pseudo_segments_or_key_conflicts():
    assert not [1 for _, d in FG.facts(lambda d: d["dims"].get("segment") == "Operating income")]
    assert not [1 for _, d in FG.facts(lambda d: "conflict_same_key" in d["flags"]) ]

def test_segments_roll_up_to_total_without_a_total_row():
    tot = next(n for n, d in FG.facts(lambda d: d["concept"] == "Revenues" and d["period"] == "FY2023" and not d["dims"] and d["source"] == "table"))
    kids = [FG.F(u)["dims"] for u, _, k in FG.G.in_edges(tot, keys=True) if k == "ROLLS_UP_TO"]
    assert sum(1 for k in kids if "segment" in k) == 5 and sum(1 for k in kids if "product" in k) == 5

def test_x_percent_or_dollar_amount_is_a_change_not_a_level():
    t = {d["label"]: d for _, d in FG.facts(lambda d: d["source"] == "text")}
    assert t["$11.0 billion"]["role"] == "change_abs" and t["$11.0 billion"]["value"] == -11.0e9
    assert t["$240 million"]["value"] == 240e6

def test_segment_sentences_are_checked_against_that_segment_not_the_total():
    texts = [d for _, d in FG.facts(lambda d: d["source"] == "text")]
    assert texts and all("verified_by_table" in d["flags"] for d in texts)
    assert not [1 for d in texts if "narrative_mismatch" in d["flags"]]

def test_unknown_slice_is_marked_unresolved_not_mismatch():
    from tenk_graphrag.narrative import extract_numbers
    from tenk_graphrag.models import Fact
    f = extract_numbers("Wearables net sales decreased 2% or $1.4 billion during 2023.", dict(fy=2023, fy_end_month=9, fy_end_day=30), "x", 0)
    fg = build_graph(os.path.join(os.path.dirname(__file__), "sample_10k.htm"))      # a graph with no 'Wearables' member
    for x in f: fg.add_fact(x)
    fg.reconcile_narrative()
    assert all("scope_unresolved" in d["flags"] for _, d in fg.facts(lambda d: d["source"] == "text" and "Wearables" in d["context"]))

def test_attribution_shows_each_segments_share_of_the_change():
    r = Retriever(FG, embedder=Embedder(model_name="definitely/not-a-model"))
    ctx = r.build_context(r.retrieve(r.plan("Which segment drove the change in revenue?")))
    assert "of the total change" in ctx and "Americas" in ctx

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
