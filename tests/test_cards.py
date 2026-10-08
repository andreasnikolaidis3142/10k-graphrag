"""Number cards, heading context, query vocabulary and the reranker-first final stage (retrieval-optimised build)."""
import os
from tenk_graphrag.cards import table_cards, HeadingContext, expand_query, xbrl_cards
from tenk_graphrag.graph_builder import build_graph
from tenk_graphrag.models import Fact
from tenk_graphrag.retrieval import Retriever, Embedder, BM25

HERE = os.path.dirname(__file__)
OFF = lambda: Embedder(model_name="definitely/not-a-model")

SEGMENT_TABLE = [["Year ended December 31,", "Consumer Banking", "Investment Bank"],
                 ["(in millions, except ratios)", "2023", "2022", "2023", "2022"],
                 ["Total net revenue", "$70,148", "$54,814", "(a)", "$48,807", "(a)", "$48,102"],
                 ["Return on equity", "38%", "29%", "13%", "14%"]]

def test_segment_table_row_becomes_a_self_describing_card():
    cards = table_cards(SEGMENT_TABLE, "Business Segment Results")
    rev = next(c for c in cards if "Total net revenue" in c)
    assert "Consumer Banking 2023: $70,148 ($70.1 billion)" in rev and "Investment Bank 2022: $48,102" in rev
    assert "(a)" not in rev                                       # footnote markers are not values
    roe = next(c for c in cards if "Return on equity" in c)
    assert "billion" not in roe                                   # a ratio is not money

def test_year_header_is_not_data_and_change_is_computed():
    cards = table_cards([["As of December 31, (in billions except ratios)"], ["2023", "2022"],
                         ["Deposits", "$2,400.7", "$2,340.2"], ["Loans-to-deposits ratio", "55%", "49%"]], "Funding")
    assert len(cards) == 2
    assert "2023: $2,400.7 ($2.4 trillion)" in cards[0] and "2023 vs 2022: +2.6%" in cards[0]

def test_rows_wider_than_the_header_do_not_crash():
    cards = table_cards([["(in millions)", "2023"], ["Revenue", "$100", "$90"], ["Cost", "50", "45"]], "Odd table")
    assert len(cards) == 2 and "$100" in cards[0]

def test_counts_and_prices_are_not_verbalised_as_dollars():
    rows = [["Year ended December 31, 2023", "Total number of shares repurchased", "Average price paid per share",
             "Aggregate purchase price (in millions)"],
            ["Full year", "69,549,259", "$142.31", "$9,898"]]
    c = table_cards(rows, "Capital actions")[0]
    assert "$9,898 ($9.9 billion)" in c and "trillion" not in c and "$142.31 (" not in c

def test_heading_context_reaches_short_sentences_and_bullets():
    h = HeadingContext()
    assert h.see("CONSUMER & COMMUNITY BANKING") and h.see("2023 compared with 2022")
    assert not h.see("Net revenue was $70.1 billion, up 28%.")
    assert h.path("Net revenue was $70.1 billion, up 28%.") == "CONSUMER & COMMUNITY BANKING > 2023 compared with 2022"
    h.see("Compensation expense increased driven by:")
    assert h.path("• an increase in employees").endswith("Compensation expense increased driven by:")

def test_query_vocabulary_expansion():
    q = expand_query("What were buybacks and the net interest margin?")
    assert "repurchase" in q and "net yield" in q
    assert expand_query("Plain question about nothing") == "Plain question about nothing"

def test_reranker_gloss_and_scope_detection():
    from tenk_graphrag.cards import gloss_query, asks_for_slice
    assert gloss_query("What was capex in 2022?") == "What was capex in 2022? (capital expenditures, payments for property, plant and equipment)"
    assert gloss_query("What was revenue?") == "What was revenue?"
    assert asks_for_slice("How much revenue did the Biopharma segment report?")
    assert asks_for_slice("What were Greater China sales?", members={"Greater China"})
    assert not asks_for_slice("What was total revenue in 2023?", members={"Greater China"})

def test_company_wide_question_prefers_the_company_total_card():
    fg = build_graph(os.path.join(HERE, "ixbrl_tagged.htm"), xbrl_min_facts=1)
    scopes = {d.get("scope") for _, d in fg.G.nodes(data=True) if d.get("kind") == "xbrl"}
    assert {"total", "slice"} <= scopes
    r = Retriever(fg, embedder=OFF())
    top = r.search("What was total revenue?", top_k=3)
    xb = [h for h in top if h["document_id"].startswith("X")]
    assert xb and xb[0]["metadata"].get("scope") == "total"

def test_table_row_scope_from_this_filings_members():
    from tenk_graphrag.cards import member_words, card_scope
    facts = [Fact(dims={"StatementBusinessSegments": "AmericasSegment"}), Fact(dims={"ProductOrService": "IPhone"}),
             Fact(dims={"FinancialInstrument": "CommercialPaper"}), Fact(dims={"ProductOrService": "SalesAndOtherOperatingRevenue"}),
             Fact(dims={"StatementBusinessSegments": "ConsumerCommunityBanking"})]
    mw = member_words(facts)
    assert mw == {"americas", "iphone", "consumer community banking"}           # no instruments, no statement lines
    assert card_scope("Segment Information | Americas: | in millions || Operating income: 2023: $60,508", mw) == "slice"
    assert card_scope("Segment Information | in millions || Total operating income: 2023: $114,301", mw) == ""
    assert card_scope("CONSUMER & COMMUNITY BANKING | in millions || Net revenue: 2023: $70,148", mw) == "slice"
    assert card_scope("BALANCE SHEETS | in millions || Commercial paper: 2023: 5,985", mw) == ""

def test_stemming_matches_plural_and_past_forms():
    assert BM25._tok("repurchases repurchased loans") == BM25._tok("repurchase repurchase loan")

def test_build_adds_table_and_xbrl_cards_and_search_finds_them():
    fg = build_graph(os.path.join(HERE, "ixbrl_tagged.htm"), xbrl_min_facts=1)
    kinds = {d.get("kind") for _, d in fg.G.nodes(data=True) if d.get("type") == "Card"}
    assert {"table", "xbrl"} <= kinds
    assert xbrl_cards(fg) and not any("{'" in t for _, t, _ in xbrl_cards(fg))      # sources read as words, not dicts
    r = Retriever(fg, embedder=OFF())
    assert r.retrieval_mode == "bm25_rerank"
    hits = r.search("What was capital expenditure?", top_k=5)
    assert any(h["document_id"][0] in "RX" for h in hits)

def test_final_stage_keeps_a_short_best_hit():
    fg = build_graph(os.path.join(HERE, "apple_like.htm"))
    fg.add_chunk("Total net revenue was $158.1 billion, up 23%.", "Item 7 MD&A", 950, [], ctx="Executive Overview")
    r = Retriever(fg, embedder=OFF())
    ids = [nv["id"] for nv in r.retrieve(r.plan("What was total net revenue?"))["narrative"]]
    assert "T00950" in ids
    assert any("[Executive Overview]" in nv["text"] for nv in r.retrieve(r.plan("What was total net revenue?"))["narrative"])

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
