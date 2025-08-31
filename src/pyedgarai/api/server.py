# API server for pyedgarai
# Moved from project root to package under src/pyedgarai/api

from flask_openapi3 import Info, Tag, OpenAPI
from flask import send_from_directory
import json
import os
import logging
from importlib.metadata import version as _pkg_version
from typing import Type, Any
from pydantic import BaseModel, Field

# Internal imports
from pyedgarai.api import schemas as mm
from pyedgarai import sec_client as sec
from pyedgarai import comparables as comp
from pyedgarai import market_data as md
from pyedgarai import features as feat
import pyedgarai.yfinance_endpoints as yf_e

logging.basicConfig(level=logging.INFO)

# Package version for API doc
_api_version = _pkg_version("pyedgarai")
info = Info(title="PyEdgarAI - Financial Data Analysis API", version=_api_version, description="""
# PyEdgarAI Financial Data Analysis API

Welcome to **PyEdgarAI**, a comprehensive API for financial data analysis using SEC EDGAR database and market data.

## 🚀 Features

- **SEC EDGAR Data**: Access company filings, facts, and concepts
- **Comparables Analysis**: Find similar companies using various financial metrics
- **Market Data**: Get stock prices and financial information
- **Machine Learning**: Advanced company comparison using ML algorithms
- **Valuation Metrics**: Calculate important financial ratios and multiples

## 📊 Available Endpoints

### Company Data
- `/company_facts` - Get comprehensive company financial facts
- `/company_concept` - Get specific financial concepts for a company
- `/submission_history` - Get filing history for a company

### Market Analysis
- `/stocks_data` - Get historical stock price data
- `/valuation_metrics` - Calculate valuation multiples and ratios

### Comparables Analysis
- `/comparables` - Find comparable companies using traditional metrics
- `/comparables_kmeans` - ML-powered company comparison
- `/comparables_sic` - Find companies with same SIC code
- `/comparable_private` - Find comparable public companies for private firms

### Utilities
- `/cik_tickers` - Get CIK to ticker mappings
- `/cik_names` - Get CIK to company name mappings
- `/all_accounts` - Get all available accounting accounts
- `/clean_name` - Clean and normalize account names

## 🔐 Authentication

Most endpoints require an API token. Set the `PYEDGARAI_API_TOKEN` environment variable or pass it as a parameter.

## 📚 Documentation

Explore the interactive API documentation below to test endpoints and see detailed schemas.

### Available Documentation UIs:
- **Swagger UI**: Interactive testing interface
- **ReDoc**: Clean, readable documentation  
- **RapiDoc**: Fast and feature-rich interface
- **RapiPDF**: Generate PDF documentation
- **Scalar**: Modern, beautiful design
- **Elements**: Stoplight Elements UI
""")
app = OpenAPI(__name__, info=info, doc_ui=True)

# Authentication (configurable via env)
# If PYEDGARAI_API_TOKEN is unset, auth is disabled (accept all)
API_TOKEN = os.getenv("PYEDGARAI_API_TOKEN")

def authenticate(api_token: str | None = None) -> bool:
    if API_TOKEN is None:
        return True
    return api_token == API_TOKEN

# ---------------------- Endpoints ---------------------- #

# Create tag objects
home_tag = Tag(name="Home", description="API Home and Information")

# Home page endpoint - serve static HTML
@app.get("/", summary="API Home Page", tags=[home_tag])
def home():
    """
    Serve the beautiful landing page for PyEdgarAI API
    """
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'static')
        return send_from_directory(static_dir, 'index.html')
    except Exception as e:
        # Fallback to JSON response if static file not found
        return {
            "message": "Welcome to PyEdgarAI API! 🚀",
            "description": "Financial Data Analysis API using SEC EDGAR database and market data",
            "version": _api_version,
            "features": [
                "SEC EDGAR data access",
                "Comparables analysis", 
                "Market data retrieval",
                "ML-powered company comparison",
                "Valuation metrics calculation"
            ],
            "documentation": "/openapi/swagger",
            "endpoints": {
                "company_data": ["/company_facts", "/company_concept", "/submission_history"],
                "market_analysis": ["/stocks_data", "/valuation_metrics"],
                "comparables": ["/comparables", "/comparables_kmeans", "/comparables_sic", "/comparable_private"],
                "utilities": ["/cik_tickers", "/cik_names", "/all_accounts", "/clean_name"]
            },
            "authentication": "Set PYEDGARAI_API_TOKEN environment variable or pass api_token parameter",
            "contact": "https://github.com/jfimbett/pyedgarai"
        }

# JSON API info endpoint
@app.get("/api", summary="API Information (JSON)", tags=[home_tag])
def api_info():
    """
    Get API information in JSON format
    """
    return {
        "message": "Welcome to PyEdgarAI API! 🚀",
        "description": "Financial Data Analysis API using SEC EDGAR database and market data",
        "version": _api_version,
        "features": [
            "SEC EDGAR data access",
            "Comparables analysis", 
            "Market data retrieval",
            "ML-powered company comparison",
            "Valuation metrics calculation"
        ],
        "documentation": "/openapi/swagger",
        "endpoints": {
            "company_data": ["/company_facts", "/company_concept", "/submission_history"],
            "market_analysis": ["/stocks_data", "/valuation_metrics"],
            "comparables": ["/comparables", "/comparables_kmeans", "/comparables_sic", "/comparable_private"],
            "utilities": ["/cik_tickers", "/cik_names", "/all_accounts", "/clean_name"]
        },
        "authentication": "Set PYEDGARAI_API_TOKEN environment variable or pass api_token parameter",
        "contact": "https://github.com/jfimbett/pyedgarai"
    }

comparables_data = Tag(name="comparables_data", description="Comparables data")
@app.get("/comparables", summary="Get comparables", tags=[comparables_data], responses={200: mm.ComparablesResponse})
def comparables(query: mm.ComparablesRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}

    params_comparables = {}
    if query.industry_digits:
        params_comparables['industry'] = {'digits': query.industry_digits}
    if query.size_interval:
        params_comparables['size'] = {'interval': query.size_interval}
    if query.profitability_interval:
        params_comparables['profitability'] = {'interval': query.profitability_interval}
    if query.growth_rate_interval:
        params_comparables['growth_rate'] = {'interval': query.growth_rate_interval}
    if query.capital_structure_interval:
        params_comparables['capital_structure'] = {'interval': query.capital_structure_interval}
    if query.location:
        params_comparables['location'] = query.location

    kwargs = {
        'params_comparables': params_comparables,
        'method': query.method,
    }
    return comp.identify_comparables(query.cik, **kwargs)

comparables_data_ml = Tag(name="comparables_data_ml", description="Comparables data using ML")
@app.get("/comparables_kmeans", summary="Get comparables using ML", tags=[comparables_data_ml], responses={200: mm.ComparablesResponseML})
def comparables_kmeans(query: mm.ComparablesRequestML):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}

    response = comp.identify_comparables_ml(query.name,
                                           query.sic,
                                           query.assets,
                                           query.profitability,
                                           query.growth_rate,
                                           query.capital_structure)
    return response

comparables_private_tag = Tag(name="comparables_private", description="Comparables analysis for private companies")
@app.get("/comparable_private", summary="Get comparable public companies for a private company", tags=[comparables_private_tag], responses={200: mm.ComparablesPrivateResponse})
def comparable_private(query: mm.ComparablesPrivateRequest):
    """
    Find comparable public companies for a private company based on financial metrics.
    
    This endpoint takes private company financial data and finds the 5 most similar
    public companies in the same SIC sector, including market data and valuation ratios.
    """
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}

    try:
        result = comp.identify_comparables_private(
            name=query.name,
            sic_code=query.sic_code,
            profitability=query.profitability,
            growth_rate=query.growth_rate,
            capital_structure=query.capital_structure
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "target_company": {
                "name": query.name,
                "sic_code": query.sic_code,
                "profitability": query.profitability,
                "growth_rate": query.growth_rate,
                "capital_structure": query.capital_structure
            },
            "comparables": [],
            "total_found": 0,
            "method": "private_comparables",
            "sic_sector": query.sic_code
        }

account_tag = Tag(name="account", description="Accounting account data for all companies")
@app.get("/account", summary="Get account data", tags=[account_tag], responses={200: mm.AccountResponse})
def account(query: mm.AccountRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    frames = sec.get_xbrl_frames(query.taxonomy, mm.clean_account_name(query.account), query.units, query.frame)
    return frames

company_tag = Tag(name="company", description="Company data")
@app.get("/company_concept", summary="Get company concept", tags=[company_tag], responses={200: mm.CompanyResponse})
def company_concept(query: mm.CompanyRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return sec.get_company_concept(int(query.cik), query.taxonomy, mm.clean_account_name(query.tag))

companies_tag = Tag(name="companies", description="Companies data")
@app.get("/cik_tickers", summary="Get CIK tickers", tags=[companies_tag], responses={200: mm.CIKTickersResponse})
def cik_tickers(query: mm.CIKTickers):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.get_cik_tickers()

names_tag = Tag(name="names", description="Company names")
@app.get("/cik_names", summary="Get CIK names", tags=[names_tag], responses={200: mm.CIKNamesResponse})
def cik_names(query: mm.CIKNames):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.return_company_names()

clean_name_tag = Tag(name="clean_name", description="Cleaned account name")
@app.get("/clean_name", summary="Get cleaned account name", tags=[clean_name_tag], responses={200: mm.CleanNameResponse})
def clean_name(query: mm.CleanName):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return {"clean_name": mm.clean_account_name(query.name)}

company_facts_tag = Tag(name="company_facts", description="Company facts")
@app.get("/company_facts", summary="Get company facts", tags=[company_facts_tag], responses={200: mm.CompanyFactsResponse})
def company_facts(query: mm.CompanyFacts):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return sec.get_company_facts(int(query.cik))

all_accounts_tag = Tag(name="accounts", description="All accounts data")
@app.get("/all_accounts", summary="Get account data for all companies", tags=[all_accounts_tag], responses={200: mm.AccountResponse})
def all_accounts(query: mm.AllAccounts):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.return_accounts()

submission_history_tag = Tag(name="submission_history", description="Submission history")
@app.get("/submission_history", summary="Get submission history", tags=[submission_history_tag], responses={200: mm.SubmissionHistoryResponse})
def submission_history(query: mm.SubmissionHistory):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return sec.get_submission_history(int(query.cik))

ciksic_tag = Tag(name="cik_sic", description="CIK SIC")
@app.get("/cik_sic", summary="Get CIK and SIC code", tags=[ciksic_tag], responses={200: mm.CIKSICResponse})
def cik_sic(query: mm.CIKSIC):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.return_cik_sic()

comparables_sic_tag = Tag(name="comparables_sic", description="Comparables with same SIC")
@app.get("/comparables_sic", summary="Get companies with same SIC", tags=[comparables_sic_tag], responses={200: mm.ComparablesSICResponse})
def comparables_sic(query: mm.ComparablesSIC):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return comp.get_companies_with_same_sic(int(query.cik))

stocks_data = Tag(name="stocks_data", description="Price data for stocks")
@app.get("/stocks_data", summary="Get stock data", tags=[stocks_data], responses={200: mm.StockDataResponse})
def stocks_data_ep(query: mm.StockDataRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    df = md.get_stocks_data(query.tickers, query.start_date, query.end_date)
    data = df.to_dict(orient='list')
    return {"data": data}

valuation_metrics = Tag(name="valuation_metrics", description="Valuation metrics")
@app.get("/valuation_metrics", summary="Get valuation metrics", tags=[valuation_metrics], responses={200: mm.ValuationMetricsResponse})
def relevant_valuation_metrics(query: mm.ValuationMetricsRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}

    tickers = query.tickers
    variables = []
    for ticker in tickers:
        try:
            temp = yf_e.get_stock_element(ticker, 'income_stmt')
            temp = json.loads(temp)
            eps = temp['data']['Basic EPS'][0]
            info = yf_e.get_stock_element(ticker, 'info')
            marketCap = info['data']['marketCap']
            enterpriseValue = info['data']['enterpriseValue']
            sharesOutstanding = info['data']['sharesOutstanding']
            priceToBook = info['data']['priceToBook']
            enterpriseToEbitda = info['data']['enterpriseToEbitda']
            currentPrice = info['data']['currentPrice']

            dict_ = {'ticker': ticker, 'eps': eps, 'marketCap': marketCap, 'enterpriseValue': enterpriseValue,
                    'sharesOutstanding': sharesOutstanding, 'priceToBook': priceToBook, 'enterpriseToEbitda': enterpriseToEbitda,
                    'currentPrice': currentPrice, 'priceToEarnings': currentPrice / eps}
            variables.append(dict_)
        except Exception:
            logging.warning(f'Error getting data for {ticker}')

    avg_multiple = {}
    multiples = ['priceToEarnings', 'priceToBook', 'enterpriseToEbitda']
    for multiple in multiples:
        avg_multiple[multiple] = sum([e[multiple] for e in variables]) / len(variables)
    return {'avg_multiples': avg_multiple, 'variables': variables}

# Note: Dynamic yfinance endpoints disabled to prevent startup issues
# They can be enabled later if needed

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
