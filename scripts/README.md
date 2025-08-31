# Scripts Directory

This directory contains utility scripts and standalone programs that support the pyedgarai library but are not part of the core library code.

## Structure

### `/api_servers/`
API server implementations and related scripts:
- `fast_api_server.py` - Lightweight Flask API server using cached data for instant responses
- `start_api.py` - API startup script with environment validation
- `simple_api_example.py` - Basic API usage examples

### `/data_generation/`
Scripts for generating and updating data files:
- `generate_cik_sic_data.py` - Generates CIK to SIC industry mapping data
- `generate_company_names.py` - Creates company name lookup tables
- `generate_data_files.py` - Master script for data generation pipeline

### `/utilities/`
General utility scripts for maintenance and development:
- `fix_schemas.py` - Schema validation and repair utilities

## Usage

These scripts are designed to be run independently:

```bash
# Activate environment first
conda activate pyedgarai

# Run data generation
python scripts/data_generation/generate_data_files.py

# Start API server
python scripts/api_servers/fast_api_server.py
```

## Development

When adding new scripts:
1. Place in appropriate subdirectory based on purpose
2. Include proper argument parsing and help text
3. Add environment validation where needed
4. Update this README with the new script description
