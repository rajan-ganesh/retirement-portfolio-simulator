from datetime import datetime
from typing import Dict

import yfinance as yf
from IPython.display import display


def fetch_historical_data(
    fund_to_ticker: Dict[str, str],
    start_year: int,
    end_year: int,
) -> Dict[str, object]:
    all_fetched_fund_data: Dict[str, object] = {}
    unique_tickers_to_fetch = set(fund_to_ticker.values())

    fetch_start_date = f"{start_year}-01-01"
    fetch_end_date = datetime.now().strftime('%Y-%m-%d')

    if end_year < datetime.now().year:
        fetch_end_date = f"{end_year}-12-31"

    for ticker_symbol in unique_tickers_to_fetch:
        print(f"Fetching data for {ticker_symbol} from {fetch_start_date} to {fetch_end_date} (monthly interval)...")
        fund_data = yf.download(ticker_symbol, start=fetch_start_date, end=fetch_end_date, interval="1mo")
        all_fetched_fund_data[ticker_symbol] = fund_data

        print(f"--- Data for {ticker_symbol} ---")
        display(fund_data.head())
        print(f"Number of monthly entries fetched: {len(fund_data)}\n")

    return {
        "data_by_ticker": all_fetched_fund_data,
        "fetch_start_date": fetch_start_date,
        "fetch_end_date": fetch_end_date,
    }
