#!/usr/bin/env python3
"""
PyEdgarAI API Server Launcher

This script starts the PyEdgarAI Flask API server with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import pyedgarai
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🚀 Starting PyEdgarAI API Server...")
    print("=" * 50)
    
    # Check if API token is set
    api_token = os.getenv("PYEDGARAI_API_TOKEN")
    if api_token:
        print("✅ API Token: Configured")
    else:
        print("⚠️  API Token: Not set (authentication disabled)")
        print("   Set PYEDGARAI_API_TOKEN environment variable to enable authentication")
    
    print("\n📚 API Documentation will be available at:")
    print("   • Swagger UI: http://127.0.0.1:5000/openapi/swagger")
    print("   • ReDoc: http://127.0.0.1:5000/openapi/redoc")
    print("   • RapiDoc: http://127.0.0.1:5000/openapi/rapidoc")
    print("   • RapiPDF: http://127.0.0.1:5000/openapi/rapipdf")
    print("   • Scalar: http://127.0.0.1:5000/openapi/scalar")
    print("   • Elements: http://127.0.0.1:5000/openapi/elements")
    print("   • OpenAPI JSON: http://127.0.0.1:5000/openapi/openapi.json")
    
    print("\n🏠 Access the API at:")
    print("   • Home page: http://127.0.0.1:5000/")
    print("   • JSON API info: http://127.0.0.1:5000/api")
    
    print("\n📡 Server Configuration:")
    print("   • Server running on: http://127.0.0.1:5000/")
    print("   • Note: Server is bound to localhost only")
    print("   • To allow network access, change host to '0.0.0.0' in start_api.py")
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50 + "\n")
    
    try:
        from pyedgarai.api.server import app
        # Bind to localhost only for simplicity (change to '0.0.0.0' for network access)
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
