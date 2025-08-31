#!/usr/bin/env python3
"""
Test which documentation UIs are available
"""

import sys
from pathlib import Path
import requests
import time
import subprocess
import threading

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def start_server():
    """Start the API server in background"""
    subprocess.Popen([sys.executable, "start_api.py"], 
                    cwd=Path(__file__).parent,
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)

def test_endpoints():
    """Test which documentation endpoints are available"""
    base_url = "http://127.0.0.1:5000"
    
    endpoints_to_test = [
        "/",
        "/api", 
        "/openapi/swagger",
        "/openapi/redoc",
        "/openapi/rapidoc",
        "/openapi/rapipdf", 
        "/openapi/scalar",
        "/openapi/elements",
        "/openapi/openapi.json"
    ]
    
    print("Testing API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Available")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 Starting server and testing endpoints...")
    
    # Start server in background
    start_server()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test endpoints
    test_endpoints()
    
    print("\n✅ Test completed! Check the results above.")
    print("💡 If some endpoints are missing, they may not be enabled in flask-openapi3.")
