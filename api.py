# Imports
#%%
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from flask_openapi3 import Info, Tag, OpenAPI
from version import version
import time

from pyedgarai.pyedgarai import (clean_account_name, get_xbrl_frames, get_company_concept,
                                 get_cik_tickers, return_company_names, get_company_facts,
                                 return_accounts, get_submission_history, return_cik_sic, 
                                 get_companies_with_same_sic)
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

# Models

class CleanName(BaseModel):
    name: str = Field( description="Name of the account", example="Gross Profit")
    api_token : str = Field( description="API token")

class CleanNameResponse(BaseModel):
    clean_name: str = Field( description="Cleaned name of the account", example="GrossProfit")
    api_token : str = Field( description="API token")

class CIKTickers(BaseModel):
    api_token : str = Field( description="API token")

class CIKTickersResponse(BaseModel):
    cik_tickers: Dict[str, List[str]] = Field(
       description="Dictionary where keys are CIKs and values are corresponding tickers",
        example={
            "0000001750": ["AIR"],
            "0000001800": ["ABT"],
            "0000001961": ["WDDD"]
        })

class CIKNames(BaseModel):
    api_token : str = Field( description="API token")

class CIKNamesResponse(BaseModel):
    cik_names: Dict[str, List[str]] = Field(
         description="Dictionary where keys are CIKs and values are company names",
        example={
            "0000001750": ["AAR CORP"],
            "0000001800": ["ABBOTT LABORATORIES"],
            "0000001961": ["WORLDS INC"]
        })

class AccountRequest(BaseModel):
    units: str = Field( description="Units of the account (e.g., USD, USD-per-share, shares).", example="USD")
    account: str = Field( description="Account name", example=clean_names[0])
    frame: str = Field( description="Data frame (e.g., year, quarter, add 'I' for instant data).", example="CY2024Q1")
    taxonomy: str = Field( description="Account taxonomy (e.g., us-gaap, dei).")
    api_token : str = Field( description="API token")

class AccountResponse(BaseModel):
    ccp: str = Field( description="Calendar period code (e.g., CY2024Q1)", example="CY2024Q1")
    description: str = Field( description="Description of the financial metric.", example="Gross Profit")
    label: str = Field( description="Label of the financial metric", example="Gross Profit")
    pts: int = Field( description="Point in time for which the data is relevant.", example=2024)
    tag: str = Field( description="Tag identifier", example="GrossProfit")
    taxonomy: str = Field( description="Taxonomy of the account", example="us-gaap")
    uom: str = Field( description="Unit of measurement", example="USD")
    data: List[Dict] = Field(
       description="List of data points for different companies",
        example=[{
            "accn": "0001104659-24-037408",
            "cik": 1750,
            "end": "2024-02-29",
            "entityName": "AAR CORP",
            "loc": "US-IL",
            "start": "2023-12-01",
            "val": 110300000
        }])

class CompanyRequest(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    tag: str = Field( description="Account name", example=clean_names[1])
    taxonomy: str = Field( description="Account taxonomy", example="us-gaap")
    api_token : str = Field( description="API token")

class CompanyResponse(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    description: str = Field( description="Account description", example="Income Tax Expense")
    entityName: str = Field( description="Company name", example="Apple Inc.")
    label: str = Field( description="Account label", example="Income Tax Expense (Benefit)")
    tag: str = Field( description="Account tag", example="IncomeTaxExpenseBenefit")
    taxonomy: str = Field( description="Account taxonomy", example="us-gaap")
    units: Dict[str, List[Dict[str, Any]]] = Field(
       description="Unit values", example={"USD": [{"accn": "0001193125-10-012091", "val": 1511000000}]})

class CompanyFacts(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    api_token : str = Field( description="API token")

class CompanyFactsResponse(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    entityName: str = Field( description="Company name", example="Apple Inc.")
    facts: Dict[str, Dict[str, Any]] = Field( description="Company facts")

class SubmissionHistory(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    api_token : str = Field( description="API token")

class SubmissionHistoryResponse(BaseModel):
    cik: str = Field( description="CIK of the company", example="320193")
    entityType: str = Field( description="Type of entity", example="operating")
    name: str = Field( description="Company name", example="Apple Inc.")
    files: List[Dict] = Field( description="Files submitted by the company")

class CIKSIC(BaseModel):
    api_token : str = Field( description="API token")

class CIKSICResponse(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    sic: str = Field( description="SIC code of the company", example="3571")

class ComparablesSIC(BaseModel):
    cik: int = Field( description="CIK of the company", example=320193)
    api_token : str = Field( description="API token")

class ComparablesSICResponse(BaseModel):
    pass

class StoredData(BaseModel):
    ciks: List[int] = Field(description="List of CIKs", example=[320193, 1750])
    accounts: List[str] = Field( description="List of accounts", example=["Net Income (Loss) Attributable to Parent", "Gross Profit"])
    api_token : str = Field( description="API token")

class StoredDataResponse(BaseModel):
    # Its a dataframe converted to json 
    data: List[Dict] = Field( description="Data for the given CIKs and accounts")

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

@app.get("/stored_data", summary="Stored data", responses={200: StoredDataResponse})
def stored_data(query: StoredData):
    """Stored data for the given CIKs and accounts."""
    if not authenticate(query.api_token):
        return {"error": "Invalid API token."}
    ciks = query.ciks
    accounts = query.accounts

    # clean account names 
    accounts = [clean_account_name(name) for name in accounts]
    df = get_data(ciks, accounts)

    # pass each column as a list in a value of a dictionary
    data = df.to_dict(orient='list')

    return {"data": data}

#%%
if __name__ == '__main__':
    app.run(debug=True)
