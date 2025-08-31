#!/usr/bin/env python3
"""
Minimal test to find the exact location of the 'str' object has no attribute 'name' error
"""

import sys
from pathlib import Path
import traceback

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_minimal_schema():
    print("Testing minimal schema import...")
    
    try:
        from pydantic import BaseModel, Field
        print("✅ Pydantic imported successfully")
    except Exception as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        # Test creating a simple model
        class TestModel(BaseModel):
            name: str = Field(description="Test field")
        print("✅ Simple Field creation works")
    except Exception as e:
        print(f"❌ Simple Field creation failed: {e}")
        return False
    
    try:
        # Import just the function part
        print("Testing clean_account_name function...")
        from pyedgarai.api.schemas import clean_account_name
        result = clean_account_name("Test Account")
        print(f"✅ clean_account_name works: {result}")
    except Exception as e:
        print(f"❌ clean_account_name import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        # Try importing the accounts list
        print("Testing accounts list...")
        from pyedgarai.api.schemas import accounts
        print(f"✅ accounts list imported: {len(accounts)} items")
    except Exception as e:
        print(f"❌ accounts list import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        # Try importing clean_names list
        print("Testing clean_names list...")
        from pyedgarai.api.schemas import clean_names
        print(f"✅ clean_names list imported: {len(clean_names)} items")
    except Exception as e:
        print(f"❌ clean_names list import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        # Try importing a simple class
        print("Testing CleanName class...")
        from pyedgarai.api.schemas import CleanName
        print("✅ CleanName class imported")
    except Exception as e:
        print(f"❌ CleanName class import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_minimal_schema()
