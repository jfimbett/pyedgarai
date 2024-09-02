#%%
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
info = Info(title="Comparable companies API", version="0.0.1")

from pyedgarai.pyedgarai import clean_account_name, get_xbrl_frames, get_company_concept
from pyedgarai.pyedgarai import get_cik_tickers, return_company_names, get_company_facts
from pyedgarai.pyedgarai import return_accounts, get_submission_history, return_cik_sic
from pyedgarai.pyedgarai import get_companies_with_same_sic
from pyedgarai.options_api import rapipdf_html_string

app = OpenAPI(__name__, info=info)
#%%
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

# clean account name
clean_names = [clean_account_name(name) for name in accounts]

#%%

account_tag = Tag(name="account",
                  description="Accounting account data for all companies")
company_tag = Tag(name="company", description="Company data")

class CleanName(BaseModel):
    name: str = Field(None, description="Name of the account", example="Gross Profit")
    
class CleanNameResponse(BaseModel):
    clean_name: str = Field(None, description="Cleaned name of the account", example="GrossProfit")

class CIKTickers(BaseModel):
    pass

class CIKNames(BaseModel):
    pass

class CIKAccounts(BaseModel):
    pass

class CIKAccountsResponse(BaseModel):
    pass

class CIKSIC(BaseModel):
    pass

class ComparablesSIC(BaseModel):
    cik : int = Field(None, description="CIK of the company", example=320193)

class ComparablesSICResponse(BaseModel):
    pass

class CIKSICResponse(BaseModel):
    cik : int = Field(None, description="CIK of the company", example=320193)
    sic : str = Field(None, description="SIC code of the company", example="3571")

class CIKNamesResponse(BaseModel):
    cik_names: Dict[str, List[str]] = Field(
        None,
        description=
        "Dictionary where the keys are CIKs and the values are the corresponding company names",
        example = {
                "0000001750": [
                    "AAR CORP"
                ],
                "0000001800": [
                    "ABBOTT LABORATORIES"
                ],
                "0000001961": [
                    "WORLDS INC"
                ]
                        }
                    )

class CIKTickersResponse(BaseModel):
    cik_tickers: Dict[str, List[str]] = Field(
        None,
        description=
        "Dictionary where the keys are CIKs and the values are the corresponding tickers",
        example = {
                "0000001750": [
                    "AIR"
                ],
                "0000001800": [
                    "ABT"
                ],
                "0000001961": [
                    "WDDD"
                ]
                        }
                    )


class AccountRequest(BaseModel):
    units: str = Field(
        None,
        description=
        "Units of the account, can be one of USD, USD-per-share, or shares.",
        example="USD")
    account: str = Field(None,
                         description=f"Account name",
                         example=clean_names[0])
    frame: str = Field(
        None,
        description=
        "Frame of the data (year and quarter), add the letter I at the end for instant data.",
        example="CY2024Q1")
    taxonomy: str = Field(
        None, description="Taxonomy of the account, us-gaap or dei.")


class CompanyRequest(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)
    tag: str = Field(None, description=f"Account name", example=clean_names[1])
    taxonomy: str = Field(None,
                          description="Taxonomy of the account",
                          example="us-gaap")

class CompanyFacts(BaseModel):
    cik : int = Field(None, description="CIK of the company", example=320193)

class CompanyFactsResponse(BaseModel):
    cik : int = Field(None, description="CIK of the company", example=320193)
    entityName: str = Field(None, description="Name of the company", example="Apple Inc.")
    facts : Dict[str, Dict[str, Any]] = Field(None, description="Facts of the company",
                                                         example = {
                                                               "dei": {
      "EntityCommonStockSharesOutstanding": {
        "description": "Indicate number of shares or other units outstanding of each of registrant's classes of capital or common stock or other ownership interests, if and as stated on cover of related periodic report. Where multiple classes or units exist define each class/interest by adding class of stock items such as Common Class A [Member], Common Class B [Member] or Partnership Interest [Member] onto the Instrument [Domain] of the Entity Listings, Instrument.",
        "label": "Entity Common Stock, Shares Outstanding",
        "units": {
          "shares": [
            {
              "accn": "0001193125-09-153165",
              "end": "2009-06-27",
              "filed": "2009-07-22",
              "form": "10-Q",
              "fp": "Q3",
              "frame": "CY2009Q2I",
              "fy": 2009,
              "val": 895816758
            },
            {
              "accn": "0001193125-09-214859",
              "end": "2009-10-16",
              "filed": "2009-10-27",
              "form": "10-K",
              "fp": "FY",
              "fy": 2009,
              "val": 900678473
            }]}}}})


class CompanyResponse(BaseModel):
    cik: int = Field(None,
                     description="CIK (Central Index Key) of the company",
                     example=320193)
    description: str = Field(
        None,
        description="Detailed description of the account requested",
        example=
        "Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations."
    )
    entityName: str = Field(None,
                            description="Name of the company",
                            example="Apple Inc.")
    label: str = Field(
        None,
        description="Human-readable label of the account requested",
        example="Income Tax Expense (Benefit)")
    tag: str = Field(None,
                     description="Tag identifier of the account requested",
                     example="IncomeTaxExpenseBenefit")
    taxonomy: str = Field(
        None,
        description=
        "Taxonomy or classification of the account requested, typically representing a financial standard",
        example="us-gaap")
    units: Dict[str, List[Dict[str, Any]]] = Field(
        None,
        description=
        "Dictionary where the keys represent the units of measurement (e.g., USD), and the values are lists of dictionaries containing the period and the corresponding value. Each dictionary within the list might include fields such as 'start', 'end', and 'value'.",
        example={
            "USD": [{
                "accn": "0001193125-10-012091",
                "end": "2007-09-29",
                "filed": "2010-01-25",
                "form": "10-K/A",
                "fp": "FY",
                "frame": "CY2007",
                "fy": 2009,
                "start": "2006-10-01",
                "val": 1511000000
            }, {
                "accn": "0001193125-09-153165",
                "end": "2008-06-28",
                "filed": "2009-07-22",
                "form": "10-Q",
                "fp": "Q3",
                "fy": 2009,
                "start": "2007-09-30",
                "val": 1615000000
            }]
        })


class AccountResponse(BaseModel):
    ccp: str = Field(
        None,
        description="Calendar period code representing the fiscal period",
        example="CY2024Q1")
    description: str = Field(
        None,
        description="Detailed description of the financial metric",
        example=
        "Aggregate revenue less cost of goods and services sold or operating expenses directly attributable to the revenue generation activity."
    )
    label: str = Field(
        None,
        description="Human-readable label of the financial metric",
        example="Gross Profit")
    pts: int = Field(
        None,
        description=
        "Point in time for which the data is relevant (e.g., fiscal year or quarter)",
        example=1967)
    tag: str = Field(None,
                     description="Tag identifier of the financial metric",
                     example="GrossProfit")
    taxonomy: str = Field(
        None,
        description=
        "Taxonomy or classification under which the financial metric is reported, typically representing a financial standard",
        example="us-gaap")
    uom: str = Field(
        None,
        description="Unit of measurement for the financial metric",
        example="USD")
    data: List[Dict] = Field(
        None,
        description=
        "List of data items, each representing a value for a specific company over a specific period",
        example=[{
            "accn": "0001104659-24-037408",
            "cik": 1750,
            "end": "2024-02-29",
            "entityName": "AAR CORP",
            "loc": "US-IL",
            "start": "2023-12-01",
            "val": 110300000
        }, {
            "accn": "0000950170-24-055586",
            "cik": 2098,
            "end": "2024-03-31",
            "entityName": "ACME UNITED CORP",
            "loc": "US-CT",
            "start": "2024-01-01",
            "val": 17396000
        }])


class SubmissionHistory(BaseModel):
    cik: int = Field(None, description="CIK of the company", example=320193)

# Example usage
response_data = {
    'cik': '320193',
    'entityType': 'operating',
    'sic': '3571',
    'sicDescription': 'Electronic Computers',
    'insiderTransactionForOwnerExists': 0,
    'insiderTransactionForIssuerExists': 1,
    'name': 'Apple Inc.',
    'tickers': ['AAPL'],
    'exchanges': ['Nasdaq'],
    'ein': '942404110',
    'description': '',
    'website': '',
    'investorWebsite': '',
    'category': 'Large accelerated filer',
    'fiscalYearEnd': '0928',
    'stateOfIncorporation': 'CA',
    'stateOfIncorporationDescription': 'CA',
    'addresses': {
        'mailing': {
            'street1': 'ONE APPLE PARK WAY',
            'street2': None,
            'city': 'CUPERTINO',
            'stateOrCountry': 'CA',
            'zipCode': '95014',
            'stateOrCountryDescription': 'CA'
        },
        'business': {
            'street1': 'ONE APPLE PARK WAY',
            'street2': None,
            'city': 'CUPERTINO',
            'stateOrCountry': 'CA',
            'zipCode': '95014',
            'stateOrCountryDescription': 'CA'
        }
    },
    'files': [
        {
            'name': 'CIK0000320193-submissions-001.json',
            'filingCount': 1075,
            'filingFrom': '1994-01-26',
            'filingTo': '2014-02-03'
        }
    ]
}

class Address(BaseModel):
    street1: str = Field(None, description="First line of the address", example="ONE APPLE PARK WAY")
    street2: Optional[str] = Field(None, description="Second line of the address")
    city: str = Field(None, description="City of the address", example="CUPERTINO")
    stateOrCountry: str = Field(None, description="State or country of the address", example="CA")
    zipCode: str = Field(None, description="Zip code of the address", example="95014")
    stateOrCountryDescription: str = Field(None, description="Description of the state or country", example="CA")

class Addresses(BaseModel):
    mailing: Address = Field(None, description="Mailing address")
    business: Address = Field(None, description="Business address")

class File(BaseModel):
    name: str = Field(None, description="Name of the file", example="CIK0000320193-submissions-001.json")
    filingCount: int = Field(None, description="Number of filings", example=1075)
    filingFrom: str = Field(None, description="Date of the first filing", example="1994-01-26")
    filingTo: str = Field(None, description="Date of the last filing", example="2014-02-03")

class SubmissionHistoryResponse(BaseModel):
    cik: str = Field(None, description="CIK of the company", example="320193")
    entityType: str = Field(None, description="Type of entity", example="operating")
    sic: str = Field(None, description="Standard Industrial Classification (SIC) code", example="3571")
    sicDescription: str = Field(None, description="Description of the SIC code", example="Electronic Computers")
    insiderTransactionForOwnerExists: int = Field(None, description="Indicates if an insider transaction for the owner exists", example=0)
    insiderTransactionForIssuerExists: int = Field(None, description="Indicates if an insider transaction for the issuer exists", example=1)
    name: str = Field(None, description="Name of the company", example="Apple Inc.")
    tickers: List[str] = Field(None, description="List of tickers", example=["AAPL"])
    exchanges: List[str] = Field(None, description="List of exchanges", example=["Nasdaq"])
    ein: str = Field(None, description="Employer Identification Number (EIN)", example="942404110")
    description: Optional[str] = Field(None, description="Description of the company")
    website: Optional[str] = Field(None, description="Website of the company")
    investorWebsite: Optional[str] = Field(None, description="Investor website of the company")
    category: str = Field(None, description="Category of the company", example="Large accelerated filer")
    fiscalYearEnd: str = Field(None, description="Fiscal year end", example="0928")
    stateOfIncorporation: str = Field(None, description="State of incorporation", example="CA")
    stateOfIncorporationDescription: str = Field(None, description="Description of the state of incorporation", example="CA")
    addresses: Addresses = Field(None, description="Addresses of the company")
    files: List[File] = Field(None, description="List of files")

# endpoint for account
@app.get("/account",
         summary="Get all accounts",
         tags=[account_tag],
         responses={
             200: AccountResponse,
             204: None,
             422: None
         })
def account(query: AccountRequest):
    """account

    Gets the same account variable for all companies

    localhost:5000/account?units=USD&account=GrossProfit&frame=CY2024Q1&taxonomy=us-gaap
    """
    # retrieve units and account
    units = query.units
    account = query.account
    frame = query.frame
    taxonomy = query.taxonomy
    account = clean_account_name(account)
    frames = get_xbrl_frames(taxonomy, account, units, frame)
    return frames


@app.get("/company_concept",
         summary="Get Company",
         tags=[company_tag],
         responses={
             200: CompanyResponse,
             204: None,
             422: None
         })
def company_concept(query: CompanyRequest):
    """company

    Gets the history of a specific account for a company

    localhost:5000/company?cik=320193&tag=IncomeTaxExpenseBenefit&taxonomy=us-gaap

    """
    # wrap get_company_concept(cik: int, taxonomy: str, tag: str)
    cik = query.cik
    # to int
    cik = int(cik)
    taxonomy = query.taxonomy
    tag = query.tag
    tag = clean_account_name(tag)
    return get_company_concept(cik, taxonomy, tag)

companies_tag = Tag(name="companies", description="Companies data")
@app.get("/cik_tickers", 
         summary="Get CIK tickers", 
         tags=[companies_tag],
          responses = {
                        200: CIKTickersResponse,
                        204: None,
                        422: None
                    })
def cik_tickers(query: CIKTickers):
    """cik_tickers

    Gets a list of CIKs and their corresponding tickers

    localhost:5000/cik_tickers
    """
    return get_cik_tickers()

names_tags = Tag(name="names", description="Company names")
@app.get("/cik_names", 
         summary="Get CIK names", 
         tags=[names_tags],
          responses = {
                        200: CIKNamesResponse,
                        204: None,
                        422: None
                    })
def cik_names(query: CIKNames):
    """cik_names

    Gets a list of CIKs and their corresponding company names

    localhost:5000/cik_names
    """
    return return_company_names()

clean_name = Tag(name="clean_name", description="Cleaned account name")
@app.get("/clean_name", 
         summary="Get cleaned account name", 
         tags=[clean_name],
          responses = {
                        200: CleanNameResponse,
                        204: None,
                        422: None
                    })
def clean_name(query: CleanName):
    """clean_name

    Gets a cleaned account name

    localhost:5000/clean_name?name=Gross%20Profit
    """
    return {"clean_name": clean_account_name(query.name)}

company_facts = Tag(name="company_facts", description="Company facts")
@app.get("/company_facts", 
         summary="Get company facts", 
         tags=[company_facts],
          responses = {
                        200: CompanyFactsResponse,
                        204: None,
                        422: None
                    })
def company_facts(query: CompanyFacts):
    """company_facts

    Gets a list of CIKs and their corresponding company names

    localhost:5000/company_facts?cik=320193
    """
    cik = int(query.cik)
    return get_company_facts(cik)


def auxiliar_create_doc_facts():
    cik = 320193
    dict_ =  get_company_facts(cik)

    dei = dict_["facts"]["dei"]
    us_gaap = dict_["facts"]["us-gaap"]

    # keep only the first two keys of each one 
    dei = {k: dei[k] for k in list(dei)[:2]}
    us_gaap = {k: us_gaap[k] for k in list(us_gaap)[:2]}

    dict_["facts"]["dei"] = dei
    dict_["facts"]["us-gaap"] = us_gaap

    print(dict_)

# return the account data 
all_accounts = Tag(name="accounts", description="All accounts data")
@app.get("/all_accounts", 
         summary="Get account data", 
         tags=[account_tag],
          responses = {
                        200: AccountResponse,
                        204: None,
                        422: None
                    })
def all_accounts():
    """all_accounts

    Gets the history of all accounts for all companies

    localhost:5000/all_accounts
    """
    return return_accounts()

submission_history_tag = Tag(name="submission_history", description="Submission history")
@app.get("/submission_history", 
         summary="Get submission history", 
         tags=[submission_history_tag],
          responses = {
                        200: SubmissionHistoryResponse,
                        204: None,
                        422: None
                    })
def submission_history(query: SubmissionHistory):
    """submission_history

    Gets the submission history of a company

    localhost:5000/submission_history?cik=320193
    """
    cik = int(query.cik)
    return get_submission_history(cik)

ciksic_tag = Tag(name="cik_sic", description="CIK SIC")
@app.get("/cik_sic", 
         summary="Get CIK SIC", 
         tags=[ciksic_tag],
          responses = {
                        200: CIKSICResponse,
                        204: None,
                        422: None
                    })
def cik_sic(query: CIKSIC):
    """cik_sic

    Gets the CIK and SIC code of a company

    localhost:5000/cik_sic
    """
    return return_cik_sic()

comparables_sic = Tag(name="comparables_sic", description="Comparables with same SIC")
@ app.get("/comparables_sic", 
         summary="Get comparables with same SIC", 
         tags=[comparables_sic],
          responses = {
                        200: ComparablesSICResponse,
                        204: None,
                        422: None
                    })
def comparables_sic(query: ComparablesSIC):
    """comparables_sic

    Gets the comparables with the same SIC code

    localhost:5000/comparables_sic?cik=320193
    """
    cik = int(query.cik)
    return get_companies_with_same_sic(cik)

if __name__ == '__main__':
    app.run(debug=True)
