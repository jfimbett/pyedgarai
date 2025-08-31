#!/usr/bin/env python3
"""
Generate CIK-SIC mapping data from SEC API

This script generates the cik_sic.json file by calling the SEC API 
to get SIC codes for companies. This is the proper way to create 
the file that the comparables API needs.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def generate_cik_sic_from_sec():
    """
    Generate CIK-SIC mapping by calling SEC API
    This is the official way the library is supposed to work
    """
    print("🏭 Generating CIK-SIC mapping from SEC API...")
    print("⚠️  This may take several minutes due to SEC rate limiting")
    
    try:
        from pyedgarai.features import cik_sic_table, CACHE_DIR
        from sec_cik_mapper import StockMapper
        
        print(f"📁 Cache directory: {CACHE_DIR}")
        
        # Get the number of companies we'll process
        try:
            mapper = StockMapper()
            total_companies = len(mapper.cik_to_tickers)
            print(f"📊 Found {total_companies} companies to process")
            print("⏱️  Estimated time: ~{:.1f} minutes (with rate limiting)".format(total_companies * 0.05 / 60))
        except Exception as e:
            print(f"⚠️  Could not get company count: {e}")
            total_companies = "unknown"
        
        # Create the cache directory
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Generate the CIK-SIC table
        print("🚀 Starting SEC API calls...")
        start_time = time.time()
        
        cik_sic_table()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ CIK-SIC mapping generated successfully!")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        
        # Verify the file was created
        cik_sic_path = Path(CACHE_DIR) / "cik_sic.json"
        if cik_sic_path.exists():
            import json
            with open(cik_sic_path, 'r') as f:
                data = json.load(f)
            print(f"📊 Generated mapping for {len(data)} companies")
            print(f"📁 File location: {cik_sic_path}")
            
            # Show a sample of the data
            print("\n📋 Sample mappings:")
            for i, (cik, sic) in enumerate(list(data.items())[:5]):
                print(f"   CIK {cik}: SIC {sic}")
            if len(data) > 5:
                print(f"   ... and {len(data) - 5} more")
            
            return True
        else:
            print(f"❌ File was not created at expected location: {cik_sic_path}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("💡 Try installing: pip install sec-cik-mapper")
        return False
    except Exception as e:
        print(f"❌ Error generating CIK-SIC data: {e}")
        return False

def generate_small_sample():
    """
    Generate a small sample for immediate testing
    """
    print("🧪 Creating small sample dataset for immediate testing...")
    
    try:
        from pyedgarai.features import CACHE_DIR
        from pyedgarai.sec_client import get_submission_history
        
        # Create cache directory
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Sample of well-known companies
        sample_ciks = [
            320193,   # Apple Inc.
            789019,   # Microsoft Corp
            1652044,  # Alphabet Inc.
            1018724,  # Amazon.com Inc
            1045810,  # NVIDIA Corp
        ]
        
        mapping = {}
        
        print(f"📊 Getting SIC codes for {len(sample_ciks)} companies...")
        
        for cik in sample_ciks:
            try:
                print(f"   Fetching CIK {cik}...")
                submission = get_submission_history(cik)
                sic = submission.get('sic')
                if sic:
                    mapping[str(cik)] = sic
                    print(f"   ✅ CIK {cik}: SIC {sic}")
                else:
                    print(f"   ⚠️  CIK {cik}: No SIC found")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ CIK {cik}: Error - {e}")
                continue
        
        if mapping:
            import json
            cik_sic_path = Path(CACHE_DIR) / "cik_sic.json"
            with open(cik_sic_path, 'w') as f:
                json.dump(mapping, f, indent=2)
            
            print(f"✅ Sample dataset created with {len(mapping)} companies")
            print(f"📁 File location: {cik_sic_path}")
            return True
        else:
            print("❌ No data was retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error creating sample: {e}")
        return False

def test_api_functionality():
    """Test if the API works after generating data"""
    print("\n🧪 Testing API functionality...")
    
    try:
        import requests
        
        # Test the API
        response = requests.get("http://127.0.0.1:5000/api", timeout=5)
        if response.status_code != 200:
            print("❌ API not responding - make sure server is running")
            return False
        
        # Test comparables endpoint
        params = {
            "cik": 320193,  # Apple
            "method": "traditional",
            "industry_digits": 2,
            "api_token": ""
        }
        
        print("📡 Testing comparables endpoint...")
        response = requests.get("http://127.0.0.1:5000/comparables", params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ Comparables API working!")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - server not running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 PyEdgarAI CIK-SIC Data Generator")
    print("=" * 60)
    
    print("This script will generate the cik_sic.json file required for comparables analysis.")
    print("The data comes from SEC API calls, so it may take some time.\n")
    
    # Ask user for preference
    print("Choose an option:")
    print("1. Generate full dataset (slow, comprehensive)")
    print("2. Generate sample dataset (fast, limited)")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        return
    
    if choice == "1":
        success = generate_cik_sic_from_sec()
    elif choice == "2":
        success = generate_small_sample()
    else:
        print("❌ Invalid choice")
        return
    
    if success:
        print(f"\n✅ Data generation successful!")
        
        # Ask if user wants to test
        try:
            test_choice = input("\nTest API functionality now? (y/n): ").strip().lower()
            if test_choice == 'y':
                test_api_functionality()
        except KeyboardInterrupt:
            print("\n👋 Skipping test")
    else:
        print(f"\n❌ Data generation failed!")

if __name__ == "__main__":
    main()
