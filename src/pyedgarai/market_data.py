"""Market data helpers using yfinance."""
from __future__ import annotations

import logging
from typing import List

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def get_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Retrieve historical OHLCV for one ticker.

    Returns a DataFrame with a 'ticker' column and reset index.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, auto_adjust=False, actions=False)
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df['ticker'] = ticker
    df.reset_index(inplace=True)
    return df


def get_stocks_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Retrieve historical OHLCV for multiple tickers, concatenated."""
    dfs = []
    for ticker in tickers:
        try:
            df = get_stock_data(ticker, start_date, end_date)
            if not df.empty:
                dfs.append(df)
        except Exception:
            logger.warning("Stock %s not found or failed to fetch", ticker)
            continue
    return pd.concat(dfs) if dfs else pd.DataFrame()


__all__ = [
    "get_stock_data",
    "get_stocks_data",
]
