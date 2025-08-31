# AUDIT.md: Repository Audit - Updated for Cleanup

**Last Updated**: August 31, 2025  
**Purpose**: Comprehensive audit for repository reorganization and cleanup  

## 1. Project Overview

This project, `pyedgarai`, is a Python library designed for financial data analysis, with a focus on interacting with the SEC's EDGAR database.

**Core capabilities:**
- ✅ SEC EDGAR data fetching and processing
- ✅ Comparables analysis with optimized performance  
- ✅ Flask API with comprehensive documentation
- ✅ Market data integration (Yahoo Finance)
- ✅ ML-powered company comparison
- ✅ Cached data pipeline for fast responses

**Current Status**: Functional with working API and optimized comparables analysis

**Primary entry points:**
- **Library**: `src/pyedgarai/` - Main library code (well organized)
- **API**: `src/pyedgarai/api/` - Flask-OpenAPI3 server with documentation
- **Tests**: `tests/` - Comprehensive test suite (55 tests passing)
- **Scripts**: Multiple utility scripts scattered in root (needs organization)

## 2. Current Issues Requiring Cleanup

### 🚨 **Critical Organizational Issues**
1. **Root Directory Clutter**: 15+ utility files scattered in project root
2. **Duplicate Files**: Multiple versions of API servers and test files  
3. **Missing Directory Structure**: No `/scripts/`, `/archive/` directories
4. **Build Artifacts**: `__pycache__/` directories not properly ignored
5. **External Tools**: `geckodriver-*/` directories should be in `/tools/`

### 📁 **Files Requiring Organization**

#### **Scripts (Root → `/scripts/`)**
- `generate_cik_sic_data.py` - Data generation utility
- `generate_company_names.py` - Company names generation
- `fast_api_server.py` - Optimized lightweight API server
- `create_user_manual.py` - Documentation generator
- `create_vba_code_endpoints.py` - VBA code generator
- `scrape_apicalls.py` - API scraping utility
- `tenks_banks.py` - Banking data processing

#### **Tests (Root → `/tests/`)**
- `test_lightweight.py` - Core functionality tests
- `test_optimized_system.py` - System integration tests  
- `test_comparables_api.py` - API endpoint tests
- `test_sic_direct.py` - Direct SIC testing
- `test_api_direct.py` - Direct API testing
- `simple_api_example.py` - Usage examples

#### **Legacy Files (Root → `/archive/`)**
- `api_tryout.txt` - Old API experiments
- `ex_13.txt` - Example data files
- `Module1.bas`, `Module2.bas`, `JsonConverter.bas` - VBA code
- `api.py` - Duplicate API implementation
- `models.py` - Possibly duplicate models
- `version.py` - Duplicate version file
- `Valuation Report template.docx` - Template document

#### **Data Files (Remove from repo)**
- `cik_company_names.json` - Should be generated in cache
- `pages_0000072971.json` - Cache data, not repo data

## 3. Tech Stack

- **Language:** Python
- **Dependency Management:** Poetry (`pyproject.toml`, `poetry.lock`)
- **Documentation:** Sphinx (`docs/conf.py`)
- **Testing:** Pytest (inferred from `tests/` structure)
- **Associated Tech:** VBA (`.bas` files) and a Word document suggest integration with Microsoft Office products.

### Build and Run Commands

- **Install dependencies:** `poetry install`
- **Run tests:** `poetry run pytest`
- **Build documentation:** `cd docs && make html` (based on `Makefile`)
- **Run library code:** As a Python library, it is meant to be imported into other applications.

## 3. Directory Inventory

| Path                               | Purpose                                                                                             | Status/Notes                                                                                             |
| ---------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `/`                                | Project root                                                                                        | Contains many files that should be moved (source, scripts, data, artifacts).                             |
| `/.github/`                        | GitHub-specific files.                                                                              | Contains Copilot instructions. Standard.                                                                 |
| `/data/`                           | Raw and processed data.                                                                             | Contains large SEC datasets. Seems appropriate.                                                          |
| `/docs/`                           | Project documentation.                                                                              | Standard Sphinx setup. Good.                                                                             |
| `/geckodriver-v*`                  | Web driver executables.                                                                             | Should not be committed to the repository. Recommend adding to `.gitignore`.                             |
| `/src/pyedgarai/`                  | Main Python source code.                                                                            | Contains mixed content: source code and data files (`.xlsx`, `.json`, `.csv`). Data should be moved out. |
| `/src/pyedgarai/api/`              | API-related source code.                                                                            | Seems organized.                                                                                         |
| `/tests/`                          | Unit tests.                                                                                         | Standard. Good.                                                                                          |
| `__pycache__/`                     | Python bytecode cache.                                                                              | Should be in `.gitignore`.                                                                               |

## 4. Module Relationships

The core logic resides in `src/pyedgarai/`. A brief dependency analysis suggests:
- `pyedgarai.py` is likely the main entry point or facade for the library.
- `sec_client.py` handles communication with the SEC data source.
- `comparables.py` and `market_data.py` consume data to perform financial analysis.
- `utils.py` probably contains helper functions used across the library.
- The root-level scripts (`scripts/tenks_banks.py`, etc.) likely import and use the `pyedgarai` library.

## 5. Suspected Unused/Orphan/Misplaced Files

The following files are candidates for moving to a more appropriate location or archiving.

| File                                                  | Location | Reason                                                                                             | Proposed Action                               |
| ----------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `src/pyedgarai/api.py`, `src/pyedgarai/models.py`, `archive/version.py`                   | Root     | Appears to be source code. `archive/version.py` is duplicated in `src/pyedgarai/`.                         | Move to `src/pyedgarai/` or `archive/` if stale. |
| `create_*.py`, `scripts/scrape_apicalls.py`, `scripts/tenks_banks.py`  | Root     | One-off utility or maintenance scripts.                                                            | Move to `scripts/`.                           |
| `*.bas`, `Valuation Report*.docx`                      | Root     | VBA and Word document artifacts. Not part of the core Python library.                              | Move to `archive/vba_integration`.            |
| `archive/temp/api_tryout.txt`, `archive/temp/ex_13.txt`                           | Root     | Temporary, example, or test files.                                                                 | Move to `archive/temp`.                       |
| `cik_company_names.json`                                | Root     | Data file.                                                                                         | Move to `data/`.                              |
| `notebooks/tutorial.ipynb`                                      | Root     | Jupyter notebook.                                                                                  | Move to `notebooks/`.                         |
| `*.xlsx`, `*.json`, `*.csv` in `src/pyedgarai/`         | Source   | Data files mixed with source code.                                                                 | Move to `data/`.                              |
| `geckodriver-v*` directories                          | Root     | Binary executables. Should not be in version control.                                              | Delete and add to `.gitignore`.               |
| `__pycache__/`                                        | Root     | Python cache. Should not be in version control.                                                    | Delete and add to `.gitignore`.               |
