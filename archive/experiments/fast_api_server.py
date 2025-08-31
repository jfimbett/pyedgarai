#!/usr/bin/env python3
"""
Simple API Server for PyEdgarAI Comparables

This lightweight server provides fast comparables functionality
using only the cached data files, avoiding slow imports.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, jsonify, request, send_from_directory


class FastComparables:
    """Fast comparables using cached JSON data only"""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "pyedgarai"
        self._sic_data = None
        self._names_data = None
    
    def load_data(self):
        """Load cached data files"""
        if self._sic_data is None:
            with open(self.cache_dir / "cik_sic.json", 'r') as f:
                self._sic_data = json.load(f)
        
        if self._names_data is None:
            with open(self.cache_dir / "cik_company_names.json", 'r') as f:
                self._names_data = json.load(f)
    
    def get_sic_comparables(self, cik: int, digits: int = 2, max_companies: int = 50) -> Dict[str, Any]:
        """Get companies with matching SIC codes"""
        self.load_data()
        
        cik_str = str(cik)
        target_sic = self._sic_data.get(cik_str)
        target_name = self._names_data.get(cik_str, "Unknown")
        
        if not target_sic:
            return {
                "error": f"No SIC code found for CIK {cik}",
                "target_company": {"cik": cik, "name": target_name},
                "companies": [],
                "total_found": 0
            }
        
        # Find matches
        target_sic_truncated = str(target_sic)[:digits]
        matches = []
        
        for other_cik, other_sic in self._sic_data.items():
            if (other_sic and 
                str(other_sic)[:digits] == target_sic_truncated and 
                other_cik != cik_str):
                
                company_name = self._names_data.get(other_cik, "Unknown")
                matches.append({
                    "cik": int(other_cik),
                    "name": company_name,
                    "sic": other_sic
                })
        
        # Limit results
        if len(matches) > max_companies:
            matches = matches[:max_companies]
        
        return {
            "target_company": {
                "cik": cik,
                "name": target_name,
                "sic": target_sic
            },
            "companies": matches,
            "total_found": len(matches),
            "method": "sic_fast",
            "sic_digits": digits,
            "timestamp": time.time()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            self.load_data()
            return {
                "status": "ok",
                "sic_data_entries": len(self._sic_data),
                "names_data_entries": len(self._names_data),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }


# Create Flask app
app = Flask(__name__)
comparables = FastComparables()

@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        "name": "PyEdgarAI Fast API",
        "version": "0.8.0",
        "description": "Fast comparables analysis using cached data",
        "status": "lightweight",
        "endpoints": {
            "health": "/health",
            "comparables": "/comparables_sic"
        },
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify(comparables.health_check())

@app.route('/comparables_sic')
def comparables_sic():
    """SIC-based comparables endpoint"""
    try:
        cik = request.args.get('cik', type=int)
        digits = request.args.get('digits', default=2, type=int)
        max_companies = request.args.get('max_companies', default=50, type=int)
        
        if not cik:
            return jsonify({"error": "CIK parameter required"}), 400
        
        if not (1 <= digits <= 4):
            return jsonify({"error": "Digits must be between 1 and 4"}), 400
        
        result = comparables.get_sic_comparables(cik, digits, max_companies)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/')
def home():
    """Serve the beautiful landing page"""
    try:
        # Try to serve the beautiful HTML landing page
        static_dir = Path(__file__).parent / "src" / "pyedgarai" / "api" / "static"
        if static_dir.exists() and (static_dir / "index.html").exists():
            return send_from_directory(str(static_dir), 'index.html')
        else:
            # Fallback to JSON if HTML not found
            return jsonify({
                "message": "Welcome to PyEdgarAI Fast API! 🚀",
                "description": "Lightweight comparables analysis using cached data",
                "documentation": {
                    "api_info": "/api",
                    "health": "/health",
                    "comparables": "/comparables_sic?cik=320193&digits=2"
                },
                "example": {
                    "apple_comparables": "/comparables_sic?cik=320193&digits=2",
                    "microsoft_comparables": "/comparables_sic?cik=789019&digits=2"
                },
                "status": "ready",
                "note": "HTML landing page not found, serving JSON fallback"
            })
    except Exception as e:
        return jsonify({
            "message": "Welcome to PyEdgarAI Fast API! 🚀",
            "description": "Lightweight comparables analysis using cached data",
            "error": f"Could not serve landing page: {str(e)}",
            "fallback": "JSON response"
        })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files for the landing page"""
    try:
        static_dir = Path(__file__).parent / "src" / "pyedgarai" / "api" / "static"
        if static_dir.exists():
            return send_from_directory(str(static_dir), filename)
        else:
            return jsonify({"error": "Static files not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Static file error: {str(e)}"}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


def main():
    """Main function"""
    print("🚀 PyEdgarAI Fast API Server")
    print("=" * 40)
    
    # Quick health check
    try:
        health = comparables.health_check()
        if health["status"] == "ok":
            print(f"✅ Health check passed")
            print(f"📊 SIC data: {health['sic_data_entries']} companies")
            print(f"🏢 Names data: {health['names_data_entries']} companies")
        else:
            print(f"❌ Health check failed: {health.get('error', 'Unknown error')}")
            return
    except Exception as e:
        print(f"❌ Cannot start server: {e}")
        print("💡 Make sure data files exist in ~/.cache/pyedgarai/")
        return
    
    print("\n🌐 Starting server...")
    print("📍 URL: http://127.0.0.1:5001")
    print("📚 API Info: http://127.0.0.1:5001/api")
    print("🏥 Health: http://127.0.0.1:5001/health")
    print("🍎 Apple Example: http://127.0.0.1:5001/comparables_sic?cik=320193&digits=2")
    print("\n⏹️  Press Ctrl+C to stop")
    
    try:
        app.run(host="127.0.0.1", port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
