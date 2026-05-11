"""Tests for top-level Research Radar configuration."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config
from fetch_papers_historical import fetch_all_historical


def test_fetch_from_year_is_2015():
    assert config.FETCH_FROM_YEAR == 2015


def test_historical_default_stops_before_current_range():
    assert fetch_all_historical.__defaults__[1] == 2014


def test_new_journals_are_configured():
    journals = {(j["name"], j["issn"]) for j in config.TARGET_JOURNALS}
    assert ("Journal of Fluid Mechanics", "0022-1120") in journals
    assert ("Applied Acoustics", "0003-682X") in journals
    assert ("Journal of Fluids and Structures", "0889-9746") in journals
