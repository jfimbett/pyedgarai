# API server for pyedgarai
# Moved from project root to package under src/pyedgarai/api

from flask_openapi3 import Info, Tag, OpenAPI
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
info = Info(title="Comparable companies API", version=_api_version)
app = OpenAPI(__name__, info=info)

# Authentication (configurable via env)
# If PYEDGARAI_API_TOKEN is unset, auth is disabled (accept all)
API_TOKEN = os.getenv("PYEDGARAI_API_TOKEN")

def authenticate(api_token: str | None = None) -> bool:
    if API_TOKEN is None:
        return True
    return api_token == API_TOKEN

# ---------------------- Endpoints ---------------------- #

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

account_tag = Tag(name="account", description="Accounting account data for all companies")
@app.get("/account", summary="Get account data", tags=[account_tag], responses={200: mm.AccountResponse})
def account(query: mm.AccountRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    frames = sec.get_xbrl_frames(query.taxonomy, mm.clean_account_name(query.account), query.units, query.frame)
    return frames

company_tag  = Tag(name="company", description="Company data")
@app.get("/company_concept", summary="Get company concept", tags=[company_tag], responses={200: mm.CompanyResponse})
def company_concept(query: mm.CompanyRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return sec.get_company_concept(int(query.cik), query.taxonomy, mm.clean_account_name(query.tag))

companies_tag  = Tag(name="companies", description="Companies data")
@app.get("/cik_tickers", summary="Get CIK tickers", tags=[companies_tag], responses={200: mm.CIKTickersResponse})
def cik_tickers(query: mm.CIKTickers):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.get_cik_tickers()

names_tag  = Tag(name="names", description="Company names")
@app.get("/cik_names", summary="Get CIK names", tags=[names_tag], responses={200: mm.CIKNamesResponse})
def cik_names(query: mm.CIKNames):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.return_company_names()

clean_name_tag  = Tag(name="clean_name", description="Cleaned account name")
@app.get("/clean_name", summary="Get cleaned account name", tags=[clean_name_tag], responses={200: mm.CleanNameResponse})
def clean_name(query: mm.CleanName):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return {"clean_name": mm.clean_account_name(query.name)}

company_facts_tag  = Tag(name="company_facts", description="Company facts")
@app.get("/company_facts", summary="Get company facts", tags=[company_facts_tag], responses={200: mm.CompanyFactsResponse})
def company_facts(query: mm.CompanyFacts):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return sec.get_company_facts(int(query.cik))

all_accounts_tag       = Tag(name="accounts", description="All accounts data")
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

ciksic_tag  = Tag(name="cik_sic", description="CIK SIC")
@app.get("/cik_sic", summary="Get CIK and SIC code", tags=[ciksic_tag], responses={200: mm.CIKSICResponse})
def cik_sic(query: mm.CIKSIC):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return feat.return_cik_sic()

comparables_sic_tag   = Tag(name="comparables_sic", description="Comparables with same SIC")
@app.get("/comparables_sic", summary="Get companies with same SIC", tags=[comparables_sic_tag], responses={200: mm.ComparablesSICResponse})
def comparables_sic(query: mm.ComparablesSIC):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return comp.get_companies_with_same_sic(int(query.cik))

stocks_data  = Tag(name="stocks_data", description="Price data for stocks")
@app.get("/stocks_data", summary="Get stock data", tags=[stocks_data], responses={200: mm.StockDataResponse})
def stocks_data_ep(query: mm.StockDataRequest):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    df = md.get_stocks_data(query.tickers, query.start_date, query.end_date)
    data = df.to_dict(orient='list')
    return {"data": data}

valuation_metrics  = Tag(name="valuation_metrics", description="Valuation metrics")
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

# Dynamically generate yfinance endpoints
request_models: dict[str, Type[BaseModel]] = {}

tags = {element: Tag(name=element) for element in yf_e.IMPLEMENTED_ELEMENTS}

class BaseRequestModel(BaseModel):
    ticker: str = Field(..., title="Ticker", description="Stock ticker", example="AAPL")
    api_token: str = Field(..., title="API token", description="API token")

def create_request_model(element_name: str) -> Type[BaseModel]:
    class DynamicRequestModel(BaseRequestModel):
        pass
    DynamicRequestModel.__name__ = f"{element_name.replace('_', ' ').title().replace(' ','')}Request"
    return DynamicRequestModel

class GenericResponseModel(BaseModel):
    message: str
    data: dict

for element in yf_e.IMPLEMENTED_ELEMENTS:
    request_model = create_request_model(element)
    request_models[element] = request_model

    def create_endpoint_func(request_model: Type[BaseRequestModel], element: str):
        def endpoint_func(query: Any):  # avoid type issues with dynamic model class at runtime
            if not authenticate(query.api_token):
                return {"error": "Invalid API token."}
            response = yf_e.get_stock_element(query.ticker, element)
            if isinstance(response, str):
                response = json.loads(response)
            return response
        return endpoint_func

    endpoint_func = create_endpoint_func(request_model, element)
    endpoint_func.__name__ = f"endpoint_func_{element}"
    app.get(f'/{element}', summary=f"Endpoint for {element}", tags=[tags[element]], responses={200: GenericResponseModel})(endpoint_func)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
