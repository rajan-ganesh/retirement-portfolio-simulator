from datetime import datetime
from typing import Dict

import requests
import yfinance as yf
from IPython.display import display


def _probe_url(url: str) -> None:
    try:
        resp = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
        content_type = resp.headers.get("content-type")
        text_head = resp.text[:200] if resp.text is not None else None
        print(f"[probe] GET {url}")
        print(f"[probe] status={resp.status_code} content-type={content_type}")
        print(f"[probe] body[0:200]={text_head}")
    except Exception as exc:
        print(f"[probe] GET {url} failed: {exc!r}")


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

    _probe_url("https://query1.finance.yahoo.com/v1/test/getcrumb")
    _probe_url("https://query2.finance.yahoo.com/v8/finance/chart/%5ENSEI")

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

        if len(fund_data) == 0:
            encoded = requests.utils.quote(ticker_symbol, safe="")
            _probe_url(f"https://query2.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1mo")

    return {
        "data_by_ticker": all_fetched_fund_data,
        "fetch_start_date": fetch_start_date,
        "fetch_end_date": fetch_end_date,
    }
