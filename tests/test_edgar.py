"""Offline tests for SEC EDGAR 10-K retrieval."""
from contextlib import redirect_stdout
from io import StringIO

from tenk_graphrag import edgar


class FakeResponse:
    def __init__(self, data=None, content=b"", status_code=200):
        self.data = data
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        return response(url) if callable(response) else response


def _filings(*rows):
    fields = {
        "accessionNumber": "accession",
        "form": "form",
        "filingDate": "filing_date",
        "reportDate": "report_date",
        "primaryDocument": "primary_doc",
    }
    return {"filings": {"recent": {
        field: [row[key] for row in rows] for field, key in fields.items()
    }}}


def _company_data():
    return {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
            "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corporation"}}


def _set_offline(monkeypatch):
    monkeypatch.setattr(edgar.config, "SEC_USER_AGENT", "Test User test@example.com")
    monkeypatch.setattr(edgar.time, "sleep", lambda _: None)
    monkeypatch.setattr(edgar, "_last_request_at", 0.0)


def test_resolve_ticker_name_and_numeric_cik(monkeypatch):
    _set_offline(monkeypatch)
    for query in ("aapl", "Apple Inc."):
        result = edgar.resolve_company(query, FakeSession([FakeResponse(_company_data())]))
        assert result == {"cik": 320193, "ticker": "AAPL", "title": "Apple Inc."}
    assert edgar.resolve_company("0000320193") == {
        "cik": 320193, "ticker": "", "title": ""
    }


def test_ambiguous_company_name_requires_ticker(monkeypatch):
    _set_offline(monkeypatch)
    data = {"0": {"cik_str": 1, "ticker": "ABC", "title": "Example Holdings"},
            "1": {"cik_str": 2, "ticker": "XYZ", "title": "Example Industries"}}
    output = StringIO()
    try:
        with redirect_stdout(output):
            edgar.resolve_company("example", FakeSession([FakeResponse(data)]))
        assert False, "ambiguous query should fail"
    except ValueError as exc:
        assert "use the exact ticker" in str(exc)
    assert "ABC: Example Holdings" in output.getvalue()


def test_missing_user_agent_stops_before_network(monkeypatch):
    monkeypatch.setattr(edgar.config, "SEC_USER_AGENT", "")
    session = FakeSession([])
    try:
        edgar.resolve_company("AAPL", session)
        assert False, "missing User-Agent should fail"
    except ValueError as exc:
        assert "SEC_USER_AGENT" in str(exc)
    assert not session.calls


def test_select_fiscal_year_and_filing_year_skips_amendments():
    filings = [
        {"form": "10-K", "report_date": "2023-09-30", "filing_date": "2024-11-03", "accession": "one"},
        {"form": "10-K", "report_date": "2022-09-24", "filing_date": "2022-10-28", "accession": "two"},
        {"form": "10-K/A", "report_date": "2023-09-30", "filing_date": "2023-11-10", "accession": "amend"},
    ]
    assert edgar.select_filing(filings, 2023)["accession"] == "one"
    assert edgar.select_filing(filings, 2024, by_filing_year=True)["accession"] == "one"
    try:
        edgar.select_filing(filings, 2021)
        assert False, "missing year should fail"
    except ValueError as exc:
        assert "Available fiscal years: 2022, 2023" in str(exc)


def test_select_amendments_and_variants_only_when_enabled():
    filings = [
        {"form": "10-K/A", "report_date": "2023-12-31", "filing_date": "2024-02-01", "accession": "amend"},
        {"form": "10-KT", "report_date": "2023-12-31", "filing_date": "2024-02-02", "accession": "variant"},
    ]
    try:
        edgar.select_filing(filings, 2023)
        assert False, "ineligible forms should fail"
    except ValueError:
        pass
    assert edgar.select_filing(filings, 2023, include_amendments=True)["accession"] == "amend"
    assert edgar.select_filing(filings, 2023, include_variants=True)["accession"] == "variant"


def test_download_constructs_archive_url_and_cik_and_accession(monkeypatch, tmp_path):
    _set_offline(monkeypatch)
    row = {"accession": "0000320193-23-000106", "form": "10-K", "filing_date": "2023-11-03",
           "report_date": "2023-09-30", "primary_doc": "aapl-20230930.htm"}
    session = FakeSession([
        FakeResponse(_company_data()),
        FakeResponse(_filings(row)),
        FakeResponse(content=b"<html>filing</html>"),
    ])
    path = edgar.download_10k("AAPL", 2023, out_dir=tmp_path, session=session)
    assert path == tmp_path / "AAPL_2023_0000320193-23-000106.htm"
    assert session.calls[-1][0] == (
        "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm"
    )
    assert session.calls[-1][1]["headers"]["User-Agent"] == "Test User test@example.com"


def test_cache_hit_skips_network_and_refresh_downloads_again(monkeypatch, tmp_path):
    _set_offline(monkeypatch)
    row = {"accession": "0000320193-23-000106", "form": "10-K", "filing_date": "2023-11-03",
           "report_date": "2023-09-30", "primary_doc": "aapl.htm"}
    initial = FakeSession([
        FakeResponse(_company_data()), FakeResponse(_filings(row)), FakeResponse(content=b"first")
    ])
    path = edgar.download_10k("AAPL", 2023, out_dir=tmp_path, session=initial)
    cached_session = FakeSession([])
    assert edgar.download_10k("AAPL", 2023, out_dir=tmp_path, session=cached_session) == path
    assert not cached_session.calls

    refresh_session = FakeSession([
        FakeResponse(_company_data()), FakeResponse(_filings(row)), FakeResponse(content=b"refreshed")
    ])
    edgar.download_10k("AAPL", 2023, out_dir=tmp_path, refresh=True, session=refresh_session)
    assert len(refresh_session.calls) == 3
    assert path.read_bytes() == b"refreshed"


def test_download_falls_back_to_older_submission_files(monkeypatch, tmp_path):
    _set_offline(monkeypatch)
    recent = {"accession": "0000320193-24-000001", "form": "10-K", "filing_date": "2024-02-01",
              "report_date": "2023-12-31", "primary_doc": "recent.htm"}
    older = {"accession": "0000320193-19-000001", "form": "10-K", "filing_date": "2019-02-01",
             "report_date": "2018-12-31", "primary_doc": "older.htm"}
    submissions = _filings(recent)
    submissions["filings"]["files"] = [{"name": "CIK0000320193-submissions-001.json"}]
    session = FakeSession([
        FakeResponse(_company_data()), FakeResponse(submissions),
        FakeResponse(_filings(older)), FakeResponse(content=b"old filing"),
    ])
    path = edgar.download_10k("AAPL", 2018, out_dir=tmp_path, session=session)
    assert session.calls[2][0].endswith("/CIK0000320193-submissions-001.json")
    assert path.name.startswith("AAPL_2018_")


def test_429_retries_then_succeeds(monkeypatch):
    _set_offline(monkeypatch)
    session = FakeSession([FakeResponse(status_code=429), FakeResponse(_company_data())])
    assert edgar.resolve_company("AAPL", session)["ticker"] == "AAPL"
    assert len(session.calls) == 2
    assert all(call[1]["headers"]["User-Agent"] for call in session.calls)


if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
