# Imports
#%%
from flask_openapi3 import Info, Tag, OpenAPI
import json
import time
from version import version
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Type
from models import (AccountRequest, AccountResponse, CompanyRequest, CompanyResponse, CIKTickers, CIKTickersResponse,
                    CIKNames, CIKNamesResponse, CleanName, CleanNameResponse, CompanyFacts, CompanyFactsResponse,
                    SubmissionHistory, SubmissionHistoryResponse, CIKSIC, CIKSICResponse, ComparablesSIC, ComparablesSICResponse,
                    AllAccounts, StoredData, StoredDataResponse, StockDataRequest, StockDataResponse,
                    ComparablesRequest, ComparablesResponse,
                    ValuationMetricsRequest, ValuationMetricsResponse)
                    

from pyedgarai.pyedgarai import (clean_account_name, get_xbrl_frames, get_company_concept,
                                 get_cik_tickers, return_company_names, get_company_facts,
                                 return_accounts, get_submission_history, return_cik_sic, 
                                 get_companies_with_same_sic,
                                 get_stocks_data, identify_comparables)
from pyedgarai.download_sec import get_data

from pyedgarai.yfinance_endpoints import IMPLEMENTED_ELEMENTS, IMPLEMENTED_FUNCTIONS, get_stock_element
import logging

logging.basicConfig(level=logging.INFO)
#%%

# API Info
info = Info(title="Comparable companies API", version=version)
app = OpenAPI(__name__, info=info)


# decorator for api token
TEST_TOKEN = "t3stt@ken"
def authenticate(api_token: str = None):
    if api_token != TEST_TOKEN:
        return False
    return True


# Tags
account_tag = Tag(name="account", description="Accounting account data for all companies")
company_tag = Tag(name="company", description="Company data")
companies_tag = Tag(name="companies", description="Companies data")
names_tag = Tag(name="names", description="Company names")
clean_name_tag = Tag(name="clean_name", description="Cleaned account name")
company_facts_tag = Tag(name="company_facts", description="Company facts")
all_accounts_tag = Tag(name="accounts", description="All accounts data")
submission_history_tag = Tag(name="submission_history", description="Submission history")
ciksic_tag = Tag(name="cik_sic", description="CIK SIC")
comparables_sic_tag = Tag(name="comparables_sic", description="Comparables with same SIC")
stocks_data = Tag(name="stocks_data", description="Price data for stocks")
comparables_data = Tag(name="comparables_data", description="Comparables data")
valuation_metrics = Tag(name="valuation_metrics", description="Valuation metrics")

@app.get("/comparables", summary="Get comparables", tags=[comparables_data], responses={200: ComparablesResponse})
def comparables(query: ComparablesRequest):
    """Retrieve comparables for a company."""
    print(query) 
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    

    kwargs = {}
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

    kwargs['params_comparables'] = params_comparables
    kwargs['variables_to_compare'] = query.variables_to_compare
    kwargs['method'] = query.method

    kwargs['extra_variables'] = query.extra_variables



    return identify_comparables(query.cik, **kwargs)


# Endpoints
@app.get("/account", summary="Get account data", tags=[account_tag], responses={200: AccountResponse})
def account(query: AccountRequest):
    """Retrieve account data for all companies."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    frames = get_xbrl_frames(query.taxonomy, clean_account_name(query.account), query.units, query.frame)
    return frames

@app.get("/company_concept", summary="Get company concept", tags=[company_tag], responses={200: CompanyResponse})
def company_concept(query: CompanyRequest):
    """Retrieve account history for a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return get_company_concept(int(query.cik), query.taxonomy, clean_account_name(query.tag))

@app.get("/cik_tickers", summary="Get CIK tickers", tags=[companies_tag], responses={200: CIKTickersResponse})
def cik_tickers(query: CIKTickers):
    """Get list of CIKs and their corresponding tickers."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return get_cik_tickers()

@app.get("/cik_names", summary="Get CIK names", tags=[names_tag], responses={200: CIKNamesResponse})
def cik_names(query: CIKNames):
    """Get list of CIKs and their corresponding company names."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return return_company_names()

@app.get("/clean_name", summary="Get cleaned account name", tags=[clean_name_tag], responses={200: CleanNameResponse})
def clean_name(query: CleanName):
    """Get a cleaned account name."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return {"clean_name": clean_account_name(query.name)}

@app.get("/company_facts", summary="Get company facts", tags=[company_facts_tag], responses={200: CompanyFactsResponse})
def company_facts(query: CompanyFacts):
    """Get facts of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return get_company_facts(int(query.cik))

@app.get("/all_accounts", summary="Get account data for all companies", tags=[all_accounts_tag], responses={200: AccountResponse})
def all_accounts(query: AllAccounts):
    """Retrieve all account data for all companies."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return return_accounts()

@app.get("/submission_history", summary="Get submission history", tags=[submission_history_tag], responses={200: SubmissionHistoryResponse})
def submission_history(query: SubmissionHistory):
    """Retrieve submission history of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return get_submission_history(int(query.cik))

@app.get("/cik_sic", summary="Get CIK and SIC code", tags=[ciksic_tag], responses={200: CIKSICResponse})
def cik_sic(query: CIKSIC):
    """Get CIK and SIC code of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return return_cik_sic()

@app.get("/comparables_sic", summary="Get companies with same SIC", tags=[comparables_sic_tag], responses={200: ComparablesSICResponse})
def comparables_sic(query: ComparablesSIC):
    """Retrieve companies with the same SIC code."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return get_companies_with_same_sic(int(query.cik))

@app.get("/stocks_data", summary="Get stock data", tags=[stocks_data], responses={200: StockDataResponse})
def stocks_data(query: StockDataRequest):
    """Retrieve stock data for the given tickers."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    df = get_stocks_data(query.tickers, query.start_date, query.end_date)
    data = df.to_dict(orient='list')
    return {"data": data}

#---------------------------------#
# Endpoints for yfinance, these are
# done inside of a loop

# A dictionary to hold request model classes
request_models: Dict[str, Type[BaseModel]] = {}

# Base request model
class BaseRequestModel(BaseModel):
    ticker: str
    api_token: str

# Generic response model
class GenericResponseModel(BaseModel):
    message: str
    data: dict

# Function to create dynamic request models
def create_request_model(element_name: str) -> Type[BaseModel]:
    class DynamicRequestModel(BaseRequestModel):
        pass

    DynamicRequestModel.__name__ = f"{element_name.replace('_', ' ').title().replace(' ','')}Request"
    return DynamicRequestModel

# Create Tag objects for each endpoint
tags = {element: Tag(name=element) for element in IMPLEMENTED_ELEMENTS}

# Dynamically create and register endpoints
for element in IMPLEMENTED_ELEMENTS:
    request_model = create_request_model(element)
    request_models[element] = request_model

    # Create the endpoint function with a unique name using a lambda
    def create_endpoint_func(request_model: Type[BaseRequestModel], element: str):
        def endpoint_func(query: request_model):
            # Here you can perform authentication with query.api_token
            # Call the get_stock_element function with appropriate parameters
            return get_stock_element(query.ticker, element)
        return endpoint_func

    # Assign a unique name to the endpoint function
    endpoint_func = create_endpoint_func(request_model, element)
    endpoint_func.__name__ = f"endpoint_func_{element}"

    # Register the endpoint with the app, using the Tag object instead of string
    app.get(f'/{element}', summary=f"Endpoint for {element}",
            tags=[tags[element]], responses={200: GenericResponseModel})(endpoint_func)

@app.get("/valuation_metrics", summary="Get valuation metrics", tags=[valuation_metrics], responses={200: ValuationMetricsResponse})
def relevant_valuation_metrics(query: ValuationMetricsRequest):
    
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    tickers = query.tickers
    # get earnings per share
    variables = []
    for ticker in tickers:
        try:
            temp = get_stock_element(ticker, 'income_stmt')
            # to json 
            temp = json.loads(temp)
            eps = temp['data']['Basic EPS'][0]
            info = get_stock_element(ticker, 'info')
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
        except:
            logging.warning(f'Error getting data for {ticker}')

    # apply the average multiple 
    avg_multiple = {}
    multiples = ['priceToEarnings', 'priceToBook', 'enterpriseToEbitda']
    for multiple in multiples:
        avg_multiple[multiple] = sum([e[multiple] for e in variables]) / len(variables)
    to_return = {'avg_multiples': avg_multiple, 'variables': variables}
    return to_return







#%%
if __name__ == '__main__':
    app.run(debug=True)
