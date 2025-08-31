#!/usr/bin/env python3
"""
Lightweight API test that bypasses heavy imports

This tests the API directly with HTTP requests to see the actual responses
without importing the heavy modules that are causing hangs.
"""

import requests
import json

def test_api_status():
    """Test basic API status"""
    print("🔌 Testing API connectivity...")
    
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

def test_documentation_endpoints():
    """Test that documentation endpoints work"""
    print("\n📚 Testing documentation endpoints...")
    
    endpoints = [
        "/openapi/swagger",
        "/openapi/redoc", 
        "/openapi/rapidoc",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:5000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - {e}")

def test_simple_endpoints():
    """Test simple endpoints that shouldn't require heavy computation"""
    print("\n🧪 Testing simple endpoints...")
    
    # Test home page
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Home page - Working")
        else:
            print(f"❌ Home page - Error {response.status_code}")
    except Exception as e:
        print(f"❌ Home page - {e}")

def check_data_files():
    """Check if our data files exist and are readable"""
    print("\n📁 Checking data files...")
    
    import os
    cache_dir = r"C:\Users\jfimb\.cache\pyedgarai"
    
    files = ["cik_sic.json", "cik_company_names.json"]
    
    for filename in files:
        filepath = os.path.join(cache_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"✅ {filename} - {len(data)} entries")
            except Exception as e:
                print(f"❌ {filename} - Error reading: {e}")
        else:
            print(f"❌ {filename} - Not found")

def test_direct_sic_endpoint():
    """Test the SIC endpoint directly with a raw request"""
    print("\n🏢 Testing SIC endpoint directly...")
    
    # Apple's CIK
    cik = 320193
    
    params = {
        "cik": cik,
        "api_token": ""
    }
    
    print(f"📤 Testing /comparables_sic with CIK {cik}")
    
    try:
        response = requests.get(
            "http://127.0.0.1:5000/comparables_sic", 
            params=params, 
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ SIC endpoint working!")
                
                # Check response structure
                if isinstance(data, dict):
                    print(f"📊 Response keys: {list(data.keys())}")
                    
                    # Look for companies data
                    if 'companies' in data:
                        companies = data['companies']
                        print(f"🏢 Found {len(companies)} companies")
                        
                        # Show sample
                        for i, company in enumerate(companies[:3]):
                            print(f"   {i+1}. {company}")
                    
                elif isinstance(data, list):
                    print(f"📋 Response is list with {len(data)} items")
                    for i, item in enumerate(data[:3]):
                        print(f"   {i+1}. {item}")
                
                return True
                
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Raw response: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ Error response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 PyEdgarAI API Direct Test")
    print("=" * 50)
    
    # Basic tests
    if not test_api_status():
        print("💡 Make sure the API server is running!")
        return
    
    check_data_files()
    test_documentation_endpoints()
    test_simple_endpoints()
    
    # Main functionality test
    print("\n" + "=" * 50)
    print("🧪 Testing main functionality...")
    test_direct_sic_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Direct API testing completed!")

if __name__ == "__main__":
    main()
