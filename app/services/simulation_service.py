from typing import Any, Dict

from app.services.data_fetcher import fetch_historical_data
from app.services.input_scenarios import prepare_simulation_inputs
from app.services.strategy_engine import run_strategy_simulations
from app.services.visualization import plot_monthly_draw_results, plot_simulation_results
from app.services.validation import run_all_validations


def run_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:

    prepared_inputs = prepare_simulation_inputs(payload)
    historical_data = fetch_historical_data(
        fund_to_ticker=prepared_inputs["fund_to_ticker"],
        start_year=prepared_inputs["start_year"],
        end_year=prepared_inputs["end_year"],
    )
    run_all_validations(
        simulation_scenarios=prepared_inputs["simulation_scenarios"],
        fund_to_ticker=prepared_inputs["fund_to_ticker"],
        all_fetched_fund_data=historical_data["data_by_ticker"],
        start_year=prepared_inputs["start_year"],
        end_year=prepared_inputs["end_year"],
        annual_draw_rate=prepared_inputs["annual_draw_rate"],
        inflation_rate=prepared_inputs["inflation_rate"],
    )
    simulation_outputs = run_strategy_simulations(
        simulation_scenarios=prepared_inputs["simulation_scenarios"],
        all_fetched_fund_data=historical_data["data_by_ticker"],
        initial_corpus=prepared_inputs["initial_corpus"],
        start_year=prepared_inputs["start_year"],
        end_year=prepared_inputs["end_year"],
        annual_draw_rate=prepared_inputs["annual_draw_rate"],
        inflation_rate=prepared_inputs["inflation_rate"],
    )
    monthly_draw_fig = plot_monthly_draw_results(
        initial_corpus=prepared_inputs["initial_corpus"],
        annual_draw_rate=prepared_inputs["annual_draw_rate"],
        inflation_rate=prepared_inputs["inflation_rate"],
        start_year=prepared_inputs["start_year"],
        end_year=prepared_inputs["end_year"],
    )
    simulation_results_fig = plot_simulation_results(
        simulation_results_dict=simulation_outputs,
        simulation_scenarios=prepared_inputs["simulation_scenarios"],
        initial_corpus=prepared_inputs["initial_corpus"],
        annual_draw_rate=prepared_inputs["annual_draw_rate"],
        inflation_rate=prepared_inputs["inflation_rate"],
    )

    return {
        "inputs": prepared_inputs,
        "historical_data": historical_data,
        "validation": {"status": "passed"},
        "simulation_results": simulation_outputs,
        "visualizations": {
            "monthly_draw": monthly_draw_fig.to_json(),
            "simulation_outcomes": simulation_results_fig.to_json(),
        },
    }
