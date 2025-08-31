"""SEC API client helpers.

Provides thin wrappers around SEC endpoints used by the library.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict

import requests

# Compliant User-Agent per SEC guidelines - Academic Research
HEADERS = {
    "User-Agent": "Academic Research Tool - pyedgarai 0.8.0 - Contact: jfimbett@gmail.com"
}

# Rate limiting: SEC requires no more than 10 requests per second
_last_request_time = 0
_min_request_interval = 0.1  # 100ms between requests (10 requests per second)

def _rate_limit():
    """Ensure we don't exceed SEC rate limits."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    if time_since_last < _min_request_interval:
        time.sleep(_min_request_interval - time_since_last)
    _last_request_time = time.time()

logger = logging.getLogger(__name__)


def get_submission_history(cik: int) -> Dict[str, Any]:
    """Get SEC submissions file for a CIK."""
    _rate_limit()  # Respect SEC rate limits
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_company_facts(cik: int) -> Dict[str, Any]:
    """Get companyfacts for a CIK."""
    _rate_limit()  # Respect SEC rate limits
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_company_concept(cik: int, taxonomy: str, tag: str) -> Dict[str, Any]:
    """Get companyconcept for a CIK/taxonomy/tag."""
    _rate_limit()  # Respect SEC rate limits
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/{taxonomy}/{tag}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_xbrl_frames(taxonomy: str, tag: str, unit: str, period: str, verbose: bool = False) -> Dict[str, Any]:
    """Get XBRL frames for (taxonomy, tag, unit, period)."""
    _rate_limit()  # Respect SEC rate limits
    url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json"
    if verbose:
        logger.info("Fetching %s", url)
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def parse_filing_text(text: str) -> str:
    """Minimal HTML to text conversion for filings (fallback).

    Use BeautifulSoup if available, else degrade to simple whitespace normalization.
    """
    try:
        from bs4 import BeautifulSoup as bs  # type: ignore

        soup = bs(text, "html.parser")
        return soup.get_text().replace("\n", " ").replace("\t", " ").replace("\xa0", " ").strip()
    except Exception:
        return " ".join(text.split())


__all__ = [
    "HEADERS",
    "get_submission_history",
    "get_company_facts",
    "get_company_concept",
    "get_xbrl_frames",
    "parse_filing_text",
]
