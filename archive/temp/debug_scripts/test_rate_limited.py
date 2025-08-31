#!/usr/bin/env python3
"""
Test the rate-limited version of comparable_private endpoint
"""

import sys
import os
sys.path.insert(0, 'src')
import requests
import json

def test_comparable_private_with_rate_limiting():
    """Test the endpoint with just a few companies to see if rate limiting helps"""
    print("🧪 Testing comparable_private with Rate Limiting")
    print("=" * 50)
    
    try:
        # Test with your example parameters
        url = "http://localhost:5000/comparable_private"
        params = {
            "api_token": "test_token",
            "sic_code": 65,
            "name": "Test Private REIT",
            "profitability": 0.05,
            "growth_rate": 0.10,
            "capital_structure": 0.40
        }
        
        print(f"🎯 Making API call to: {url}")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data.get('comparables', []))} comparables")
            
            # Check if we got market data for any companies
            market_data_count = 0
            for comp in data.get('comparables', []):
                if comp.get('market_cap') is not None:
                    market_data_count += 1
            
            print(f"📊 Companies with market data: {market_data_count}/{len(data.get('comparables', []))}")
            
            # Show first comparable with details
            if data.get('comparables'):
                first_comp = data['comparables'][0]
                print(f"\n📈 Sample Comparable:")
                print(f"   Company: {first_comp.get('name')}")
                print(f"   Ticker: {first_comp.get('ticker')}")
                print(f"   Market Cap: ${first_comp.get('market_cap'):,}" if first_comp.get('market_cap') else "   Market Cap: None")
                print(f"   Current Price: ${first_comp.get('current_price')}" if first_comp.get('current_price') else "   Current Price: None")
                print(f"   P/E Ratio: {first_comp.get('price_to_earnings')}" if first_comp.get('price_to_earnings') else "   P/E Ratio: None")
                print(f"   Distance: {first_comp.get('distance'):.3f}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("💡 Make sure the Flask server is running:")
        print("   cd src && python -m pyedgarai.api.server")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comparable_private_with_rate_limiting()
