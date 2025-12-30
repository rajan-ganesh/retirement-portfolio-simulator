from abc import ABC, abstractmethod
from typing import Dict, Type

import pandas as pd  # noqa: F401  # preserved from notebook context
from IPython.display import display


class InvestmentStrategy(ABC):
    """
    Abstract Base Class for investment simulation strategies.
    Concrete strategies must implement `simulate`.
    """

    @abstractmethod
    def simulate(
        self,
        input,
        all_fetched_fund_data,
        initial_corpus,
        start_year,
        end_year,
        annual_draw_rate,
        inflation_rate,
    ):
        raise NotImplementedError


class SingleFundStrategy(InvestmentStrategy):
    """
    Simulates a FIRE plan with a single selected fund, applying historical returns
    and inflation-adjusted monthly withdrawals.
    """

    def simulate(
        self,
        input,
        all_fetched_fund_data,
        initial_corpus,
        start_year,
        end_year,
        annual_draw_rate,
        inflation_rate,
    ):
        fund = input['funds'][0]
        fund_name = fund['name']
        ticker = fund['ticker']
        historical_data = all_fetched_fund_data[ticker]

        start_date = pd.Timestamp(year=start_year, month=1, day=1)
        end_date = pd.Timestamp(year=end_year, month=12, day=31)
        simulation_months = pd.date_range(start=start_date, end=end_date, freq='MS')

        simulation_results = []
        current_corpus = initial_corpus

        monthly_returns = historical_data['Close'].pct_change()

        for month_start in simulation_months:
            current_year = month_start.year

            monthly_return = monthly_returns.get(month_start)
            if pd.isna(monthly_return):
                monthly_return = 0.0

            corpus_at_start_of_month = current_corpus

            inflation_adjusted_annual_draw = initial_corpus * annual_draw_rate * ((1 + inflation_rate) ** (current_year - start_year))
            monthly_draw = inflation_adjusted_annual_draw / 12

            corpus_after_growth = corpus_at_start_of_month * (1 + monthly_return)

            corpus_at_end_of_month = corpus_after_growth - monthly_draw

            simulation_results.append({
                'YearMonth': month_start.strftime('%Y-%m'),
                'Starting Corpus': corpus_at_start_of_month,
                'Monthly Return': monthly_return,
                'Monthly Draw': monthly_draw,
                'Corpus After Growth': corpus_after_growth,
                'Ending Corpus': corpus_at_end_of_month
            })
            current_corpus = corpus_at_end_of_month

        return pd.DataFrame(simulation_results)


class RebalancingStrategy(InvestmentStrategy):
    """
    Multi-fund strategy:
    - Allocate initial corpus by target weights
    - Apply monthly returns fund-by-fund
    - At year-end: withdraw inflation-adjusted annual amount, then rebalance
    """

    def simulate(
        self,
        input,
        all_fetched_fund_data,
        initial_corpus,
        start_year,
        end_year,
        annual_draw_rate,
        inflation_rate,
    ):
        funds = input['funds']

        start_date = pd.Timestamp(year=start_year, month=1, day=1)
        end_date = pd.Timestamp(year=end_year, month=12, day=31)
        simulation_months = pd.date_range(start=start_date, end=end_date, freq='MS')

        fund_monthly_returns = {}
        for fund in funds:
            fund_name = fund['name']
            ticker = fund['ticker']
            historical_data = all_fetched_fund_data[ticker]

            close_prices = historical_data['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]

            monthly_return = close_prices.pct_change()
            fund_monthly_returns[fund_name] = monthly_return

        holdings = {fund['name']: initial_corpus * fund['weight'] for fund in funds}

        base_annual_draw = initial_corpus * annual_draw_rate
        simulation_results = []

        for month_start in simulation_months:
            current_year = month_start.year

            corpus_at_start_of_month = sum(holdings.values())

            corpus_after_growth = 0.0
            weighted_return_numerator = 0.0

            for fund in funds:
                fund_name = fund['name']

                monthly_return = fund_monthly_returns[fund_name].get(month_start)
                if pd.isna(monthly_return):
                    monthly_return = 0.0

                starting_holding = holdings[fund_name]
                ending_holding = starting_holding * (1 + monthly_return)
                holdings[fund_name] = ending_holding

                corpus_after_growth += ending_holding
                weighted_return_numerator += starting_holding * monthly_return

            monthly_return_portfolio = (
                weighted_return_numerator / corpus_at_start_of_month if corpus_at_start_of_month else 0.0
            )

            is_december = (month_start.month == 12)
            monthly_draw_reported = 0.0

            if is_december:
                annual_draw = base_annual_draw * ((1 + inflation_rate) ** (current_year - start_year))
                monthly_draw_reported = annual_draw / 12.0

                corpus_after_withdraw = corpus_after_growth - annual_draw

                for fund in funds:
                    fund_name = fund['name']
                    holdings[fund_name] = corpus_after_withdraw * fund['weight']

            corpus_at_end_of_month = sum(holdings.values())

            simulation_results.append({
                'YearMonth': month_start.strftime('%Y-%m'),
                'Starting Corpus': corpus_at_start_of_month,
                'Monthly Return': monthly_return_portfolio,
                'Monthly Draw': monthly_draw_reported,
                'Corpus After Growth': corpus_after_growth,
                'Ending Corpus': corpus_at_end_of_month
            })

        return pd.DataFrame(simulation_results)


def run_strategy_simulations(
    simulation_scenarios,
    all_fetched_fund_data,
    initial_corpus,
    start_year,
    end_year,
    annual_draw_rate,
    inflation_rate,
):
    simulation_outputs_to_plot = {}

    strategy_map: Dict[str, Type[InvestmentStrategy]] = {
        'Single Fund Strategy': SingleFundStrategy,
        'Rebalancing Strategy': RebalancingStrategy,
    }

    for i, scenario in enumerate(simulation_scenarios):
        scenario_name = f"Scenario {i+1}: {scenario['strategy_type']}"

        strategy_class = strategy_map.get(scenario['strategy_type'])

        if strategy_class is None:
            print(f"Error: Unknown strategy type '{scenario['strategy_type']}'. Skipping scenario.")
            continue

        current_strategy_simulator = strategy_class()
        scenario_output_df = current_strategy_simulator.simulate(
            input=scenario,
            all_fetched_fund_data=all_fetched_fund_data,
            initial_corpus=initial_corpus,
            start_year=start_year,
            end_year=end_year,
            annual_draw_rate=annual_draw_rate,
            inflation_rate=inflation_rate,
        )
        simulation_outputs_to_plot[scenario_name] = scenario_output_df

        print(f"--- Simulation results for {scenario_name} ---")
        display(scenario_output_df.head())
        print("\n")

    print("All simulations complete.")
    return simulation_outputs_to_plot
