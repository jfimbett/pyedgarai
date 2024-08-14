#%%
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import json 
from dataclasses import dataclass
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import time
# import HTTPError 
from requests.exceptions import HTTPError

HEADERS = {"User-Agent": "PyEdgarAI a library for fetching data from the SEC"}

class Options():
    pass

@dataclass
class OpenAIWrapper():
    model : str
    api_key : str

    def create_client(self):
        return OpenAI(api_key = self.api_key)
    
    def standardize_filing_description(self, description, client, model):
        client = self.create_client()

        relevant_sec_filings = ["Form S-1",
                                "Form 10-K",
                                "Form 10-Q",
                                "Form 8-K",
                                "DEF 14A",
                                "Form 3",
                                "Form 4",
                                "Form 5",
                                "Schedule 13D",
                                "Form 144",
                                "Foreign Investment Disclosures"
                                ]
    
        prompt = f"Standardize the description of the following SEC filing: {description}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "system", "content": f""" 
                Standardize the description of the SEC filing to one of the following: {relevant_sec_filings}. Return a JSON object with the standardized description, the keys should be the original description and the standardized description the values. 
                """}
            ],
            temperature=0.0
        )

        standardized_description = response.choices[0].message.content.strip()
        return standardized_description
    

def get_submission_history(cik: int):
    """
    Fetches the submission history of a company from the SEC (Securities and Exchange Commission) given its Central Index Key (CIK).

    Args:
        cik (int): The Central Index Key (CIK) of the company.

    Returns:
        dict: A dictionary containing the submission history of the company if the request is successful.

    Raises:
        HTTPError: An error is raised if the request fails (i.e., if the response status code is not 200).
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
        HTTPError: An error is raised if the request fails (i.e., if the response status code is not 200).
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
        HTTPError: An error is raised if the request fails (i.e., if the response status code is not 200).
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
        HTTPError: An error is raised if the request fails (i.e., if the response status code is not 200).
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

def df_formerNames(dict_ : dict):
    # return df of formerNames 
    former_names = dict_['formerNames']
    df_former_names = pd.DataFrame(former_names)
    df_former_names['cik'] = dict_['cik']
    return df_former_names

def df_mailing_addresses(dict_ : dict):
    # addresses 
    df_mailing_address =  pd.DataFrame(dict_['addresses']['mailing'], index=[0])
    df_mailing_address['cik'] = dict_['cik']
    return df_mailing_address

def df_business_addresses(dict_ : dict):
    df_business_address = pd.DataFrame(dict_['addresses']['business'], index=[0])
    df_business_address['cik'] = dict_['cik']
    return df_business_address

def df_filing_history(dict_ : dict):
    # now for filings (last 1000)
    df_recent_filings = pd.DataFrame(dict_['filings']['recent'])
    df_recent_filings['cik'] = dict_['cik']

    # extra files live in dict_['filings']['files']
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


def df_company_facts(dict_ : dict):
    facts = dict_['facts']
    facts_dei = facts['dei']
    facts_us_gaap = facts['us-gaap']

    keys_dei = list(facts_dei.keys())

    df = pd.DataFrame()
    for i, k in enumerate(keys_dei):
        label_       = facts_dei[k]['label']
        description_ = facts_dei[k]['description']
        units_       = facts_dei[k]['units']
        label_unit   = list(units_.keys())[0]
        elements     = units_[label_unit]

        df_ = pd.DataFrame(elements)
        df_['account'] = label_
        df_['description'] = description_
        df_['cik'] = dict_['cik']
        df_['units'] = label_unit
        df_['taxonomy'] = 'dei'

        df = pd.concat([df, df_])

    keys_us_gaap = list(facts_us_gaap.keys())

    for i, k in enumerate(keys_us_gaap):
        label_       = facts_us_gaap[k]['label']
        description_ = facts_us_gaap[k]['description']
        units_       = facts_us_gaap[k]['units']
        label_unit   = list(units_.keys())[0]
        elements     = units_[label_unit]

        df_ = pd.DataFrame(elements)
        df_['account'] = label_
        df_['description'] = description_
        df_['cik'] = dict_['cik']
        df_['units'] = label_unit
        df_['taxonomy'] = 'us-gaap'

        df = pd.concat([df, df_])

    return df



def identify_cross_variables_from_facts(df_facts, subset=['account', 'taxonomy', 'units', 'frame']):
    df_facts = df_facts[subset]
    # unique, account, taxonomy, units, and frame 
    df_facts = df_facts.drop_duplicates()
    # drop if account is None 
    df_facts = df_facts.dropna(subset=['account'])
    
    # loop row by row 
    n_rows = df_facts.shape[0]
    df = pd.DataFrame()
    pbar = tqdm(range(n_rows))
    n_not = 0
    for i in pbar:
        pbar.set_description(f"{n_not} not found")
        pbar.refresh()
        time.sleep(0.05)
        row = df_facts.iloc[i]
        account = row['account']
        taxonomy = row['taxonomy']
        units = row['units']

        # in accounts drop commas and spaces 
        account = account.replace(',', '').replace(' ', '')
        frame = row['frame']
        # get xbrl frames
        try:
            dict_ = get_xbrl_frames(taxonomy, account, units, frame)
        except HTTPError as e:
            if e.args[0] == '404':
                n_not += 1
                continue
            else:
                raise e

        df_frames = pd.DataFrame()
        # if there are frames, add the account, taxonomy, and units to the frame
        df_frames['account'] = account
        df_frames['taxonomy'] = taxonomy
        df_frames['units'] = units
        df_frames['nobs'] = len(dict_['data'])
        df_frames['frame'] = frame

        df = pd.concat([df, df_frames])

    return df

def load_variable_names():
    cik = 320193
    dict_ = get_company_facts(cik)
    df_facts = df_company_facts(dict_)
    descriptions = df_facts[['account', 'description', 'taxonomy', 'units', 'frame']]
    descriptions = descriptions.drop_duplicates()

    # by account we want to know if the variable frame contains at least one string with the letter I inside
    df_instant = descriptions.groupby('account').apply(lambda x: x['frame'].str.contains('I').any())
    df_instant = df_instant.reset_index()
    # rename 0 to instant
    df_instant = df_instant.rename(columns={0: 'instant'})
    # create dictionary 
    load = {k : v for k, v in zip(descriptions['account'], descriptions['description'])}
    load_taxonomy = {k : v for k, v in zip(descriptions['account'], descriptions['taxonomy'])}
    load_units = {k : v for k, v in zip(descriptions['account'], descriptions['units'])}
    load_instant = {k : v for k, v in zip(df_instant['account'], df_instant["instant"])}
    accounts = df_facts['account'].value_counts()
    # to dataframe 
    accounts = pd.DataFrame(accounts)
    # add column with the descripiton 
    accounts['description'] = accounts.index.map(load)
    accounts['taxonomy'] = accounts.index.map(load_taxonomy)
    accounts['units'] = accounts.index.map(load_units)
    accounts['instant'] = accounts.index.map(load_instant)
    # instant to 1 if True, 0 if False
    accounts['instant'] = accounts['instant'].astype(int)
    # to excel 
    accounts.to_excel('accounts.xlsx')


# test the frames 
def modify_name_if_needed(name):
    if name == "Longterm Debt Excluding Current Maturities":
        return "Long Term Debt Noncurrent"
    
    return name
def process(element):
    # drop spaces before and after 
    element = element.strip()
    # split by spaces 
    s= element.split(' ')
    # capitalize the first letter of each word if it is not already 
    s = [word.capitalize() if word[0].islower() else word for word in s]

    return ' '.join(s)

def accounts_available():
    df = pd.read_excel('accounts.xlsx')
    dep = 0
    not_found = []
    found = []
    pbar = tqdm(range(df.shape[0]))
    for i in pbar:
        # for debugging 

        time.sleep(0.1)
        row = df.iloc[i]
        pbar.set_description(f"{len(not_found)} not found - {dep} deprecated -> Processing {row['account']}.")
        pbar.refresh()
        instant = row['instant']
        account = row['account']

        if "Deprecated" in account:
            dep += 1
            continue

        account = (account
                .replace(',', '')
                .replace('(', '')
                .replace(')', '')
                .replace("'", '')
                .replace("Attributable to Parent",'')
                .replace('-', '')
        )
        # capitalize the first letter of each word
        account = process(account)
        account = modify_name_if_needed(account)
        account = account.replace(' ', '')
        taxonomy = row["taxonomy"]
        units = row["units"].replace('/', '-per-')
        ending = 'I' if instant else ''
        frame = f"CY2024Q1{ending}"
        try:
            dict_ = get_xbrl_frames(taxonomy, account, units, frame)
            found.append(row['account'])
        except:
            not_found.append(account)
            continue
    
    # save found in a file
    with open('found.txt', 'w') as f:
        for item in found:
            f.write("%s\n" % item)


# %%
