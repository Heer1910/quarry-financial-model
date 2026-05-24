"""
main.py

Orchestrator for the Chipotle 3-statement financial model.

Provides a single function `run_full_model()` that:
1. Loads historical data
2. Forecasts IS, BS, CF for the chosen scenario
3. Plugs cash into BS
4. Runs DCF
5. Returns all results in one structured dict

This is the function Streamlit will call.
"""

from src.data_loader import (
    load_income_statement as load_hist_is,
    load_balance_sheet as load_hist_bs,
    load_cash_flow as load_hist_cf,
)
from src.assumptions import get_assumptions
from src.income_statement import forecast_income_statement
from src.balance_sheet import forecast_balance_sheet
from src.cash_flow import forecast_cash_flow, plug_cash_into_bs
from src.dcf import run_dcf


def run_full_model(scenario: str = "Base") -> dict:
    """
    Run the full Chipotle financial model for a given scenario.

    Parameters
    ----------
    scenario : str
        "Base", "Bull", or "Bear"

    Returns
    -------
    dict with keys:
        - historical_is, historical_bs, historical_cf
        - forecast_is, forecast_bs, forecast_cf
        - dcf (dict of DCF results)
        - assumptions
        - scenario
    """
    # Load historicals
    historical_is = load_hist_is()
    historical_bs = load_hist_bs()
    historical_cf = load_hist_cf()

    # Get assumptions for this scenario
    assumptions = get_assumptions(scenario)

    # Build forecasts
    forecast_is = forecast_income_statement(historical_is, assumptions)
    forecast_bs = forecast_balance_sheet(historical_bs, forecast_is, assumptions)
    forecast_cf = forecast_cash_flow(
        historical_bs, historical_cf, forecast_is, forecast_bs, assumptions
    )
    forecast_bs_final = plug_cash_into_bs(forecast_bs, forecast_cf)

    # Run DCF
    dcf_results = run_dcf(
        forecast_is, forecast_bs_final, forecast_cf, historical_bs, assumptions
    )

    return {
        "scenario": scenario,
        "assumptions": assumptions,
        "historical_is": historical_is,
        "historical_bs": historical_bs,
        "historical_cf": historical_cf,
        "forecast_is": forecast_is,
        "forecast_bs": forecast_bs_final,
        "forecast_cf": forecast_cf,
        "dcf": dcf_results,
    }


def print_summary(results: dict) -> None:
    """Pretty-print the key valuation results."""
    dcf = results["dcf"]
    print(f"\n{'=' * 60}")
    print(f"CHIPOTLE DCF — {results['scenario'].upper()} CASE")
    print("=" * 60)
    print(f"  2030E Revenue:       ${results['forecast_is'].loc['Revenue', '2030E']:>15,.0f}K")
    print(f"  2030E Net Income:    ${results['forecast_is'].loc['Net_income', '2030E']:>15,.0f}K")
    print(f"  WACC:                 {dcf['wacc']:>15.2%}")
    print(f"  Terminal Growth:      {results['assumptions']['terminal_growth']:>15.2%}")
    print(f"  Enterprise Value:    ${dcf['enterprise_value']:>15,.0f}K")
    print(f"  Equity Value:        ${dcf['equity_value']:>15,.0f}K")
    print(f"  Implied Price:       ${dcf['implied_price']:>15,.2f}")
    print(f"  Current Price:       ${dcf['current_price']:>15,.2f}")
    print(f"  Upside/(Downside):    {dcf['upside_pct']:>15.1%}")


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# CHIPOTLE MEXICAN GRILL — FINANCIAL MODEL")
    print("# Python implementation")
    print("#" * 60)

    for scenario in ["Bear", "Base", "Bull"]:
        results = run_full_model(scenario)
        print_summary(results)

    # Scenario comparison table
    print(f"\n{'=' * 60}")
    print("SCENARIO COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Scenario':<10}{'Implied Price':>18}{'Upside':>15}")
    print("-" * 50)
    for scenario in ["Bear", "Base", "Bull"]:
        results = run_full_model(scenario)
        dcf = results["dcf"]
        print(f"{scenario:<10}${dcf['implied_price']:>15,.2f}{dcf['upside_pct']:>14.1%}")
    print("-" * 50)
    print(f"{'Current':<10}${32.89:>15,.2f}{'':>15}")