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


def identify_comparables_private(name: str, sic_code: str, profitability: float, 
                               growth_rate: float, capital_structure: float) -> Dict[str, Any]:
    """
    Find comparable public companies for a private company based on financial metrics.
    
    Args:
        name: Name of the private company
        sic_code: Two-digit SIC code for sector filtering
        profitability: ROA (net income / assets)
        growth_rate: Asset growth rate over last 5 years
        capital_structure: Debt-to-equity ratio
        
    Returns:
        Dictionary containing target company info and list of 5 closest comparables
        with market data and financial ratios
    """
    logger.info("Finding private company comparables for %s in SIC sector %s", name, sic_code)
    
    # Validate input data
    if not all(isinstance(x, (int, float)) for x in [profitability, growth_rate, capital_structure]):
        return {
            "target_company": {"name": name, "sic_code": sic_code},
            "comparables": [],
            "total_found": 0,
            "method": "private_comparables",
            "sic_sector": sic_code,
            "error": "Invalid input data: all financial metrics must be numeric"
        }
    
    # Check for reasonable ranges
    if not (0 <= profitability <= 1):  # ROA should be between 0 and 100%
        logger.warning("Profitability %f seems outside normal range [0, 1]", profitability)
    
    if not (-1 <= growth_rate <= 5):  # Growth rate should be reasonable
        logger.warning("Growth rate %f seems outside normal range [-1, 5]", growth_rate)
    
    if capital_structure < 0:  # Debt/equity should be non-negative
        logger.warning("Capital structure %f is negative", capital_structure)
    
    # Get all data for public companies
    df_size = get_all_size()
    df_profit = get_all_profitability() 
    df_growth = get_all_growth_rate()
    df_capital = get_all_capital_structure()
    
    # Ensure CIK columns are integers
    for df in [df_size, df_profit, df_growth, df_capital]:
        df['cik'] = df['cik'].astype(int)
    
    # Filter by SIC sector (2-digit)
    sic_int = int(sic_code)
    df_industry = get_companies_in_sic(sic_int, digits=2)
    df_industry['cik'] = df_industry['cik'].astype(int)
    
    if len(df_industry) == 0:
        logger.warning("No companies found in SIC sector %s", sic_code)
        return {
            "target_company": {
                "name": name,
                "sic_code": sic_code,
                "profitability": profitability,
                "growth_rate": growth_rate,
                "capital_structure": capital_structure
            },
            "comparables": [],
            "total_found": 0,
            "method": "private_comparables",
            "sic_sector": sic_code,
            "error": f"No companies found in SIC sector {sic_code}"
        }
    
    # Merge all financial data
    df = df_size
    df = pd.merge(df, df_profit, on='cik', how='inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_growth, on='cik', how='inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_capital, on='cik', how='inner', suffixes=('', '_drop'))
    df = pd.merge(df, df_industry, on='cik', how='inner', suffixes=('', '_drop'))
    
    # Clean up duplicate columns
    df = df[['cik', 'sic', 'entityName', 'assets', 'profitability', 'growth_rate', 'debt_to_equity']]
    
    # Remove any rows with missing data
    df = df.dropna(subset=['profitability', 'growth_rate', 'debt_to_equity'])
    
    # Clean financial data - remove infinite values and extreme outliers
    def clean_financial_data(df, variables):
        """Clean financial data by removing inf/nan values and extreme outliers"""
        df_clean = df.copy()
        
        for var in variables:
            if var in df_clean.columns:
                # Replace infinite values with NaN
                df_clean[var] = df_clean[var].replace([float('inf'), float('-inf')], float('nan'))
                
                # Remove extreme outliers (beyond 99.5th percentile or below 0.5th percentile)
                if not df_clean[var].isna().all():
                    q005 = df_clean[var].quantile(0.005)
                    q995 = df_clean[var].quantile(0.995)
                    df_clean = df_clean[
                        (df_clean[var] >= q005) & 
                        (df_clean[var] <= q995) & 
                        (df_clean[var].notna())
                    ]
        
        return df_clean
    
    variables = ['profitability', 'growth_rate', 'debt_to_equity']
    df = clean_financial_data(df, variables)
    
    # Final check for remaining data
    df = df.dropna(subset=variables)
    
    # Debug: Log data statistics
    logger.info("Data after cleaning: %d companies in SIC %s", len(df), sic_code)
    if len(df) > 0:
        for var in variables:
            if var in df.columns:
                logger.info("Variable %s: min=%.4f, max=%.4f, mean=%.4f", 
                           var, df[var].min(), df[var].max(), df[var].mean())
    
    if len(df) == 0:
        logger.warning("No companies with clean financial data in SIC sector %s", sic_code)
        return {
            "target_company": {
                "name": name,
                "sic_code": sic_code,
                "profitability": profitability,
                "growth_rate": growth_rate,
                "capital_structure": capital_structure
            },
            "comparables": [],
            "total_found": 0,
            "method": "private_comparables", 
            "sic_sector": sic_code,
            "error": f"No companies with clean financial data in SIC sector {sic_code}"
        }
    
    # Define variables for distance calculation
    variables = ['profitability', 'growth_rate', 'debt_to_equity']
    
    # Standardize the variables
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[variables] = scaler.fit_transform(df[variables])
    
    # Create target company data point
    target_data = pd.DataFrame({
        'profitability': [profitability],
        'growth_rate': [growth_rate], 
        'debt_to_equity': [capital_structure]
    })
    target_scaled = scaler.transform(target_data)
    
    # Calculate distances using KNN
    nn = NearestNeighbors(n_neighbors=min(5, len(df)), metric='euclidean')
    nn.fit(df_scaled[variables])
    distances, indices = nn.kneighbors(target_scaled)
    
    # Get the closest companies
    closest_companies = df.iloc[indices[0]].copy()
    closest_companies['distance'] = distances[0]
    
    # Get CIK to ticker mapping
    cik_tickers = get_cik_tickers()
    
    # Build results with market data (only for the top 5 selected companies)
    comparables = []
    
    # Simple cache to avoid duplicate calls for same ticker
    market_data_cache = {}
    
    for _, company in closest_companies.iterrows():
        cik = int(company['cik'])
        
        # Format CIK with leading zeros to match StockMapper format (10 digits)
        cik_padded = f"{cik:010d}"
        
        # Get ticker for market data using the padded CIK format
        tickers = cik_tickers.get(cik_padded, [])
        # Convert set to list if needed
        if isinstance(tickers, set):
            tickers = list(tickers)
        primary_ticker = tickers[0] if tickers else None
        
        comparable = {
            "cik": cik,
            "name": company['entityName'],
            "ticker": primary_ticker,
            "sic": str(company['sic']),
            "profitability": float(company['profitability']),
            "growth_rate": float(company['growth_rate']),
            "capital_structure": float(company['debt_to_equity']),
            "distance": float(company['distance'])
        }
        
        # Add market data if ticker is available (using cache to avoid duplicate calls)
        if primary_ticker:
            # Check cache first
            if primary_ticker in market_data_cache:
                market_data = market_data_cache[primary_ticker]
                comparable.update(market_data)
            else:
                try:
                    import yfinance as yf
                    import json
                    import time
                    from . import yfinance_endpoints as yf_e
                    
                    # Initialize market data structure with all available yfinance fields
                    market_data = {
                        # Keep the original fields for backward compatibility
                        "market_cap": None,
                        "enterprise_value": None,
                        "price_to_book": None,
                        "enterprise_to_ebitda": None,
                        "current_price": None,
                        "price_to_earnings": None,
                        # Add all yfinance info fields
                        "yfinance_data": {}
                    }
                    
                    # Add longer delay to avoid Yahoo Finance rate limiting (only for non-cached calls)
                    time.sleep(2.0)  # Increased to 2 seconds delay between calls
                    
                    # Get market data directly from yfinance (simpler approach)
                    import yfinance as yf
                    ticker_obj = yf.Ticker(primary_ticker)
                    info = ticker_obj.info
                    
                    if info and isinstance(info, dict):
                        # Store all yfinance data
                        market_data["yfinance_data"] = info
                        
                        # Keep backward compatibility with original fields
                        market_data.update({
                            "market_cap": info.get('marketCap'),
                            "enterprise_value": info.get('enterpriseValue'),
                            "price_to_book": info.get('priceToBook'),
                            "enterprise_to_ebitda": info.get('enterpriseToEbitda'),
                            "current_price": info.get('currentPrice'),
                            "price_to_earnings": info.get('trailingPE')  # Use trailingPE directly
                        })
                        
                        logger.info("Successfully retrieved %d yfinance fields for %s", len(info), primary_ticker)
                    else:
                        logger.warning("No info data returned for %s", primary_ticker)
                    
                    # Cache the result (whether successful or not)
                    market_data_cache[primary_ticker] = market_data
                    comparable.update(market_data)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Too Many Requests" in error_msg:
                        logger.warning("Rate limited by Yahoo Finance for %s. Implementing backoff delay...", primary_ticker)
                        # Exponential backoff: wait longer and try once more
                        time.sleep(5.0)  # Wait 5 seconds for rate limit to reset
                        try:
                            # Single retry attempt with direct yfinance
                            ticker_obj = yf.Ticker(primary_ticker)
                            info = ticker_obj.info
                            if info and isinstance(info, dict):
                                market_data["yfinance_data"] = info
                                market_data.update({
                                    "market_cap": info.get('marketCap'),
                                    "enterprise_value": info.get('enterpriseValue'),
                                    "price_to_book": info.get('priceToBook'),
                                    "enterprise_to_ebitda": info.get('enterpriseToEbitda'),
                                    "current_price": info.get('currentPrice'),
                                    "price_to_earnings": info.get('trailingPE')
                                })
                                logger.info("Successfully retrieved market data for %s on retry", primary_ticker)
                        except Exception as retry_error:
                            logger.warning("Retry also failed for %s: %s", primary_ticker, str(retry_error))
                    else:
                        logger.warning("Could not get market data for %s: %s", primary_ticker, error_msg)
                    
                    # Cache the result (whether successful or not) to avoid repeated failures
                    market_data_cache[primary_ticker] = market_data
                    comparable.update(market_data)
        else:
            # No ticker available, add None values for market data
            comparable.update({
                "market_cap": None,
                "enterprise_value": None,
                "price_to_book": None,
                "enterprise_to_ebitda": None,
                "current_price": None,
                "price_to_earnings": None,
                "yfinance_data": {}
            })
        
        comparables.append(comparable)
    
    # Sort by distance (should already be sorted, but ensure it)
    comparables.sort(key=lambda x: x['distance'])
    
    result = {
        "target_company": {
            "name": name,
            "sic_code": sic_code,
            "profitability": profitability,
            "growth_rate": growth_rate,
            "capital_structure": capital_structure
        },
        "comparables": comparables,
        "total_found": len(comparables),
        "method": "private_comparables",
        "sic_sector": sic_code
    }
    
    logger.info("Found %d comparable companies for %s", len(comparables), name)
    return result


__all__ = [
    "identify_comparables",
    "identify_comparables_ml",
    "identify_comparables_private",
    "get_companies_with_same_sic",
    "get_companies_in_sic",
    "get_companies_similar_size",
    "get_companies_similar_profitability",
    "get_companies_similar_growth_rate",
    "get_companies_similar_capital_structure",
]
