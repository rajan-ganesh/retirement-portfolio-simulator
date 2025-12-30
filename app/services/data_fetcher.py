from datetime import datetime
from typing import Dict

import yfinance as yf
from IPython.display import display


def fetch_historical_data(
    simulation_scenarios,
    start_year: int,
    end_year: int,
) -> Dict[str, object]:
    all_fetched_fund_data: Dict[str, object] = {}
    unique_tickers_to_fetch = {
        fund["ticker"]
        for scenario in simulation_scenarios
        for fund in scenario.get("funds", [])
        if fund.get("ticker")
    }

    fetch_start_date = f"{start_year}-01-01"
    fetch_end_date = datetime.now().strftime('%Y-%m-%d')

    if end_year < datetime.now().year:
        fetch_end_date = f"{end_year}-12-31"

    for ticker_symbol in unique_tickers_to_fetch:
        print(f"Fetching data for {ticker_symbol} from {fetch_start_date} to {fetch_end_date} (monthly interval)...")
        try:
            fund_data = yf.download(ticker_symbol, start=fetch_start_date, end=fetch_end_date, interval="1mo")
        except Exception as exc:
            print(f"[yfinance] download failed for {ticker_symbol}: {exc!r}")
            fund_data = None

        if fund_data is None:
            all_fetched_fund_data[ticker_symbol] = fund_data
            continue

        all_fetched_fund_data[ticker_symbol] = fund_data

        print(f"--- Data for {ticker_symbol} ---")
        display(fund_data.head())
        try:
            print(f"shape={fund_data.shape} columns={list(fund_data.columns)}")
        except Exception as exc:
            print(f"[yfinance] could not inspect dataframe for {ticker_symbol}: {exc!r}")
        print(f"Number of monthly entries fetched: {len(fund_data)}\n")

    return {
        "data_by_ticker": all_fetched_fund_data,
        "fetch_start_date": fetch_start_date,
        "fetch_end_date": fetch_end_date,
    }
