"""Shared utilities for cleaning and small helpers."""
from __future__ import annotations

import re


def modify_name_if_needed(name: str) -> str:
    if name == "Longterm Debt Excluding Current Maturities":
        return "Long Term Debt Noncurrent"
    return name


def process(element: str) -> str:
    element = element.strip()
    s = element.split(" ")
    s = [word.capitalize() if word and word[0].islower() else word for word in s]
    return " ".join(s)


def clean_account_name(account: str) -> str:
    """Clean account name by removing special characters and formatting."""
    if not account:
        return ""
    
    account = (
        account.replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .replace("Attributable to Parent", "")
        .replace("-", "")
        .replace(".", "")
        .replace(":", "")
        .replace(";", "")
        .replace("!", "")
        .replace("@", "")
        .replace("#", "")
        .replace("$", "")
        .replace("%", "")
        .replace("^", "")
        .replace("&", "")
        .replace("*", "")
    )
    try:
        account = process(account)
        account = modify_name_if_needed(account)
    except Exception:
        pass
    
    # Remove any remaining non-alphanumeric characters except spaces
    account = re.sub(r'[^a-zA-Z0-9\s]', '', account)
    return account.replace(" ", "")


def clean_df_bad_endings(df, bad_endings=None):
    """Remove columns with bad endings like _x, _y or custom endings."""
    if bad_endings is None:
        bad_endings = ["_x", "_y"]
    
    to_drop = [col for col in df.columns if any(col.endswith(ending) for ending in bad_endings)]
    return df.drop(columns=to_drop) if to_drop else df


__all__ = [
    "modify_name_if_needed",
    "process",
    "clean_account_name",
    "clean_df_bad_endings",
]
