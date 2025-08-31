#!/usr/bin/env python3
"""
Debug yfinance integration for comparable_private endpoint
"""

import sys
import os
sys.path.insert(0, 'src')

def test_ticker_availability():
    """Test how many companies actually have tickers"""
    print("🎯 Testing Ticker Availability")
    print("=" * 40)
    
    try:
        from pyedgarai.features import get_cik_tickers
        from pyedgarai.comparables import get_companies_in_sic
        
        # Get SIC 65 companies (like in your example)
        companies_65 = get_companies_in_sic(65, digits=2)
        print(f"📊 Total companies in SIC 65: {len(companies_65)}")
        
        # Get ticker mapping
        cik_tickers = get_cik_tickers()
        
        # Check ticker availability
        with_tickers = 0
        sample_with_tickers = []
        sample_without_tickers = []
        
        for _, company in companies_65.iterrows():
            cik = str(int(company['cik']))
            name = company.get('name', 'Unknown')
            tickers = cik_tickers.get(cik, [])
            
            if tickers:
                with_tickers += 1
                if len(sample_with_tickers) < 5:
                    sample_with_tickers.append((cik, name, tickers))
            else:
                if len(sample_without_tickers) < 5:
                    sample_without_tickers.append((cik, name))
        
        print(f"✅ Companies with tickers: {with_tickers}/{len(companies_65)} ({with_tickers/len(companies_65)*100:.1f}%)")
        
        print(f"\n📈 Sample companies WITH tickers:")
        for cik, name, tickers in sample_with_tickers:
            print(f"   CIK {cik}: {name} → {tickers}")
            
        print(f"\n📉 Sample companies WITHOUT tickers:")
        for cik, name in sample_without_tickers:
            print(f"   CIK {cik}: {name} → No ticker")
        
        return sample_with_tickers
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def test_yfinance_calls(sample_tickers):
    """Test yfinance calls directly"""
    print(f"\n🧪 Testing yfinance Integration")
    print("=" * 40)
    
    try:
        from pyedgarai import yfinance_endpoints as yf_e
        import json
        
        for cik, name, tickers in sample_tickers[:3]:  # Test first 3
            ticker = tickers[0]  # Use first ticker
            print(f"\n🎯 Testing {ticker} ({name}):")
            
            try:
                # Test info call
                info = yf_e.get_stock_element(ticker, 'info')
                print(f"   ✅ Info call successful: {type(info)}")
                
                if isinstance(info, dict) and 'data' in info:
                    info_data = info['data']
                    market_cap = info_data.get('marketCap')
                    current_price = info_data.get('currentPrice')
                    pe_ratio = info_data.get('priceToBook')
                    print(f"   💰 Market Cap: {market_cap}")
                    print(f"   💲 Current Price: {current_price}")
                    print(f"   📊 P/B Ratio: {pe_ratio}")
                else:
                    print(f"   ⚠️  Unexpected info format: {info}")
                
                # Test income statement call
                income = yf_e.get_stock_element(ticker, 'income_stmt')
                print(f"   ✅ Income call successful: {type(income)}")
                
                if isinstance(income, str):
                    income = json.loads(income)
                
                if isinstance(income, dict) and 'data' in income:
                    eps_data = income['data'].get('Basic EPS')
                    eps = eps_data[0] if eps_data and len(eps_data) > 0 else None
                    print(f"   📈 EPS: {eps}")
                else:
                    print(f"   ⚠️  Unexpected income format: {income}")
                    
            except Exception as e:
                print(f"   ❌ yfinance error for {ticker}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ yfinance test error: {str(e)}")
        return False

def test_simple_yfinance():
    """Test yfinance with a well-known ticker"""
    print(f"\n🍎 Testing with Apple (AAPL)")
    print("=" * 30)
    
    try:
        from pyedgarai import yfinance_endpoints as yf_e
        import json
        
        # Test with Apple
        print("📱 Testing AAPL info...")
        info = yf_e.get_stock_element('AAPL', 'info')
        
        if isinstance(info, dict) and 'data' in info:
            data = info['data']
            print(f"   ✅ Market Cap: {data.get('marketCap')}")
            print(f"   ✅ Current Price: {data.get('currentPrice')}")
            print(f"   ✅ P/E: {data.get('trailingPE')}")
            print(f"   ✅ P/B: {data.get('priceToBook')}")
            print(f"   ✅ EV/EBITDA: {data.get('enterpriseToEbitda')}")
        else:
            print(f"   ❌ Unexpected format: {info}")
        
        print("\n📊 Testing AAPL income statement...")
        income = yf_e.get_stock_element('AAPL', 'income_stmt')
        
        if isinstance(income, str):
            income = json.loads(income)
            
        if isinstance(income, dict) and 'data' in income:
            eps_data = income['data'].get('Basic EPS')
            if eps_data:
                print(f"   ✅ EPS: {eps_data[0]}")
            else:
                print(f"   ⚠️  No EPS data found")
                print(f"   Available keys: {list(income['data'].keys())[:10]}")
        else:
            print(f"   ❌ Unexpected income format: {type(income)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Apple test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Debugging yfinance Integration for comparable_private")
    print("=" * 60)
    
    # Test ticker availability
    sample_tickers = test_ticker_availability()
    
    # Test yfinance calls
    if sample_tickers:
        test_yfinance_calls(sample_tickers)
    
    # Test with known good ticker
    test_simple_yfinance()
    
    print("\n" + "=" * 60)
    print("💡 Findings will help us fix the market data integration!")
