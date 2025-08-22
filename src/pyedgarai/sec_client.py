"""SEC API client helpers.

Provides thin wrappers around SEC endpoints used by the library.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

import requests

# Compliant User-Agent per SEC guidelines
HEADERS = {"User-Agent": "pyedgarai (github.com/jfimbett/pyedgarai)"}

logger = logging.getLogger(__name__)


def get_submission_history(cik: int) -> Dict[str, Any]:
    """Get SEC submissions file for a CIK."""
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_company_facts(cik: int) -> Dict[str, Any]:
    """Get companyfacts for a CIK."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_company_concept(cik: int, taxonomy: str, tag: str) -> Dict[str, Any]:
    """Get companyconcept for a CIK/taxonomy/tag."""
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/{taxonomy}/{tag}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_xbrl_frames(taxonomy: str, tag: str, unit: str, period: str, verbose: bool = False) -> Dict[str, Any]:
    """Get XBRL frames for (taxonomy, tag, unit, period)."""
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
