# Imports
#%%
from flask_openapi3 import Info, Tag, OpenAPI
import json
import time
from version import version
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Type
import models as mm
import pyedgarai.pyedgarai as pea
import pyedgarai.download_sec as ds
import pyedgarai.yfinance_endpoints as yf_e
import logging
logging.basicConfig(level=logging.INFO)
#%%
# API Info
info = Info(title="Comparable companies API", version=version)
app = OpenAPI(__name__, info=info)
# decorator for api token
TEST_TOKEN = "t3stt@ken"
def authenticate(api_token: str = None):
    return api_token in [TEST_TOKEN]

# Tags
comparables_data = Tag(name="comparables_data", description="Comparables data")
@app.get("/comparables", summary="Get comparables", tags=[comparables_data], responses={200: mm.ComparablesResponse})
def comparables(query: mm.ComparablesRequest):
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
    #kwargs['variables_to_compare'] = query.variables_to_compare
    kwargs['method'] = query.method
    #kwargs['extra_variables'] = query.extra_variables
    return pea.identify_comparables(query.cik, **kwargs)

comparables_data_ml = Tag(name="comparables_data_ml", description="Comparables data using ML")
@app.get("/comparables_kmeans", summary="Get comparables using ML", tags=[comparables_data_ml], responses={200: mm.ComparablesResponseML})
def comparables_kmeans(query: mm.ComparablesRequestML):
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}

    # use pea.identify_comparables_ml
    response = pea.identify_comparables_ml(query.name,
                                           query.sic, 
                                           query.assets, 
                                           query.profitability, 
                                           query.growth_rate, 
                                           query.capital_structure)
    
    return response


# Endpoints
account_tag = Tag(name="account", description="Accounting account data for all companies")
@app.get("/account", summary="Get account data", tags=[account_tag], responses={200: mm.AccountResponse})
def account(query: mm.AccountRequest):
    """Retrieve account data for all companies."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    frames = pea.get_xbrl_frames(query.taxonomy, pea.clean_account_name(query.account), query.units, query.frame)
    return frames

company_tag  = Tag(name="company", description="Company data")
@app.get("/company_concept", summary="Get company concept", tags=[company_tag], responses={200: mm.CompanyResponse})
def company_concept(query: mm.CompanyRequest):
    """Retrieve account history for a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.get_company_concept(int(query.cik), query.taxonomy, pea.clean_account_name(query.tag))

companies_tag  = Tag(name="companies", description="Companies data")
@app.get("/cik_tickers", summary="Get CIK tickers", tags=[companies_tag], responses={200: mm.CIKTickersResponse})
def cik_tickers(query: mm.CIKTickers):
    """Get list of CIKs and their corresponding tickers."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.get_cik_tickers()

names_tag  = Tag(name="names", description="Company names")
@app.get("/cik_names", summary="Get CIK names", tags=[names_tag], responses={200: mm.CIKNamesResponse})
def cik_names(query: mm.CIKNames):
    """Get list of CIKs and their corresponding company names."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.return_company_names()

clean_name_tag  = Tag(name="clean_name", description="Cleaned account name")
@app.get("/clean_name", summary="Get cleaned account name", tags=[clean_name_tag], responses={200: mm.CleanNameResponse})
def clean_name(query: mm.CleanName):
    """Get a cleaned account name."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return {"clean_name": pea.clean_account_name(query.name)}

company_facts_tag  = Tag(name="company_facts", description="Company facts")
@app.get("/company_facts", summary="Get company facts", tags=[company_facts_tag], responses={200: mm.CompanyFactsResponse})
def company_facts(query: mm.CompanyFacts):
    """Get facts of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.get_company_facts(int(query.cik))

all_accounts_tag       = Tag(name="accounts", description="All accounts data")
@app.get("/all_accounts", summary="Get account data for all companies", tags=[all_accounts_tag], responses={200: mm.AccountResponse})
def all_accounts(query: mm.AllAccounts):
    """Retrieve all account data for all companies."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.return_accounts()

submission_history_tag = Tag(name="submission_history", description="Submission history")
@app.get("/submission_history", summary="Get submission history", tags=[submission_history_tag], responses={200: mm.SubmissionHistoryResponse})
def submission_history(query: mm.SubmissionHistory):
    """Retrieve submission history of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.get_submission_history(int(query.cik))

ciksic_tag  = Tag(name="cik_sic", description="CIK SIC")
@app.get("/cik_sic", summary="Get CIK and SIC code", tags=[ciksic_tag], responses={200: mm.CIKSICResponse})
def cik_sic(query: mm.CIKSIC):
    """Get CIK and SIC code of a company."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.return_cik_sic()

comparables_sic_tag   = Tag(name="comparables_sic", description="Comparables with same SIC")
@app.get("/comparables_sic", summary="Get companies with same SIC", tags=[comparables_sic_tag], responses={200: mm.ComparablesSICResponse})
def comparables_sic(query: mm.ComparablesSIC):
    """Retrieve companies with the same SIC code."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    return pea.get_companies_with_same_sic(int(query.cik))

stocks_data  = Tag(name="stocks_data", description="Price data for stocks")
@app.get("/stocks_data", summary="Get stock data", tags=[stocks_data], responses={200: mm.StockDataResponse})
def stocks_data(query: mm.StockDataRequest):
    """Retrieve stock data for the given tickers."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    df = pea.get_stocks_data(query.tickers, query.start_date, query.end_date)
    data = df.to_dict(orient='list')
    return {"data": data}

valuation_metrics  = Tag(name="valuation_metrics", description="Valuation metrics")
@app.get("/valuation_metrics", summary="Get valuation metrics", tags=[valuation_metrics], responses={200: mm.ValuationMetricsResponse})
def relevant_valuation_metrics(query: mm.ValuationMetricsRequest):
    
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    
    tickers = query.tickers
    # get earnings per share
    variables = []
    for ticker in tickers:
        try:
            temp = yf_e.get_stock_element(ticker, 'income_stmt')
            # to json 
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
        except:
            logging.warning(f'Error getting data for {ticker}')

    # apply the average multiple 
    avg_multiple = {}
    multiples = ['priceToEarnings', 'priceToBook', 'enterpriseToEbitda']
    for multiple in multiples:
        avg_multiple[multiple] = sum([e[multiple] for e in variables]) / len(variables)
    to_return = {'avg_multiples': avg_multiple, 'variables': variables}
    return to_return

#---------------------------------#
# Endpoints for yfinance, these are
# done inside of a loop

# A dictionary to hold request model classes
request_models: Dict[str, Type[BaseModel]] = {}

# Base request model
class BaseRequestModel(BaseModel):
    ticker: str = Field(..., title="Ticker", description="Stock ticker", example="AAPL")
    api_token: str = Field(..., title="API token", description="API token", example=TEST_TOKEN)

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
tags = {element: Tag(name=element) for element in yf_e.IMPLEMENTED_ELEMENTS}

# Dynamically create and register endpoints
for element in yf_e.IMPLEMENTED_ELEMENTS:
    request_model = create_request_model(element)
    request_models[element] = request_model

    # Create the endpoint function with a unique name using a lambda
    def create_endpoint_func(request_model: Type[BaseRequestModel], element: str):
        def endpoint_func(query:  request_model):
            # Here you can perform authentication with query.api_token
            # Call the get_stock_element function with appropriate parameters
            response = yf_e.get_stock_element(query.ticker, element)
            # make sure you return the response as a dictionary
            # if response is a string, convert it to a dictionary
            if isinstance(response, str):
                response = json.loads(response)
            
            return response
        return endpoint_func

    # Assign a unique name to the endpoint function
    endpoint_func = create_endpoint_func(request_model, element)
    endpoint_func.__name__ = f"endpoint_func_{element}"

    # Register the endpoint with the app, using the Tag object instead of string
    app.get(f'/{element}', summary=f"Endpoint for {element}",
            tags=[tags[element]], responses={200: GenericResponseModel})(endpoint_func)



#%%
if __name__ == '__main__':
    app.run(debug=True)
