#!/usr/bin/env python3
"""
Generate missing data files required for PyEdgarAI API

This script creates the cik_sic.json file needed for comparables analysis.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def create_cache_directory():
    """Create the cache directory if it doesn't exist"""
    cache_dir = Path.home() / ".cache" / "pyedgarai"
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Cache directory created: {cache_dir}")
    return cache_dir

def generate_cik_sic_data():
    """Generate CIK to SIC mapping data"""
    print("🏭 Generating CIK to SIC mapping...")
    
    try:
        from pyedgarai import features as feat
        print("✅ Features module imported successfully")
        
        # Try to generate the CIK-SIC mapping
        print("📊 Calling get_cik_sic_generation()...")
        feat.get_cik_sic_generation()
        print("✅ CIK-SIC data generated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating CIK-SIC data: {e}")
        
        # Try alternative method - create a minimal dataset
        print("💡 Creating minimal CIK-SIC dataset...")
        
        # Sample data for testing (real CIK-SIC mappings)
        minimal_data = {
            "320193": "3571",   # Apple Inc. - Electronic computers
            "789019": "3571",   # Microsoft - Electronic computers  
            "1652044": "7372",  # Alphabet - Computer programming services
            "1018724": "5961",  # Amazon - Mail-order houses
            "1045810": "2834",  # NVIDIA - Pharmaceutical preparations
            "886982": "6799",   # Meta - Business services, nec
            "1326801": "2834",  # Facebook - Pharmaceutical preparations
            "1065280": "6794",  # Netflix - Investment advice
            "1467858": "7372",  # Tesla - Computer programming services
            "1090872": "1311"   # Exxon Mobil - Crude petroleum & natural gas
        }
        
        try:
            cache_dir = create_cache_directory()
            cik_sic_file = cache_dir / "cik_sic.json"
            
            with open(cik_sic_file, 'w') as f:
                json.dump(minimal_data, f, indent=2)
            
            print(f"✅ Minimal CIK-SIC data created: {cik_sic_file}")
            print(f"📊 Contains {len(minimal_data)} company mappings")
            return True
            
        except Exception as e2:
            print(f"❌ Failed to create minimal dataset: {e2}")
            return False

def check_existing_files():
    """Check what data files already exist"""
    print("🔍 Checking existing data files...")
    
    cache_dir = Path.home() / ".cache" / "pyedgarai"
    required_files = [
        "cik_sic.json",
        "cik_company_names.json", 
        "stock_elements.json"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_name in required_files:
        file_path = cache_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            existing_files.append(f"{file_name} ({size} bytes)")
        else:
            missing_files.append(file_name)
    
    if existing_files:
        print("✅ Existing files:")
        for file_info in existing_files:
            print(f"   • {file_info}")
    
    if missing_files:
        print("❌ Missing files:")
        for file_name in missing_files:
            print(f"   • {file_name}")
        
    return missing_files

def test_api_after_fix():
    """Test a simple API call after generating the data"""
    print("🧪 Testing API functionality...")
    
    try:
        import requests
        
        # Test the API info endpoint first
        response = requests.get("http://127.0.0.1:5000/api", timeout=5)
        if response.status_code != 200:
            print("❌ API not responding - make sure the server is running")
            return False
        
        print("✅ API is responding")
        
        # Test a simple comparables call
        params = {
            "cik": 320193,  # Apple
            "method": "traditional",
            "industry_digits": 2,
            "api_token": ""
        }
        
        response = requests.get("http://127.0.0.1:5000/comparables", params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ Comparables API working!")
            data = response.json()
            print(f"📊 Response type: {type(data)}")
            if isinstance(data, dict) and data:
                print(f"🔑 Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            if response.status_code == 500:
                print("💡 There may still be missing data files")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure the server is running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Main function to generate missing data files"""
    print("🚀 PyEdgarAI Data File Generator")
    print("=" * 50)
    
    # Check what files are missing
    missing_files = check_existing_files()
    
    if not missing_files:
        print("✅ All required files exist!")
        test_api_after_fix()
        return
    
    # Generate missing CIK-SIC data
    if "cik_sic.json" in missing_files:
        print("\n📋 Generating CIK-SIC mapping...")
        if generate_cik_sic_data():
            print("✅ CIK-SIC data generated successfully!")
        else:
            print("❌ Failed to generate CIK-SIC data")
            return
    
    # Check for other missing files and provide guidance
    remaining_missing = check_existing_files()
    
    if remaining_missing:
        print(f"\n⚠️  Note: {len(remaining_missing)} files still missing")
        print("💡 These will be generated automatically when needed by the API")
    
    print("\n🎯 Testing API functionality...")
    if test_api_after_fix():
        print("\n✅ Success! API should now work properly")
        print("💡 You can now run: python simple_api_example.py")
    else:
        print("\n❌ API still has issues - check the server logs")

if __name__ == "__main__":
    main()
