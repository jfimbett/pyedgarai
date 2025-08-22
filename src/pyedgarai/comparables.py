"""Comparable companies helpers."""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from .sec_client import get_xbrl_frames
from .utils import clean_account_name, clean_df_bad_endings
from .features import (
    return_cik_sic,
    return_company_names,
    get_cik_tickers,
    get_companies_similar_location,
    get_instant_dict,
)

logger = logging.getLogger(__name__)


def _current_year() -> int:
    return time.localtime().tm_year


def get_all_size() -> pd.DataFrame:
    data = get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", "CY2024Q1I")
    df = pd.DataFrame(data["data"]).rename(columns={"val": "assets"})
    return df


def get_all_profitability() -> pd.DataFrame:
    size = get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", "CY2024Q1I")
    profit = get_xbrl_frames("us-gaap", clean_account_name("NetIncomeLoss"), "USD", "CY2024Q1")
    df_size = pd.DataFrame(size["data"]).rename(columns={"val": "assets"})
    df_profit = pd.DataFrame(profit["data"]).rename(columns={"val": "profit"})
    df = pd.merge(df_size, df_profit, on="cik")
    df["profitability"] = df["profit"] / df["assets"]
    return df.drop(columns=["assets", "profit"]) 


def get_all_growth_rate() -> pd.DataFrame:
    cy = _current_year()
    size_now = get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", f"CY2024Q1I")
    size_5 = get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", f"CY{cy-5}Q1I")
    df_now = pd.DataFrame(size_now["data"])[["cik", "val"]].rename(columns={"val": "assets"})
    df_5 = pd.DataFrame(size_5["data"])[["cik", "val"]].rename(columns={"val": "assets_5"})
    df = pd.merge(df_now, df_5, on="cik")
    df["growth_rate"] = (df["assets"] - df["assets_5"]) / df["assets_5"]
    return df.drop(columns=["assets", "assets_5"]) 


def get_all_capital_structure() -> pd.DataFrame:
    eq = get_xbrl_frames("us-gaap", clean_account_name("StockholdersEquity"), "USD", "CY2024Q1I")
    li = get_xbrl_frames("us-gaap", clean_account_name("Liabilities"), "USD", "CY2024Q1I")
    df_e = pd.DataFrame(eq["data"]) [["cik", "val"]].rename(columns={"val": "equity"})
    df_l = pd.DataFrame(li["data"]) [["cik", "val"]].rename(columns={"val": "liabilities"})
    df = pd.merge(df_e, df_l, on="cik")
    df["debt_to_equity"] = df["liabilities"] / df["equity"]
    return df.drop(columns=["equity", "liabilities"]) 


# Public APIs originally provided

def get_companies_similar_size(cik: int, interval: int = 100) -> pd.DataFrame:
    df = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", "CY2024Q1I")["data"])
    size = df[df["cik"] == cik]["val"].values[0]
    lb, ub = size * (1 - interval / 100), size * (1 + interval / 100)
    return df[(df["val"] >= lb) & (df["val"] <= ub)]


def get_companies_similar_profitability(cik: int, interval: int = 100) -> pd.DataFrame:
    df_size = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", "CY2024Q1I")["data"])
    df_profit = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("NetIncomeLoss"), "USD", "CY2024Q1")["data"])
    size = df_size[df_size["cik"] == cik]["val"].values[0]
    profit = df_profit[df_profit["cik"] == cik]["val"].values[0]
    df = pd.merge(df_size.rename(columns={"val": "assets"}), df_profit.rename(columns={"val": "profit"}), on="cik")
    df["profitability"] = df["profit"] / df["assets"]
    p = profit / size
    lb, ub = p * (1 - interval / 100), p * (1 + interval / 100)
    return df[(df["profitability"] >= lb) & (df["profitability"] <= ub)]


def get_companies_similar_growth_rate(cik: int, interval: int = 100) -> pd.DataFrame:
    cy = _current_year()
    df_now = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", f"CY2024Q1I")["data"]) \
        [["cik", "val"]].rename(columns={"val": "assets"})
    df_5 = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("Assets"), "USD", f"CY{cy-5}Q1I")["data"]) \
        [["cik", "val"]].rename(columns={"val": "assets_5"})
    size, size_5 = df_now[df_now["cik"] == cik]["assets"].values[0], df_5[df_5["cik"] == cik]["assets_5"].values[0]
    gr = (size - size_5) / size_5
    lb, ub = gr - (interval / 100), gr + (interval / 100)
    df = pd.merge(df_now, df_5, on="cik")
    df["growth_rate"] = (df["assets"] - df["assets_5"]) / df["assets_5"]
    return df[(df["growth_rate"] >= lb) & (df["growth_rate"] <= ub)]


def get_companies_similar_capital_structure(cik: int, interval: int = 100) -> pd.DataFrame:
    df_e = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("StockholdersEquity"), "USD", "CY2024Q1I")["data"]) \
        [["cik", "val"]].rename(columns={"val": "equity"})
    df_l = pd.DataFrame(get_xbrl_frames("us-gaap", clean_account_name("Liabilities"), "USD", "CY2024Q1I")["data"]) \
        [["cik", "val"]].rename(columns={"val": "liabilities"})
    equity, liab = df_e[df_e["cik"] == cik]["equity"].values[0], df_l[df_l["cik"] == cik]["liabilities"].values[0]
    cs = liab / equity
    lb, ub = cs - (interval / 100), cs + (interval / 100)
    df = pd.merge(df_e, df_l, on="cik")
    df["debt_to_equity"] = df["liabilities"] / df["equity"]
    return df[(df["debt_to_equity"] >= lb) & (df["debt_to_equity"] <= ub)]


# SIC-based comparables retained as-is for now, can be moved to features later
from .pyedgarai import return_cik_sic, return_company_names, get_cik_tickers  # reuse until fully split


def get_companies_in_sic(sic: int, digits: int = 2) -> pd.DataFrame:
    def adjust_sic(sic_):
        try:
            return int(str(sic_)[:digits])
        except Exception:
            return None

    ciks = [k for k, v in return_cik_sic().items() if adjust_sic(v) == adjust_sic(sic)]
    company_names = return_company_names()
    cik_tickers = get_cik_tickers()
    cik_tickers = {str(int(k)): v for k, v in cik_tickers.items()}

    companies = {}
    for cik in ciks:
        name = company_names.get(cik)
        tickers = cik_tickers.get(cik)
        companies[cik] = {"name": name, "tickers": tickers, "sic": adjust_sic(return_cik_sic()[cik])}

    df = pd.DataFrame(companies).T.reset_index().rename(columns={"index": "cik"})
    return df


essential_columns = ["cik"]


def get_companies_with_same_sic(cik: int, digits: int = 1) -> pd.DataFrame:
    sic = return_cik_sic()[str(cik)]

    def adjust_sic(sic_):
        try:
            return int(str(sic_)[:digits])
        except Exception:
            return None

    ciks = [k for k, v in return_cik_sic().items() if adjust_sic(v) == adjust_sic(sic)]
    company_names = return_company_names()
    cik_tickers = get_cik_tickers()
    cik_tickers = {str(int(k)): v for k, v in cik_tickers.items()}

    companies = {}
    for cik_ in ciks:
        name = company_names.get(cik_)
        tickers = cik_tickers.get(cik_)
        companies[cik_] = {"name": name, "tickers": tickers, "sic": adjust_sic(return_cik_sic()[cik_])}

    df = pd.DataFrame(companies).T.reset_index().rename(columns={"index": "cik"})
    return df


# High-level public functions

def identify_comparables(cik: int, **kwargs) -> Dict[str, Any]:
    variables_to_compare = ['industry', 'size', 'profitability', 'growth_rate', 'capital_structure', 'location']
    params_comparables = kwargs.get('params_comparables', {})

    data_frames: List[pd.DataFrame] = []
    labels: List[str] = []

    if 'industry' in variables_to_compare:
        labels.append('industry')
        temp = get_companies_with_same_sic(cik, **params_comparables.get('industry', {}))
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for industry.")
        data_frames.append(temp)

    if 'size' in variables_to_compare:
        labels.append('size')
        temp = get_companies_similar_size(cik, **params_comparables.get('size', {}))
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for size.")
        data_frames.append(temp)

    if 'profitability' in variables_to_compare:
        labels.append('profitability')
        temp = get_companies_similar_profitability(cik, **params_comparables.get('profitability', {}))
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for profitability.")
        data_frames.append(temp)

    if 'growth_rate' in variables_to_compare:
        labels.append('growth_rate')
        temp = get_companies_similar_growth_rate(cik, **params_comparables.get('growth_rate', {}))
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for growth rate.")
        data_frames.append(temp)

    if 'capital_structure' in variables_to_compare:
        labels.append('capital_structure')
        temp = get_companies_similar_capital_structure(cik, **params_comparables.get('capital_structure', {}))
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for capital structure.")
        data_frames.append(temp)

    # Location uses submission history state; now from features
    if 'location' in variables_to_compare:
        labels.append('location')
        temp = get_companies_similar_location(cik)
        temp['cik'] = temp['cik'].astype(int)
        if cik not in temp['cik'].values:
            raise ValueError(f"Company with cik {cik} not found in the dataframe for location.")
        data_frames.append(temp)

    df = data_frames[0]
    logger.info("Step 1: %d observations for %s.", df.shape[0], labels[0])
    for i in range(1, len(data_frames)):
        temp = data_frames[i]
        df = pd.merge(df, temp, on='cik', how='inner', suffixes=('', '_drop'))
        logger.info("Step %d: %d observations for %s. Using has %d observations.", i+1, df.shape[0], labels[i], len(temp))

    df = df[df.columns.drop(list(df.filter(regex='_drop')))]
    df = clean_df_bad_endings(df)

    def get_extra_variables(ciks, var):
        cy = _current_year()
        instant, units, taxonomy = get_instant_dict()[clean_account_name(var)]
        instant_end = 'I' if instant else ''
        units_end = units.replace('/', '-per-')
        units_end = re.sub(r'[A-Z]{3}', 'USD', units_end)
        data = get_xbrl_frames(taxonomy, clean_account_name(var), units_end, f'CY{cy}Q1{instant_end}', verbose=True)
        df_var = pd.DataFrame(data['data'])[['cik', 'val']].rename(columns={'val': var})
        return df_var[df_var['cik'].isin(ciks)]

    # Hardcoded extras kept
    for var in ['GrossProfit', 'NetIncomeLoss', 'EarningsPerShareBasic']:
        temp = get_extra_variables(df['cik'], var)
        df = pd.merge(df, temp, on='cik', how='left')
        df = clean_df_bad_endings(df)

    return json.loads(df.to_json())


def identify_comparables_ml(name, sic, assets, profitability, growth_rate, capital_structure):
    df_size = get_all_size(); df_size['cik'] = df_size['cik'].astype(int)
    df_profit = get_all_profitability(); df_profit['cik'] = df_profit['cik'].astype(int)
    df_growth = get_all_growth_rate(); df_growth['cik'] = df_growth['cik'].astype(int)
    df_capital = get_all_capital_structure(); df_capital['cik'] = df_capital['cik'].astype(int)

    df_industry = get_companies_in_sic(sic, digits=2)
    df_industry['cik'] = df_industry['cik'].astype(int)

    df = df_size
    df = pd.merge(df, df_profit, on='cik', how='inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_growth, on='cik', how='inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_capital, on='cik', how='inner', suffixes=('', '_drop'))

    if len(df_industry) > 0:
        df = pd.merge(df, df_industry, on='cik', how='inner', suffixes=('', '_drop'))

    df = df[['cik', 'sic', 'entityName', 'assets', 'profitability', 'growth_rate', 'debt_to_equity']]
    variables = ['assets', 'profitability', 'growth_rate', 'debt_to_equity']

    current = {
        "cik": 0,
        "sic": sic,
        "entityName": name,
        "assets": assets,
        "profitability": profitability,
        "growth_rate": growth_rate,
        "debt_to_equity": capital_structure,
    }

    current = pd.DataFrame(current, index=[0])
    df = pd.concat([df, current])

    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[variables] = scaler.fit_transform(df[variables])
    df_features = df_scaled[variables]

    nn = NearestNeighbors(n_neighbors=5, metric='euclidean')
    nn.fit(df_features)
    distances, indices = nn.kneighbors(current[variables])

    closest = df.iloc[indices[0]]
    closest = clean_df_bad_endings(closest)

    def get_extra_variables(ciks, var):
        cy = _current_year() - 1
        instant, units, taxonomy = get_instant_dict()[clean_account_name(var)]
        instant_end = 'I' if instant else ''
        units_end = units.replace('/', '-per-')
        units_end = re.sub(r'[A-Z]{3}', 'USD', units_end)
        data = get_xbrl_frames(taxonomy, clean_account_name(var), units_end, f'CY{cy}Q1{instant_end}', verbose=True)
        df_var = pd.DataFrame(data['data'])[['cik', 'val']].rename(columns={'val': var})
        return df_var[df_var['cik'].isin(ciks)]

    for var in ['GrossProfit', 'NetIncomeLoss', 'EarningsPerShareBasic']:
        ciks_exclude_current = [c for c in closest['cik'] if c != 0]
        temp = get_extra_variables(ciks_exclude_current, var)
        closest = pd.merge(closest, temp, on='cik', how='left')
        closest = clean_df_bad_endings(closest)

    return closest.to_json()


__all__ = [
    "identify_comparables",
    "identify_comparables_ml",
    "get_companies_with_same_sic",
    "get_companies_in_sic",
    "get_companies_similar_size",
    "get_companies_similar_profitability",
    "get_companies_similar_growth_rate",
    "get_companies_similar_capital_structure",
]
