#%%
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import json
from dataclasses import dataclass
try:
    from openai import OpenAI  # optional
except Exception:  # ImportError or runtime env issues
    OpenAI = None
import pandas as pd
import time
from sec_cik_mapper import StockMapper
from requests.exceptions import HTTPError
import yfinance as yf
import logging
import re
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)

FAKE_CIK = 00000

# Determine cache directory for generated artifacts (json, xlsx)
def _get_cache_dir() -> str:
    # Allow override via env var
    env = os.getenv("PYEDGARAI_CACHE_DIR")
    if env:
        Path(env).mkdir(parents=True, exist_ok=True)
        return env if env.endswith('/') else env + '/'
    # Default: ~/.cache/pyedgarai on Unix/macOS
    default = os.path.join(Path.home(), ".cache", "pyedgarai")
    Path(default).mkdir(parents=True, exist_ok=True)
    return default + "/" if not default.endswith('/') else default

RELATIVE_PATH = _get_cache_dir()  # used throughout to read/write cache files
DATA_PATH = "data/"

# Set up HTTP headers for requests to the SEC API
HEADERS = {"User-Agent": "pyedgarai (github.com/jfimbett/pyedgarai)"}
# Get a list of CIKs from the StockMapper, remove leading zeros, and convert to integers
CIKS = list(StockMapper().cik_to_tickers.keys())
CIKS = [int(str(cik).lstrip('0')) for cik in CIKS]

# download from yfinance data from a list of tickers 
def get_stock_data(ticker, start_date, end_date):
    """get_stock_data retrieves historical data on prices for a given stock

    Args:
        ticker (str): The stock ticker
        start_date (str): Start date in the format 'YYYY-MM-DD'
        end_date (str): End date in the format 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: A pandas dataframe with the historical data

    Example:
        df = get_stock_data('AAPL', '2000-01-01', '2020-12-31')
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, auto_adjust=False, actions=False)
    # as dataframe 
    df = pd.DataFrame(data)
    df['ticker'] = ticker
    df.reset_index(inplace=True)
    return df

def get_stocks_data(tickers, start_date, end_date):
    """get_stocks_data retrieves historical data on prices for a list of stocks

    Args:
        tickers (list): List of stock tickers
        start_date (str): Start date in the format 'YYYY-MM-DD'
        end_date (str): End date in the format 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: A pandas dataframe with the historical data

    Example:
        df = get_stocks_data(['AAPL', 'MSFT'], '2000-01-01', '2020-12-31')
    """
    # get the data for each stock
    # try/except to avoid errors when a stock is not found
    dfs = []
    for ticker in tickers:
        try:
            df = get_stock_data(ticker, start_date, end_date)
            # append if not empty
            if not df.empty:
                dfs.append(df)
        except:
            logging.warning(f"Stock {ticker} not found")
    # concatenate all dataframes
    data = pd.concat(dfs)
    return data

# function that returns a dictionary of cik to company names, store it in a csv file 
# use company facts function
def get_cik_company_names(relative_path = RELATIVE_PATH):
    dict_ = {}
    for cik in tqdm(CIKS):
        try:
            dict_[cik] = get_company_facts(cik)['entityName']
        except:
            continue
    # save as json 
    with open(f'{relative_path}cik_company_names.json', 'w') as f:
        json.dump(dict_, f)

def return_company_names(relative_path = RELATIVE_PATH):
    with open(f'{relative_path}cik_company_names.json', 'r') as f:
        dict_ = json.load(f)
    return dict_

def return_accounts():
    df = pd.read_excel('data/subset_accounts.xlsx')
    names = df['account'].tolist()
    clean_names = df['account'].apply(clean_account_name).tolist()
    description = df['description'].tolist()
    units = df['units'].tolist()
    taxonomy = df['taxonomy'].tolist()
    instant = df['instant'].tolist()

    dict_ = {clean_names[i] : {'name': names[i], 'description': description[i], 'units': units[i], 'taxonomy': taxonomy[i], 'instant': instant[i]} for i in range(len(names))}
    return dict_

# get the cik_to_ticker dictionary
def get_cik_tickers():
    dict_ = StockMapper().cik_to_tickers
    # values are sets so convert to list
    for k, v in dict_.items():
        dict_[k] = list(v)  
    return dict_

class Options():
    """Placeholder class for potential future configurations."""
    pass

@dataclass
class OpenAIWrapper():
    """A wrapper class to interact with OpenAI's API for standardizing SEC filing descriptions."""
    model: str
    api_key: str

    def create_client(self):
        """Creates and returns an OpenAI client using the provided API key."""
        if OpenAI is None:
            raise ImportError("openai is not installed. Install with `pip install pyedgarai[llm]`." )
        return OpenAI(api_key=self.api_key)
    
    def standardize_filing_description(self, description, client, model):
        """
        Standardizes the description of an SEC filing using OpenAI's API.

        Args:
            description (str): The original description of the SEC filing.
            client (OpenAI): The OpenAI client instance.
            model (str): The OpenAI model to be used for the request.

        Returns:
            str: A JSON object containing the original description and the standardized description.
        """
        client = self.create_client()

        relevant_sec_filings = ["Form S-1", "Form 10-K", "Form 10-Q", "Form 8-K", 
                                "DEF 14A", "Form 3", "Form 4", "Form 5", "Schedule 13D", 
                                "Form 144", "Foreign Investment Disclosures"]
    
        prompt = f"Standardize the description of the following SEC filing: {description}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": f"""
                Standardize the description of the SEC filing to one of the following: {relevant_sec_filings}.
                Return a JSON object with the standardized description, the keys should be the original 
                description and the standardized description the values.
                """}
            ],
            temperature=0.0
        )

        standardized_description = response.choices[0].message.content.strip()
        return standardized_description
    

def get_submission_history(cik: int):
    """
    Fetches the submission history of a company from the SEC given its CIK.

    Args:
        cik (int): The Central Index Key (CIK) of the company.

    Returns:
        dict: A dictionary containing the submission history if the request is successful.

    Raises:
        HTTPError: If the request fails (i.e., if the response status code is not 200).
    """
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_company_facts(cik: int):
    """
    Fetches the company facts from the SEC for a given company's CIK.

    Args:
        cik (int): The Central Index Key (CIK) of the company.

    Returns:
        dict: A dictionary containing the company facts if the request is successful.

    Raises:
        HTTPError: If the request fails (i.e., if the response status code is not 200).
    """
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_company_concept(cik: int, taxonomy: str, tag: str):
    """
    Fetches specific company concept data from the SEC based on the company's CIK, taxonomy, and tag.

    Args:
        cik (int): The Central Index Key (CIK) of the company.
        taxonomy (str): The taxonomy (e.g., "us-gaap") used in XBRL.
        tag (str): The specific tag within the taxonomy (e.g., "Revenues").

    Returns:
        dict: A dictionary containing the company concept data if the request is successful.

    Raises:
        HTTPError: If the request fails (i.e., if the response status code is not 200).
    """
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/{taxonomy}/{tag}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_xbrl_frames(taxonomy: str, tag: str, unit: str, period: str, verbose=False):
    """
    Fetches XBRL (eXtensible Business Reporting Language) frame data from the SEC based on taxonomy, tag, unit, and period.

    Args:
        taxonomy (str): The taxonomy (e.g., "us-gaap") used in XBRL.
        tag (str): The specific tag within the taxonomy (e.g., "Revenues").
        unit (str): The unit of measurement (e.g., "USD").
        period (str): The reporting period (e.g., "2022-Q1").

    Returns:
        dict: A dictionary containing the XBRL frame data if the request is successful.

    Raises:
        HTTPError: If the request fails (i.e., if the response status code is not 200).
    """
    url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json"
    verbose and logging.info(f"Fetching data from {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def print_dict(d: dict):
    """
    Recursively prints the keys and values of a dictionary in a readable format.

    Args:
        d (dict): The dictionary to be printed.

    Returns:
        None
    """
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"{k}:")
            print_dict(v)
        elif isinstance(v, list):
            print(f"{k}: {v[0]}")
        else:
            print(f"{k}: {v}")

def parse_filing_text(text: str) -> str:
    """
    Parses HTML-formatted filing text and returns a clean, plain-text version.

    Args:
        text (str): The HTML-formatted filing text.

    Returns:
        str: A plain-text version of the filing, with HTML tags and unnecessary whitespace removed.
    """
    soup = bs(text, 'html.parser')
    return soup.get_text().replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').strip()

def df_formerNames(dict_: dict) -> pd.DataFrame:
    """
    Converts the 'formerNames' section of a company's submission data into a DataFrame.

    Args:
        dict_ (dict): The dictionary containing company data.

    Returns:
        pd.DataFrame: A DataFrame containing the former names and associated CIK of the company.
    """
    former_names = dict_['formerNames']
    df_former_names = pd.DataFrame(former_names)
    df_former_names['cik'] = dict_['cik']
    return df_former_names

def df_mailing_addresses(dict_: dict) -> pd.DataFrame:
    """
    Converts the 'mailing addresses' section of a company's submission data into a DataFrame.

    Args:
        dict_ (dict): The dictionary containing company data.

    Returns:
        pd.DataFrame: A DataFrame containing the mailing addresses and associated CIK of the company.
    """
    df_mailing_address = pd.DataFrame(dict_['addresses']['mailing'], index=[0])
    df_mailing_address['cik'] = dict_['cik']
    return df_mailing_address

def df_business_addresses(dict_: dict) -> pd.DataFrame:
    """
    Converts the 'business addresses' section of a company's submission data into a DataFrame.

    Args:
        dict_ (dict): The dictionary containing company data.

    Returns:
        pd.DataFrame: A DataFrame containing the business addresses and associated CIK of the company.
    """
    df_business_address = pd.DataFrame(dict_['addresses']['business'], index=[0])
    df_business_address['cik'] = dict_['cik']
    return df_business_address

def df_filing_history(dict_: dict) -> pd.DataFrame:
    """
    Converts the filing history of a company into a DataFrame.

    Args:
        dict_ (dict): The dictionary containing company data.

    Returns:
        pd.DataFrame: A DataFrame containing the recent and old filings along with the associated CIK.
    """
    df_recent_filings = pd.DataFrame(dict_['filings']['recent'])
    df_recent_filings['cik'] = dict_['cik']

    df_old_filings = pd.DataFrame()
    for i, element in enumerate(dict_['filings']['files']):
        df_ = pd.DataFrame(element, index=[i])
        df_['cik'] = dict_['cik']
        df_old_filings = pd.concat([df_old_filings, df_])
   
    for i, name in enumerate(df_old_filings['name']):
        response = requests.get(f"https://data.sec.gov/submissions/{name}", headers=HEADERS)
        if response.status_code != 200:
            continue

        dict_ = response.json()
        df_ = pd.DataFrame(dict_)
        df_['cik'] = df_old_filings['cik'][i]
        df_recent_filings = pd.concat([df_recent_filings, df_])

    return df_recent_filings

def df_company_facts(dict_: dict) -> pd.DataFrame:
    """
    Converts the 'facts' section of a company's submission data into a DataFrame.

    Args:
        dict_ (dict): The dictionary containing company data.

    Returns:
        pd.DataFrame: A DataFrame containing the company facts with additional information like account, description, and taxonomy.
    """
    if 'facts' not in dict_:
        return pd.DataFrame()
    
    facts = dict_['facts']
    if 'dei' not in facts:
        facts_dei = {}
    else:
        facts_dei = facts['dei']
    
    keys_dei = list(facts_dei.keys())
    df = pd.DataFrame()

    for i, k in enumerate(keys_dei):
        label_ = facts_dei[k]['label']
        description_ = facts_dei[k]['description']
        units_ = facts_dei[k]['units']
        label_unit = list(units_.keys())[0]
        elements = units_[label_unit]

        df_ = pd.DataFrame(elements)
        df_['account'] = label_
        df_['description'] = description_
        df_['cik'] = dict_['cik']
        df_['units'] = label_unit
        df_['taxonomy'] = 'dei'

        df = pd.concat([df, df_])

    if 'us-gaap' not in facts:
        facts_us_gaap = {}
    else: 
        facts_us_gaap = facts['us-gaap']

    keys_us_gaap = list(facts_us_gaap.keys())

    for i, k in enumerate(keys_us_gaap):
        label_ = facts_us_gaap[k]['label']
        description_ = facts_us_gaap[k]['description']
        units_ = facts_us_gaap[k]['units']
        label_unit = list(units_.keys())[0]
        elements = units_[label_unit]

        df_ = pd.DataFrame(elements)
        df_['account'] = label_
        df_['description'] = description_
        df_['cik'] = dict_['cik']
        df_['units'] = label_unit
        df_['taxonomy'] = 'us-gaap'

        df = pd.concat([df, df_])

    return df

def identify_cross_variables_from_facts(df_facts: pd.DataFrame, subset=['account', 'taxonomy', 'units', 'frame']) -> pd.DataFrame:
    """
    Identifies and processes cross-variable relationships within company facts.

    Args:
        df_facts (pd.DataFrame): The DataFrame containing company facts.
        subset (list, optional): A list of columns to consider for cross-variable identification. Defaults to ['account', 'taxonomy', 'units', 'frame'].

    Returns:
        pd.DataFrame: A DataFrame containing the identified cross-variable relationships.
    """
    df_facts = df_facts[subset]
    df_facts = df_facts.drop_duplicates()
    df_facts = df_facts.dropna(subset=['account'])
    
    df = pd.DataFrame()
    pbar = tqdm(range(df_facts.shape[0]))
    n_not = 0

    for i in pbar:
        pbar.set_description(f"{n_not} not found")
        pbar.refresh()
        time.sleep(0.05)

        row = df_facts.iloc[i]
        account = row['account'].replace(',', '').replace(' ', '')
        taxonomy = row['taxonomy']
        units = row['units']
        frame = row['frame']

        try:
            dict_ = get_xbrl_frames(taxonomy, account, units, frame)
        except HTTPError as e:
            if e.args[0] == '404':
                n_not += 1
                continue
            else:
                raise e

        df_frames = pd.DataFrame()
        df_frames['account'] = account
        df_frames['taxonomy'] = taxonomy
        df_frames['units'] = units
        df_frames['nobs'] = len(dict_['data'])
        df_frames['frame'] = frame

        df = pd.concat([df, df_frames])

    return df

def load_variable_names(relative_path = RELATIVE_PATH):
    """
    Loads variable names from SEC data and saves them to an Excel file.

    The function fetches company facts, processes them, and identifies variables, 
    then saves the results to an 'accounts.xlsx' file.

    example cik = 0000320193
    """
    df = pd.DataFrame()
    pbar = tqdm(CIKS)
    problematic = []

    for cik in pbar:
        pbar.set_description(f"{len(problematic)} problematic - cik {cik}.")
        pbar.refresh()

        try:
            dict_ = get_company_facts(cik)
            df_facts = df_company_facts(dict_)
            vars = ['account', 'description', 'taxonomy', 'units', 'frame']

            if any(var not in df_facts.columns for var in vars):
                problematic.append(cik)
                continue

            descriptions = df_facts[vars].drop_duplicates()
            df_instant = descriptions.groupby('account')['frame'].apply(lambda x: x.str.contains('I').any()).reset_index()
            df_instant = df_instant.rename(columns={'frame': 'instant'})

            load = {k: v for k, v in zip(descriptions['account'], descriptions['description'])}
            load_taxonomy = {k: v for k, v in zip(descriptions['account'], descriptions['taxonomy'])}
            load_units = {k: v for k, v in zip(descriptions['account'], descriptions['units'])}
            load_instant = {k: v for k, v in zip(df_instant['account'], df_instant["instant"])}

            accounts = pd.DataFrame(df_facts['account'].value_counts())
            accounts['description'] = accounts.index.map(load)
            accounts['taxonomy'] = accounts.index.map(load_taxonomy)
            accounts['units'] = accounts.index.map(load_units)
            accounts['instant'] = accounts.index.map(load_instant).astype(int)

            df = pd.concat([df, accounts])
        except:
            problematic.append(cik)
            continue

    df = df.drop_duplicates()
    df.to_excel(f'{relative_path}accounts.xlsx')

def modify_name_if_needed(name: str) -> str:
    """
    Modifies certain account names if they match specific criteria.

    Args:
        name (str): The original name of the account.

    Returns:
        str: The modified name of the account if it matches specific criteria; otherwise, the original name.
    """
    if name == "Longterm Debt Excluding Current Maturities":
        return "Long Term Debt Noncurrent"
    return name

def process(element: str) -> str:
    """
    Processes a string by capitalizing the first letter of each word and removing extra spaces.

    Args:
        element (str): The string to be processed.

    Returns:
        str: The processed string.
    """
    element = element.strip()
    s = element.split(' ')
    s = [word.capitalize() if word[0].islower() else word for word in s]
    return ' '.join(s)

def clean_account_name(account: str) -> str:
    """
    Cleans an account name by removing special characters and capitalizing words.

    Args:
        account (str): The original account name.

    Returns:
        str: The cleaned account name.
    """
    account = (account
               .replace(',', '')
               .replace('(', '')
               .replace(')', '')
               .replace("'", '')
               .replace("Attributable to Parent", '')
               .replace('-', ''))
    try:
        account = process(account)
        account = modify_name_if_needed(account)
        
    except:
        pass

    account = account.replace(' ', '')
    return account

# Try to read accounts.xlsx from cache; fallback to packaged data
try:
    df = pd.read_excel(f'{RELATIVE_PATH}accounts.xlsx')
except Exception:
    # Fallback to provided subset if full accounts cache is missing
    fallback_path = os.path.join(DATA_PATH, 'subset_accounts.xlsx')
    df = pd.read_excel(fallback_path)

# dictionary between clean name and instant
instant_dict = {clean_account_name(k): (v, u, t) for k, v, u, t in zip(df['account'], df['instant'], df['units'], df['taxonomy'])}
# force change the one in NetIncomeLoss to a 0
instant_dict['NetIncomeLoss'] = (0, 'USD', 'us-gaap')

def accounts_available(relative_path = RELATIVE_PATH):
    """
    Checks the availability of accounts based on predefined criteria and saves the results in a JSON file.
    
    The function processes a maximum of 1,000 accounts from 'accounts.xlsx' and verifies 
    their existence using the SEC API, then saves the found accounts in 'found_accounts.json'.
    """
    df = pd.read_excel(f'{relative_path}/accounts.xlsx')
    dep = 0
    not_found = []
    found = {}
    max_ = min(1000, df.shape[0])
    pbar = tqdm(range(max_))

    for i in pbar:
        time.sleep(0.1)
        row = df.iloc[i]
        pbar.set_description(f"{len(not_found)} not found - {dep} deprecated -> Processing {row['account']}.")
        pbar.refresh()

        instant = row['instant']
        account = row['account']

        if "Deprecated" in account:
            dep += 1
            continue

        account = clean_account_name(account)
        taxonomy = row["taxonomy"]
        units = row["units"].replace('/', '-per-')
        ending = 'I' if instant else ''
        frame = f"CY2024Q1{ending}"

        try:
            dict_ = get_xbrl_frames(taxonomy, account, units, frame)
            found.append({ 'name': row['account'],
                           'clean_name': account,
                           'taxonomy': row['taxonomy'],
                           'units': row['units'],
                           'frame': frame,
                           'instant': instant,
                           'ending': ending,
                           'description': row['description']})
        except:
            not_found.append(account)
            continue
    
    # Save found accounts to a JSON file
    dit_ = {'accounts': found}
    with open(f'{relative_path}found_accounts.json', 'w') as f:
        json.dump(dit_, f)


def cik_sic_table(relative_path = RELATIVE_PATH):
    # loop through all ciks and get the sic code from the submission history
    dict_ = {}
    for cik in tqdm(CIKS):
        time.sleep(0.1)
        try:
            dict_[cik] = get_submission_history(cik)['sic']
        except:
            continue
    
    # save as json
    with open(f'{relative_path}cik_sic.json', 'w') as f:
        json.dump(dict_, f)

def return_cik_sic(relative_path = RELATIVE_PATH):
    with open(f'{relative_path}cik_sic.json', 'r') as f:
        dict_ = json.load(f)
    return dict_

def get_companies_in_sic(sic: int, digits=2):
    # adjust the sic code to the number of digits
    def adjust_sic(sic_):
        try:
            return int(str(sic_)[:digits])
        except:
            return None

    # get all the ciks that have the same sic code
    ciks = [k for k, v in return_cik_sic().items() if adjust_sic(v) == adjust_sic(sic)]
    # return also the company names and tickers
    company_names = return_company_names()
    cik_tickers = get_cik_tickers()
    # convert key to int and then to str again in cik_tickers
    cik_tickers = {str(int(k)): v for k, v in cik_tickers.items()}

    companies = {}
    for i, cik in enumerate(ciks):
        name = company_names[cik] if cik in company_names else None
        tickers = cik_tickers[cik] if cik in cik_tickers else None
        companies[cik] = {'name': name, 'tickers': tickers, 'sic': adjust_sic(return_cik_sic()[cik])}

    # return a dataframe with columns cik, name, tickers and industry
    df = pd.DataFrame(companies).T
    # reset index and name it cik 
    df = df.reset_index()
    df = df.rename(columns={'index': 'cik'})

    return df

# Function that given a cik gets all the companies that have the same sic code
def get_companies_with_same_sic(cik: int, digits=1):
    # get the sic code for the cik
    sic = return_cik_sic()[str(cik)]

    # adjust the sic code to the number of digits
    def adjust_sic(sic_):
        try:
            return int(str(sic_)[:digits])
        except:
            return None

    # get all the ciks that have the same sic code
    ciks = [k for k, v in return_cik_sic().items() if adjust_sic(v) == adjust_sic(sic)]
    # return also the company names and tickers
    company_names = return_company_names()
    cik_tickers = get_cik_tickers()
    # convert key to int and then to str again in cik_tickers
    cik_tickers = {str(int(k)): v for k, v in cik_tickers.items()}

    companies = {}
    for i, cik in enumerate(ciks):
        name = company_names[cik] if cik in company_names else None
        tickers = cik_tickers[cik] if cik in cik_tickers else None
        companies[cik] = {'name': name, 'tickers': tickers, 'sic': adjust_sic(return_cik_sic()[cik])}

    # return a dataframe with columns cik, name, tickers and industry
    df = pd.DataFrame(companies).T
    # reset index and name it cik 
    df = df.reset_index()
    df = df.rename(columns={'index': 'cik'})

    return df


def get_all_size():
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         'CY2024Q1I')
    df_size = pd.DataFrame(data['data'])

    df_size = df_size.rename(columns={'val': 'assets'})

    return df_size

def get_companies_similar_size(cik: int, interval= 100):
    # get the Assets of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         'CY2024Q1I')
    # to dataframe 
    df_size = pd.DataFrame(data['data'])

    # return a dataframe with companies +- interval% 
    size = df_size[df_size['cik'] == cik]['val'].values[0]
    upper_bound = size*(1+interval/100)
    lower_bound = size*(1-interval/100)

    df_size = df_size[(df_size['val'] >= lower_bound) & (df_size['val'] <= upper_bound)]

    return df_size

def get_all_profitability():
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         'CY2024Q1I')
    # to dataframe 
    df_size = pd.DataFrame(data['data'])

    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('NetIncomeLoss'), 
                         'USD', 
                         'CY2024Q1')
    # to dataframe
    df_profit = pd.DataFrame(data['data'])

    df_size = df_size.rename(columns={'val': 'assets'})
    df_profit = df_profit.rename(columns={'val': 'profit'})

    # merge the two dataframes
    df = pd.merge(df_size, df_profit, on='cik')
    # calculate the profitability
    df['profitability'] = df['profit']/df['assets']

    # drop assets and profit
    df = df.drop(['assets', 'profit'], axis=1)

    return df

# same for profitability, Revenue from Contract with Customer, Including Assessed Tax over total assets 
def get_companies_similar_profitability(cik: int, interval= 100):
    # get the Assets of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         'CY2024Q1I')
    # to dataframe 
    df_size = pd.DataFrame(data['data'])

    # return a dataframe with companies +- interval% 
    size = df_size[df_size['cik'] == cik]['val'].values[0]
    
    # now get revenues 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('NetIncomeLoss'), 
                         'USD', 
                         'CY2024Q1')
    # to dataframe
    df_profit = pd.DataFrame(data['data'])

    profit = df_profit[df_profit['cik'] == cik]['val'].values[0]
    # rename val in df_size to assets and
    # val in df_profit to profit

    df_size = df_size.rename(columns={'val': 'assets'})
    df_profit = df_profit.rename(columns={'val': 'profit'})

    # merge the two dataframes
    df = pd.merge(df_size, df_profit, on='cik')
    # calculate the profitability
    df['profitability'] = df['profit']/df['assets']

    profitability = profit/size
    upper_bound = profitability*(1+interval/100)
    lower_bound = profitability*(1-interval/100)

    df = df[(df['profitability'] >= lower_bound) & (df['profitability'] <= upper_bound)]

    return df

def get_all_growth_rate():
    current_year = time.localtime().tm_year
    # get the Assets of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_size = pd.DataFrame(data['data'])
    
    # now get assets 5 years ago
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         f'CY{current_year-5}Q1I')
    # to dataframe
    df_size_5 = pd.DataFrame(data['data'])
    # keep only cik and val 
    df_size = df_size[['cik', 'val']]
    df_size_5 = df_size_5[['cik', 'val']]
    df_size = df_size.rename(columns={'val': 'assets'})
    df_size_5 = df_size_5.rename(columns={'val': 'assets_5'})

    df = pd.merge(df_size, df_size_5, on='cik')
    df['growth_rate'] = (df['assets']-df['assets_5'])/df['assets_5']

    # drop assets and assets_5
    df = df.drop(['assets', 'assets_5'], axis=1)

    return df

# similar growth rate, compare assets in the last 5 years, compare assets year today with assets 5 years ago
def get_companies_similar_growth_rate(cik: int, interval= 100):
    current_year = time.localtime().tm_year
    # get the Assets of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_size = pd.DataFrame(data['data'])

    # return a dataframe with companies +- interval% 
    size = df_size[df_size['cik'] == cik]['val'].values[0]
    
    # now get assets 5 years ago
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name('Assets'), 
                         'USD', 
                         f'CY{current_year-5}Q1I')
    # to dataframe
    df_size_5 = pd.DataFrame(data['data'])

    size_5 = df_size_5[df_size_5['cik'] == cik]['val'].values[0]

    growth_rate = (size-size_5)/size_5
    upper_bound = growth_rate + (interval/100)
    lower_bound = growth_rate - (interval/100)

    # keep only cik and val 
    df_size = df_size[['cik', 'val']]
    df_size_5 = df_size_5[['cik', 'val']]
    df_size = df_size.rename(columns={'val': 'assets'})
    df_size_5 = df_size_5.rename(columns={'val': 'assets_5'})

    df = pd.merge(df_size, df_size_5, on='cik')
    df['growth_rate'] = (df['assets']-df['assets_5'])/df['assets_5']

    df = df[(df['growth_rate'] >= lower_bound) & (df['growth_rate'] <= upper_bound)]

    return df


def get_all_capital_structure():
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name("StockholdersEquity"), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_equity = pd.DataFrame(data['data'])

    # get the Total Liabilities of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name("Liabilities"), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_liabilities = pd.DataFrame(data['data'])
    # keep only cik and val
    df_equity = df_equity[['cik', 'val']]
    df_liabilities = df_liabilities[['cik', 'val']]

    df_equity = df_equity.rename(columns={'val': 'equity'})
    df_liabilities = df_liabilities.rename(columns={'val': 'liabilities'})

    df = pd.merge(df_equity, df_liabilities, on='cik')
    
    df['debt_to_equity'] = df['liabilities']/df['equity']

    # drop equity and liabilities
    df = df.drop(['equity', 'liabilities'], axis=1)

    return df

# similar capital structure, compare debt to equity ratio
# Stockholder's Equity over Total Liabilities
# use only data from this year 
def get_companies_similar_capital_structure(cik: int, interval= 100):
    current_year = time.localtime().tm_year
    # get the Stockholder's Equity of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name("StockholdersEquity"), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_equity = pd.DataFrame(data['data'])

    # get the Total Liabilities of all companies 
    data = get_xbrl_frames('us-gaap', 
                         clean_account_name("Liabilities"), 
                         'USD', 
                         f'CY2024Q1I')
    # to dataframe 
    df_liabilities = pd.DataFrame(data['data'])

    # return a dataframe with companies +- interval% 
    equity = df_equity[df_equity['cik'] == cik]['val'].values[0]
    liabilities = df_liabilities[df_liabilities['cik'] == cik]['val'].values[0]

    capital_structure = liabilities/equity
    upper_bound = capital_structure + (interval/100)
    lower_bound = capital_structure - (interval/100)

    # keep only cik and val
    df_equity = df_equity[['cik', 'val']]
    df_liabilities = df_liabilities[['cik', 'val']]

    # retrieve fror cik 
    temp = df_equity[df_equity['cik'] == cik]
    temp = df_liabilities[df_liabilities['cik'] == cik]

    df_equity = df_equity.rename(columns={'val': 'equity'})
    df_liabilities = df_liabilities.rename(columns={'val': 'liabilities'})

    df = pd.merge(df_equity, df_liabilities, on='cik')
    
    temp = df[df['cik'] == cik]
    
    df['debt_to_equity'] = df['liabilities']/df['equity']

    df = df[(df['debt_to_equity'] >= lower_bound) & (df['debt_to_equity'] <= upper_bound)]
    
    temp = df[df['cik'] == cik]

    return df

def clean_df_bad_endings(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if col.endswith('_x') or col.endswith('_y'):
            df = df.drop(col, axis=1)
    return df

# download state of all companies
def get_state_of_companies():
    all_ciks = return_cik_sic().keys()
    states = {}
    for cik in tqdm(all_ciks):
        time.sleep(0.05)
        try:
            data = get_submission_history(int(cik))
            state = data['addresses']['business']['stateOrCountryDescription']
            states[cik] = state
        except:
            continue
    # to json 
    with open(f'{RELATIVE_PATH}states.json', 'w') as f:
        json.dump(states, f)


# similar geographic location, compare companies in the same state
def get_companies_similar_location(cik: int):
    # get the state of the company
    data = get_submission_history(cik)
    current_state = data['addresses']['business']['stateOrCountryDescription']
    
    # load the states
    with open(f'{RELATIVE_PATH}states.json', 'r') as f:
        states = json.load(f)

    # get all the ciks that have the same state
    ciks = [k for k, v in states.items() if v == current_state]

    # in dataframe one column the cik and the other the state
    df = pd.DataFrame(ciks, columns=['cik'])
    df['state'] = current_state

    return df

"""
' For debugging 

cik = 320193

kwargs = {'params_comparables': {'industry': {'digits': 2}, 'size': {'interval': 200}, 'profitability': {'interval': 200}, 'growth_rate': {'interval': 200}, 'capital_structure': {'interval': 200}}, 'variables_to_compare': ['industry', 'size', 'profitability', 'growth_rate', 'capital_structure', 'location'], 'method': 'kmeans', 'extra_variables': ['GrossProfit', 'NetIncomeLoss', 'EarningsPerShareBasic']}

"""

def identify_comparables(*args, **kwargs):
    cik = args[0]
    print("-----------------")
    print("kwargs")
    print(kwargs)
    print("-----------------")
    method = kwargs['method']
    #variables_to_compare = kwargs['variables_to_compare']
    variables_to_compare = ['industry', 'size', 'profitability', 'growth_rate', 'capital_structure', 'location']
    params_comparables = kwargs['params_comparables']

    #extra_variables = kwargs['extra_variables']
    extra_variables = ['GrossProfit', 'NetIncomeLoss', 'EarningsPerShareBasic']

    # it must be a subset of the following variables
    # industry, size, profitability, growth_rate, capital_structure, location

    # check that there is at least one variable to compare 
    if not variables_to_compare:
        raise ValueError("At least one variable to compare must be provided.")
    
    vars_not_rec = []
    for var in variables_to_compare:
        if var not in ['industry', 'size', 'profitability', 'growth_rate', 'capital_structure', 'location']:
            vars_not_rec.append(var)

    if vars_not_rec:
        raise ValueError(f"Variables not recognized: {vars_not_rec}")


    data_frames = []
    labels = []

    if 'industry' in variables_to_compare:
        labels.append('industry')
        temp = get_companies_with_same_sic(cik, **params_comparables['industry'])
        # cik to int 
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for industry.")
        data_frames.append(temp)

    if 'size' in variables_to_compare:
        labels.append('size')
        temp = get_companies_similar_size(cik, **params_comparables['size'])
        # cik to int
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for size.")
    
        data_frames.append(temp)

    if 'profitability' in variables_to_compare:
        labels.append('profitability')
        temp = get_companies_similar_profitability(cik, **params_comparables['profitability'])
        # cik to int
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for profitability.")
        
        data_frames.append(temp)

    if 'growth_rate' in variables_to_compare:
        labels.append('growth_rate')
        temp = get_companies_similar_growth_rate(cik, **params_comparables['growth_rate'])
        # cik to int
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for growth rate.")
        
        data_frames.append(temp)

    if 'capital_structure' in variables_to_compare:
        labels.append('capital_structure')
        temp = get_companies_similar_capital_structure(cik, **params_comparables['capital_structure'])
        # cik to int
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for capital structure.")
        
        data_frames.append(temp)

    if 'location' in variables_to_compare:
        labels.append('location')
        temp = get_companies_similar_location(cik)
        # cik to int
        temp['cik'] = temp['cik'].astype(int)
        # check the cik is in the dataframe
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for location.")
        
        data_frames.append(temp)

    # merge all dataframes
    df = data_frames[0] 
    # log how many observations are in the dataframe together with the step 
    logging.info(f"Step 1: {df.shape[0]} observations for {labels[0]}.")
    for i in range(1, len(data_frames)):
        temp = data_frames[i]
        df = pd.merge(df, temp, on='cik', how = 'inner', suffixes=('', '_drop'))
        logging.info(f"Step {i+1}: {df.shape[0]} observations for {labels[i]}. Using has {len(temp)} observations.")

    # drop columns ending in _drop 
    df = df[df.columns.drop(list(df.filter(regex='_drop')))]

    # if we have keys that look like cik cik_x cik_y we drop the _x and _y variables
    df = clean_df_bad_endings(df)

    def get_extra_variables(ciks, var):
        current_year = time.localtime().tm_year
        # we need to know the instant 
        instant = instant_dict[clean_account_name(var)][0]
        units = instant_dict[clean_account_name(var)][1]
        instant_end = 'I' if instant else ''
        units_end = units.replace('/', '-per-')

        # in units_end replace three consecutive uppercase letters with USD 
        units_end = re.sub(r'[A-Z]{3}', 'USD', units_end)

        # get the var of all companies 
        taxonomy = instant_dict[clean_account_name(var)][2]
        data = get_xbrl_frames(taxonomy, 
                         clean_account_name(var), 
                         units_end, 
                         f'CY{current_year}Q1{instant_end}', verbose=True)
        
        # to dataframe
        df_var = pd.DataFrame(data['data'])
        # keep only cik and val
        df_var = df_var[['cik', 'val']]
        # rename val to var
        df_var = df_var.rename(columns={'val': var})
        # return the value for the ciks
        return df_var[df_var['cik'].isin(ciks)]
    
    # add the extra variables 
    if extra_variables:
        for var in extra_variables:
            temp = get_extra_variables(df['cik'], var)
            df = pd.merge(df, temp, on='cik', how = 'left')
            df = clean_df_bad_endings(df)

    # return the df as json 
    to_return = df.to_json()
    # drop if the key ends in _x or _y
    to_return = json.loads(to_return)
    
    return to_return



def identify_comparables_ml(name,sic, assets, profitability, growth_rate, capital_structure):
    
    extra_variables = ['GrossProfit', 'NetIncomeLoss', 'EarningsPerShareBasic']

    # big interval since we want first to have them all
    df_size = get_all_size()
    df_size['cik'] = df_size['cik'].astype(int)
    df_profit = get_all_profitability()
    df_profit['cik'] = df_profit['cik'].astype(int)
    df_growth = get_all_growth_rate()
    df_growth['cik'] = df_growth['cik'].astype(int)
    df_capital = get_all_capital_structure()
    df_capital['cik'] = df_capital['cik'].astype(int)

    # same 2 digits sic code
    df_industry = get_companies_in_sic(sic, digits=2)
    df_industry['cik'] = df_industry['cik'].astype(int)

    # merge all dataframes
    df = df_size
    df = pd.merge(df, df_profit, on='cik', how = 'inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_growth, on='cik', how = 'inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_capital, on='cik', how = 'inner', suffixes=('', '_drop'))


    if len(df_industry) > 0: # Because sometimes the AI wont get the industry
        df = pd.merge(df, df_industry, on='cik', how = 'inner', suffixes=('', '_drop'))

    # accn,cik,entityName,loc,end,val,accn_x,entityName_x,loc_x,end_x,assets,accn_y,entityName_y,loc_y,start,end_y,profit,profitability,assets_drop,assets_5,growth_rate,equity,liabilities,debt_to_equity

    # cik, entityName, assets, profitability, growth_rate, debt_to_equity

    df = df[['cik', 'sic', 'entityName', 'assets', 'profitability', 'growth_rate', 'debt_to_equity']]

    # Variables of interest
    variables = ['assets', 'profitability', 'growth_rate', 'debt_to_equity']

    # Extract the baseline observation
    current = {"cik" : FAKE_CIK,
                "sic" : sic,
                "entityName" : name,
                "assets" : assets,
                "profitability" : profitability,
                "growth_rate" : growth_rate,
                "debt_to_equity" : capital_structure}
    
    # in df 
    current = pd.DataFrame(current, index=[0])

    # append 
    df = pd.concat([df, current])

    # Standardize the variables
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[variables] = scaler.fit_transform(df[variables])
    # Drop non-numeric columns for distance calculation
    df_features = df_scaled[variables]

    # Fit Nearest Neighbors model
    nn = NearestNeighbors(n_neighbors=5, metric='euclidean')  # Adjust `n_neighbors` as needed
    nn.fit(df_features)

    # Find the closest observations
    distances, indices = nn.kneighbors(current[variables])

    # Retrieve the closest observations
    closest = df.iloc[indices[0]]

    closest = clean_df_bad_endings(closest)

    def get_extra_variables(ciks, var):
        current_year = time.localtime().tm_year - 1 #!TODO: Change to most recent data
        # we need to know the instant 
        instant = instant_dict[clean_account_name(var)][0]
        units = instant_dict[clean_account_name(var)][1]
        instant_end = 'I' if instant else ''
        units_end = units.replace('/', '-per-')

        # in units_end replace three consecutive uppercase letters with USD 
        units_end = re.sub(r'[A-Z]{3}', 'USD', units_end)

        # get the var of all companies 
        taxonomy = instant_dict[clean_account_name(var)][2]
        data = get_xbrl_frames(taxonomy, 
                         clean_account_name(var), 
                         units_end, 
                         f'CY{current_year}Q1{instant_end}', verbose=True)
        
        # to dataframe
        df_var = pd.DataFrame(data['data'])
        # keep only cik and val
        df_var = df_var[['cik', 'val']]
        # rename val to var
        df_var = df_var.rename(columns={'val': var})
        # return the value for the ciks
        return df_var[df_var['cik'].isin(ciks)]
    
    
    # add the extra variables 
    if extra_variables:
        for var in extra_variables:
            ciks_exclude_current = [cik for cik in closest['cik'] if cik != FAKE_CIK]
            temp = get_extra_variables(ciks_exclude_current, var)
            closest = pd.merge(closest, temp, on='cik', how = 'left')
            closest = clean_df_bad_endings(closest)

    return closest.to_json()

