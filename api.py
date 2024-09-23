# Imports
#%%
from flask_openapi3 import Info, Tag, OpenAPI
from version import version

from models import (AccountRequest, AccountResponse, CompanyRequest, CompanyResponse, CIKTickers, CIKTickersResponse,
                    CIKNames, CIKNamesResponse, CleanName, CleanNameResponse, CompanyFacts, CompanyFactsResponse,
                    SubmissionHistory, SubmissionHistoryResponse, CIKSIC, CIKSICResponse, ComparablesSIC, ComparablesSICResponse,
                    StoredData, StoredDataResponse, StockDataRequest, StockDataResponse) 

from pyedgarai.pyedgarai import (clean_account_name, get_xbrl_frames, get_company_concept,
                                 get_cik_tickers, return_company_names, get_company_facts,
                                 return_accounts, get_submission_history, return_cik_sic, 
                                 get_companies_with_same_sic,
                                 get_stocks_data)
from pyedgarai.download_sec import get_data

# API Info
info = Info(title="Comparable companies API", version=version)
app = OpenAPI(__name__, info=info)


# decorator for api token
TEST_TOKEN = "t3stt@ken"
def authenticate(api_token: str = None):
    if api_token != TEST_TOKEN:
        return False
    return True

# Predefined accounts list
accounts = [
    "Net Income (Loss) Attributable to Parent",
    "Accumulated Other Comprehensive Income (Loss), Net of Tax",
    "Earnings Per Share, Basic", "Earnings Per Share, Diluted", "Gross Profit",
    "Income (Loss) from Continuing Operations, Per Diluted Share",
    "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest",
    "Stockholders' Equity, Including Portion Attributable to Noncontrolling Interest",
    "Income (Loss) from Continuing Operations, Per Basic Share",
    "Interest Expense", "Selling, General and Administrative Expense"
]

# Clean account names
clean_names = [clean_account_name(name) for name in accounts]

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
def all_accounts():
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
    df = get_stocks_data(query.tickers)
    data = df.to_dict(orient='list')
    return {"data": data}

#%%
if __name__ == '__main__':
    app.run(debug=True)
