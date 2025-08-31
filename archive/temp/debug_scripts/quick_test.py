#!/usr/bin/env python3
"""
Simple test script for the new comparable_private endpoint - syntax only
"""

import sys
import os
sys.path.insert(0, 'src')

def test_function_exists():
    """Test that our function can be imported"""
    print("🧪 Testing function import...")
    
    try:
        from pyedgarai.comparables import identify_comparables_private
        print("✅ Function imported successfully!")
        
        # Check function signature
        import inspect
        sig = inspect.signature(identify_comparables_private)
        print(f"📋 Function signature: {sig}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_schemas():
    """Test API schemas"""
    print("\n🧪 Testing API schemas...")
    
    try:
        from pyedgarai.api.schemas import ComparablesPrivateRequest, ComparablesPrivateResponse
        
        # Test creating a request
        request = ComparablesPrivateRequest(
            api_token="test",
            name="Test Company",
            sic_code="73",
            profitability=0.15,
            growth_rate=0.12,
            capital_structure=0.25
        )
        
        print("✅ Schemas work correctly!")
        print(f"   Request: {request.name} in SIC {request.sic_code}")
        return True
        
    except Exception as e:
        print(f"❌ Schema error: {str(e)}")
        return False

def test_api_endpoint():
    """Test that the API endpoint is properly defined"""
    print("\n🧪 Testing API endpoint...")
    
    try:
        # Import the server module
        from pyedgarai.api.server import app
        
        # Check if our endpoint exists
        endpoints = []
        for rule in app.url_map.iter_rules():
            endpoints.append(rule.rule)
        
        if '/comparable_private' in endpoints:
            print("✅ API endpoint '/comparable_private' is properly registered!")
            return True
        else:
            print("❌ API endpoint not found in registered endpoints")
            print(f"Available endpoints: {endpoints}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 PyEdgarAI Private Comparables - Quick Validation")
    print("=" * 55)
    
    success = True
    success &= test_function_exists()
    success &= test_schemas() 
    success &= test_api_endpoint()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 All validation tests passed!")
        print("\n📋 Implementation Summary:")
        print("   ✅ Core function: identify_comparables_private()")
        print("   ✅ API schemas: ComparablesPrivateRequest/Response")
        print("   ✅ API endpoint: GET /comparable_private")
        print("\n🔗 Usage example:")
        print("   GET /comparable_private?api_token=test&name=MyCompany&sic_code=73&profitability=0.15&growth_rate=0.12&capital_structure=0.25")
    else:
        print("❌ Some validation tests failed.")
        
    print("\n📝 Next steps:")
    print("   1. Start the API server: python -m src.pyedgarai.api.server")
    print("   2. Visit: http://localhost:5000/openapi/swagger")
    print("   3. Test the /comparable_private endpoint in the docs")
