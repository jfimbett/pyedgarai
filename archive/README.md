# Archive README

This directory contains files that are not part of the active `pyedgarai` library but are kept for historical reference or potential future use.

## Archival Policy

- **Purpose:** To keep the main repository clean and focused without permanently deleting potentially useful assets.
- **Contents:** This can include legacy code, old data files, temporary test scripts, and integrations that are no longer maintained.
- **Exclusions:** Files in this directory are excluded from the build, tests, and packaging process.

## Current Contents

### /experiments/
- `fast_api_server.py` - Early FastAPI server experiment
- `move_map.json` - File reorganization mapping
- `pages_0000072971.json` - Sample SEC data file
- `geckodriver-*` folders - WebDriver downloads for browser automation

### /temp/
- `api_tryout.txt` - API testing notes
- `ex_13.txt` - Example data file
- `/debug_scripts/` - Temporary debugging and testing scripts created during comparable_private endpoint development:
  - `debug_yfinance.py` - yfinance integration debugging
  - `test_rate_limited.py` - Rate limiting test script
  - `test_yfinance_simple.py` - Simple yfinance functionality test
  - `quick_test.py` - Quick API testing script
  - `test_private_comparables.py` - Private comparables endpoint testing
  - `verify_real_data.py` - SEC data verification script

### /vba_integration/
- `JsonConverter.bas` - VBA JSON conversion module
- `Module1.bas`, `Module2.bas` - VBA integration modules
- `Valuation Report template for private equity firm.docx` - Excel/Word template

### /version.py
- Legacy version management file moved during reorganization
