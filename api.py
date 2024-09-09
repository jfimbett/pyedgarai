# Imports
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from flask_openapi3 import Info, Tag, OpenAPI
import time

from pyedgarai.pyedgarai import (clean_account_name, get_xbrl_frames, get_company_concept,
                                 get_cik_tickers, return_company_names, get_company_facts,
                                 return_accounts, get_submission_history, return_cik_sic, 
                                 get_companies_with_same_sic)
from pyedgarai.download_sec import get_data

# API Info
info = Info(title="Comparable companies API", version="0.0.1")
app = OpenAPI(__name__, info=info)

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
    name: str = Field(None, description="Name of the account", example="Gross Profit")

class CleanNameResponse(BaseModel):
    clean_name: str = Field(None, description="Cleaned name of the account", example="GrossProfit")

class CIKTickers(BaseModel):
    pass

class CIKTickersResponse(BaseModel):
    cik_tickers: Dict[str, List[str]] = Field(
        None, description="Dictionary where keys are CIKs and values are corresponding tickers",
        example={
            "0000001750": ["AIR"],
            "0000001800": ["ABT"],
            "0000001961": ["WDDD"]
        })

class CIKNames(BaseModel):
    pass

class CIKNamesResponse(BaseModel):
    cik_names: Dict[str, List[str]] = Field(
        None, description="Dictionary where keys are CIKs and values are company names",
        example={
            "0000001750": ["AAR CORP"],
            "0000001800": ["ABBOTT LABORATORIES"],
            "0000001961": ["WORLDS INC"]
        })

class AccountRequest(BaseModel):
    units: str = Field(None, description="Units of the account (e.g., USD, USD-per-share, shares).", example="USD")
    account: str = Field(None, description="Account name", example=clean_names[0])
    frame: str = Field(None, description="Data frame (e.g., year, quarter, add 'I' for instant data).", example="CY2024Q1")
    taxonomy: str = Field(None, description="Account taxonomy (e.g., us-gaap, dei).")

class AccountResponse(BaseModel):
    ccp: str = Field(None, description="Calendar period code (e.g., CY2024Q1)", example="CY2024Q1")
    description: str = Field(None, description="Description of the financial metric.", example="Gross Profit")
    label: str = Field(None, description="Label of the financial metric", example="Gross Profit")
    pts: int = Field(None, description="Point in time for which the data is relevant.", example=2024)
    tag: str = Field(None, description="Tag identifier", example="GrossProfit")
    taxonomy: str = Field(None, description="Taxonomy of the account", example="us-gaap")
    uom: str = Field(None, description="Unit of measurement", example="USD")
    data: List[Dict] = Field(
        None, description="List of data points for different companies",
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
    cik: int = Field(None, description="CIK of the company", example=320193)
    tag: str = Field(None, description="Account name", example=clean_names[1])
    taxonomy: str = Field(None, description="Account taxonomy", example="us-gaap")

class CompanyResponse(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)
    description: str = Field(None, description="Account description", example="Income Tax Expense")
    entityName: str = Field(None, description="Company name", example="Apple Inc.")
    label: str = Field(None, description="Account label", example="Income Tax Expense (Benefit)")
    tag: str = Field(None, description="Account tag", example="IncomeTaxExpenseBenefit")
    taxonomy: str = Field(None, description="Account taxonomy", example="us-gaap")
    units: Dict[str, List[Dict[str, Any]]] = Field(
        None, description="Unit values", example={"USD": [{"accn": "0001193125-10-012091", "val": 1511000000}]})

class CompanyFacts(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)

class CompanyFactsResponse(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)
    entityName: str = Field(None, description="Company name", example="Apple Inc.")
    facts: Dict[str, Dict[str, Any]] = Field(None, description="Company facts")

class SubmissionHistory(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)

class SubmissionHistoryResponse(BaseModel):
    cik: str = Field(None, description="CIK of the company", example="320193")
    entityType: str = Field(None, description="Type of entity", example="operating")
    name: str = Field(None, description="Company name", example="Apple Inc.")
    files: List[Dict] = Field(None, description="Files submitted by the company")

class CIKSIC(BaseModel):
    pass

class CIKSICResponse(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)
    sic: str = Field(None, description="SIC code of the company", example="3571")

class ComparablesSIC(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)

class ComparablesSICResponse(BaseModel):
    pass

# Endpoints

@app.get("/account", summary="Get account data", tags=[account_tag], responses={200: AccountResponse})
def account(query: AccountRequest):
    """Retrieve account data for all companies."""
    frames = get_xbrl_frames(query.taxonomy, clean_account_name(query.account), query.units, query.frame)
    return frames

@app.get("/company_concept", summary="Get company concept", tags=[company_tag], responses={200: CompanyResponse})
def company_concept(query: CompanyRequest):
    """Retrieve account history for a company."""
    return get_company_concept(int(query.cik), query.taxonomy, clean_account_name(query.tag))

@app.get("/cik_tickers", summary="Get CIK tickers", tags=[companies_tag], responses={200: CIKTickersResponse})
def cik_tickers(query: CIKTickers):
    """Get list of CIKs and their corresponding tickers."""
    return get_cik_tickers()

@app.get("/cik_names", summary="Get CIK names", tags=[names_tag], responses={200: CIKNamesResponse})
def cik_names(query: CIKNames):
    """Get list of CIKs and their corresponding company names."""
    return return_company_names()

@app.get("/clean_name", summary="Get cleaned account name", tags=[clean_name_tag], responses={200: CleanNameResponse})
def clean_name(query: CleanName):
    """Get a cleaned account name."""
    return {"clean_name": clean_account_name(query.name)}

@app.get("/company_facts", summary="Get company facts", tags=[company_facts_tag], responses={200: CompanyFactsResponse})
def company_facts(query: CompanyFacts):
    """Get facts of a company."""
    return get_company_facts(int(query.cik))

@app.get("/all_accounts", summary="Get account data for all companies", tags=[all_accounts_tag], responses={200: AccountResponse})
def all_accounts():
    """Retrieve all account data for all companies."""
    return return_accounts()

@app.get("/submission_history", summary="Get submission history", tags=[submission_history_tag], responses={200: SubmissionHistoryResponse})
def submission_history(query: SubmissionHistory):
    """Retrieve submission history of a company."""
    return get_submission_history(int(query.cik))

@app.get("/cik_sic", summary="Get CIK and SIC code", tags=[ciksic_tag], responses={200: CIKSICResponse})
def cik_sic(query: CIKSIC):
    """Get CIK and SIC code of a company."""
    return return_cik_sic()

@app.get("/comparables_sic", summary="Get companies with same SIC", tags=[comparables_sic_tag], responses={200: ComparablesSICResponse})
def comparables_sic(query: ComparablesSIC):
    """Retrieve companies with the same SIC code."""
    return get_companies_with_same_sic(int(query.cik))

if __name__ == '__main__':
    app.run(debug=True)
