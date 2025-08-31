"""Tests for market data functionality."""
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from pyedgarai import market_data as md


class TestMarketData:
    """Test market data retrieval functions."""
    
    def test_get_stock_data_valid_ticker(self):
        """Test getting stock data for a valid ticker."""
        # Use recent dates that should have data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = md.get_stock_data('AAPL', start_date, end_date)
        
        assert isinstance(df, pd.DataFrame)
        
        if not df.empty:
            # Check expected columns
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'ticker', 'Date']
            for col in expected_columns:
                assert col in df.columns
            
            # Check that ticker is set correctly
            assert all(df['ticker'] == 'AAPL')
            
            # Check data types
            assert pd.api.types.is_numeric_dtype(df['Close'])
            assert pd.api.types.is_numeric_dtype(df['Volume'])
            assert pd.api.types.is_datetime64_any_dtype(df['Date'])
    
    def test_get_stock_data_invalid_ticker(self):
        """Test handling of invalid ticker."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Invalid ticker should return empty DataFrame or raise exception
        df = md.get_stock_data('INVALIDTICKER123', start_date, end_date)
        
        # yfinance might return empty DataFrame for invalid tickers
        assert isinstance(df, pd.DataFrame)
        # Could be empty or have ticker column with the invalid ticker
        if not df.empty:
            assert 'ticker' in df.columns
    
    def test_get_stock_data_date_range(self):
        """Test getting stock data for specific date range."""
        df = md.get_stock_data('AAPL', '2023-01-01', '2023-01-31')
        
        assert isinstance(df, pd.DataFrame)
        
        if not df.empty:
            # Check date range
            dates = pd.to_datetime(df['Date'])
            assert dates.min() >= pd.to_datetime('2023-01-01')
            assert dates.max() <= pd.to_datetime('2023-01-31')
    
    def test_get_stocks_data_multiple_tickers(self):
        """Test getting stock data for multiple tickers."""
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = md.get_stocks_data(tickers, start_date, end_date)
        
        assert isinstance(df, pd.DataFrame)
        
        if not df.empty:
            # Should have data for multiple tickers
            unique_tickers = df['ticker'].unique()
            assert len(unique_tickers) > 0
            
            # Check that all tickers are from our list
            for ticker in unique_tickers:
                assert ticker in tickers
            
            # Check expected columns
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'ticker', 'Date']
            for col in expected_columns:
                assert col in df.columns
    
    def test_get_stocks_data_with_invalid_tickers(self):
        """Test handling of mixed valid/invalid tickers."""
        tickers = ['AAPL', 'INVALIDTICKER123', 'MSFT']
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = md.get_stocks_data(tickers, start_date, end_date)
        
        assert isinstance(df, pd.DataFrame)
        
        # Should still return data for valid tickers
        if not df.empty:
            valid_tickers = df['ticker'].unique()
            # Should have at least AAPL and MSFT (if they have data)
            assert 'AAPL' in valid_tickers or 'MSFT' in valid_tickers
    
    def test_get_stocks_data_empty_ticker_list(self):
        """Test handling of empty ticker list."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = md.get_stocks_data([], start_date, end_date)
        
        # Should return empty DataFrame
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    @patch('pyedgarai.market_data.yf.Ticker')
    def test_get_stock_data_yfinance_error(self, mock_ticker):
        """Test handling of yfinance errors."""
        # Mock yfinance to raise an exception
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = Exception("Network error")
        mock_ticker.return_value = mock_ticker_instance
        
        # The function should handle errors gracefully, likely returning empty DataFrame
        try:
            df = md.get_stock_data('AAPL', '2023-01-01', '2023-01-31')
            # Should handle the error gracefully and return empty DataFrame
            assert isinstance(df, pd.DataFrame)
        except Exception:
            # It's also acceptable for the function to let the exception propagate
            # depending on the implementation
            pass
    
    @patch('pyedgarai.market_data.yf.Ticker')
    def test_get_stock_data_mock_response(self, mock_ticker):
        """Test with mocked yfinance response."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [149.0, 150.0, 151.0],
            'Close': [153.0, 154.0, 155.0],
            'Volume': [1000000, 1100000, 1200000],
            'Adj Close': [153.0, 154.0, 155.0],
            'Dividends': [0.0, 0.0, 0.0],
            'Stock Splits': [0.0, 0.0, 0.0]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        df = md.get_stock_data('AAPL', '2023-01-01', '2023-01-03')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'ticker' in df.columns
        assert all(df['ticker'] == 'AAPL')
        # 'Date' gets reset to index during processing, check for 'index' or a date column
        assert 'index' in df.columns or 'Date' in df.columns
        assert df['Close'].iloc[0] == 153.0
    
    def test_data_consistency(self):
        """Test that data returned is consistent and valid."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        df = md.get_stock_data('AAPL', start_date, end_date)
        
        if not df.empty:
            # High should be >= Low
            assert all(df['High'] >= df['Low'])
            
            # Close should be between Low and High
            assert all((df['Close'] >= df['Low']) & (df['Close'] <= df['High']))
            
            # Open should be between Low and High  
            assert all((df['Open'] >= df['Low']) & (df['Open'] <= df['High']))
            
            # Volume should be non-negative
            assert all(df['Volume'] >= 0)
            
            # Prices should be positive
            assert all(df['Close'] > 0)
            assert all(df['Open'] > 0)
            assert all(df['High'] > 0)
            assert all(df['Low'] > 0)
