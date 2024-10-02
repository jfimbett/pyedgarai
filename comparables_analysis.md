# Comparables Analysis Module

## Instructions

Confidential, for internal use only. Do not distribute.

**Description**: This module provides the user the ability to *compare* public companies to a target company. 


**Note for the developer**: Most functionality will be provided by an API that handles the data querying and processing. For completeness we provide the exact API endpoints that we believe are required for each task. All API endpoints require a `api_token` parameter which for testing puroses is set to `t3stt@ken` and is ignored in the examples for simplicity. The full documentation of the API as well as an interface for testing is available at 
https://pyedgarai-jfimbett.replit.app/openapi
### Identification of firms to compare. 

#### Task 1: Search bar for firms

The first requirement of the module is a search bar for firms, using different type of identifiers (CIK, ticker, name, etc…) via which the user selects a company for which the comparables will be retrieved. This implies a connection to the API endpoint of the backend. There are two API endpoints necessary for this task: `/cik_tickers`, and `/cik_names`. Apart from the `api_token` these endpoints do not require any additional parameter. 

Example:
```bash 
curl -X 'GET' \
  'https://pyedgarai-jfimbett.replit.app/cik_tickers?api_token=t3stt%40ken' \
  -H 'accept: application/json'
```

Response
```json
{
"0000012040": [
    "BDL"
  ],
  "0000012208": [
    "BIO",
    "BIO-B"
  ],
  "0000012239": [
    "DOMH"
  ],
  "0000012659": [
    "HRB"
  ],
  "0000012927": [
    "BA"
  ],
  "0000013156": [
    "GLXZ"
  ],
  "0000013372": [
    "NSARP",
    "NSARO"
  ],
  "0000014177": [
    "BRID"
  ],
  "0000014272": [
    "BMYMP",
    "BMY",
    "CELG-RI"
  ],
  "0000014693": [
    "BF-A",
    "BF-B"
  ],
  "0000014707": [
    "CAL"
  ],
  "0000014846": [
    "BRT"
  ],
  "0000014930": [
    "BC-PB",
    "BC-PC",
    "BC",
    "BC-PA"
  ],
}
```
where the keys are the CIKS (treated as strings with leading zeros) and the values are lists of tickers. Note how one CIK can have multiple tickers, this happens when a company has different classes of shares.

Equivalently for the `/cik_names` endpoint the response is a dictionary with the keys being the CIKs (without the leading zeros) and the values being the names of the companies.

```bash
curl -X 'GET' \
  'https://pyedgarai-jfimbett.replit.app/cik_names?api_token=t3stt%40ken' \
  -H 'accept: application/json'
```
Response
```json
{
  "1750": "AAR CORP",
  "1800": "ABBOTT LABORATORIES",
  "1961": "WORLDS INC.",
  "2098": "ACME UNITED CORP",
  "2178": "ADAMS RESOURCES & ENERGY, INC.",
  "2186": "BK Technologies Corporation",
  ...
}
```

The module can perform a request to both endpoints and with the information queried to provide the user with a search bar that can search by CIK, ticker, or company name. The search bar should be able to autocomplete the search query. We require a single input for the search bar that accepts the three types of identifiers, and the user should be able to select the company from the search bar. In the options, provide the complete name of the company, the ticker, and the CIK.

#### Task 2: Add a new company for comparable search. 


If the user wants to add his own company (that is not part of the database) a new section should open where the user can either import data from a document (this functionality will be provided by another module and it is not required at the moment) or input data for the new firm. The user should be able to input the basic information of the company (name), and select the industry and specific accounting variables to fill. The variables that the user can choose to fill are provided in endpoint `/all_accounts`. An example of the response of this endpoint is provided below:

```bash
curl -X 'GET' \
  'https://pyedgarai-jfimbett.replit.app/all_accounts?api_token=t3stt%40ken' \
  -H 'accept: application/json'
```

```json
{
  "AccountsPayableCurrent": {
    "description": "Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the current portion of the liabilities (due within one year or within the normal operating cycle if longer).",
    "instant": 1,
    "name": "Accounts Payable, Current",
    "taxonomy": "us-gaap",
    "units": "USD"
  },
  "AccountsReceivableAfterAllowanceForCreditLossCurrent": {
    "description": "Amount, after allowance for credit loss, of right to consideration from customer for product sold and service rendered in normal course of business, classified as current.",
    "instant": 1,
    "name": "Accounts Receivable, after Allowance for Credit Loss, Current",
    "taxonomy": "us-gaap",
    "units": "USD"
  },
  "AccountsReceivableAllowanceForCreditLossCurrent": {
    "description": "Amount of allowance for credit loss on accounts receivable, classified as current.",
    "instant": 1,
    "name": "Accounts Receivable, Allowance for Credit Loss, Current",
    "taxonomy": "us-gaap",
    "units": "USD"
  },
  ...
}
```

The user should be able to select the variables that he wants to fill, and search for them by typing in the search bar. The search bar should be able to autocomplete the search query or to provide a list of possible variables that the user can select. 

The companies added by the user should be stored inside of the website and should be available for the user to select in the future. However, these companies should not be stored in the database of the API, since we do not have a way to verify the data input by the user.

### Identification of comparables model:

 A dropdown menu where the user selects a method for choosing the comparables (also chooses how many comparables to show). For the moment the developer can have a dropdown menu with the following ***methods*** available:
- Automatic
- LLM

However for the moment the API only has implemented one method, the Automatic method. The output of all methods have the same format, so for the moment there is no need to send the method to the API.

#### Comparable selection of variables
When computing comparable firms, the user should be able to select a subset of variables from the following list:
- industry
- size
- profitability
- growth_rate 
- capital_structure
- location

Finally there are some optional parameters that the user can select:

- industry_digits: The number of digits to consider when comparing the industry. For example, if the user selects 2, the industry will be compared at the 2-digit SIC level.
- size_interval: Interval in % to consider similar companies, e.g. 100. 
- profitability_interval: Interval in % to consider similar companies, e.g. 100.
- growth_rate_interval: Interval in % to consider similar companies, e.g. 100.
- capital_structure_interval: Interval in % to consider similar companies, e.g. 100.
- location: Parameter not yet implemented in the API, but the user should be able to select one of the following:
  - state_level
  - country_level
  - region_level

Example of the API endpoint for the list of comparables:

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/comparables?cik=320193&variables_to_compare=industry&variables_to_compare=size&variables_to_compare=profitability&variables_to_compare=growth_rate&variables_to_compare=capital_structure&variables_to_compare=location&method=kmeans&api_token=t3stt%40ken&industry_digits=2&size_interval=200&profitability_interval=200&growth_rate_interval=200&capital_structure_interval=200' \
  -H 'accept: application/json'
```

Response:
```json
{
  "accn": {
    "0": "0000320193-24-000069"
  },
  "accn_x": {
    "0": "0000320193-24-000069"
  },
  "accn_y": {
    "0": "0000320193-24-000069"
  },
  "assets": {
    "0": 337411000000
  },
  "assets_5": {
    "0": 341998000000
  },
  "cik": {
    "0": 320193
  },
  "debt_to_equity": {
    "0": 3.5476857967
  },
  "end": {
    "0": "2024-03-30"
  },
  "end_x": {
    "0": "2024-03-30"
  },
  "end_y": {
    "0": "2024-03-30"
  },
  "entityName": {
    "0": "Apple Inc."
  },
  "entityName_x": {
    "0": "Apple Inc."
  },
  "entityName_y": {
    "0": "Apple Inc."
  },
  "equity": {
    "0": 74194000000
  },
  "growth_rate": {
    "0": -0.0134123591
  },
  "liabilities": {
    "0": 263217000000
  },
  "loc": {
    "0": "US-CA"
  },
  "loc_x": {
    "0": "US-CA"
  },
  "loc_y": {
    "0": "US-CA"
  },
  "name": {
    "0": "Apple Inc."
  },
  "profit": {
    "0": 23636000000
  },
  "profitability": {
    "0": 0.0700510653
  },
  "sic": {
    "0": 35
  },
  "start": {
    "0": "2023-12-31"
  },
  "state": {
    "0": "CA"
  },
  "tickers": {
    "0": [
      "AAPL"
    ]
  },
  "val": {
    "0": 337411000000
  }
}
```

Identification of variables to be shown in the output:

 When showing information about the comparables, the user should be able to select the variables that he wants to see. These variables should be selected from the same list of variables that the user can select when adding a new company. 


