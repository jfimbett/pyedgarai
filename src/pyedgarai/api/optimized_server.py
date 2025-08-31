"""
Updated API Server with Requirements Checking and Optimized Performance

This version includes:
- Requirements checking before startup
- Optimized comparables functions 
- Better error handling and timeouts
- Fallback methods for reliability
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir / "src"))

try:
    from flask import send_from_directory
    from flask_openapi3 import OpenAPI, APIBlueprint, Tag
    from flask_openapi3.models import BaseModel
    from pydantic import Field
    
    # Import our modules
    from pyedgarai.requirements_checker import RequirementsChecker
    from pyedgarai.optimized_comparables import get_optimized_comparables
    from pyedgarai import __version__ as _api_version
    from pyedgarai.api import models as mm
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run requirements checker first: python -m pyedgarai.requirements_checker")
    sys.exit(1)

# API Information with requirements checking
info = {
    "title": "PyEdgarAI API - Optimized",
    "version": _api_version,
    "description": """
# PyEdgarAI Financial Data API (Optimized Version)

High-performance financial data analysis API with comprehensive requirements checking.

## Features
- **SEC EDGAR Data**: Access to company facts, financial statements, and historical data
- **Optimized Comparables**: Fast company comparison using cached data
- **Market Data**: Stock prices, financial metrics, and valuation analysis  
- **ML Analysis**: Machine learning-powered company similarity analysis
- **Requirements Checking**: Comprehensive validation of all prerequisites

## Performance Optimizations
- Cached data loading for faster response times
- Lazy imports to reduce startup time  
- Fallback methods for improved reliability
- Comprehensive error handling and timeouts

### Quick Start
1. Run requirements check: `python -m pyedgarai.requirements_checker`
2. Generate data files if needed
3. Start API server: `python -m pyedgarai.api.optimized_server`

### Comparables Analysis  
- `/comparables_fast` - Fast industry-based comparison (recommended)
- `/comparables_lite` - Lightweight traditional analysis
- `/comparables_ml_cached` - ML analysis using cached data
- `/comparables_sic` - SIC code-based comparison

### Documentation
- [Swagger UI](/openapi/swagger) - Interactive API documentation
- [ReDoc](/openapi/redoc) - Clean documentation format
- [RapiDoc](/openapi/rapidoc) - Feature-rich documentation
- [RapiPDF](/openapi/rapipdf) - PDF export capability
- [Scalar](/openapi/scalar) - Modern API documentation
- [Elements](/openapi/elements) - Stoplight Elements

### Status & Health
- `/health` - System health check
- `/requirements` - Requirements validation
- `/api` - API information
"""
}

# Create Flask-OpenAPI3 app
app = OpenAPI(__name__, info=info)

# Configuration
API_TOKEN = os.getenv("PYEDGARAI_API_TOKEN")

def authenticate(api_token: str | None = None) -> bool:
    if API_TOKEN is None:
        return True
    return api_token == API_TOKEN

# ---------------------- System Health Endpoints ---------------------- #

system_tag = Tag(name="System", description="System health and requirements")

@app.get("/health", summary="System Health Check", tags=[system_tag])
def health_check():
    """
    Comprehensive system health check including data files and API connectivity
    """
    try:
        # Check optimized comparables health
        comparables = get_optimized_comparables()
        health = comparables.health_check()
        
        # Add API server status
        health["api_server"] = {
            "status": "ok",
            "timestamp": time.time(),
            "version": _api_version
        }
        
        return health
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": time.time(),
            "api_server": {"status": "error", "version": _api_version}
        }

@app.get("/requirements", summary="Requirements Check", tags=[system_tag])
def requirements_check():
    """
    Run comprehensive requirements validation
    """
    try:
        checker = RequirementsChecker()
        results = checker.check_all()
        return {
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# ---------------------- Home and Info ---------------------- #

home_tag = Tag(name="Home", description="API Home and Information")

@app.get("/", summary="API Home Page", tags=[home_tag])
def home():
    """Serve the beautiful landing page for PyEdgarAI API"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'static')
        return send_from_directory(static_dir, 'index.html')
    except Exception:
        return {
            "message": "Welcome to PyEdgarAI API! 🚀 (Optimized Version)",
            "description": "High-performance financial data analysis with requirements checking",
            "version": _api_version,
            "features": [
                "Optimized comparables analysis",
                "Comprehensive requirements checking", 
                "Cached data loading",
                "Fallback methods for reliability"
            ],
            "documentation": "/openapi/swagger",
            "health_check": "/health"
        }

@app.get("/api", summary="API Information", tags=[home_tag])
def api_info():
    """Get API version and basic information"""
    return {
        "name": "PyEdgarAI API - Optimized",
        "version": _api_version,
        "description": "High-performance financial data analysis API",
        "features": [
            "SEC EDGAR data access",
            "Optimized comparables analysis", 
            "Market data retrieval",
            "ML-powered company comparison",
            "Requirements validation"
        ],
        "documentation": {
            "swagger": "/openapi/swagger",
            "redoc": "/openapi/redoc", 
            "rapidoc": "/openapi/rapidoc"
        },
        "endpoints": {
            "system": ["/health", "/requirements"],
            "comparables": ["/comparables_fast", "/comparables_lite", "/comparables_ml_cached", "/comparables_sic"]
        },
        "status": "optimized",
        "timestamp": time.time()
    }

# ---------------------- Optimized Comparables Endpoints ---------------------- #

comparables_tag = Tag(name="Comparables", description="Optimized comparables analysis")

class ComparablesRequestFast(BaseModel):
    cik: int = Field(description="Company CIK", example=320193)
    max_companies: int = Field(default=20, description="Maximum companies to return", example=20)
    api_token: str = Field(default="", description="API token")

class ComparablesRequestLite(BaseModel):
    cik: int = Field(description="Company CIK", example=320193)
    max_companies: int = Field(default=20, description="Maximum companies to return", example=20)
    api_token: str = Field(default="", description="API token")

class ComparablesRequestML(BaseModel):
    cik: int = Field(description="Company CIK", example=320193)
    name: str = Field(default="", description="Company name", example="Apple Inc.")
    sic: int = Field(default=None, description="SIC code", example=3571)
    assets: float = Field(default=None, description="Total assets", example=352755000000)
    max_companies: int = Field(default=20, description="Maximum companies to return", example=20)
    api_token: str = Field(default="", description="API token")

class ComparablesSICRequest(BaseModel):
    cik: int = Field(description="Company CIK", example=320193)
    digits: int = Field(default=2, description="SIC digits to match", example=2)
    api_token: str = Field(default="", description="API token")

@app.get("/comparables_fast", summary="Fast Industry Comparables", tags=[comparables_tag])
def comparables_fast(query: ComparablesRequestFast):
    """
    Fast industry-based comparables using cached data (recommended endpoint)
    
    This endpoint provides the best balance of speed and accuracy by using 
    cached SIC code mappings and company name data.
    """
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    try:
        comparables = get_optimized_comparables()
        result = comparables.get_industry_comparables(
            query.cik, 
            max_companies=query.max_companies
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "target_company": {"cik": query.cik},
            "companies": [],
            "total_found": 0,
            "method": "fast_industry"
        }

@app.get("/comparables_lite", summary="Lite Traditional Comparables", tags=[comparables_tag])
def comparables_lite(query: ComparablesRequestLite):
    """
    Lightweight traditional comparables analysis using cached data only
    
    Provides industry-based comparison with ticker lookup when available.
    No SEC API calls for improved performance.
    """
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    try:
        comparables = get_optimized_comparables()
        result = comparables.get_traditional_comparables_lite(
            query.cik,
            max_companies=query.max_companies
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "target_company": {"cik": query.cik},
            "companies": [],
            "total_found": 0,
            "method": "traditional_lite"
        }

@app.get("/comparables_ml_cached", summary="ML Comparables (Cached)", tags=[comparables_tag])
def comparables_ml_cached(query: ComparablesRequestML):
    """
    ML-powered comparables using cached data with similarity scoring
    
    Uses industry matching and name similarity for company comparison.
    Faster than full ML analysis while maintaining good accuracy.
    """
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    try:
        comparables = get_optimized_comparables()
        result = comparables.get_ml_comparables_cached(
            cik=query.cik,
            name=query.name,
            sic=query.sic,
            assets=query.assets,
            max_companies=query.max_companies
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "target_company": {
                "cik": query.cik,
                "name": query.name
            },
            "companies": [],
            "total_found": 0,
            "method": "ml_cached"
        }

@app.get("/comparables_sic", summary="SIC Code Comparables", tags=[comparables_tag])
def comparables_sic(query: ComparablesSICRequest):
    """
    Find companies with matching SIC codes
    
    Fast comparison based on Standard Industrial Classification codes.
    Adjust digits parameter for broader (fewer digits) or narrower (more digits) matches.
    """
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    try:
        comparables = get_optimized_comparables()
        result_df = comparables.get_companies_with_same_sic_fast(
            query.cik, 
            digits=query.digits
        )
        
        companies = result_df.to_dict('records')
        
        return {
            "target_company": {
                "cik": query.cik,
                "sic": comparables.get_sic_for_cik(query.cik),
                "name": comparables.get_company_name_for_cik(query.cik)
            },
            "companies": companies,
            "total_found": len(companies),
            "method": "sic_match",
            "sic_digits": query.digits,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "target_company": {"cik": query.cik},
            "companies": [],
            "total_found": 0,
            "method": "sic_match"
        }

# ---------------------- Startup Checks ---------------------- #

def startup_checks():
    """Run startup checks to ensure everything is ready"""
    print("🚀 PyEdgarAI Optimized API Server")
    print("=" * 50)
    
    print("🔍 Running startup checks...")
    
    try:
        # Quick health check
        comparables = get_optimized_comparables()
        health = comparables.health_check()
        
        if health["status"] == "ok":
            print("✅ All systems ready!")
            return True
        elif health["status"] == "missing_data":
            print("⚠️  Some data files missing, but basic functionality available")
            print("💡 Run requirements checker for full validation")
            return True
        else:
            print("❌ System health check failed")
            print("💡 Run: python -m pyedgarai.requirements_checker")
            return False
            
    except Exception as e:
        print(f"❌ Startup check error: {e}")
        print("💡 Run requirements checker to identify issues")
        return False

# ---------------------- Main ---------------------- #

if __name__ == "__main__":
    if startup_checks():
        print("\n🌐 Starting server on http://127.0.0.1:5001")
        print("📚 Documentation: http://127.0.0.1:5001/openapi/swagger")
        print("🏥 Health check: http://127.0.0.1:5001/health")
        print("📋 Requirements: http://127.0.0.1:5001/requirements")
        print("\n⏹️  Press Ctrl+C to stop")
        
        try:
            app.run(host="127.0.0.1", port=5001, debug=False)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
    else:
        print("\n💡 Fix issues and try again")
        sys.exit(1)
