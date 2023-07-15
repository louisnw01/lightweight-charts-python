"""Shared Test Fixtures"""
import pathlib
import pytest
import pandas as pd

OHLC_PATH = pathlib.Path(__file__).parent/"ohlcv.csv"
NEXT_OHLC_PATH = pathlib.Path(__file__).parent/"ohlcv.csv"

@pytest.fixture
def ohlcv():
    return pd.read_csv(OHLC_PATH)

@pytest.fixture
def next_ohlcv():
    return pd.read_csv(NEXT_OHLC_PATH)
    