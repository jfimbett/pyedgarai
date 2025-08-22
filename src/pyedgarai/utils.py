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
    account = (
        account.replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .replace("Attributable to Parent", "")
        .replace("-", "")
    )
    try:
        account = process(account)
        account = modify_name_if_needed(account)
    except Exception:
        pass
    return account.replace(" ", "")


def clean_df_bad_endings(df):
    to_drop = [col for col in df.columns if col.endswith("_x") or col.endswith("_y")]
    return df.drop(columns=to_drop) if to_drop else df


__all__ = [
    "modify_name_if_needed",
    "process",
    "clean_account_name",
    "clean_df_bad_endings",
]
