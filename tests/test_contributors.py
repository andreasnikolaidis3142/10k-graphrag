"""Evidence ordering/wording for attribution, readable slice names, and the 'did the answer mention the biggest mover?' check."""
import os
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.retrieval import Retriever, Embedder, slice_label
from tenk_graphrag.answer import missing_contributors, ask
from tenk_graphrag import llm

HERE = os.path.dirname(__file__)
FG = build_graph(os.path.join(HERE, "apple_like.htm"))
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

def _ev(q="Which segment drove the change in revenue?"):
    r = Retriever(FG, embedder=OFFLINE()); ev = r.retrieve(r.plan(q)); return r, ev, r.build_context(ev)

def test_components_are_ordered_by_size_of_change_and_the_top_one_is_marked():
    _, ev, ctx = _ev()
    firsts = {a["axis"]: a["children"][0]["d"]["dims"] for a in ev["attribution"]}
    assert firsts["product"] == {"product": "Mac"} and firsts["segment"] == {"segment": "Americas"}
    assert ctx.count("<- LARGEST CONTRIBUTOR TO THE CHANGE") == 2

def test_offsets_are_described_as_offsets_not_negative_shares():
    _, _, ctx = _ev()
    assert "moves AGAINST the total change (offsets 64% of it)" in ctx and "-64% of the total change" not in ctx

def test_slice_names_come_from_the_table_row_or_group_when_available():
    d = {"dims": {"StatementBusinessSegments": "AmericasSegment"}, "source": "ixbrl", "label": "x",
         "appears_in": [{"row": "Net sales", "group": "Americas", "table_no": 3}]}
    assert slice_label(d) == "Americas"
    d2 = {"dims": {"ProductOrService": "WearablesHomeandAccessories"}, "source": "ixbrl", "label": "x",
          "appears_in": [{"row": "Wearables, Home and Accessories (1)", "group": "", "table_no": 8}]}
    assert slice_label(d2) == "Wearables, Home and Accessories"
    assert slice_label({"dims": {"StatementBusinessSegments": "RestOfAsiaPacificSegment"}, "source": "ixbrl", "label": "x"}) == "Rest Of Asia Pacific"

def test_missing_biggest_mover_is_detected_and_name_or_id_satisfies_it():
    _, ev, _ = _ev()
    gaps = missing_contributors(ev, {"summary": "Europe moved slightly."})
    assert {g["label"] for g in gaps} == {"Mac", "Americas"}
    assert missing_contributors(ev, {"summary": "Mac and Americas drove it."}) == []
    top_ids = [a["children"][0]["id"] for a in ev["attribution"]]
    assert missing_contributors(ev, {"summary": " ".join(f"[{i}]" for i in top_ids)}) == []

def test_ask_runs_one_repair_pass_when_the_biggest_mover_is_missing():
    calls = []
    answers = [({"summary": "Europe moved slightly."}, "mock"), ({"summary": "Mac and Americas drove the change."}, "mock")]
    original = llm.chat_json
    llm.chat_json = lambda msgs, **k: (calls.append(msgs[-1]["content"]), answers[len(calls) - 1])[1]
    try:
        res = ask(FG, "Which segment drove the change in revenue?", retriever=Retriever(FG, embedder=OFFLINE()))
    finally:
        llm.chat_json = original
    assert len(calls) == 2 and "largest contributor" in calls[1] and "Americas" in calls[1]
    assert res["coverage_gaps"] == [] and "Mac and Americas" in res["answer"]["summary"]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
