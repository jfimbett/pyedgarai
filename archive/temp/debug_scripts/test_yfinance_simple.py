#!/usr/bin/env python3
"""
Quick test script to check if yfinance is working
"""
#%%
import yfinance as yf
import time

ticker = yf.Ticker('AAPL')
info = ticker.info
#%%

def test_basic_yfinance():
    """Test yfinance with well-known tickers"""
    print("🧪 Testing Basic yfinance Functionality")
    print("=" * 40)
    
    # Test with common, reliable tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    for ticker_symbol in test_tickers:
        print(f"\n📊 Testing {ticker_symbol}:")
        
        try:
            # Create ticker object
            ticker = yf.Ticker(ticker_symbol)
            
            # Test basic info
            print("   Getting info...")
            info = ticker.info
            
            if info and 'currentPrice' in info:
                print(f"   ✅ Current Price: ${info['currentPrice']}")
                print(f"   ✅ Market Cap: ${info.get('marketCap', 'N/A')}")
                print(f"   ✅ P/E Ratio: {info.get('trailingPE', 'N/A')}")
            else:
                print(f"   ⚠️  No price info available")
                
            # Test history (less likely to be rate limited)
            print("   Getting 1 day history...")
            hist = ticker.history(period="1d")
            if not hist.empty:
                latest_close = hist['Close'].iloc[-1]
                print(f"   ✅ Latest Close: ${latest_close:.2f}")
            else:
                print(f"   ⚠️  No history data")
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"   ❌ Rate Limited: {ticker_symbol}")
            else:
                print(f"   ❌ Error for {ticker_symbol}: {error_msg}")
        
        # Small delay between requests
        time.sleep(1)

def test_problematic_tickers():
    """Test the actual tickers from your comparables"""
    print(f"\n🎯 Testing Your Actual Comparables Tickers")
    print("=" * 45)
    
    # These are from your error log
    problem_tickers = ['IBOC', 'BSVN', 'ESQ', 'WABC', 'AX']
    
    for ticker_symbol in problem_tickers:
        print(f"\n📈 Testing {ticker_symbol}:")
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Try just getting basic info
            info = ticker.info
            
            if info and isinstance(info, dict) and len(info) > 0:
                print(f"   ✅ Info available: {len(info)} fields")
                print(f"   💰 Market Cap: {info.get('marketCap', 'Not found')}")
                print(f"   💲 Current Price: {info.get('currentPrice', 'Not found')}")
            else:
                print(f"   ⚠️  No info or empty response")
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"   ❌ Rate Limited!")
            elif "404" in error_msg:
                print(f"   ❌ Ticker not found")
            else:
                print(f"   ❌ Error: {error_msg}")
        
        # Longer delay to avoid rate limiting
        time.sleep(2)

def test_yfinance_status():
    """Check overall yfinance status"""
    print(f"\n🔍 yfinance Library Status")
    print("=" * 30)
    
    try:
        import yfinance as yf
        print(f"✅ yfinance version: {yf.__version__}")
        
        # Test with a simple, reliable ticker
        spy = yf.Ticker("SPY")
        info = spy.info
        
        if info and 'currentPrice' in info:
            print(f"✅ Basic functionality works")
            print(f"📊 SPY Price: ${info['currentPrice']}")
        else:
            print(f"⚠️  Basic functionality has issues")
            
    except Exception as e:
        print(f"❌ yfinance library issue: {str(e)}")

if __name__ == "__main__":
    print("🔧 yfinance Quick Test")
    print("=" * 25)
    
    # Test basic functionality
    test_yfinance_status()
    
    # Test with major tickers
    test_basic_yfinance()
    
    # Test problematic tickers
    test_problematic_tickers()
    
    print(f"\n" + "=" * 50)
    print("💡 If you see rate limiting (429 errors), wait a few minutes and try again")
    print("💡 If specific tickers fail, they might be delisted or have data issues")
