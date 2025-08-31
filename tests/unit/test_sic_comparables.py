#!/usr/bin/env python3
"""
Quick API test with SIC-only comparables (fast method)

This tests the API using only SIC-based comparison, which should be fast
since we have the data cached locally.
"""

import requests
import json

def test_sic_comparables():
    """Test the SIC-only comparables endpoint"""
    print("🚀 PyEdgarAI SIC Comparables Test")
    print("=" * 50)
    
    # Test with Apple Inc.
    cik = 320193
    
    print(f"🍎 Testing SIC comparables for Apple Inc. (CIK: {cik})")
    
    # Test the SIC-only endpoint
    url = "http://127.0.0.1:5000/comparables_sic"
    params = {
        "cik": cik,
        "digits": 2,
        "api_token": ""
    }
    
    print(f"📤 Request URL: {url}")
    print(f"📊 Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"📊 Found {len(data.get('companies', []))} comparable companies")
            
            # Show sample results
            companies = data.get('companies', [])[:5]
            print("\n📋 Sample comparable companies:")
            for company in companies:
                cik = company.get('cik', 'N/A')
                name = company.get('name', 'Unknown')
                sic = company.get('sic', 'N/A')
                print(f"   • {name} (CIK: {cik}, SIC: {sic})")
                
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_info():
    """Test basic API connectivity"""
    print("\n🔌 Testing API connectivity...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/api", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connected - Version: {data.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def main():
    """Main test function"""
    if not test_api_info():
        print("💡 Make sure the API server is running: python -m src.pyedgarai.api.server")
        return
    
    test_sic_comparables()
    
    print("\n" + "=" * 50)
    print("💡 For full comparables (slower), use the /comparables endpoint")
    print("💡 For ML comparables, use the /comparables_kmeans endpoint")

if __name__ == "__main__":
    main()
