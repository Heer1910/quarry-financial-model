"""
cash_flow.py

Forecasts Chipotle's Cash Flow Statement for 2026E-2030E.

CF is derived from the IS and BS — it shows how cash moves between
the two statements. Once CF is calculated, the ending cash balance
gets plugged back into the BS.
"""

import pandas as pd
from src.assumptions import FORECAST_YEARS


def forecast_cash_flow(
    historical_bs: pd.DataFrame,
    historical_cf: pd.DataFrame,
    forecast_is: pd.DataFrame,
    forecast_bs: pd.DataFrame,
    assumptions: dict,
) -> pd.DataFrame:
    """
    Build forecast Cash Flow Statement for 2026E-2030E.

    Returns DataFrame with line items as rows, forecast years as columns.
    Also updates the BS cash row as a side effect (returned via tuple).
    """
    forecast = {}
    years = FORECAST_YEARS

    # ===================================================
    # OPERATING CASH FLOW
    # ===================================================

    # 1. Net Income (from IS)
    forecast["Net_income"] = pd.Series({
        y: forecast_is.loc["Net_income", f"{y}E"] for y in years
    })

    # 2. Add back D&A (non-cash)
    forecast["DA_addback"] = pd.Series({
        y: forecast_is.loc["DA", f"{y}E"] for y in years
    })

    # 3. Add back Impairment (non-cash)
    forecast["Impairment_addback"] = pd.Series({
        y: forecast_is.loc["Impairment", f"{y}E"] for y in years
    })

    # 4. Add back SBC (non-cash)
    forecast["SBC_addback"] = pd.Series({
        y: assumptions["sbc"] for y in years
    })

    # 5. Working capital changes — need BS values
    # For each WC item: Change = -(this_year − last_year)
    # Increase in asset = USE of cash (negative)
    # Increase in liability = SOURCE of cash (positive)

    def _get_bs_value(line_item, year):
        """Get BS value for a given year (handles 2025A historical vs forecast)."""
        if year == 2025:
            return historical_bs.loc[line_item, "2025A"]
        return forecast_bs.loc[line_item, f"{year}E"]

    # Map of forecast BS keys to historical BS line items (where names differ)
    wc_items = [
        # (forecast_key, historical_key, is_asset)
        ("Accounts_receivable", "Accounts receivable", True),
        ("Inventory", "Inventory", True),
        ("Prepaid_other_ca", "Prepaid expenses and other current assets", True),
        ("Accounts_payable", "Accounts payable", False),
        ("Accrued_payroll", "Accrued payroll and benefits", False),
        ("Accrued_liabilities", "Accrued liabilities", False),
        ("Unearned_revenue", "Unearned revenue", False),
    ]

    wc_changes = {y: 0.0 for y in years}
    prev_values = {}
    
    # Initialize previous year (2025A historical)
    for fc_key, hist_key, _ in wc_items:
        prev_values[fc_key] = historical_bs.loc[hist_key, "2025A"]

    for y in years:
        for fc_key, hist_key, is_asset in wc_items:
            current = forecast_bs.loc[fc_key, f"{y}E"]
            change = current - prev_values[fc_key]
            # Asset increase = cash outflow (negative)
            # Liability increase = cash inflow (positive)
            cf_impact = -change if is_asset else change
            wc_changes[y] += cf_impact
            prev_values[fc_key] = current

    forecast["Working_capital_changes"] = pd.Series(wc_changes)

    # 6. Operating CF total
    forecast["CFO"] = (
        forecast["Net_income"]
        + forecast["DA_addback"]
        + forecast["Impairment_addback"]
        + forecast["SBC_addback"]
        + forecast["Working_capital_changes"]
    )

    # ===================================================
    # INVESTING CASH FLOW
    # ===================================================

    # CapEx (outflow — negative)
    capex = {}
    for y in years:
        capex[y] = -(
            assumptions["openings"][y] * assumptions["capex_per_store"]
            + assumptions["maintenance_capex_pct"] * forecast_is.loc["Revenue", f"{y}E"]
        )
    forecast["CapEx"] = pd.Series(capex)

    # Investing CF total
    forecast["CFI"] = forecast["CapEx"]

    # ===================================================
    # FINANCING CASH FLOW
    # ===================================================

    # Buybacks (outflow — negative)
    forecast["Buybacks"] = pd.Series({
        y: -assumptions["buybacks"][y] for y in years
    })

    # Financing CF total
    forecast["CFF"] = forecast["Buybacks"]

    # ===================================================
    # NET CHANGE IN CASH
    # ===================================================

    forecast["Net_change_in_cash"] = (
        forecast["CFO"] + forecast["CFI"] + forecast["CFF"]
    )

    # Cash roll-forward
    starting_cash = historical_bs.loc["Cash and equivalents", "2025A"]
    cash_balances = {}
    prev_cash = starting_cash
    for y in years:
        new_cash = prev_cash + forecast["Net_change_in_cash"][y]
        cash_balances[y] = new_cash
        prev_cash = new_cash
    forecast["Ending_cash"] = pd.Series(cash_balances)

    df = pd.DataFrame(forecast).T
    df.columns = [f"{y}E" for y in years]
    return df


def plug_cash_into_bs(forecast_bs: pd.DataFrame, forecast_cf: pd.DataFrame) -> pd.DataFrame:
    """
    Take the ending cash from CF and place it into the BS Cash row.
    """
    bs_updated = forecast_bs.copy()
    for y in FORECAST_YEARS:
        bs_updated.loc["Cash", f"{y}E"] = forecast_cf.loc["Ending_cash", f"{y}E"]
    return bs_updated


if __name__ == "__main__":
    from src.data_loader import load_balance_sheet, load_cash_flow, load_income_statement
    from src.income_statement import forecast_income_statement
    from src.balance_sheet import forecast_balance_sheet
    from src.assumptions import get_assumptions

    historical_bs = load_balance_sheet()
    historical_cf = load_cash_flow()
    historical_is = load_income_statement()
    base = get_assumptions("Base")

    forecast_is = forecast_income_statement(historical_is, base)
    forecast_bs = forecast_balance_sheet(historical_bs, forecast_is, base)
    forecast_cf = forecast_cash_flow(
        historical_bs, historical_cf, forecast_is, forecast_bs, base
    )

    print("=" * 60)
    print("FORECAST CASH FLOW STATEMENT (Base case)")
    print("=" * 60)
    print(forecast_cf.round(0))
    print("\nEnding cash by year:")
    print(forecast_cf.loc["Ending_cash"].round(0))