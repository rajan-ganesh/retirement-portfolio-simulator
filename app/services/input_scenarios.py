from typing import Any, Dict, List

import pandas as pd  # noqa: F401  # preserved from notebook

from app.services.fund_catalog import get_available_funds

REQUIRED_FIELDS = [
    "simulation_scenarios",
    "start_year",
    "end_year",
    "annual_draw_rate",
    "initial_corpus",
    "inflation_rate",
]


def prepare_simulation_inputs(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    simulation_scenarios: List[Dict[str, Any]] = payload["simulation_scenarios"]
    start_year = payload["start_year"]
    end_year = payload["end_year"]
    annual_draw_rate = payload["annual_draw_rate"]
    initial_corpus = payload["initial_corpus"]
    inflation_rate = payload["inflation_rate"]

    available_funds = get_available_funds()
    fund_to_ticker = dict(zip(available_funds['Fund Name'], available_funds['Ticker']))

    for scenario in simulation_scenarios:
        for scenario_fund in scenario['funds']:
            fund_name = scenario_fund['name']
            scenario_fund['ticker'] = fund_to_ticker[fund_name]

    print(f"Simulation Period: {start_year} to {end_year}")
    print(f"Initial Corpus: {initial_corpus:,.2f}")
    print(f"Initial Draw Rate: {annual_draw_rate*100}%")
    print(f"Inflation Rate: {inflation_rate*100}%\n")
    print(f"Fund to Ticker: {fund_to_ticker}")

    return {
        "simulation_scenarios": simulation_scenarios,
        "start_year": start_year,
        "end_year": end_year,
        "annual_draw_rate": annual_draw_rate,
        "initial_corpus": initial_corpus,
        "inflation_rate": inflation_rate,
        "fund_to_ticker": fund_to_ticker,
    }
