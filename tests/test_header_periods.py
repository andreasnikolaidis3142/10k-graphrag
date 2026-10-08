"""Table header periods: spelled-out month counts ('Three Months Ended') must parse, not crash the build."""
from tenk_graphrag.table_parser import parse_header_periods

def test_word_month_count_in_header_parses():
    ps = parse_header_periods(["Three Months Ended December 31, 2023"], "IS", 12, 31)
    assert ps and ps[0]["months"] == 3 and ps[0]["ptype"] == "duration"

def test_digit_month_count_still_parses():
    ps = parse_header_periods(["6 months ended June 30, 2023"], "IS", 12, 31)
    assert ps and ps[0]["months"] == 6

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
