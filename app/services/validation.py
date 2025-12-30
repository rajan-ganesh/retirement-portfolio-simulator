import pandas as pd


def validate_simulation_parameters(start_year, end_year, annual_draw_rate, inflation_rate):
    """
    Validates global simulation parameters.
    Raises a ValueError if any validation fails.
    """
    error_messages = []

    if start_year > end_year:
        error_messages.append("Error: Start year cannot be after end year.")

    if not (0 <= annual_draw_rate <= 1):
        error_messages.append(f"Error: Draw rate ({annual_draw_rate*100}%) must be between 0% and 100%.")

    if not (0 <= inflation_rate <= 1):
        error_messages.append(f"Error: Inflation rate ({inflation_rate*100}%) must be between 0% and 100%.")

    if error_messages:
        raise ValueError("\n".join(error_messages))


def validate_single_fund_date_range(fund_data_df, requested_start_year, requested_end_year, fund_name="Selected Fund"):
    """
    Validates if the fetched fund data covers the requested start and end years.
    Raises a ValueError if the date range is insufficient.
    """
    error_messages = []

    if fund_data_df.empty:
        error_messages.append(f"Could not fetch historical data for {fund_name}. Cannot proceed with the simulation.")
        raise ValueError("\n".join(error_messages))

    actual_min_date = fund_data_df.index.min()
    actual_max_date = fund_data_df.index.max()

    requested_start_date_obj = pd.to_datetime(f'{requested_start_year}-01-01')
    requested_end_date_obj = pd.to_datetime(f'{requested_end_year}-01-01')

    if actual_min_date > requested_start_date_obj:
        error_messages.append(
            f"Available data for {fund_name} starts on {actual_min_date.strftime('%Y-%m-%d')}, but requested simulation starts in {requested_start_year}."
        )

    if actual_max_date < requested_end_date_obj:
        error_messages.append(
            f"Available data for {fund_name} ends on {actual_max_date.strftime('%Y-%m-%d')}, but requested simulation needs data up to January 1st, {requested_end_year}."
        )

    if error_messages:
        raise ValueError("\n".join(error_messages))


def validate_scenario(scenario, fund_to_ticker, all_fetched_fund_data):
    """
    Validates a single scenario's structure and funds.
    Raises a ValueError if any validation fails.
    """
    error_messages = []
    strategy_type = scenario.get('strategy_type')
    funds = scenario.get('funds', [])

    if not strategy_type:
        error_messages.append("Error: Scenario missing 'strategy_type'.")

    if not funds:
        error_messages.append(f"Error: Scenario '{strategy_type}' has no funds defined.")

    # Validate each fund has a name and exists in fund_to_ticker
    for i, fund in enumerate(funds):
        fund_name = fund.get('name')
        if not fund_name:
            error_messages.append(f"Error: Fund {i+1} in '{strategy_type}' is missing 'name'.")
            continue

        if fund_name not in fund_to_ticker:
            error_messages.append(f"Error: Fund '{fund_name}' not found in available funds.")
            continue

        ticker = fund_to_ticker[fund_name]
        if ticker not in all_fetched_fund_data:
            error_messages.append(f"Error: No fetched data for ticker '{ticker}' (fund: {fund_name}).")

    # Rebalancing-specific validations
    if strategy_type == 'Rebalancing Strategy':
        if len(funds) < 2:
            error_messages.append(f"Error: Rebalancing Strategy requires at least 2 funds. Got {len(funds)}.")

        weights = []
        for i, fund in enumerate(funds):
            weight = fund.get('weight')
            if weight is None:
                error_messages.append(f"Error: Fund '{fund.get('name', i+1)}' in Rebalancing Strategy is missing 'weight'.")
            elif not (0 < weight <= 1):
                error_messages.append(f"Error: Fund '{fund.get('name', i+1)}' has invalid weight {weight}. Must be between 0 and 1.")
            else:
                weights.append(weight)

        if weights and abs(sum(weights) - 1.0) > 1e-6:
            error_messages.append(f"Error: Rebalancing Strategy weights must sum to 1. Got {sum(weights):.4f}.")

    # Single Fund Strategy validations
    if strategy_type == 'Single Fund Strategy':
        if len(funds) != 1:
            error_messages.append(f"Error: Single Fund Strategy requires exactly 1 fund. Got {len(funds)}.")

    if error_messages:
        raise ValueError("\n".join(error_messages))


def run_all_validations(simulation_scenarios, fund_to_ticker, all_fetched_fund_data, start_year, end_year, annual_draw_rate, inflation_rate):
    """
    Orchestrates all validation checks.
    """
    validate_simulation_parameters(start_year, end_year, annual_draw_rate, inflation_rate)

    for i, scenario in enumerate(simulation_scenarios):
        try:
            validate_scenario(scenario, fund_to_ticker, all_fetched_fund_data)
        except ValueError as e:
            raise ValueError(f"Scenario {i+1} validation failed:\n{e}")

    validated_funds = set()
    for scenario in simulation_scenarios:
        for fund in scenario['funds']:
            fund_name = fund['name']
            if fund_name in validated_funds:
                continue

            ticker = fund_to_ticker[fund_name]
            fund_data_df = all_fetched_fund_data[ticker]
            validate_single_fund_date_range(fund_data_df, start_year, end_year, fund_name)
            validated_funds.add(fund_name)

    print("All validations passed successfully!")
