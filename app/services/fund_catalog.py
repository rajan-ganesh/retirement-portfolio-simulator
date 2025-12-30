import pandas as pd
import yfinance as yf  # noqa: F401  # imported to mirror notebook environment
from IPython.display import display

_AVAILABLE_FUNDS_DF = None


def build_available_funds():
    available_funds = pd.DataFrame({
        'Fund Name': ['Nifty 50 Index', 'SBI Large Cap Reg Gr', 'SBI Debt Fund', 'HDFC liquid fund', 'HDFC Small Cap Growth', 'Apple', 'NASDAQ', 'Treasury Bond', 'Nippon India Small Cap'],
        'Ticker': ['^NSEI', '0P00005WF0.BO', '0P0001DDNG.BO', '0P0000XW89.BO', '0P0000AEKG.BO', 'AAPL', '^IXIC', 'TLT', '0P0000XVFY.BO']
    })

    display(available_funds)
    print("Available funds loaded into memory")

    return available_funds


def initialize_available_funds():
    global _AVAILABLE_FUNDS_DF
    if _AVAILABLE_FUNDS_DF is None:
        _AVAILABLE_FUNDS_DF = build_available_funds()
    return _AVAILABLE_FUNDS_DF


def get_available_funds():
    if _AVAILABLE_FUNDS_DF is None:
        return initialize_available_funds()
    return _AVAILABLE_FUNDS_DF.copy()
