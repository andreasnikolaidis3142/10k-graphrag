"""Download and select company 10-K filings from SEC EDGAR."""
import json
import logging
import re
import time
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from . import config

log = logging.getLogger("tenk_graphrag.edgar")

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
_last_request_at = 0.0


def _get_json(url: str, session: requests.Session) -> Any:
    """Fetch SEC JSON with a descriptive identity, throttling, and retry handling."""
    global _last_request_at
    user_agent = config.SEC_USER_AGENT.strip()
    if not user_agent:
        raise ValueError(
            "SEC_USER_AGENT is missing. Add SEC_USER_AGENT=\"Your Name your@email.com\" to your .env file."
        )
    for attempt in range(4):
        wait = 0.15 - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        try:
            response = session.get(url, headers={"User-Agent": user_agent}, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError(f"SEC request failed for {url}: {exc}. Check your network and try again.") from exc
        _last_request_at = time.monotonic()
        status = response.status_code
        if status in (403, 429):
            if attempt < 3:
                delay = max(0.15, 2 ** attempt)
                log.warning("SEC returned HTTP %s; retrying in %s seconds", status, delay)
                time.sleep(delay)
                continue
            raise RuntimeError(
                f"SEC returned HTTP {status} after 3 retries. Wait before retrying and verify SEC_USER_AGENT."
            )
        try:
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"SEC request failed for {url}: {exc}. Check the URL and try again.") from exc
        except (ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"SEC returned invalid JSON for {url}. Try again later.") from exc
    raise RuntimeError(f"SEC request failed for {url} after retries.")


def _records(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert parallel EDGAR filing arrays into individual filing records."""
    recent = data.get("filings", {}).get("recent", data)
    accessions = recent.get("accessionNumber", [])
    fields = ("form", "filingDate", "reportDate", "primaryDocument")
    result = []
    for index, accession in enumerate(accessions):
        row = {"accession": accession}
        for field in fields:
            values = recent.get(field, [])
            row[{"form": "form", "filingDate": "filing_date", "reportDate": "report_date",
                 "primaryDocument": "primary_doc"}[field]] = values[index] if index < len(values) else ""
        result.append(row)
    return result


def _request_session(session: requests.Session | None) -> requests.Session:
    return session if session is not None else requests.Session()


def resolve_company(query: str, session: requests.Session | None = None) -> dict[str, Any]:
    """Resolve a ticker, company name, or numeric CIK to SEC company metadata."""
    query = query.strip()
    if not query:
        raise ValueError("Company is empty. Supply a ticker, company name, or numeric CIK.")
    if query.isdigit():
        return {"cik": int(query), "ticker": "", "title": ""}

    records = _get_json(_TICKERS_URL, _request_session(session))
    companies = list(records.values()) if isinstance(records, dict) else records
    exact_ticker = [item for item in companies if str(item.get("ticker", "")).casefold() == query.casefold()]
    exact_name = [item for item in companies if str(item.get("title", "")).casefold() == query.casefold()]
    matches = exact_ticker or exact_name
    if not matches:
        matches = [item for item in companies if query.casefold() in str(item.get("title", "")).casefold()]
    if len(matches) > 1:
        candidates = ", ".join(f"{item.get('ticker', '?')}: {item.get('title', '?')}" for item in matches)
        print(f"Company name is ambiguous. Matching SEC entries: {candidates}")
        raise ValueError("Company name matches multiple companies; use the exact ticker instead.")
    if len(matches) != 1:
        raise ValueError(f"No unique SEC company matched {query!r}. Check the name or use its ticker/CIK.")
    item = matches[0]
    return {"cik": int(item["cik_str"]), "ticker": str(item.get("ticker", "")),
            "title": str(item.get("title", ""))}


def _eligible(filing: dict[str, Any], include_amendments: bool, include_variants: bool) -> bool:
    form = str(filing.get("form", "")).upper()
    base = form[:-2] if form.endswith("/A") else form
    if form.endswith("/A"):
        if not include_amendments:
            return False
    elif form not in ("10-K", "10-K405", "10-KT"):
        return False
    return base in ("10-K", "10-K405") or (base == "10-KT" and include_variants)


def _available_years(filings: list[dict[str, Any]], include_amendments: bool,
                     include_variants: bool) -> list[int]:
    years = set()
    for filing in filings:
        if _eligible(filing, include_amendments, include_variants):
            try:
                years.add(date.fromisoformat(filing["report_date"]).year)
            except (KeyError, TypeError, ValueError):
                continue
    return sorted(years)


def _find_matches(filings: list[dict[str, Any]], year: int, by_filing_year: bool,
                  include_amendments: bool, include_variants: bool) -> list[dict[str, Any]]:
    date_key = "filing_date" if by_filing_year else "report_date"
    matches = []
    for filing in filings:
        if not _eligible(filing, include_amendments, include_variants):
            continue
        try:
            matches_year = date.fromisoformat(filing[date_key]).year == year
        except (KeyError, TypeError, ValueError):
            continue
        if matches_year:
            matches.append(filing)
    return matches


def select_filing(filings: list[dict[str, Any]], year: int, by_filing_year: bool = False,
                  include_amendments: bool = False, include_variants: bool = False) -> dict[str, Any]:
    """Select the most recently filed eligible 10-K for a fiscal or filing year."""
    matches = _find_matches(filings, year, by_filing_year, include_amendments, include_variants)
    if not matches:
        years = _available_years(filings, include_amendments, include_variants)
        available = ", ".join(map(str, years)) if years else "none"
        basis = "filing year" if by_filing_year else "fiscal year"
        raise ValueError(f"No eligible 10-K found for {basis} {year}. Available fiscal years: {available}.")
    matches.sort(key=lambda item: item.get("filing_date", ""), reverse=True)
    if len(matches) > 1:
        chosen = matches[0]
        print(f"Multiple 10-K filings match {year}; using accession {chosen['accession']} filed "
              f"{chosen['filing_date']}.")
    return matches[0]


def _load_filings(cik: int, session: requests.Session, year: int, by_filing_year: bool,
                  include_amendments: bool, include_variants: bool) -> list[dict[str, Any]]:
    data = _get_json(f"{_SUBMISSIONS_URL}/CIK{cik:010d}.json", session)
    filings = _records(data)
    if _find_matches(filings, year, by_filing_year, include_amendments, include_variants):
        return filings
    older_files = data.get("filings", {}).get("files", [])
    for old_file in older_files:
        older = _get_json(f"{_SUBMISSIONS_URL}/{quote(old_file['name'], safe='')}", session)
        filings.extend(_records(older))
    return filings


def list_10k_filings(cik: int, session: requests.Session | None = None) -> list[dict[str, Any]]:
    """List recent 10-K filings, consulting older submission files if recent has none."""
    sess = _request_session(session)
    data = _get_json(f"{_SUBMISSIONS_URL}/CIK{cik:010d}.json", sess)
    filings = _records(data)
    if not any(_eligible(filing, include_amendments=False, include_variants=False) for filing in filings):
        for old_file in data.get("filings", {}).get("files", []):
            older = _get_json(f"{_SUBMISSIONS_URL}/{quote(old_file['name'], safe='')}", sess)
            filings.extend(_records(older))
    return [filing for filing in filings
            if _eligible(filing, include_amendments=False, include_variants=False)]


def _cache_match(root: Path, company: str, year: int,
                 by_filing_year: bool) -> tuple[Path, dict[str, Any]] | None:
    """Find a cached filing by the caller's identifier without contacting the SEC."""
    query = company.strip().casefold()
    for metadata_path in root.glob("*.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("Ignoring unreadable EDGAR cache metadata %s: %s", metadata_path, exc)
            continue
        date_key = "filing_date" if by_filing_year else "report_date"
        try:
            if date.fromisoformat(metadata[date_key]).year != year:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        identifiers = (metadata.get("query", ""), metadata.get("ticker", ""),
                       metadata.get("title", ""), str(metadata.get("cik", "")))
        if query in {str(value).casefold() for value in identifiers}:
            filing_path = metadata_path.with_suffix(".htm")
            if filing_path.is_file():
                return filing_path, metadata
    safe_query = re.sub(r"[^A-Za-z0-9.-]+", "_", company.strip()).strip("_")
    if not by_filing_year:
        for filing_path in sorted(root.glob(f"{safe_query}_{year}_*.htm")):
            return filing_path, {"query": company, "ticker": safe_query, "report_date": "",
                                 "filing_date": "", "form": "10-K", "accession": filing_path.stem}
    return None


def download_10k(company: str, year: int, out_dir: str | Path | None = None, refresh: bool = False,
                 session: requests.Session | None = None, company_info: dict[str, Any] | None = None,
                 **flags: Any) -> Path:
    """Fetch a selected 10-K into the EDGAR cache and return its local path."""
    by_filing_year = bool(flags.pop("by_filing_year", False))
    include_amendments = bool(flags.pop("include_amendments", False))
    include_variants = bool(flags.pop("include_variants", False))
    if flags:
        raise TypeError(f"Unsupported download_10k option(s): {', '.join(sorted(flags))}")
    root = Path(out_dir) if out_dir is not None else Path(config.CACHE_DIR) / "edgar"
    if not refresh:
        cached = _cache_match(root, company, year, by_filing_year)
        if cached:
            path, metadata = cached
            if company_info is not None:
                company_info.update({key: metadata[key] for key in ("cik", "ticker", "title")
                                     if key in metadata})
            _print_fetch_details(metadata, path, metadata.get("source_url", "(cached)"))
            return path

    sess = _request_session(session)
    info = company_info if company_info and "cik" in company_info else resolve_company(company, sess)
    if company_info is not None:
        company_info.update(info)
    filings = _load_filings(info["cik"], sess, year, by_filing_year, include_amendments, include_variants)
    selected = select_filing(filings, year, by_filing_year, include_amendments, include_variants)
    fiscal_year = int(selected["report_date"][:4]) if selected.get("report_date") else year
    accession = selected["accession"]
    source_url = (f"{_ARCHIVES_URL}/{info['cik']}/{accession.replace('-', '')}/"
                  f"{quote(selected['primary_doc'], safe='')}")
    prefix = info["ticker"] or str(info["cik"])
    path = root / f"{prefix}_{fiscal_year}_{accession}.htm"
    if not path.is_file() or refresh:
        user_agent = config.SEC_USER_AGENT.strip()
        if not user_agent:
            raise ValueError(
                "SEC_USER_AGENT is missing. Add SEC_USER_AGENT=\"Your Name your@email.com\" to your .env file."
            )
        response = _get_response(source_url, sess)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
    metadata = {
        "query": company, "ticker": info["ticker"], "title": info["title"], "cik": info["cik"],
        "form": selected["form"], "report_date": selected["report_date"],
        "filing_date": selected["filing_date"], "accession": accession, "source_url": source_url,
    }
    path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    _print_fetch_details(metadata, path, source_url)
    return path


def _get_response(url: str, session: requests.Session) -> Any:
    """Fetch SEC filing bytes using the same rate-limit and retry policy as JSON calls."""
    global _last_request_at
    user_agent = config.SEC_USER_AGENT.strip()
    if not user_agent:
        raise ValueError(
            "SEC_USER_AGENT is missing. Add SEC_USER_AGENT=\"Your Name your@email.com\" to your .env file."
        )
    for attempt in range(4):
        wait = 0.15 - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        try:
            response = session.get(url, headers={"User-Agent": user_agent}, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError(f"SEC request failed for {url}: {exc}. Check your network and try again.") from exc
        _last_request_at = time.monotonic()
        if response.status_code in (403, 429):
            if attempt < 3:
                delay = max(0.15, 2 ** attempt)
                log.warning("SEC returned HTTP %s; retrying in %s seconds", response.status_code, delay)
                time.sleep(delay)
                continue
            raise RuntimeError(
                f"SEC returned HTTP {response.status_code} after 3 retries. Wait before retrying and verify SEC_USER_AGENT."
            )
        try:
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            raise RuntimeError(f"SEC download failed for {url}: {exc}. Check the URL and try again.") from exc
    raise RuntimeError(f"SEC download failed for {url} after retries.")


def _print_fetch_details(metadata: dict[str, Any], path: Path, source_url: str) -> None:
    print(f"Company: {metadata.get('title') or metadata.get('ticker') or metadata.get('query')}")
    print(f"CIK: {metadata.get('cik', '(cached)')}")
    print(f"Form: {metadata.get('form', '(cached)')}")
    print(f"Period end: {metadata.get('report_date') or '(cached)'}")
    print(f"Filing date: {metadata.get('filing_date') or '(cached)'}")
    print(f"Accession number: {metadata.get('accession', '(cached)')}")
    print(f"Local path: {path}")
    print(f"Source URL: {source_url}")
