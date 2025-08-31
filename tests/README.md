# Tests Directory

This directory contains all test files organized by type and scope.

## Structure

### `/unit/`
Unit tests for individual components and functions:
- `test_lightweight.py` - Core functionality tests without heavy dependencies
- `test_optimized_system.py` - Tests for optimized comparables system
- `test_schemas_minimal.py` - Schema validation tests
- `test_sic_comparables.py` - SIC-based comparables analysis tests
- `test_sic_direct.py` - Direct SIC code functionality tests

### `/integration/`
Integration tests for API endpoints and system interactions:
- `test_api_direct.py` - Direct API functionality tests
- `test_api_imports.py` - API import validation tests  
- `test_comparables_api.py` - Comparables API endpoint tests
- `test_docs_endpoints.py` - Documentation endpoint tests
- `test_sec_api.py` - SEC API integration tests

### `/examples/`
Example test files and usage demonstrations (reserved for future use)

## Running Tests

### All Tests
```bash
# From project root
pytest tests/
```

### By Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Specific test file
pytest tests/unit/test_lightweight.py
```

### Test Configuration
- Configuration: `pytest.ini` in project root
- Coverage: Uses `.coverage` for tracking
- Environment: Tests require `pyedgarai` conda environment

## Adding Tests

1. **Unit Tests**: Place in `tests/unit/` for testing individual functions/classes
2. **Integration Tests**: Place in `tests/integration/` for testing system interactions
3. **Examples**: Place in `tests/examples/` for tutorial-style test demonstrations

Follow existing naming convention: `test_[component]_[type].py`
