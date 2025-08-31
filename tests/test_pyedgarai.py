"""Legacy tests for pyedgarai - kept for backward compatibility."""
import os
import time
import pandas as pd
from unittest.mock import patch

from pyedgarai import sec_client as sec
from pyedgarai import features as ft
from pyedgarai import market_data as md


APPLE_CIK = 320193  # Apple Inc.


@patch('pyedgarai.sec_client.requests.get')
def test_sec_submission_history_has_core_fields(mock_get):
    """Test SEC submission history returns required fields."""
    # Mock the API response
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'cik': '0000320193',
        'name': 'Apple Inc.',
        'filings': {'recent': {'form': ['10-K', '10-Q']}}
    }
    
    data = sec.get_submission_history(APPLE_CIK)
    assert 'cik' in data and 'name' in data


@patch('pyedgarai.sec_client.requests.get')
def test_sec_company_facts_and_concept(mock_get):
    """Test SEC company facts and concept endpoints."""
    # Mock company facts response
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    
    # First call - company facts
    mock_response.json.return_value = {
        'facts': {'us-gaap': {'Assets': {'units': {'USD': []}}}},
        'entityName': 'Apple Inc.'
    }
    
    facts = sec.get_company_facts(APPLE_CIK)
    assert 'facts' in facts and isinstance(facts['facts'], dict)

    # Second call - company concept
    mock_response.json.return_value = {
        'tag': 'Assets',
        'taxonomy': 'us-gaap',
        'units': {'USD': []}
    }
    
    concept = sec.get_company_concept(APPLE_CIK, 'us-gaap', 'Assets')
    assert concept.get('tag') == 'Assets'
    assert concept.get('taxonomy') == 'us-gaap'


@patch('pyedgarai.sec_client.requests.get')
def test_xbrl_frames_assets_cy2023q4i(mock_get):
    """Test XBRL frames endpoint for Assets data."""
    # Mock the API response
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [
            {'cik': 320193, 'val': 1000000000, 'end': '2023-12-31'},
            {'cik': 789019, 'val': 1200000000, 'end': '2023-12-31'}
        ]
    }
    
    frames = sec.get_xbrl_frames('us-gaap', 'Assets', 'USD', 'CY2023Q4I')
    assert 'data' in frames and isinstance(frames['data'], list)


def test_features_accounts_and_instant_dict():
    """Test features module functions."""
    accounts = ft.return_accounts()
    assert isinstance(accounts, dict) and len(accounts) > 0

    inst = ft.get_instant_dict()
    # NetIncomeLoss should be duration (0), not instant (1)
    assert inst['NetIncomeLoss'][0] == 0


def test_market_data_aapl_recent_range():
    """Test market data retrieval for AAPL."""
    # Use a more conservative date range
    df = md.get_stock_data('AAPL', '2024-01-01', '2024-01-15')
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        # Check for key columns (case insensitive)
        columns_lower = [c.lower() for c in df.columns]
        assert any('close' in col for col in columns_lower)
        assert 'ticker' in df.columns
        assert all(df['ticker'] == 'AAPL')
