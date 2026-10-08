"""
Ask a question and save the answer to files (no terminal copy-paste, no encoding problems).

  python ask_to_file.py aapl_2023.json "Which segment drove revenue growth?" answer
    -> answer.json   full answer incl. sources (UTF-8)
    -> answer.md     readable version: summary, drivers, red flags, and a one-line source for every cited number
"""
import json, pathlib, sys
from tenk_graphrag.graph_builder import FilingGraph
from tenk_graphrag.retrieval import Retriever
from tenk_graphrag import answer

def _bullets(items):
    return "\n".join(f"- {x}" for x in (items or [])) or "- (none)"

def to_markdown(out):
    a = out.get("answer") or {}
    lines = [f"# {out['question']}", "", f"*model: {out['model']} | ungrounded numbers: {out['ungrounded'] or 'none'} | missing contributors: {out.get('coverage_gaps') or 'none'} | uncited claims: {len(out.get('uncited_claims') or [])}*", "",
             "## Summary", a.get("summary", ""), "", f"**Status:** {a.get('status', '')}", "", "## Key numbers"]
    for k in a.get("key_numbers", []):
        lines.append(f"- {k.get('metric')} ({k.get('period')}): **{k.get('value')}**  [{k.get('fact_id')}]")
    lines += ["", "## Drivers", _bullets(a.get("drivers")), "", "## Risks and red flags", _bullets(a.get("risks_and_red_flags")),
              "", "## Data quality", _bullets(a.get("data_quality_notes")), "", "## Outlook"]
    o = a.get("outlook") or {}
    lines += [f"- Actuals: {o.get('actuals_view', '')}", f"- Guidance: {o.get('forward_looking_guidance', '')}", "",
              "## Follow-up checks", _bullets(a.get("follow_up_checks")), "", "## Sources (where each cited number came from)"]
    for fid, s in (a.get("sources") or {}).items():
        head = f"- **{fid}** " + (f"{s.get('value')} {s.get('concept')} {s.get('period')}" if s.get("value") else "")
        if s.get("slice"): head += f" [{s['slice']}]"
        if s.get("note"): head += f" ({s['note']})"
        lines.append(f"{head} - *{s.get('source')}*: {s.get('where')}")
        for t in s.get("also_displayed_in", []) + s.get("also_in", []):
            lines.append(f"    - also shown in {t}")
        if s.get("inputs"):
            lines.append(f"    - computed from {', '.join(s['inputs'])}")
    return "\n".join(lines) + "\n"

def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        sys.exit(__doc__)
    graph, question = argv[0], argv[1]
    base = argv[2] if len(argv) > 2 else "answer"
    fg = FilingGraph.load(graph)
    res = answer.ask(fg, question, retriever=Retriever(fg, index_path=graph + ".dense"))
    out = dict(question=question, model=res["model"], ungrounded=res["ungrounded"], coverage_gaps=res.get("coverage_gaps", []), uncited_claims=res.get("uncited_claims", []), stripped_pseudo_citations=res.get("stripped_pseudo_citations", 0), answer=res["answer"])
    pathlib.Path(base + ".json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    pathlib.Path(base + ".md").write_text(to_markdown(out), encoding="utf-8")
    print(f"wrote {base}.json and {base}.md  (model: {res['model']}, ungrounded: {res['ungrounded'] or 'none'})")

if __name__ == "__main__":
    main()
