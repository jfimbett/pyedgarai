"""Integration tests for pyedgarai functionality."""
import pytest
import pandas as pd
from datetime import datetime, timedelta

from pyedgarai import pyedgarai as pe
from pyedgarai import sec_client as sec
from pyedgarai import comparables as comp
from pyedgarai import market_data as md


class TestIntegration:
    """Integration tests that verify end-to-end functionality."""
    
    APPLE_CIK = 320193
    MICROSOFT_CIK = 789019
    
    @pytest.mark.integration
    def test_complete_company_analysis_workflow(self):
        """Test a complete workflow for analyzing a company."""
        # Step 1: Get company basic info
        submission_data = sec.get_submission_history(self.APPLE_CIK)
        assert 'name' in submission_data
        assert 'Apple' in submission_data['name']
        
        # Step 2: Get detailed financial facts
        facts = sec.get_company_facts(self.APPLE_CIK)
        assert 'facts' in facts
        assert 'entityName' in facts
        
        # Step 3: Get specific financial metric (Assets)
        assets_concept = sec.get_company_concept(self.APPLE_CIK, 'us-gaap', 'Assets')
        assert assets_concept.get('tag') == 'Assets'
        
        # Step 4: Find comparable companies by size
        similar_size_companies = comp.get_companies_similar_size(self.APPLE_CIK, interval=50)
        assert isinstance(similar_size_companies, pd.DataFrame)
        # Apple should be in the results
        assert self.APPLE_CIK in similar_size_companies['cik'].values
        
        # Step 5: Get stock market data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        stock_data = md.get_stock_data('AAPL', start_date, end_date)
        assert isinstance(stock_data, pd.DataFrame)
        
        if not stock_data.empty:
            assert 'Close' in stock_data.columns
            assert all(stock_data['ticker'] == 'AAPL')
    
    @pytest.mark.integration
    def test_comparables_analysis_consistency(self):
        """Test that comparables analysis produces consistent results."""
        # Get all metrics for comparison
        size_data = comp.get_all_size()
        profitability_data = comp.get_all_profitability()
        growth_data = comp.get_all_growth_rate()
        capital_structure_data = comp.get_all_capital_structure()
        
        # Verify all return DataFrames
        assert all(isinstance(df, pd.DataFrame) for df in [
            size_data, profitability_data, growth_data, capital_structure_data
        ])
        
        # Verify they all have CIK columns
        assert all('cik' in df.columns for df in [
            size_data, profitability_data, growth_data, capital_structure_data
        ])
        
        # Check for overlapping CIKs (companies that appear in multiple metrics)
        size_ciks = set(size_data['cik'])
        profit_ciks = set(profitability_data['cik'])
        
        overlap = size_ciks.intersection(profit_ciks)
        assert len(overlap) > 0, "Should have companies with both size and profitability data"
    
    @pytest.mark.integration
    def test_multi_company_stock_data_retrieval(self):
        """Test retrieving stock data for multiple companies."""
        # Get ticker mappings
        from pyedgarai.features import get_cik_tickers
        cik_tickers = get_cik_tickers()
        
        # Find tickers for our test companies
        apple_tickers = cik_tickers.get('0000320193', ['AAPL'])
        microsoft_tickers = cik_tickers.get('0000789019', ['MSFT'])
        
        test_tickers = []
        if apple_tickers:
            test_tickers.extend(apple_tickers[:1])  # Take first ticker
        if microsoft_tickers:
            test_tickers.extend(microsoft_tickers[:1])  # Take first ticker
        
        if test_tickers:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            stock_data = md.get_stocks_data(test_tickers, start_date, end_date)
            
            assert isinstance(stock_data, pd.DataFrame)
            if not stock_data.empty:
                # Should have data for multiple tickers
                unique_tickers = stock_data['ticker'].unique()
                assert len(unique_tickers) >= 1
    
    @pytest.mark.integration
    def test_xbrl_frames_data_quality(self):
        """Test the quality and consistency of XBRL frames data."""
        # Get recent quarterly data
        frames = sec.get_xbrl_frames('us-gaap', 'Assets', 'USD', 'CY2023Q4I')
        
        assert 'data' in frames
        assert isinstance(frames['data'], list)
        
        if frames['data']:
            # Check data structure
            sample_record = frames['data'][0]
            required_fields = ['cik', 'val', 'end']
            for field in required_fields:
                assert field in sample_record
            
            # Verify data types and ranges
            for record in frames['data'][:10]:  # Check first 10 records
                assert isinstance(record['cik'], int)
                assert isinstance(record['val'], (int, float))
                assert record['val'] > 0  # Assets should be positive
                assert isinstance(record['end'], str)  # Date string
    
    @pytest.mark.integration 
    def test_error_handling_with_invalid_data(self):
        """Test error handling with invalid inputs."""
        # Test invalid CIK
        with pytest.raises(Exception):  # Should raise HTTPError or similar
            sec.get_company_facts(999999999)
        
        # Test invalid stock ticker
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # This should not crash, might return empty DataFrame
        result = md.get_stock_data('INVALIDTICKER123', start_date, end_date)
        assert isinstance(result, pd.DataFrame)
        
        # Test invalid XBRL parameters
        with pytest.raises(Exception):
            sec.get_xbrl_frames('invalid-taxonomy', 'InvalidTag', 'USD', 'CY2023Q4I')
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_performance(self):
        """Test performance with larger datasets."""
        # Get industry-wide data which should be large
        start_time = datetime.now()
        
        frames = sec.get_xbrl_frames('us-gaap', 'Assets', 'USD', 'CY2023Q4I')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust as needed)
        assert duration < 30, f"Request took {duration} seconds, which is too long"
        
        # Should return substantial data
        assert len(frames['data']) > 100, "Should return data for many companies"
    
    @pytest.mark.integration
    def test_data_consistency_across_apis(self):
        """Test that data is consistent across different API endpoints."""
        # Get Apple's assets via company concept
        concept_data = sec.get_company_concept(self.APPLE_CIK, 'us-gaap', 'Assets')
        
        # Get Apple's data from company facts
        facts_data = sec.get_company_facts(self.APPLE_CIK)
        
        # Both should contain Apple's asset information
        assert concept_data.get('taxonomy') == 'us-gaap'
        assert concept_data.get('tag') == 'Assets'
        
        assert 'facts' in facts_data
        if 'us-gaap' in facts_data['facts'] and 'Assets' in facts_data['facts']['us-gaap']:
            # The data structures should be compatible
            assert isinstance(facts_data['facts']['us-gaap']['Assets'], dict)
    
    @pytest.mark.integration 
    def test_openai_wrapper_initialization(self):
        """Test OpenAI wrapper can be initialized (without making API calls)."""
        from pyedgarai.pyedgarai import OpenAIWrapper
        
        # Test initialization (doesn't require valid API key for this test)
        wrapper = OpenAIWrapper(model="gpt-3.5-turbo", api_key="test-key")
        
        assert wrapper.model == "gpt-3.5-turbo"
        assert wrapper.api_key == "test-key"
        
        # Test that it requires OpenAI to be installed
        # (We can't test actual API calls without valid credentials)
