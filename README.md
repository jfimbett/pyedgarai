# pyedgarai

A Python toolkit and API for retrieving SEC data (submissions, company facts, XBRL frames) and computing comparable companies. All data is fetched live from SEC and yfinance; no mocks.

## Requirements
- Python 3.11+
- macOS with zsh (default)
- Internet access (SEC and yfinance requests)

## Install (from source)
If you’re working with this repository directly:

- Create and activate a virtual environment (Python 3.11):
  - Using venv
    - `python3.11 -m venv .venv`
    - `source .venv/bin/activate`
  - Or using Poetry
    - `pipx install poetry` (once)
    - `poetry env use 3.11`
    - `poetry install`

- Install with pip (venv):
  - `pip install -U pip wheel`
  - `pip install -e .`

Notes:
- If you see “could not be resolved” for imports in your editor, ensure the Python interpreter is your 3.11 venv/Poetry env.

## Quick sanity check
In Python:
- `from pyedgarai import sec_client as sec`
- `sec.get_submission_history(320193)["name"]`  # should return "Apple Inc." (or similar)
- `sec.get_xbrl_frames('us-gaap','Assets','USD','CY2024Q1I')["data"][:1]`

## Run the API server
- Optional auth: `export PYEDGARAI_API_TOKEN=your_token`
- Start server: `python -m pyedgarai.api.server`
- Server listens on `http://0.0.0.0:5000`

Endpoints include:
- `GET /comparables` (identify comparables for a CIK)
- `GET /company_facts` (SEC company facts)
- `GET /company_concept` (SEC concept by tag)
- `GET /account` (XBRL frames)
- Dynamic yfinance endpoints (e.g., `/info`, `/income_stmt`)

## Cache
Generated artifacts (e.g., `cik_sic.json`, `cik_company_names.json`, `states.json`, `accounts.xlsx`) are stored in:
- `$PYEDGARAI_CACHE_DIR` if set, else `~/.cache/pyedgarai`

## Tests
These tests hit live services; ensure network access.
- With Poetry: `poetry run pytest -q`
- With venv:
  - `pip install pytest pytest-cov`
  - `pytest -q`

## Uninstall
- `pip uninstall pyedgarai`
- Remove cache if desired: `rm -rf ~/.cache/pyedgarai` (or your `$PYEDGARAI_CACHE_DIR`)

## License
MIT
