#!/usr/bin/env python3
"""
Minimal test to identify the 'str' object has no attribute 'name' error
"""

import sys
from pathlib import Path

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    print("Testing imports...")
    
    try:
        from flask_openapi3 import Info, Tag, OpenAPI
        print("✅ flask_openapi3 imported successfully")
    except Exception as e:
        print(f"❌ flask_openapi3 import failed: {e}")
        return False
    
    try:
        from pyedgarai.api import schemas as mm
        print("✅ schemas imported successfully")
    except Exception as e:
        print(f"❌ schemas import failed: {e}")
        return False
    
    try:
        # Test Tag creation
        test_tag = Tag(name="test", description="Test tag")
        print("✅ Tag creation successful")
    except Exception as e:
        print(f"❌ Tag creation failed: {e}")
        return False
    
    try:
        from pyedgarai import sec_client as sec
        print("✅ sec_client imported successfully")
    except Exception as e:
        print(f"❌ sec_client import failed: {e}")
        return False
    
    try:
        from pyedgarai import comparables as comp
        print("✅ comparables imported successfully")  
    except Exception as e:
        print(f"❌ comparables import failed: {e}")
        return False
    
    try:
        from pyedgarai import market_data as md
        print("✅ market_data imported successfully")
    except Exception as e:
        print(f"❌ market_data import failed: {e}")
        return False
    
    try:
        from pyedgarai import features as feat
        print("✅ features imported successfully")
    except Exception as e:
        print(f"❌ features import failed: {e}")
        return False
    
    try:
        import pyedgarai.yfinance_endpoints as yf_e
        print("✅ yfinance_endpoints imported successfully")
    except Exception as e:
        print(f"❌ yfinance_endpoints import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_imports():
        print("\n🎉 All imports successful! Trying to create the app...")
        try:
            from pyedgarai.api.server import app
            print("✅ App created successfully!")
            print("🚀 Ready to start server")
        except Exception as e:
            print(f"❌ App creation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Import issues found. Fix these first.")
