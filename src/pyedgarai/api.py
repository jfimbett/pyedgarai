#%%
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
info = Info(title="Comparable companies API", version="0.0.1")

from pyedgarai import clean_account_name, get_xbrl_frames, get_company_concept
from options_api import rapipdf_html_string

app = OpenAPI(__name__, info=info)
#%%
accounts = ["Net Income (Loss) Attributable to Parent",
"Accumulated Other Comprehensive Income (Loss), Net of Tax",
"Earnings Per Share, Basic",
"Earnings Per Share, Diluted",
"Gross Profit",
"Income (Loss) from Continuing Operations, Per Diluted Share",
"Net Income (Loss), Including Portion Attributable to Noncontrolling Interest",
"Stockholders' Equity, Including Portion Attributable to Noncontrolling Interest",
"Income (Loss) from Continuing Operations, Per Basic Share",
"Interest Expense",
"Selling, General and Administrative Expense"]

# clean account name
clean_names = [clean_account_name(name) for name in accounts]

#%%


account_tag = Tag(name="account", description="Accounting account data for all companies") 
company_tag = Tag(name="company", description="Company data")

class AccountRequest(BaseModel):
    units: str = Field(None,description="Units of the account, can be one of USD, USD-per-share, or shares.", example="USD")
    account: str = Field(None,description=f"Account name", example = clean_names[0])
    frame: str = Field(None,description="Frame of the data (year and quarter), add the letter I at the end for instant data.", example="CY2024Q1")
    taxonomy: str = Field(None,description="Taxonomy of the account, us-gaap or dei.")

class CompanyRequest(BaseModel):
    cik: int = Field(None,description="CIK of the company", example=320193)
    tag: str = Field(None,description=f"Account name", example = clean_names[1])
    taxonomy: str = Field(None, description="Taxonomy of the account", example="us-gaap")

from pydantic import BaseModel, Field
from typing import Dict, List, Any

class CompanyResponse(BaseModel):
    cik: int = Field(None, description="CIK (Central Index Key) of the company", example=320193)
    description: str = Field(None, description="Detailed description of the account requested", example="Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.")
    entityName: str = Field(None, description="Name of the company", example="Apple Inc.")
    label: str = Field(None, description="Human-readable label of the account requested", example="Income Tax Expense (Benefit)")
    tag: str = Field(None, description="Tag identifier of the account requested", example="IncomeTaxExpenseBenefit")
    taxonomy: str = Field(None, description="Taxonomy or classification of the account requested, typically representing a financial standard", example="us-gaap")
    units: Dict[str, List[Dict[str, Any]]] = Field(
        None,
        description="Dictionary where the keys represent the units of measurement (e.g., USD), and the values are lists of dictionaries containing the period and the corresponding value. Each dictionary within the list might include fields such as 'start', 'end', and 'value'.",
        example={
            "USD": [
                {  "accn": "0001193125-10-012091",
                    "end": "2007-09-29",
                    "filed": "2010-01-25",
                    "form": "10-K/A",
                    "fp": "FY",
                    "frame": "CY2007",
                    "fy": 2009,
                    "start": "2006-10-01",
                    "val": 1511000000},
                { "accn": "0001193125-09-153165",
                        "end": "2008-06-28",
                        "filed": "2009-07-22",
                        "form": "10-Q",
                        "fp": "Q3",
                        "fy": 2009,
                        "start": "2007-09-30",
                        "val": 1615000000}
            ]
        }
    )


class AccountResponse(BaseModel):
    ccp: str = Field(None, description="Calendar period code representing the fiscal period", example="CY2024Q1")
    description: str = Field(None, description="Detailed description of the financial metric", example="Aggregate revenue less cost of goods and services sold or operating expenses directly attributable to the revenue generation activity.")
    label: str = Field(None, description="Human-readable label of the financial metric", example="Gross Profit")
    pts: int = Field(None, description="Point in time for which the data is relevant (e.g., fiscal year or quarter)", example=1967)
    tag: str = Field(None, description="Tag identifier of the financial metric", example="GrossProfit")
    taxonomy: str = Field(None, description="Taxonomy or classification under which the financial metric is reported, typically representing a financial standard", example="us-gaap")
    uom: str = Field(None, description="Unit of measurement for the financial metric", example="USD")
    data: List[Dict] = Field(
        None,
        description="List of data items, each representing a value for a specific company over a specific period",
        example=[
            {
                "accn": "0001104659-24-037408",
                "cik": 1750,
                "end": "2024-02-29",
                "entityName": "AAR CORP",
                "loc": "US-IL",
                "start": "2023-12-01",
                "val": 110300000
            },
            {
                "accn": "0000950170-24-055586",
                "cik": 2098,
                "end": "2024-03-31",
                "entityName": "ACME UNITED CORP",
                "loc": "US-CT",
                "start": "2024-01-01",
                "val": 17396000
            }
        ]
    )


# endpoint for account 
@app.get("/account", summary="Get all accounts", tags=[account_tag], responses = {200 : AccountResponse, 204 : None, 422 : None})
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

@app.get("/company", summary="Get Company", tags=[company_tag], responses = {200 : CompanyResponse, 204 : None, 422 : None})
def company(query: CompanyRequest):
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

# test e.g. using 0000320193 and Income Tax Expense (Benefit)
# http://localhost:5000/company?cik=320193&tag=IncomeTaxExpenseBenefit&taxonomy=us-gaap&frame=CY2024Q1

# test e.g. using GrossProfit and USD
# http://localhost:5000/account?units=USD&account=GrossProfit&frame=CY2024Q1&taxonomy=us-gaap

if __name__ == '__main__':
    app.run(debug=True)