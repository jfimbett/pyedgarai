#!/usr/bin/env python3
"""
Generate CIK-Company Names mapping from SEC API

This script generates the cik_company_names.json file by calling the SEC API 
to get company names for all CIKs.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def generate_company_names():
    """Generate CIK to company names mapping"""
    print("🏢 Generating CIK-Company Names mapping from SEC API...")
    print("⚠️  This may take several minutes due to SEC rate limiting")
    
    try:
        from pyedgarai.features import get_cik_company_names, CACHE_DIR
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
        
        # Generate the company names mapping
        print("🚀 Starting SEC API calls...")
        start_time = time.time()
        
        get_cik_company_names()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ CIK-Company Names mapping generated successfully!")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        
        # Verify the file was created
        cik_names_path = Path(CACHE_DIR) / "cik_company_names.json"
        if cik_names_path.exists():
            import json
            with open(cik_names_path, 'r') as f:
                data = json.load(f)
            print(f"📊 Generated names for {len(data)} companies")
            print(f"📁 File location: {cik_names_path}")
            
            # Show a sample of the data
            print("\n📋 Sample company names:")
            for i, (cik, name) in enumerate(list(data.items())[:5]):
                print(f"   CIK {cik}: {name}")
            if len(data) > 5:
                print(f"   ... and {len(data) - 5} more")
            
            return True
        else:
            print(f"❌ File was not created at expected location: {cik_names_path}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("💡 Try installing: pip install sec-cik-mapper")
        return False
    except Exception as e:
        print(f"❌ Error generating company names data: {e}")
        return False

def main():
    """Main function"""
    print("🏢 PyEdgarAI CIK-Company Names Generator")
    print("=" * 60)
    
    success = generate_company_names()
    
    if success:
        print(f"\n✅ Company names generation successful!")
        print("Now you can test the comparables API endpoints!")
    else:
        print(f"\n❌ Company names generation failed!")

if __name__ == "__main__":
    main()
