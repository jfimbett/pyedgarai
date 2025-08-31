#!/usr/bin/env python3
"""
Lightweight test for optimized PyEdgarAI that bypasses heavy imports

This test focuses on what we can verify without the slow imports:
- Data files existence and validity
- Basic JSON operations for comparables
- Simple HTTP test of any running API
"""

import json
import os
import time
from pathlib import Path

import requests


def test_data_files():
    """Test that our data files are working properly"""
    print("📊 Testing Data Files")
    print("-" * 30)
    
    cache_dir = Path.home() / ".cache" / "pyedgarai"
    
    # Test CIK-SIC data
    cik_sic_path = cache_dir / "cik_sic.json"
    if cik_sic_path.exists():
        try:
            with open(cik_sic_path, 'r') as f:
                sic_data = json.load(f)
            print(f"✅ CIK-SIC data: {len(sic_data)} companies")
            
            # Test Apple's data
            apple_sic = sic_data.get("320193")
            if apple_sic:
                print(f"✅ Apple SIC: {apple_sic}")
                
                # Find companies with same 2-digit SIC
                matching = [cik for cik, sic in sic_data.items() 
                           if sic and str(sic)[:2] == str(apple_sic)[:2]]
                print(f"✅ Companies with SIC {str(apple_sic)[:2]}**: {len(matching)}")
            else:
                print("❌ Apple not found in SIC data")
                return False
                
        except Exception as e:
            print(f"❌ Error reading SIC data: {e}")
            return False
    else:
        print(f"❌ CIK-SIC file missing: {cik_sic_path}")
        return False
    
    # Test company names
    names_path = cache_dir / "cik_company_names.json"
    if names_path.exists():
        try:
            with open(names_path, 'r') as f:
                names_data = json.load(f)
            print(f"✅ Company names: {len(names_data)} companies")
            
            apple_name = names_data.get("320193")
            if apple_name:
                print(f"✅ Apple name: {apple_name}")
            else:
                print("⚠️  Apple name not found")
                
        except Exception as e:
            print(f"❌ Error reading names data: {e}")
            return False
    else:
        print(f"❌ Company names file missing: {names_path}")
        return False
    
    return True


def test_simple_comparables_logic():
    """Test our comparables logic using just the JSON data"""
    print("\n🔍 Testing Comparables Logic")
    print("-" * 30)
    
    cache_dir = Path.home() / ".cache" / "pyedgarai"
    
    try:
        # Load data
        with open(cache_dir / "cik_sic.json", 'r') as f:
            sic_data = json.load(f)
        with open(cache_dir / "cik_company_names.json", 'r') as f:
            names_data = json.load(f)
        
        # Test Apple comparables
        apple_cik = "320193"
        apple_sic = sic_data.get(apple_cik)
        apple_name = names_data.get(apple_cik, "Unknown")
        
        print(f"🍎 Target: {apple_name} (CIK: {apple_cik}, SIC: {apple_sic})")
        
        if not apple_sic:
            print("❌ No SIC for Apple")
            return False
        
        # Find matches with same 2-digit SIC
        matches = []
        target_sic_2d = str(apple_sic)[:2]
        
        for cik, sic in sic_data.items():
            if sic and str(sic)[:2] == target_sic_2d and cik != apple_cik:
                company_name = names_data.get(cik, "Unknown")
                matches.append({
                    "cik": int(cik),
                    "name": company_name,
                    "sic": sic
                })
        
        # Sort and limit
        matches = matches[:10]  # Top 10
        
        print(f"✅ Found {len(matches)} comparable companies:")
        for i, company in enumerate(matches[:5], 1):
            print(f"   {i}. {company['name']} (CIK: {company['cik']}, SIC: {company['sic']})")
        
        if len(matches) > 5:
            print(f"   ... and {len(matches) - 5} more")
        
        return len(matches) > 0
        
    except Exception as e:
        print(f"❌ Error in comparables logic: {e}")
        return False


def test_api_if_running():
    """Test API endpoints if a server is running"""
    print("\n🌐 Testing API (if running)")
    print("-" * 30)
    
    # Test different ports
    ports_to_try = [5000, 5001]
    
    for port in ports_to_try:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API running on port {port}")
                print(f"   Version: {data.get('version', 'unknown')}")
                
                # Test health if available
                try:
                    health_response = requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                    if health_response.status_code == 200:
                        print("✅ Health endpoint working")
                except:
                    pass
                
                # Test fast SIC endpoint if available
                try:
                    sic_response = requests.get(
                        f"http://127.0.0.1:{port}/comparables_sic",
                        params={"cik": 320193, "digits": 2, "api_token": ""},
                        timeout=5
                    )
                    if sic_response.status_code == 200:
                        sic_data = sic_response.json()
                        companies_found = sic_data.get("total_found", 0)
                        print(f"✅ SIC comparables: {companies_found} companies")
                    else:
                        print(f"⚠️  SIC endpoint returned {sic_response.status_code}")
                except:
                    print("⚠️  SIC endpoint not available or timed out")
                
                return True
                
        except requests.exceptions.ConnectionError:
            continue
        except Exception as e:
            print(f"⚠️  Error testing port {port}: {e}")
            continue
    
    print("⚠️  No API server detected on ports 5000 or 5001")
    print("💡 To start the API server:")
    print("   python src\\pyedgarai\\api\\optimized_server.py")
    return False


def main():
    """Run lightweight tests"""
    print("🚀 PyEdgarAI Lightweight Test Suite")
    print("=" * 50)
    print("This test bypasses slow imports and focuses on core functionality.\n")
    
    results = []
    
    # Test data files
    results.append(("Data Files", test_data_files()))
    
    # Test comparables logic
    results.append(("Comparables Logic", test_simple_comparables_logic()))
    
    # Test API if running
    results.append(("API Test", test_api_if_running()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core functionality is working.")
    else:
        print("⚠️  Some tests failed, but this might be expected if API server isn't running.")
    
    print(f"\n💡 Next steps:")
    if passed >= 2:  # Data and logic working
        print("   • Start API server: python src\\pyedgarai\\api\\optimized_server.py")
        print("   • Test full system: python test_optimized_system.py")
    else:
        print("   • Check data file generation")
        print("   • Verify cache directory permissions")
    
    return passed == total


if __name__ == "__main__":
    main()
