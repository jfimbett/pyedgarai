#!/usr/bin/env python3
"""
Simple example of how to call PyEdgarAI Comparables API

This shows the basic structure of GET requests and response handling.
"""

import requests
import json

# API Configuration
BASE_URL = "http://127.0.0.1:5000"
API_TOKEN = ""  # Empty string for development mode

def simple_comparables_example():
    """
    Simple example: Find companies comparable to Apple Inc.
    """
    print("🍎 Finding companies comparable to Apple Inc. (CIK: 320193)")
    print("-" * 60)
    
    # Prepare the request parameters
    url = f"{BASE_URL}/comparables"
    params = {
        "cik": 320193,           # Apple's CIK
        "method": "traditional", # Use traditional comparison method
        "industry_digits": 2,    # Match 2-digit SIC codes
        "size_interval": 50000000000,  # 50B size interval
        "api_token": API_TOKEN   # API token (empty for dev mode)
    }
    
    print("📤 Request URL:", url)
    print("📊 Request parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        # Make the GET request
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📈 Response Status: {response.status_code}")
        print(f"📏 Response Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            print("✅ Success! Response received")
            print(f"📋 Response Type: {type(data)}")
            
            # Show response structure
            if isinstance(data, dict):
                print("🔑 Response Keys:")
                for key in data.keys():
                    value = data[key]
                    print(f"   {key}: {type(value).__name__}")
                    
                    # Show details for lists and dicts
                    if isinstance(value, list):
                        print(f"      └─ List with {len(value)} items")
                        if len(value) > 0:
                            print(f"         First item type: {type(value[0]).__name__}")
                    elif isinstance(value, dict):
                        print(f"      └─ Dict with keys: {list(value.keys())}")
            
            # Print the actual response (formatted)
            print("\n📄 Full Response:")
            print(json.dumps(data, indent=2, default=str))
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to the API")
        print("💡 Make sure the API server is running: python start_api.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError:
        print("❌ Invalid JSON response")

def simple_ml_example():
    """
    Simple example: ML-powered comparison
    """
    print("\n🤖 ML-powered comparison example")
    print("-" * 60)
    
    url = f"{BASE_URL}/comparables_kmeans"
    params = {
        "name": "Apple Inc.",
        "sic": "3571",                # Electronic computers
        "assets": 352755000000,       # ~$353B
        "profitability": 0.25,        # 25%
        "growth_rate": 0.05,          # 5%
        "capital_structure": 0.3,     # 30%
        "api_token": API_TOKEN
    }
    
    print("📤 Request URL:", url)
    print("📊 ML Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ML Analysis Complete!")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 PyEdgarAI Comparables API - Simple Examples")
    print("=" * 80)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/api", timeout=5)
        if response.status_code == 200:
            api_info = response.json()
            print(f"✅ API Connected - Version: {api_info.get('version', 'Unknown')}")
        else:
            print(f"⚠️  API responded with status: {response.status_code}")
    except:
        print("❌ Cannot connect to API - make sure it's running")
        exit(1)
    
    # Run examples
    simple_comparables_example()
    simple_ml_example()
    
    print("\n✅ Examples completed!")
    print("💡 For more detailed testing, run: python test_comparables_api.py")
