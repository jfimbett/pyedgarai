"""Tests for features and utility functions."""
import pytest
import pandas as pd
import json
import os
from unittest.mock import patch, Mock
from pathlib import Path

from pyedgarai import features as ft
from pyedgarai import utils


class TestFeatures:
    """Test feature extraction and metadata functions."""
    
    def test_return_accounts(self):
        """Test loading accounts catalog."""
        accounts = ft.return_accounts()
        
        assert isinstance(accounts, dict)
        assert len(accounts) > 0
        
        # Check structure of account entries
        sample_key = next(iter(accounts.keys()))
        sample_account = accounts[sample_key]
        
        expected_fields = ['name', 'description', 'units', 'taxonomy', 'instant']
        for field in expected_fields:
            assert field in sample_account
    
    def test_get_cik_tickers(self):
        """Test CIK to ticker mapping."""
        cik_tickers = ft.get_cik_tickers()
        
        assert isinstance(cik_tickers, dict)
        assert len(cik_tickers) > 0
        
        # Check that values are lists
        for cik, tickers in cik_tickers.items():
            assert isinstance(tickers, list)
            # Each ticker should be a string
            for ticker in tickers:
                assert isinstance(ticker, str)
    
    @patch('pyedgarai.features.get_company_facts')
    def test_get_cik_company_names_generation(self, mock_get_facts):
        """Test generating CIK to company name mappings."""
        # Mock the company facts response
        mock_get_facts.return_value = {'entityName': 'Apple Inc.'}
        
        # Mock CIKS to a small set for testing
        with patch('pyedgarai.features.StockMapper') as mock_mapper:
            mock_mapper.return_value.cik_to_tickers.keys.return_value = ['0000320193']
            
            # Use a temporary directory for testing
            temp_dir = Path.cwd() / 'temp_test'
            temp_dir.mkdir(exist_ok=True)
            
            try:
                ft.get_cik_company_names(str(temp_dir) + '/')
                
                # Check that file was created
                output_file = temp_dir / 'cik_company_names.json'
                assert output_file.exists()
                
                # Check content
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                assert isinstance(data, dict)
                # CIK keys are stored as strings in JSON
                assert '320193' in data
                assert data['320193'] == 'Apple Inc.'
                
            finally:
                # Clean up
                if temp_dir.exists():
                    for file in temp_dir.iterdir():
                        file.unlink()
                    temp_dir.rmdir()
    
    def test_return_company_names(self):
        """Test loading company names from cache."""
        # Create a temporary JSON file
        temp_dir = Path.cwd() / 'temp_test'
        temp_dir.mkdir(exist_ok=True)
        
        # JSON stores all keys as strings
        test_data = {'320193': 'Apple Inc.', '789019': 'Microsoft Corporation'}
        json_file = temp_dir / 'cik_company_names.json'
        
        try:
            with open(json_file, 'w') as f:
                json.dump(test_data, f)
            
            names = ft.return_company_names(str(temp_dir) + '/')
            
            assert isinstance(names, dict)
            # Keys are strings in JSON
            assert names['320193'] == 'Apple Inc.'
            assert names['789019'] == 'Microsoft Corporation'
            
        finally:
            # Clean up
            if temp_dir.exists():
                for file in temp_dir.iterdir():
                    file.unlink()
                temp_dir.rmdir()
    
    def test_get_companies_similar_location(self):
        """Test finding companies in similar locations."""
        # This function takes a CIK and finds companies in the same location
        # We'll mock the function since it requires API calls
        with patch('pyedgarai.features.get_submission_history') as mock_submission:
            mock_submission.return_value = {
                'addresses': {
                    'business': {'stateOrCountryDescription': 'California'}
                }
            }
            
            # Create a temporary states.json file
            temp_dir = Path.cwd() / 'temp_test_states'
            temp_dir.mkdir(exist_ok=True)
            states_file = temp_dir / 'states.json'
            
            try:
                # Create states.json with test data
                states_data = {
                    '320193': 'California',
                    '789019': 'California', 
                    '12345': 'New York'
                }
                with open(states_file, 'w') as f:
                    json.dump(states_data, f)
                
                companies = ft.get_companies_similar_location(320193, str(temp_dir) + '/')
                
                assert isinstance(companies, pd.DataFrame)
                assert 'cik' in companies.columns
                assert 'state' in companies.columns
                assert len(companies) >= 2  # Should find Apple and Microsoft
                
            finally:
                # Clean up
                if temp_dir.exists():
                    for file in temp_dir.iterdir():
                        file.unlink()
                    temp_dir.rmdir()
    
    def test_get_instant_dict(self):
        """Test getting instant/duration classification."""
        instant_dict = ft.get_instant_dict()
        
        assert isinstance(instant_dict, dict)
        assert len(instant_dict) > 0
        
        # Check some known accounts
        if 'NetIncomeLoss' in instant_dict:
            # Net income is typically a duration measure (0)
            assert instant_dict['NetIncomeLoss'][0] == 0
        
        if 'Assets' in instant_dict:
            # Assets are typically instant measures (1)
            assert instant_dict['Assets'][0] == 1


class TestUtils:
    """Test utility functions."""
    
    def test_clean_account_name(self):
        """Test account name cleaning."""
        # Test various account name formats
        test_cases = [
            ('Assets', 'Assets'),
            ('Net Income (Loss)', 'NetIncomeLoss'),
            ('Revenue from Contract with Customer, Excluding Assessed Tax', 'RevenueFromContractWithCustomerExcludingAssessedTax'),
            ('Cash and Cash Equivalents', 'CashAndCashEquivalents'),
        ]
        
        for input_name, expected in test_cases:
            result = utils.clean_account_name(input_name)
            assert result == expected
    
    def test_clean_account_name_edge_cases(self):
        """Test edge cases for account name cleaning."""
        # Empty string
        assert utils.clean_account_name('') == ''
        
        # String with only special characters - should be cleaned
        result = utils.clean_account_name('!@#$%^&*()')
        assert result == ''  # All special chars should be removed
        
        # String with numbers
        result = utils.clean_account_name('Revenue 2023')
        assert 'Revenue' in result
        assert '2023' in result
    
    def test_clean_df_bad_endings(self):
        """Test DataFrame cleaning for bad column endings."""
        # Create test DataFrame with problematic column names
        test_df = pd.DataFrame({
            'account': ['Assets', 'Revenue', 'NetIncome'],
            'value_bad': [1000, 2000, 3000],
            'price_old': [100, 200, 300],
            'clean_column': [10, 20, 30]
        })
        
        cleaned_df = utils.clean_df_bad_endings(test_df, ['_bad', '_old'])
        
        # Should remove columns with bad endings
        assert len(cleaned_df.columns) == 2  # Only 'account' and 'clean_column' should remain
        assert 'account' in cleaned_df.columns
        assert 'clean_column' in cleaned_df.columns
        assert 'value_bad' not in cleaned_df.columns
        assert 'price_old' not in cleaned_df.columns
        # All rows should still be present
        assert len(cleaned_df) == 3
    
    def test_parse_filing_text(self):
        """Test HTML parsing of filing text."""
        html_text = """
        <html>
            <body>
                <p>This is a test filing.</p>
                <div>With multiple sections.</div>
                <table><tr><td>And tables</td></tr></table>
            </body>
        </html>
        """
        
        # Import the function from pyedgarai.py since it's in the main module
        from pyedgarai.pyedgarai import parse_filing_text
        
        result = parse_filing_text(html_text)
        
        assert isinstance(result, str)
        assert 'This is a test filing.' in result
        assert 'With multiple sections.' in result
        assert 'And tables' in result
        # HTML tags should be removed
        assert '<p>' not in result
        assert '<div>' not in result
    
    def test_print_dict_function(self):
        """Test dictionary printing utility."""
        from pyedgarai.pyedgarai import print_dict
        
        test_dict = {
            'key1': 'value1',
            'key2': {'nested_key': 'nested_value'},
            'key3': ['list_item1', 'list_item2']
        }
        
        # This function prints to stdout, so we just test it doesn't crash
        try:
            print_dict(test_dict)
            assert True  # If we get here, function didn't crash
        except Exception as e:
            pytest.fail(f"print_dict failed with error: {e}")


class TestCacheManagement:
    """Test cache directory management."""
    
    def test_get_cache_dir_default(self):
        """Test default cache directory creation."""
        # Remove environment variable if set
        original_env = os.environ.get("PYEDGARAI_CACHE_DIR")
        if "PYEDGARAI_CACHE_DIR" in os.environ:
            del os.environ["PYEDGARAI_CACHE_DIR"]
        
        try:
            cache_dir = ft._get_cache_dir()
            
            assert isinstance(cache_dir, str)
            assert cache_dir.endswith('/')
            assert '.cache' in cache_dir
            assert 'pyedgarai' in cache_dir
            
            # Directory should exist
            assert os.path.exists(cache_dir.rstrip('/'))
            
        finally:
            # Restore environment variable
            if original_env:
                os.environ["PYEDGARAI_CACHE_DIR"] = original_env
    
    def test_get_cache_dir_custom(self):
        """Test custom cache directory via environment variable."""
        custom_dir = Path.cwd() / 'custom_cache_test'
        
        # Set environment variable
        os.environ["PYEDGARAI_CACHE_DIR"] = str(custom_dir)
        
        try:
            cache_dir = ft._get_cache_dir()
            
            assert str(custom_dir) in cache_dir
            assert os.path.exists(custom_dir)
            
        finally:
            # Clean up
            if "PYEDGARAI_CACHE_DIR" in os.environ:
                del os.environ["PYEDGARAI_CACHE_DIR"]
            if custom_dir.exists():
                custom_dir.rmdir()
