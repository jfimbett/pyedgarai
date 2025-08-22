#%%


# %%
import os
import time

import pandas as pd

from pyedgarai import sec_client as sec
from pyedgarai import features as ft
from pyedgarai import market_data as md


APPLE_CIK = 320193  # Apple Inc.


def test_sec_submission_history_has_core_fields():
    data = sec.get_submission_history(APPLE_CIK)
    assert 'cik' in data and 'name' in data


def test_sec_company_facts_and_concept():
    facts = sec.get_company_facts(APPLE_CIK)
    assert 'facts' in facts and isinstance(facts['facts'], dict)

    concept = sec.get_company_concept(APPLE_CIK, 'us-gaap', 'NetIncomeLoss')
    assert concept.get('tag') == 'NetIncomeLoss'
    assert concept.get('taxonomy') == 'us-gaap'


def test_xbrl_frames_assets_cy2024q1i():
    frames = sec.get_xbrl_frames('us-gaap', 'Assets', 'USD', 'CY2024Q1I')
    assert 'data' in frames and isinstance(frames['data'], list)


def test_features_accounts_and_instant_dict():
    accounts = ft.return_accounts()
    assert isinstance(accounts, dict) and len(accounts) > 0

    inst = ft.get_instant_dict()
    assert inst['NetIncomeLoss'][0] == 0


def test_market_data_aapl_recent_range():
    # Use a short recent range; may be empty depending on window
    df = md.get_stock_data('AAPL', '2025-07-01', '2025-07-15')
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert 'Close' in df.columns or 'close' in [c.lower() for c in df.columns]
