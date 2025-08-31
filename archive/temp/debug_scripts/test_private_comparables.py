#!/usr/bin/env python3
"""
Test script for the new comparable_private endpoint
"""

import sys
import os
sys.path.insert(0, 'src')

from pyedgarai.comparables import identify_comparables_private

def test_private_comparables():
    """Test the private comparables functionality"""
    print("🧪 Testing private company comparables functionality...")
    
    try:
        # Test with a technology company in SIC sector 73 (Business Services)
        result = identify_comparables_private(
            name="TechStartup Inc.",
            sic_code="73",  # Business services
            profitability=0.12,  # 12% ROA
            growth_rate=0.15,    # 15% asset growth
            capital_structure=0.30  # 30% debt-to-equity
        )
        
        print("✅ Function executed successfully!")
        print(f"📊 Result structure:")
        print(f"   - Target company: {result.get('target_company', {}).get('name')}")
        print(f"   - Total comparables found: {result.get('total_found', 0)}")
        print(f"   - Method: {result.get('method')}")
        print(f"   - SIC sector: {result.get('sic_sector')}")
        
        if 'error' in result:
            print(f"⚠️  Warning: {result['error']}")
        
        # Show first comparable if available
        comparables = result.get('comparables', [])
        if comparables:
            first_comp = comparables[0]
            print(f"\n📈 First comparable company:")
            print(f"   - Name: {first_comp.get('name')}")
            print(f"   - Ticker: {first_comp.get('ticker')}")
            print(f"   - CIK: {first_comp.get('cik')}")
            print(f"   - Profitability: {first_comp.get('profitability', 'N/A')}")
            print(f"   - Growth rate: {first_comp.get('growth_rate', 'N/A')}")
            print(f"   - Capital structure: {first_comp.get('capital_structure', 'N/A')}")
            print(f"   - Distance: {first_comp.get('distance', 'N/A')}")
            
            # Market data
            if first_comp.get('market_cap'):
                print(f"   - Market cap: ${first_comp.get('market_cap'):,}")
            if first_comp.get('price_to_earnings'):
                print(f"   - P/E ratio: {first_comp.get('price_to_earnings'):.2f}")
            if first_comp.get('price_to_book'):
                print(f"   - P/B ratio: {first_comp.get('price_to_book'):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_schemas():
    """Test that the API schemas are properly defined"""
    print("\n🧪 Testing API schemas...")
    
    try:
        from pyedgarai.api.schemas import ComparablesPrivateRequest, ComparablesPrivateResponse
        
        # Test request schema
        request = ComparablesPrivateRequest(
            api_token="test_token",
            name="Test Company",
            sic_code="73",
            profitability=0.15,
            growth_rate=0.12,
            capital_structure=0.25
        )
        
        print("✅ Request schema works!")
        print(f"   - Company name: {request.name}")
        print(f"   - SIC code: {request.sic_code}")
        print(f"   - Profitability: {request.profitability}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing PyEdgarAI Private Comparables Implementation")
    print("=" * 60)
    
    success = True
    
    # Test schemas first
    success &= test_api_schemas()
    
    # Test core functionality
    success &= test_private_comparables()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        print("\n📋 Next steps:")
        print("   1. Run the API server: python -m src.pyedgarai.api.server")
        print("   2. Test the endpoint: GET /comparable_private")
        print("   3. Check the OpenAPI documentation at /openapi/swagger")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\n🔗 New endpoint URL pattern:")
    print("   GET /comparable_private?api_token=<token>&name=<name>&sic_code=<sic>&profitability=<prof>&growth_rate=<growth>&capital_structure=<capital>")
