from pyedgarai import pyedgarai
import time
# test get_submission_history for AAPl
def test_get_submission_history():
    cik = 320193
    response = pyedgarai.get_submission_history(cik)
    assert len(response) > 0

def test_get_company_facts():
    cik = 320193
    response = pyedgarai.get_company_facts(cik)
    assert len(response) > 0

def test_get_company_concept():
    cik = 320193
    taxonomy = "us-gaap"
    tag = "Revenues"
    time.sleep(1)
    response = pyedgarai.get_company_concept(cik, taxonomy, tag)
    assert len(response) > 0

def test_get_xbrl_frames():
    taxonomy = "us-gaap"
    tag = "AccountsPayableCurrent"
    unit = "USD"
    period = "CY2019Q1I"
    response = pyedgarai.get_xbrl_frames(taxonomy, tag, unit, period)
    assert len(response) > 0


