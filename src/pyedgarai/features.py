"""Feature and metadata helpers.

Utilities to load accounts, map CIKs to tickers/names/SIC, compute states, and
build instant/unit/taxonomy lookups from the accounts catalog.

All data is fetched live from public sources (SEC and yfinance via sec-cik-mapper)
and cached under a user cache dir (~/.cache/pyedgarai by default) to avoid mocks.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Iterable

import pandas as pd
from sec_cik_mapper import StockMapper

from .sec_client import get_company_facts, get_submission_history, get_xbrl_frames
from .utils import clean_account_name

# ---------------- Cache dir ---------------- #

def _get_cache_dir() -> str:
    env = os.getenv("PYEDGARAI_CACHE_DIR")
    if env:
        Path(env).mkdir(parents=True, exist_ok=True)
        return env if env.endswith('/') else env + '/'
    default = os.path.join(Path.home(), ".cache", "pyedgarai")
    Path(default).mkdir(parents=True, exist_ok=True)
    return default + "/" if not default.endswith('/') else default

CACHE_DIR = _get_cache_dir()
DATA_DIR = os.path.join(Path(__file__).resolve().parents[2], "data")

# ---------------- Accounts catalog ---------------- #

def return_accounts() -> Dict[str, Dict[str, Any]]:
    """Return an accounts catalog as a dict keyed by cleaned name.

    Tries to load a cached accounts.xlsx from CACHE_DIR; falls back to
    the bundled data/subset_accounts.xlsx when missing.
    """
    # Prefer cached
    xlsx_cache = os.path.join(CACHE_DIR, "accounts.xlsx")
    if os.path.exists(xlsx_cache):
        df = pd.read_excel(xlsx_cache)
    else:
        df = pd.read_excel(os.path.join(DATA_DIR, "subset_accounts.xlsx"))
    names = df['account'].tolist()
    clean_names = df['account'].apply(clean_account_name).tolist()
    description = df['description'].tolist()
    units = df['units'].tolist()
    taxonomy = df['taxonomy'].tolist()
    instant = df['instant'].tolist()
    return {clean_names[i]: {
        'name': names[i],
        'description': description[i],
        'units': units[i],
        'taxonomy': taxonomy[i],
        'instant': instant[i],
    } for i in range(len(names))}


def load_variable_names(relative_path: str | None = None) -> None:
    """Build accounts.xlsx by scanning company facts across CIKs.

    Writes accounts.xlsx into the cache directory.
    """
    if relative_path is None:
        relative_path = CACHE_DIR

    ciks = [int(str(c).lstrip('0')) for c in StockMapper().cik_to_tickers.keys()]
    df_all = pd.DataFrame()
    problematic: list[int] = []

    for cik in ciks:
        try:
            facts = get_company_facts(cik)
            df_facts = df_company_facts(facts)
            vars = ['account', 'description', 'taxonomy', 'units', 'frame']
            if any(v not in df_facts.columns for v in vars):
                problematic.append(cik)
                continue
            descriptions = df_facts[vars].drop_duplicates()
            df_instant = descriptions.groupby('account')['frame'].apply(lambda x: x.str.contains('I').any()).reset_index()
            df_instant = df_instant.rename(columns={'frame': 'instant'})

            load = {k: v for k, v in zip(descriptions['account'], descriptions['description'])}
            load_taxonomy = {k: v for k, v in zip(descriptions['account'], descriptions['taxonomy'])}
            load_units = {k: v for k, v in zip(descriptions['account'], descriptions['units'])}
            load_instant = {k: v for k, v in zip(df_instant['account'], df_instant['instant'])}

            accounts = pd.DataFrame(df_facts['account'].value_counts())
            accounts['description'] = accounts.index.map(load)
            accounts['taxonomy'] = accounts.index.map(load_taxonomy)
            accounts['units'] = accounts.index.map(load_units)
            accounts['instant'] = accounts.index.map(load_instant).astype(int)
            df_all = pd.concat([df_all, accounts])
        except Exception:
            problematic.append(cik)
            continue

    df_all = df_all.drop_duplicates()
    Path(relative_path).mkdir(parents=True, exist_ok=True)
    df_all.to_excel(os.path.join(relative_path, 'accounts.xlsx'))


# ---------------- Instant dict ---------------- #

def _build_instant_dict() -> Dict[str, tuple[int, str, str]]:
    # Use accounts catalog
    accounts = return_accounts()
    mapping: Dict[str, tuple[int, str, str]] = {}
    for clean, meta in accounts.items():
        mapping[clean] = (int(meta['instant']), meta['units'], meta['taxonomy'])
    # Ensure NetIncomeLoss is a period measure
    mapping['NetIncomeLoss'] = (0, 'USD', 'us-gaap')
    return mapping

_INSTANT_DICT: Dict[str, tuple[int, str, str]] | None = None

def get_instant_dict() -> Dict[str, tuple[int, str, str]]:
    global _INSTANT_DICT
    if _INSTANT_DICT is None:
        _INSTANT_DICT = _build_instant_dict()
    return _INSTANT_DICT


# ---------------- CIK tickers and company names ---------------- #

def get_cik_tickers() -> Dict[str, list[str]]:
    mapping = StockMapper().cik_to_tickers
    # Convert sets to lists and keys to str (no leading zeros)
    out: Dict[str, list[str]] = {}
    for k, v in mapping.items():
        out[str(int(k))] = list(v)
    return out


def get_cik_company_names(relative_path: str | None = None) -> None:
    """Fetch company names for all CIKs and save to cache as cik_company_names.json."""
    if relative_path is None:
        relative_path = CACHE_DIR

    ciks = [int(str(c).lstrip('0')) for c in StockMapper().cik_to_tickers.keys()]
    names: Dict[str, str] = {}
    for cik in ciks:
        try:
            facts = get_company_facts(cik)
            names[str(cik)] = facts.get('entityName')
        except Exception:
            continue
    with open(os.path.join(relative_path, 'cik_company_names.json'), 'w') as f:
        json.dump(names, f)


def return_company_names(relative_path: str | None = None) -> Dict[str, str]:
    if relative_path is None:
        relative_path = CACHE_DIR
    path = os.path.join(relative_path, 'cik_company_names.json')
    if not os.path.exists(path):
        get_cik_company_names(relative_path)
    with open(path, 'r') as f:
        return json.load(f)


# ---------------- SIC mapping ---------------- #

def cik_sic_table(relative_path: str | None = None) -> None:
    if relative_path is None:
        relative_path = CACHE_DIR
    ciks = [int(str(c).lstrip('0')) for c in StockMapper().cik_to_tickers.keys()]
    mapping: Dict[str, Any] = {}
    for cik in ciks:
        time.sleep(0.05)
        try:
            mapping[str(cik)] = get_submission_history(cik).get('sic')
        except Exception:
            continue
    with open(os.path.join(relative_path, 'cik_sic.json'), 'w') as f:
        json.dump(mapping, f)


def return_cik_sic(relative_path: str | None = None) -> Dict[str, Any]:
    if relative_path is None:
        relative_path = CACHE_DIR
    path = os.path.join(relative_path, 'cik_sic.json')
    if not os.path.exists(path):
        cik_sic_table(relative_path)
    with open(path, 'r') as f:
        return json.load(f)


# ---------------- Company facts helpers ---------------- #

def df_company_facts(dict_: dict) -> pd.DataFrame:
    if 'facts' not in dict_:
        return pd.DataFrame()
    facts = dict_['facts']
    facts_dei = facts.get('dei', {})
    keys_dei = list(facts_dei.keys())
    df = pd.DataFrame()

    for k in keys_dei:
        try:
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
        except Exception:
            continue

    facts_us_gaap = facts.get('us-gaap', {})
    for k in list(facts_us_gaap.keys()):
        try:
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
        except Exception:
            continue
    return df


def identify_cross_variables_from_facts(df_facts: pd.DataFrame, subset: Iterable[str] | None = None) -> pd.DataFrame:
    if subset is None:
        subset = ['account', 'taxonomy', 'units', 'frame']
    df_facts = df_facts[subset].drop_duplicates().dropna(subset=['account'])

    df = pd.DataFrame()
    n_not = 0
    for _idx in range(df_facts.shape[0]):
        row = df_facts.iloc[_idx]
        account = clean_account_name(str(row['account']))
        taxonomy = row['taxonomy']
        units = row['units']
        frame = row['frame']
        try:
            dict_ = get_xbrl_frames(taxonomy, account, units, frame)
        except Exception as e:
            n_not += 1
            continue
        df_frames = pd.DataFrame()
        df_frames['account'] = [account]
        df_frames['taxonomy'] = [taxonomy]
        df_frames['units'] = [units]
        df_frames['nobs'] = [len(dict_.get('data', []))]
        df_frames['frame'] = [frame]
        df = pd.concat([df, df_frames])
    return df


# ---------------- States and location ---------------- #

def get_state_of_companies(relative_path: str | None = None) -> None:
    if relative_path is None:
        relative_path = CACHE_DIR
    all_ciks = return_cik_sic(relative_path).keys()
    states: Dict[str, str] = {}
    for cik in all_ciks:
        time.sleep(0.05)
        try:
            data = get_submission_history(int(cik))
            state = data['addresses']['business']['stateOrCountryDescription']
            states[cik] = state
        except Exception:
            continue
    with open(os.path.join(relative_path, 'states.json'), 'w') as f:
        json.dump(states, f)


def get_companies_similar_location(cik: int, relative_path: str | None = None) -> pd.DataFrame:
    if relative_path is None:
        relative_path = CACHE_DIR
    data = get_submission_history(cik)
    current_state = data['addresses']['business']['stateOrCountryDescription']
    path = os.path.join(relative_path, 'states.json')
    if not os.path.exists(path):
        get_state_of_companies(relative_path)
    with open(path, 'r') as f:
        states = json.load(f)
    ciks = [int(k) for k, v in states.items() if v == current_state]  # Convert back to int
    df = pd.DataFrame(ciks, columns=['cik'])
    df['state'] = current_state
    return df


__all__ = [
    'return_accounts',
    'load_variable_names',
    'get_instant_dict',
    'get_cik_tickers',
    'get_cik_company_names',
    'return_company_names',
    'cik_sic_table',
    'return_cik_sic',
    'df_company_facts',
    'identify_cross_variables_from_facts',
    'get_state_of_companies',
    'get_companies_similar_location',
]
