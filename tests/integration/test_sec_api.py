#!/usr/bin/env python3
"""Simple script to test SEC API access."""

import requests
import time

# SEC API test - try different approaches
HEADERS_APPROACHES = [
    # Approach 1: Standard browser-like headers
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 pyedgarai/0.8.0 (+https://github.com/jfimbett/pyedgarai; jfimbett@gmail.com)",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    },
    # Approach 2: Simple academic/research identifier
    {
        "User-Agent": "Academic Research Tool - pyedgarai 0.8.0 - Contact: jfimbett@gmail.com"
    },
    # Approach 3: Standard requests library
    {
        "User-Agent": "python-requests/2.31.0 (Academic Research; Contact: jfimbett@gmail.com)"
    }
]

def test_sec_api():
    """Test basic SEC API access with different header approaches."""
    apple_cik = 320193
    url = f"https://data.sec.gov/submissions/CIK{apple_cik:010d}.json"
    
    print(f"Testing URL: {url}")
    
    for i, headers in enumerate(HEADERS_APPROACHES, 1):
        print(f"\n--- Approach {i} ---")
        print(f"Headers: {headers}")
        
        try:
            time.sleep(0.2)  # Rate limiting
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Company: {data.get('name', 'Unknown')}")
                print(f"CIK: {data.get('cik', 'Unknown')}")
                return True, headers
            else:
                print(f"❌ Error: {response.status_code} - {response.reason}")
                if response.status_code == 403:
                    print(f"Response snippet: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
    
    return False, None

if __name__ == "__main__":
    print("Testing SEC API access with different approaches...")
    success, working_headers = test_sec_api()
    if success:
        print(f"\n🎉 SEC API access successful with headers:")
        print(working_headers)
    else:
        print(f"\n💥 All approaches failed. SEC API may be blocking all automated access.")
