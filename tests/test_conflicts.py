"""Regression tests for the 'FY2022 operating income $10.42B' anomaly: slice tables read as company-wide numbers."""
import os, tempfile
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.signals import get_series, series_findings
from tenk_graphrag.retrieval import Retriever, Embedder

HERE = os.path.dirname(__file__)
OFFLINE = lambda: Embedder(model_name="definitely/not-a-model")

def _build(html_path):
    return build_graph(html_path)

def _active(fg, concept, period):
    return [d for _, d in fg.facts(lambda d: d["concept"] == concept and d["period"] == period and not d["dims"]
                                   and d["source"] == "table" and d["role"] == "level")]

def _with_scale_caption():
    """Same filing, but the MD&A table DOES have '(In millions)', so scale is not what saves us."""
    html = open(os.path.join(HERE, "apple_mdna.htm")).read().replace("<p>Rest of Asia Pacific</p>", "<p>Rest of Asia Pacific</p>\n<p>(In millions)</p>")
    p = os.path.join(tempfile.mkdtemp(), "mdna_scaled.htm"); open(p, "w").write(html); return p

def test_segment_table_without_scale_is_set_aside():
    fg = _build(os.path.join(HERE, "apple_mdna.htm"))
    act = _active(fg, "OperatingIncomeLoss", "FY2022")
    assert len(act) == 1 and act[0]["value"] == 119_437e6
    assert [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]

def test_segment_table_with_scale_is_still_set_aside_by_statement_priority():
    fg = _build(_with_scale_caption())
    act = _active(fg, "OperatingIncomeLoss", "FY2022")
    assert len(act) == 1 and act[0]["value"] == 119_437e6                  # NOT the 10,417 segment figure
    assert _active(fg, "Revenues", "FY2023")[0]["value"] == 383_285e6

def test_series_has_one_point_per_period_and_no_fake_findings():
    fg = _build(_with_scale_caption())
    r = Retriever(fg, embedder=OFFLINE())
    periods = [fg.F(n)["period"] for _, n in r._facts_for("OperatingIncomeLoss", None)]
    assert periods == ["FY2021", "FY2022", "FY2023"]
    text = " ".join(series_findings(fg, get_series(fg, "OperatingIncomeLoss")))
    assert "-100" not in text and "INFLECTION" not in text

def test_context_tells_the_model_that_duplicates_were_set_aside():
    fg = _build(_with_scale_caption())
    r = Retriever(fg, embedder=OFFLINE())
    ctx = r.build_context(r.retrieve(r.plan("operating income trend")))
    assert "set aside" in ctx

def test_clean_filing_has_nothing_shadowed():
    fg = build_graph(os.path.join(HERE, "apple_like.htm"))
    assert not [1 for _, d in fg.facts(lambda d: d["role"] == "shadowed")]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
