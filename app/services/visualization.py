import pandas as pd
import plotly.express as px


def build_monthly_draw_dataset(initial_corpus, annual_draw_rate, inflation_rate, start_year, end_year):
    start_date = pd.Timestamp(year=start_year, month=1, day=1)
    end_date = pd.Timestamp(year=end_year, month=12, day=31)
    simulation_months = pd.date_range(start=start_date, end=end_date, freq='MS')

    monthly_draw_data = []
    for month_start in simulation_months:
        current_year = month_start.year
        inflation_adjusted_annual_draw = initial_corpus * annual_draw_rate * ((1 + inflation_rate) ** (current_year - start_year))
        monthly_draw = inflation_adjusted_annual_draw / 12
        monthly_draw_data.append({
            'YearMonth': month_start.strftime('%Y-%m'),
            'Monthly Draw': monthly_draw
        })

    df_monthly_draw = pd.DataFrame(monthly_draw_data)
    df_monthly_draw['YearMonth_dt'] = pd.to_datetime(df_monthly_draw['YearMonth'])
    return df_monthly_draw


def plot_monthly_draw_results(initial_corpus, annual_draw_rate, inflation_rate, start_year, end_year):
    df_monthly_draw = build_monthly_draw_dataset(initial_corpus, annual_draw_rate, inflation_rate, start_year, end_year)

    fig = px.line(
        df_monthly_draw,
        x='YearMonth_dt',
        y='Monthly Draw',
        title=f"Monthly Draw (Initial Draw Rate:{annual_draw_rate*100}%, Inflation:{inflation_rate*100}% )",
        labels={'YearMonth_dt': 'Date', 'Monthly Draw': 'Monthly Draw Amount'}
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Monthly Draw Amount",
        hovermode="x unified",
        title_font_size=18,
        title_x=0.5
    )
    fig.update_traces(mode='lines+markers', marker=dict(size=4), line=dict(color='blue'))
    return fig


def plot_simulation_results(simulation_results_dict, simulation_scenarios=None, initial_corpus=0, annual_draw_rate=0.0, inflation_rate=0.0):
    all_results_df = pd.DataFrame()

    for i, (strategy_name, df) in enumerate(simulation_results_dict.items()):
        df_copy = df.copy()
        df_copy['YearMonth_dt'] = pd.to_datetime(df_copy['YearMonth'])

        if simulation_scenarios and i < len(simulation_scenarios):
            scenario = simulation_scenarios[i]
            fund_names = [f['name'] for f in scenario['funds']]
            funds_str = ", ".join(fund_names)
            legend_label = f"{strategy_name} ({funds_str})"
        else:
            legend_label = strategy_name

        df_copy['Strategy'] = legend_label
        all_results_df = pd.concat([all_results_df, df_copy])

    fig = px.line(
        all_results_df,
        x='YearMonth_dt',
        y='Ending Corpus',
        color='Strategy',
        title=f"FIRE Simulation(Initial corpus:{initial_corpus:,.0f}, Draw rate:{annual_draw_rate*100}%, {inflation_rate*100}% inflation)",
        labels={'YearMonth_dt': 'Date', 'Ending Corpus': 'Ending Corpus'}
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Corpus",
        hovermode="x unified",
        title_font_size=18,
        legend_title_text='Investment Strategy & Fund',
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    fig.update_traces(mode='lines+markers', marker=dict(size=4))
    return fig
