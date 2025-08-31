"""Tests for SEC API client functionality."""
import pytest
import requests
from unittest.mock import patch, Mock
import pandas as pd

from pyedgarai import sec_client as sec


class TestSECClient:
    """Test SEC API client functions."""
    
    APPLE_CIK = 320193
    MICROSOFT_CIK = 789019
    INVALID_CIK = 999999999
    
    @patch('pyedgarai.sec_client.requests.get')
    def test_get_submission_history_valid_cik(self, mock_get):
        """Test fetching submission history for valid CIK."""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'cik': '0000320193',
            'name': 'Apple Inc.',
            'filings': {'recent': {'form': ['10-K', '10-Q']}}
        }
        
        data = sec.get_submission_history(self.APPLE_CIK)
        
        # Verify structure
        assert isinstance(data, dict)
        assert 'cik' in data
        assert 'name' in data
        assert 'filings' in data
        
        # Verify Apple-specific data
        assert data['cik'] == '0000320193'  # SEC formats with leading zeros
        assert 'Apple' in data['name']
        
    def test_get_submission_history_invalid_cik(self):
        """Test handling of invalid CIK."""
        with pytest.raises(requests.exceptions.HTTPError):
            sec.get_submission_history(self.INVALID_CIK)
    
    @patch('pyedgarai.sec_client.requests.get')
    def test_get_company_facts_valid_cik(self, mock_get):
        """Test fetching company facts for valid CIK."""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'facts': {'us-gaap': {'Assets': {'units': {'USD': []}}}},
            'entityName': 'Apple Inc.'
        }
        
        facts = sec.get_company_facts(self.APPLE_CIK)
        
        # Verify structure
        assert isinstance(facts, dict)
        assert 'facts' in facts
        assert 'entityName' in facts
        assert isinstance(facts['facts'], dict)
        
        # Should contain standard taxonomies
        assert 'us-gaap' in facts['facts'] or 'dei' in facts['facts']
        
    def test_get_company_facts_invalid_cik(self):
        """Test handling of invalid CIK for company facts."""
        with pytest.raises(requests.exceptions.HTTPError):
            sec.get_company_facts(self.INVALID_CIK)
    
    @patch('pyedgarai.sec_client.requests.get')
    def test_get_company_concept_valid_data(self, mock_get):
        """Test fetching specific company concept."""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag': 'Assets',
            'taxonomy': 'us-gaap',
            'units': {'USD': []}
        }
        
        concept = sec.get_company_concept(self.APPLE_CIK, 'us-gaap', 'Assets')
        
        # Verify structure
        assert isinstance(concept, dict)
        assert concept.get('tag') == 'Assets'
        assert concept.get('taxonomy') == 'us-gaap'
        assert 'units' in concept
        
    def test_get_company_concept_invalid_params(self):
        """Test handling of invalid concept parameters."""
        with pytest.raises(requests.exceptions.HTTPError):
            sec.get_company_concept(self.APPLE_CIK, 'invalid-taxonomy', 'InvalidTag')
    
    @patch('pyedgarai.sec_client.requests.get')
    def test_get_xbrl_frames_valid_params(self, mock_get):
        """Test fetching XBRL frames with valid parameters."""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'cik': 320193, 'val': 1000000000, 'end': '2023-12-31', 'accn': '0000320193-24-000006'},
                {'cik': 789019, 'val': 1200000000, 'end': '2023-12-31', 'accn': '0000789019-24-000007'}
            ]
        }
        
        frames = sec.get_xbrl_frames('us-gaap', 'Assets', 'USD', 'CY2023Q4I')
        
        # Verify structure
        assert isinstance(frames, dict)
        assert 'data' in frames
        assert isinstance(frames['data'], list)
        
        # Verify data contains expected fields
        if frames['data']:
            sample_record = frames['data'][0]
            expected_fields = ['cik', 'val', 'end', 'accn']
            for field in expected_fields:
                assert field in sample_record
    
    def test_get_xbrl_frames_invalid_params(self):
        """Test handling of invalid XBRL frame parameters."""
        with pytest.raises(requests.exceptions.HTTPError):
            sec.get_xbrl_frames('invalid-taxonomy', 'InvalidTag', 'USD', 'CY2023Q4I')
    
    @patch('pyedgarai.sec_client.requests.get')
    def test_http_error_handling(self, mock_get):
        """Test proper HTTP error handling."""
        # Mock a 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            sec.get_company_facts(self.INVALID_CIK)
    
    def test_headers_are_set(self):
        """Test that proper headers are being sent to SEC API."""
        # This is important for SEC API compliance
        with patch('pyedgarai.sec_client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'test': 'data'}
            mock_get.return_value = mock_response
            
            sec.get_company_facts(self.APPLE_CIK)
            
            # Verify headers were passed
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert 'headers' in kwargs
            assert 'User-Agent' in kwargs['headers']
            assert 'pyedgarai' in kwargs['headers']['User-Agent']
