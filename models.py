from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

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

class StockDataRequest(BaseModel):
    tickers: List[str] = Field( description="List of tickers", example=["AAPL", "MSFT"])
    start_date: str = Field( description="Start date", example="2024-01-01")
    end_date: str = Field( description="End date", example="2024-12-31")

class StockDataResponse(BaseModel):
    # returns a dataframe converted to json
    data: List[Dict] = Field( description="Stock data for the given tickers")