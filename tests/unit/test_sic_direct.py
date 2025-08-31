#!/usr/bin/env python3
"""
Direct test of comparables functions to identify the timeout issue
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_sic_function():
    """Test the SIC function directly"""
    print("🧪 Direct test of get_companies_with_same_sic function")
    print("=" * 60)
    
    try:
        from pyedgarai.comparables import get_companies_with_same_sic
        
        cik = 320193  # Apple
        print(f"🍎 Testing with Apple (CIK: {cik})")
        
        print("⏱️  Calling get_companies_with_same_sic...")
        result = get_companies_with_same_sic(cik, digits=2)
        
        print(f"✅ Success! Found {len(result)} companies")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Columns: {list(result.columns) if hasattr(result, 'columns') else 'No columns'}")
        
        # Show first few results
        if hasattr(result, 'head'):
            print("\n📋 First 5 results:")
            print(result.head())
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sic_mapping():
    """Test if we can read the SIC mapping"""
    print("\n🗂️  Testing SIC mapping data...")
    
    try:
        from pyedgarai.features import return_cik_sic
        
        print("📁 Loading CIK-SIC mapping...")
        sic_data = return_cik_sic()
        
        print(f"✅ Loaded {len(sic_data)} CIK-SIC mappings")
        
        # Test Apple's SIC
        apple_cik = "320193"
        if apple_cik in sic_data:
            print(f"🍎 Apple (CIK {apple_cik}): SIC {sic_data[apple_cik]}")
        else:
            print(f"❌ Apple CIK {apple_cik} not found in SIC data")
            
        return True
        
    except Exception as e:
        print(f"❌ Error loading SIC data: {e}")
        return False

def main():
    """Main test"""
    test_sic_mapping()
    test_sic_function()

if __name__ == "__main__":
    main()
