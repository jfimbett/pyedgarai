#!/usr/bin/env python3
"""
Test script for PyEdgarAI Comparables API endpoints

This script demonstrates how to call the comparables API endpoints
and shows the structure and content of the responses.

Make sure the API server is running before executing this script:
python start_api.py
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://127.0.0.1:5000"
API_TOKEN = ""  # Leave empty if authentication is disabled

def make_request(endpoint: str, params: Dict[str, Any]) -> Dict:
    """
    Make a GET request to the API endpoint with parameters
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"🔗 Making request to: {url}")
        print(f"📊 Parameters: {json.dumps(params, indent=2)}")
        print("-" * 60)
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received successfully")
            print(f"📋 Response type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"🔑 Response keys: {list(data.keys())}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detail": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"error": "Request failed", "detail": str(e)}

def test_traditional_comparables():
    """
    Test the traditional comparables endpoint
    """
    print("\n" + "=" * 80)
    print("🏢 TESTING TRADITIONAL COMPARABLES ANALYSIS")
    print("=" * 80)
    
    # Example: Find companies similar to Apple Inc. (CIK: 320193)
    params = {
        "cik": 320193,  # Apple Inc.
        "method": "traditional",
        "industry_digits": 2,  # 2-digit SIC code matching
        "size_interval": 1000000000,  # Size interval in USD (1B)
        "profitability_interval": 0.05,  # 5% profitability interval
        "growth_rate_interval": 0.1,  # 10% growth rate interval
        "capital_structure_interval": 0.2,  # 20% capital structure interval
        "api_token": API_TOKEN
    }
    
    response = make_request("/comparables", params)
    
    print("\n📊 RESPONSE ANALYSIS:")
    print(f"Response type: {type(response)}")
    
    if "error" not in response:
        print(f"✅ Success! Found comparable analysis for CIK {params['cik']}")
        
        # Analyze response structure
        if isinstance(response, dict):
            for key, value in response.items():
                print(f"🔑 {key}: {type(value)}")
                if isinstance(value, list) and len(value) > 0:
                    print(f"   📝 List with {len(value)} items")
                    print(f"   📋 First item type: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"   🗝️  First item keys: {list(value[0].keys())}")
                elif isinstance(value, dict) and len(value) > 0:
                    print(f"   🗝️  Dict keys: {list(value.keys())}")
        
        # Print formatted response
        print("\n📄 FULL RESPONSE:")
        print(json.dumps(response, indent=2, default=str))
    else:
        print(f"❌ Error in response: {response}")
    
    return response

def test_ml_comparables():
    """
    Test the ML-powered comparables endpoint
    """
    print("\n" + "=" * 80)
    print("🤖 TESTING ML-POWERED COMPARABLES ANALYSIS")
    print("=" * 80)
    
    # Example: Find companies similar to a hypothetical tech company
    params = {
        "name": "Apple Inc.",
        "sic": "3571",  # Electronic Computers
        "assets": 352755000000,  # $352.755B in assets (Apple's approximate)
        "profitability": 0.25,  # 25% profitability (Net Income/Assets)
        "growth_rate": 0.05,  # 5% annual growth rate
        "capital_structure": 0.3,  # 30% debt-to-equity ratio
        "api_token": API_TOKEN
    }
    
    response = make_request("/comparables_kmeans", params)
    
    print("\n📊 RESPONSE ANALYSIS:")
    print(f"Response type: {type(response)}")
    
    if "error" not in response:
        print(f"✅ Success! Found ML-based comparables for {params['name']}")
        
        # Analyze response structure
        if isinstance(response, dict):
            for key, value in response.items():
                print(f"🔑 {key}: {type(value)}")
                if isinstance(value, list) and len(value) > 0:
                    print(f"   📝 List with {len(value)} items")
                elif isinstance(value, dict) and len(value) > 0:
                    print(f"   🗝️  Dict keys: {list(value.keys())}")
        
        # Print formatted response
        print("\n📄 FULL RESPONSE:")
        print(json.dumps(response, indent=2, default=str))
    else:
        print(f"❌ Error in response: {response}")
    
    return response

def test_sic_comparables():
    """
    Test the SIC-based comparables endpoint
    """
    print("\n" + "=" * 80)
    print("🏭 TESTING SIC-BASED COMPARABLES ANALYSIS")
    print("=" * 80)
    
    # Example: Find companies with same SIC code as Apple
    params = {
        "cik": 320193,  # Apple Inc.
        "api_token": API_TOKEN
    }
    
    response = make_request("/comparables_sic", params)
    
    print("\n📊 RESPONSE ANALYSIS:")
    print(f"Response type: {type(response)}")
    
    if "error" not in response:
        print(f"✅ Success! Found SIC-based comparables for CIK {params['cik']}")
        
        # Analyze response structure
        if isinstance(response, list):
            print(f"📝 Response is a list with {len(response)} items")
            if len(response) > 0:
                print(f"📋 First item type: {type(response[0])}")
                if isinstance(response[0], dict):
                    print(f"🗝️  First item keys: {list(response[0].keys())}")
        elif isinstance(response, dict):
            for key, value in response.items():
                print(f"🔑 {key}: {type(value)}")
        
        # Print formatted response (limit output if too large)
        if isinstance(response, list) and len(response) > 10:
            print(f"\n📄 SAMPLE RESPONSE (showing first 3 of {len(response)} items):")
            print(json.dumps(response[:3], indent=2, default=str))
            print("... (truncated)")
        else:
            print("\n📄 FULL RESPONSE:")
            print(json.dumps(response, indent=2, default=str))
    else:
        print(f"❌ Error in response: {response}")
    
    return response

def test_api_connectivity():
    """
    Test basic API connectivity
    """
    print("\n" + "=" * 80)
    print("🔍 TESTING API CONNECTIVITY")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and accessible")
            api_info = response.json()
            print(f"🏷️  API Version: {api_info.get('version', 'Unknown')}")
            print(f"📝 Description: {api_info.get('description', 'No description')}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the API server is running with: python start_api.py")
        return False

def main():
    """
    Main test function
    """
    print("🚀 PyEdgarAI Comparables API Test Suite")
    print("=" * 80)
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ Cannot proceed with tests - API is not accessible")
        return
    
    print(f"\n⏰ Starting comprehensive API tests...")
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"🔐 API Token: {'Set' if API_TOKEN else 'Not set (using development mode)'}")
    
    # Run all tests
    tests = [
        ("Traditional Comparables", test_traditional_comparables),
        ("ML Comparables", test_ml_comparables),
        ("SIC Comparables", test_sic_comparables)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n⏱️  Running {test_name} test...")
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            results[test_name] = {
                "success": "error" not in result,
                "duration": round(end_time - start_time, 2),
                "response_size": len(str(result))
            }
            
            print(f"⏱️  Test completed in {results[test_name]['duration']} seconds")
            
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = {"success": False, "error": str(e)}
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        duration = f"({result.get('duration', 0)}s)" if result.get('duration') else ""
        print(f"{status} {test_name} {duration}")
        
        if not result["success"] and "error" in result:
            print(f"   Error: {result['error']}")
    
    print(f"\n🎯 Total tests: {len(results)}")
    print(f"✅ Passed: {sum(1 for r in results.values() if r['success'])}")
    print(f"❌ Failed: {sum(1 for r in results.values() if not r['success'])}")

if __name__ == "__main__":
    main()
