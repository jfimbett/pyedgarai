# STRUCTURE.md: Current Repository Structure

This document outlines the current directory structure for the `pyedgarai` repository after reorganization.

## 1. Current Directory Tree

The repository is organized by function, separating code, tests, data, scripts, and documentation:

```
pyedgarai/
├── .github/                    # GitHub configuration
├── .gitignore                  # Git ignore rules
├── archive/                    # Archived/experimental files
│   ├── README.md              # Archive documentation
│   ├── experiments/           # Experimental code and data
│   ├── legacy_api/           # Legacy API implementations
│   └── vba_code/             # VBA integration code
├── data/                      # Data files and cache
│   ├── sec/                  # SEC EDGAR quarterly data
│   └── subset_accounts.xlsx  # Account subset data
├── docs/                      # Documentation
│   ├── comparables_analysis.md    # Comparables analysis documentation
│   ├── comparables_analysis.pdf   # Analysis PDF
│   └── ... # Sphinx documentation
├── notebooks/                 # Jupyter notebooks
│   └── tutorial.ipynb        # Tutorial notebook
├── scripts/                   # Utility scripts
│   ├── README.md             # Scripts documentation
│   ├── api_servers/          # API server scripts
│   │   ├── fast_api_server.py    # Lightweight Flask API
│   │   ├── start_api.py          # API startup script
│   │   └── simple_api_example.py # API examples
│   ├── data_generation/      # Data generation scripts
│   │   ├── generate_cik_sic_data.py    # CIK-SIC mapping
│   │   ├── generate_company_names.py   # Company names
│   │   └── generate_data_files.py      # Master generator
│   └── utilities/            # General utilities
│       └── fix_schemas.py    # Schema utilities
├── src/                      # Source code
│   └── pyedgarai/           # Main package
│       ├── __init__.py      # Package initialization
│       ├── api/             # API modules
│       ├── *.py             # Core modules
│       └── __pycache__/     # Python cache
├── tests/                    # Test suite
│   ├── README.md            # Test documentation
│   ├── integration/         # Integration tests
│   │   ├── test_api_*.py    # API tests
│   │   └── test_sec_api.py  # SEC API tests
│   ├── unit/                # Unit tests
│   │   ├── test_lightweight.py     # Core tests
│   │   ├── test_optimized_system.py # Performance tests
│   │   └── test_sic_*.py          # SIC functionality tests
│   └── examples/            # Example tests (future)
├── CHANGELOG.md             # Change log
├── LICENSE                  # License file
├── poetry.lock              # Poetry lock file
├── pyproject.toml          # Project configuration
├── pytest.ini             # Test configuration
└── README.md               # Main documentation
```

## 2. Organization Benefits

### Improved Maintainability
- **Clear separation of concerns**: Source code, tests, scripts, and documentation are in dedicated directories
- **Logical grouping**: Related functionality is grouped together (e.g., all API servers in one location)
- **Reduced clutter**: Root directory contains only essential configuration and documentation files

### Enhanced Development Workflow
- **Script organization**: Utility scripts are categorized by purpose (data generation, API servers, utilities)
- **Test structure**: Tests are separated by type (unit vs integration) for better test management
- **Archive system**: Legacy and experimental code is preserved but kept separate from active development

### Better Navigation
- **Intuitive structure**: Directory names clearly indicate their purpose
- **README files**: Each major directory has documentation explaining its contents
- **Consistent naming**: File and directory names follow consistent conventions

## 3. Key Features

### Performance Optimizations
- **Fast API Server**: `scripts/api_servers/fast_api_server.py` provides instant responses using cached data
- **Lightweight tests**: Unit tests avoid heavy imports for faster execution
- **Optimized comparables**: Separate optimized module bypasses slow imports

### Data Management
- **Cached data**: 7,869+ companies with SIC codes and 6,706 company names
- **Organized SEC data**: Quarterly data organized by period in `data/sec/`
- **Generated datasets**: Scripts for regenerating all data files from source

### Comprehensive Testing
- **Unit tests**: Core functionality testing without external dependencies
- **Integration tests**: API endpoint and system interaction testing
- **Performance tests**: Validation of optimized system components

## 4. Usage Patterns

### Running Scripts
```bash
# Activate environment
conda activate pyedgarai

# Generate data
python scripts/data_generation/generate_data_files.py

# Start API server
python scripts/api_servers/fast_api_server.py

# Run utilities
python scripts/utilities/fix_schemas.py
```

### Running Tests
```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test
pytest tests/unit/test_lightweight.py
```

### Development
- **Source code**: All modifications should be made in `src/pyedgarai/`
- **New scripts**: Add to appropriate subdirectory in `scripts/`
- **New tests**: Add to `tests/unit/` or `tests/integration/` as appropriate
- **Documentation**: Update relevant README files when adding new functionality

## 3. Risk Analysis & Mitigations

| Risk                               | Mitigation                                                                                                                                                                                          |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Broken Imports**                 | After moving files, Python `import` statements will fail. These must be updated. The `move_files.py` script will attempt to perform a find-and-replace for common import paths. A manual review will be necessary. |
| **Broken Data File Paths**         | Code that reads data files (e.g., `pd.read_csv('src/pyedgarai/data.csv')`) will break. All hardcoded paths must be updated to point to the new `/data` or `/notebooks` directories. This is the highest risk. |
| **Build/CI Failures**              | `pyproject.toml` and test configurations must be updated to exclude the `/archive` directory and correctly locate source files if paths change.                                                        |
| **Notebook Execution Failure**     | The `notebooks/tutorial.ipynb` notebook likely uses relative paths to access data files. These paths must be updated from, e.g., `../data/comparables.csv` to `../data/comparables.csv`.                 |
| **Environment Issues**             | The presence of `geckodriver` suggests a dependency on Selenium/web scraping. This should be managed via environment setup, not by committing binaries. This change may affect how users run the code. |
