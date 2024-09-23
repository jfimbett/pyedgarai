#%%
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import json
from dataclasses import dataclass
from openai import OpenAI
import pandas as pd
import time
from sec_cik_mapper import StockMapper
from requests.exceptions import HTTPError
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    RELATIVE_PATH = ""
    DATA_PATH = "../../data/"
else:
    RELATIVE_PATH = 'src/pyedgarai/' # make this the standard relative path for the project, and only if this file is ran from the root directory we change it. 
    DATA_PATH = "data/"
#%%

# Set up HTTP headers for requests to the SEC API
HEADERS = {"User-Agent": "PyEdgarAI a library for fetching data from the SEC"}
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

def get_xbrl_frames(taxonomy: str, tag: str, unit: str, period: str):
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
    account = process(account)
    account = modify_name_if_needed(account)
    account = account.replace(' ', '')
    return account

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

# Function that given a cik gets all the companies that have the same sic code
def get_companies_with_same_sic(cik: int):
    # get the sic code for the cik
    sic = return_cik_sic()[str(cik)]
    # get all the ciks that have the same sic code
    ciks = [k for k, v in return_cik_sic().items() if v == sic]
    # return also the company names and tickers
    company_names = return_company_names()
    cik_tickers = get_cik_tickers()
    # convert key to int and then to str again in cik_tickers
    cik_tickers = {str(int(k)): v for k, v in cik_tickers.items()}

    companies = {}
    for cik in ciks:
        name = company_names[cik] if cik in company_names else None
        tickers = cik_tickers[cik] if cik in cik_tickers else None
        companies[cik] = {'name': name, 'tickers': tickers}
    
    return companies

    
