import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import json 

HEADERS = {"User-Agent": "PyEdgarAI a library for fetching data from the SEC"}

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
