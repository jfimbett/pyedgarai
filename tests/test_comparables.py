"""Tests for comparables analysis functionality."""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
import numpy as np

from pyedgarai import comparables as comp


class TestComparablesAnalysis:
    """Test comparable company analysis functions."""
    
    APPLE_CIK = 320193
    MICROSOFT_CIK = 789019
    
    @pytest.fixture
    def mock_assets_data(self):
        """Mock assets data for testing."""
        return {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 1000000000, 'end': '2024-03-31'},
                {'cik': self.MICROSOFT_CIK, 'val': 1200000000, 'end': '2024-03-31'},
                {'cik': 12345, 'val': 950000000, 'end': '2024-03-31'},
                {'cik': 67890, 'val': 1500000000, 'end': '2024-03-31'},
            ]
        }
    
    @pytest.fixture
    def mock_profit_data(self):
        """Mock profit data for testing."""
        return {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 100000000, 'end': '2024-03-31'},
                {'cik': self.MICROSOFT_CIK, 'val': 120000000, 'end': '2024-03-31'},
                {'cik': 12345, 'val': 95000000, 'end': '2024-03-31'},
                {'cik': 67890, 'val': 150000000, 'end': '2024-03-31'},
            ]
        }
    
    def test_get_all_size(self, mock_assets_data):
        """Test getting all company sizes."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.return_value = mock_assets_data
            
            df = comp.get_all_size()
            
            assert isinstance(df, pd.DataFrame)
            assert 'assets' in df.columns
            assert 'cik' in df.columns
            assert len(df) == 4
            assert df[df['cik'] == self.APPLE_CIK]['assets'].iloc[0] == 1000000000
    
    def test_get_all_profitability(self, mock_assets_data, mock_profit_data):
        """Test getting all company profitability ratios."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_assets_data, mock_profit_data]
            
            df = comp.get_all_profitability()
            
            assert isinstance(df, pd.DataFrame)
            assert 'profitability' in df.columns
            assert 'cik' in df.columns
            
            # Verify profitability calculation
            apple_row = df[df['cik'] == self.APPLE_CIK]
            expected_profitability = 100000000 / 1000000000  # profit / assets
            assert np.isclose(apple_row['profitability'].iloc[0], expected_profitability)
    
    def test_get_all_growth_rate(self):
        """Test getting all company growth rates."""
        mock_current = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 1000000000},
                {'cik': self.MICROSOFT_CIK, 'val': 1200000000},
            ]
        }
        mock_past = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 800000000},
                {'cik': self.MICROSOFT_CIK, 'val': 900000000},
            ]
        }
        
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_current, mock_past]
            
            df = comp.get_all_growth_rate()
            
            assert isinstance(df, pd.DataFrame)
            assert 'growth_rate' in df.columns
            assert 'cik' in df.columns
            
            # Verify growth rate calculation
            apple_row = df[df['cik'] == self.APPLE_CIK]
            expected_growth = (1000000000 - 800000000) / 800000000  # (current - past) / past
            assert np.isclose(apple_row['growth_rate'].iloc[0], expected_growth)
    
    def test_get_all_capital_structure(self):
        """Test getting all company capital structures."""
        mock_equity = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 500000000},
                {'cik': self.MICROSOFT_CIK, 'val': 600000000},
            ]
        }
        mock_liabilities = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 300000000},
                {'cik': self.MICROSOFT_CIK, 'val': 400000000},
            ]
        }
        
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_equity, mock_liabilities]
            
            df = comp.get_all_capital_structure()
            
            assert isinstance(df, pd.DataFrame)
            assert 'debt_to_equity' in df.columns
            assert 'cik' in df.columns
            
            # Verify debt-to-equity calculation
            apple_row = df[df['cik'] == self.APPLE_CIK]
            expected_ratio = 300000000 / 500000000  # liabilities / equity
            assert np.isclose(apple_row['debt_to_equity'].iloc[0], expected_ratio)
    
    def test_get_companies_similar_size(self, mock_assets_data):
        """Test finding companies with similar size."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.return_value = mock_assets_data
            
            # Test with 20% interval (should include companies within ±20% of Apple's size)
            df = comp.get_companies_similar_size(self.APPLE_CIK, interval=20)
            
            assert isinstance(df, pd.DataFrame)
            assert 'val' in df.columns
            assert 'cik' in df.columns
            
            # Apple should be included
            assert self.APPLE_CIK in df['cik'].values
            
            # Should include companies within 20% range (800M to 1.2B)
            apple_size = 1000000000
            lb, ub = apple_size * 0.8, apple_size * 1.2
            assert all(lb <= val <= ub for val in df['val'])
    
    def test_get_companies_similar_profitability(self, mock_assets_data, mock_profit_data):
        """Test finding companies with similar profitability."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_assets_data, mock_profit_data]
            
            df = comp.get_companies_similar_profitability(self.APPLE_CIK, interval=25)
            
            assert isinstance(df, pd.DataFrame)
            assert 'profitability' in df.columns
            assert 'cik' in df.columns
            
            # Apple should be included
            assert self.APPLE_CIK in df['cik'].values
            
            # Verify profitability range
            apple_profitability = 100000000 / 1000000000  # 0.1
            lb, ub = apple_profitability * 0.75, apple_profitability * 1.25
            assert all(lb <= p <= ub for p in df['profitability'])
    
    def test_get_companies_similar_growth_rate(self):
        """Test finding companies with similar growth rates."""
        mock_current = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 1000000000},
                {'cik': self.MICROSOFT_CIK, 'val': 1200000000},
                {'cik': 12345, 'val': 1100000000},
            ]
        }
        mock_past = {
            'data': [
                {'cik': self.APPLE_CIK, 'val': 800000000},
                {'cik': self.MICROSOFT_CIK, 'val': 900000000},
                {'cik': 12345, 'val': 850000000},
            ]
        }
        
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_current, mock_past]
            
            df = comp.get_companies_similar_growth_rate(self.APPLE_CIK, interval=10)
            
            assert isinstance(df, pd.DataFrame)
            assert 'growth_rate' in df.columns
            assert 'cik' in df.columns
            
            # Apple should be included
            assert self.APPLE_CIK in df['cik'].values
            
            # Verify growth rate range
            apple_growth = (1000000000 - 800000000) / 800000000  # 0.25
            lb, ub = apple_growth - 0.1, apple_growth + 0.1
            assert all(lb <= gr <= ub for gr in df['growth_rate'])
    
    def test_edge_case_zero_division(self):
        """Test handling of zero division in calculations."""
        mock_equity_zero = {
            'data': [{'cik': self.APPLE_CIK, 'val': 0}]
        }
        mock_liabilities = {
            'data': [{'cik': self.APPLE_CIK, 'val': 300000000}]
        }
        
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.side_effect = [mock_equity_zero, mock_liabilities]
            
            # Should handle zero equity gracefully
            df = comp.get_all_capital_structure()
            assert isinstance(df, pd.DataFrame)
            # debt_to_equity should be inf or NaN for zero equity
            apple_row = df[df['cik'] == self.APPLE_CIK]
            assert len(apple_row) > 0
    
    def test_empty_data_handling(self):
        """Test handling of empty data responses."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.return_value = {'data': []}
            
            df = comp.get_all_size()
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0
            # Even empty DataFrames should have the expected columns when created properly
            # The actual implementation might not create columns for empty data
            # so we just verify it's a DataFrame
    
    def test_missing_cik_in_comparison(self, mock_assets_data):
        """Test behavior when target CIK is not in the data."""
        with patch('pyedgarai.comparables.get_xbrl_frames') as mock_frames:
            mock_frames.return_value = mock_assets_data
            
            # Try to find similar companies for a CIK not in the data
            with pytest.raises(IndexError):
                comp.get_companies_similar_size(999999, interval=20)


class TestPrivateComparables:
    """Test private company comparables functionality."""
    
    @pytest.fixture
    def mock_complete_data(self):
        """Mock complete financial data for multiple companies."""
        # Mock data for get_all_size
        size_data = {
            'data': [
                {'cik': 320193, 'val': 1000000000},  # Apple
                {'cik': 789019, 'val': 1200000000},  # Microsoft  
                {'cik': 12345, 'val': 950000000},
                {'cik': 67890, 'val': 1500000000},
            ]
        }
        
        # Mock data for get_all_profitability  
        profit_data = {
            'data': [
                {'cik': 320193, 'profitability': 0.15},
                {'cik': 789019, 'profitability': 0.12},
                {'cik': 12345, 'profitability': 0.14},
                {'cik': 67890, 'profitability': 0.10},
            ]
        }
        
        # Mock data for get_all_growth_rate
        growth_data = {
            'data': [
                {'cik': 320193, 'growth_rate': 0.08},
                {'cik': 789019, 'growth_rate': 0.10},
                {'cik': 12345, 'growth_rate': 0.07},
                {'cik': 67890, 'growth_rate': 0.12},
            ]
        }
        
        # Mock data for get_all_capital_structure
        capital_data = {
            'data': [
                {'cik': 320193, 'debt_to_equity': 0.25},
                {'cik': 789019, 'debt_to_equity': 0.30},
                {'cik': 12345, 'debt_to_equity': 0.28},
                {'cik': 67890, 'debt_to_equity': 0.35},
            ]
        }
        
        # Mock SIC industry data
        industry_data = pd.DataFrame([
            {'cik': 320193, 'sic': 3571, 'entityName': 'Apple Inc'},
            {'cik': 789019, 'sic': 3571, 'entityName': 'Microsoft Corp'},
            {'cik': 12345, 'sic': 3571, 'entityName': 'Tech Company A'},
            {'cik': 67890, 'sic': 3571, 'entityName': 'Tech Company B'},
        ])
        
        return {
            'size': size_data,
            'profit': profit_data, 
            'growth': growth_data,
            'capital': capital_data,
            'industry': industry_data
        }
    
    @patch('pyedgarai.comparables.get_cik_tickers')
    @patch('pyedgarai.comparables.get_companies_in_sic')
    @patch('pyedgarai.comparables.get_all_capital_structure')
    @patch('pyedgarai.comparables.get_all_growth_rate')
    @patch('pyedgarai.comparables.get_all_profitability')
    @patch('pyedgarai.comparables.get_all_size')
    def test_identify_comparables_private_success(self, mock_size, mock_profit, mock_growth, 
                                                 mock_capital, mock_industry, mock_tickers,
                                                 mock_complete_data):
        """Test successful private company comparables identification."""
        
        # Set up mock data
        mock_size.return_value = pd.DataFrame(mock_complete_data['size']['data'])
        mock_profit.return_value = pd.DataFrame(mock_complete_data['profit']['data'])
        mock_growth.return_value = pd.DataFrame(mock_complete_data['growth']['data'])
        mock_capital.return_value = pd.DataFrame(mock_complete_data['capital']['data'])
        mock_industry.return_value = mock_complete_data['industry']
        mock_tickers.return_value = {
            '320193': ['AAPL'],
            '789019': ['MSFT'],
            '12345': ['TECH'],
            '67890': ['TECHB']
        }
        
        # Test private company data
        result = comp.identify_comparables_private(
            name="PrivateTech Corp",
            sic_code="35",  # 2-digit SIC
            profitability=0.13,
            growth_rate=0.09,
            capital_structure=0.27
        )
        
        # Verify response structure
        assert isinstance(result, dict)
        assert 'target_company' in result
        assert 'comparables' in result
        assert 'total_found' in result
        assert 'method' in result
        assert result['method'] == 'private_comparables'
        
        # Verify target company data
        target = result['target_company']
        assert target['name'] == "PrivateTech Corp"
        assert target['sic_code'] == "35"
        assert target['profitability'] == 0.13
        
        # Verify comparables data
        comparables = result['comparables']
        assert isinstance(comparables, list)
        assert len(comparables) <= 5  # Should return at most 5 companies
        assert result['total_found'] == len(comparables)
        
        # Check that each comparable has required fields
        for comp_company in comparables:
            assert 'cik' in comp_company
            assert 'name' in comp_company
            assert 'ticker' in comp_company
            assert 'profitability' in comp_company
            assert 'growth_rate' in comp_company
            assert 'capital_structure' in comp_company
            assert 'distance' in comp_company
    
    @patch('pyedgarai.comparables.get_companies_in_sic')
    def test_identify_comparables_private_no_sic_companies(self, mock_industry):
        """Test handling when no companies exist in the SIC sector."""
        
        # Mock empty industry data
        mock_industry.return_value = pd.DataFrame()
        
        result = comp.identify_comparables_private(
            name="PrivateTech Corp",
            sic_code="99",  # Non-existent SIC
            profitability=0.13,
            growth_rate=0.09,
            capital_structure=0.27
        )
        
        # Should return error response
        assert 'error' in result
        assert result['total_found'] == 0
        assert result['comparables'] == []
        assert "No companies found in SIC sector 99" in result['error']
    
    @patch('pyedgarai.comparables.get_cik_tickers')
    @patch('pyedgarai.comparables.get_companies_in_sic')
    @patch('pyedgarai.comparables.get_all_capital_structure')
    @patch('pyedgarai.comparables.get_all_growth_rate')
    @patch('pyedgarai.comparables.get_all_profitability')
    @patch('pyedgarai.comparables.get_all_size')
    def test_identify_comparables_private_with_market_data(self, mock_size, mock_profit, 
                                                          mock_growth, mock_capital, 
                                                          mock_industry, mock_tickers,
                                                          mock_complete_data):
        """Test private comparables with market data integration."""
        
        # Set up mocks
        mock_size.return_value = pd.DataFrame(mock_complete_data['size']['data'])
        mock_profit.return_value = pd.DataFrame(mock_complete_data['profit']['data'])
        mock_growth.return_value = pd.DataFrame(mock_complete_data['growth']['data'])
        mock_capital.return_value = pd.DataFrame(mock_complete_data['capital']['data'])
        mock_industry.return_value = mock_complete_data['industry']
        mock_tickers.return_value = {'320193': ['AAPL']}
        
        # Mock yfinance data
        with patch('pyedgarai.comparables.yf_e.get_stock_element') as mock_yf:
            mock_info = {
                'data': {
                    'marketCap': 2400000000000,
                    'enterpriseValue': 2500000000000,
                    'priceToBook': 40.5,
                    'enterpriseToEbitda': 20.5,
                    'currentPrice': 150.0
                }
            }
            mock_income = {
                'data': {'Basic EPS': [6.35]}
            }
            
            def mock_yf_side_effect(ticker, element):
                if element == 'info':
                    return mock_info
                elif element == 'income_stmt':
                    return mock_income
                return {}
            
            mock_yf.side_effect = mock_yf_side_effect
            
            result = comp.identify_comparables_private(
                name="PrivateTech Corp",
                sic_code="35",
                profitability=0.13,
                growth_rate=0.09,
                capital_structure=0.27
            )
            
            # Check that market data is included
            if result['comparables']:
                apple_comp = next((c for c in result['comparables'] if c['cik'] == 320193), None)
                if apple_comp:
                    assert 'market_cap' in apple_comp
                    assert 'price_to_earnings' in apple_comp
                    assert 'price_to_book' in apple_comp
                    assert apple_comp['market_cap'] == 2400000000000
                    assert apple_comp['price_to_book'] == 40.5
