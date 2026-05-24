"""
balance_sheet.py

Forecasts Chipotle's Balance Sheet for 2026E-2030E.
Cash is set to a placeholder of 0; it gets populated by cash_flow.py
once the CF statement is built.

Logic mirrors the Sheets model.
"""

import pandas as pd
from src.assumptions import FORECAST_YEARS


def forecast_balance_sheet(
    historical_bs: pd.DataFrame,
    forecast_is: pd.DataFrame,
    assumptions: dict,
) -> pd.DataFrame:
    """
    Forecast Balance Sheet for 2026E-2030E.

    Parameters
    ----------
    historical_bs : DataFrame
        Historical balance sheet (2021A-2025A).
    forecast_is : DataFrame
        Forecasted income statement (2026E-2030E).
    assumptions : dict
        Scenario assumptions.

    Returns
    -------
    DataFrame
        Forecast BS with line items as rows, years as columns.
    """
    forecast = {}
    years = FORECAST_YEARS

    # ===================================================
    # PASS A — Working capital items (driven by IS)
    # ===================================================

    # Accounts receivable = (DSO / 365) × Revenue
    forecast["Accounts_receivable"] = pd.Series({
        y: (assumptions["dso_days"] / 365) * forecast_is.loc["Revenue", f"{y}E"]
        for y in years
    })

    # Inventory = (DIO / 365) × Food/bev/pkg COGS
    forecast["Inventory"] = pd.Series({
        y: (assumptions["dio_days"] / 365) * forecast_is.loc["Food_bev_pkg", f"{y}E"]
        for y in years
    })

    # Income tax receivable: hold flat at 2025A
    last_hist_tax_rec = historical_bs.loc["Income tax receivable", "2025A"]
    forecast["Income_tax_receivable"] = pd.Series({
        y: last_hist_tax_rec for y in years
    })

    # Prepaid expenses & other current assets = % of revenue
    forecast["Prepaid_other_ca"] = pd.Series({
        y: assumptions["other_current_pct"] * forecast_is.loc["Revenue", f"{y}E"]
        for y in years
    })

    # ===================================================
    # PASS B — Long-term assets
    # ===================================================

    # PP&E roll-forward:
    # Ending PP&E = Beginning PP&E + CapEx − D&A − Impairment
    ppe_line = "Leasehold improvements, property and equipment, net"
    last_hist_ppe = historical_bs.loc[ppe_line, "2025A"]

    ppe_balances = {}
    prev_ppe = last_hist_ppe
    for y in years:
        # CapEx = openings × $K per store + maintenance % × revenue
        capex = (
            assumptions["openings"][y] * assumptions["capex_per_store"]
            + assumptions["maintenance_capex_pct"] * forecast_is.loc["Revenue", f"{y}E"]
        )
        da = forecast_is.loc["DA", f"{y}E"]
        impairment = forecast_is.loc["Impairment", f"{y}E"]
        ending_ppe = prev_ppe + capex - da - impairment
        ppe_balances[y] = ending_ppe
        prev_ppe = ending_ppe

    forecast["PPE_net"] = pd.Series(ppe_balances)

    # Investments, restricted cash, goodwill, other LT assets: hold flat
    flat_lt_items = {
        "Short_term_investments": "Short-term investments",
        "Long_term_investments": "Long-term investments",
        "Restricted_cash": "restricted cash",
        "Other_lt_assets": "Other long-term assets",
        "Goodwill": "Goodwill",
    }
    for fc_key, hist_key in flat_lt_items.items():
        last_val = historical_bs.loc[hist_key, "2025A"]
        forecast[fc_key] = pd.Series({y: last_val for y in years})

    # Operating lease assets: grow with revenue at same growth as 2025A→2026E
    # Then roll forward in lockstep with operating lease liabilities (ASC 842).
    # For simplicity: grow at revenue growth rate.
    last_hist_op_lease_asset = historical_bs.loc["Operating lease assets", "2025A"]
    last_hist_rev = forecast_is.loc["Revenue", "2026E"] / 1  # placeholder
    
    # Use historical 2025A revenue from prior data
    # Approach: grow lease assets proportional to revenue growth
    op_lease_assets = {}
    prev_assets = last_hist_op_lease_asset
    prev_rev = 11925601  # 2025A revenue (from your historical)
    for y in years:
        rev = forecast_is.loc["Revenue", f"{y}E"]
        growth = (rev / prev_rev) - 1
        new_assets = prev_assets * (1 + growth)
        op_lease_assets[y] = new_assets
        prev_assets = new_assets
        prev_rev = rev
    forecast["Operating_lease_assets"] = pd.Series(op_lease_assets)

    # Cash placeholder (filled by CF later)
    forecast["Cash"] = pd.Series({y: 0.0 for y in years})

    # ===================================================
    # PASS C — Liabilities
    # ===================================================

    # Accounts payable = (DPO / 365) × Food/bev/pkg
    forecast["Accounts_payable"] = pd.Series({
        y: (assumptions["dpo_days"] / 365) * forecast_is.loc["Food_bev_pkg", f"{y}E"]
        for y in years
    })

    # Accrued payroll = % of labor expense (use 2025A ratio)
    last_payroll_ratio = (
        historical_bs.loc["Accrued payroll and benefits", "2025A"]
        / forecast_is.loc["Labor", "2026E"]  # close enough
    )
    forecast["Accrued_payroll"] = pd.Series({
        y: last_payroll_ratio * forecast_is.loc["Labor", f"{y}E"]
        for y in years
    })

    # Accrued liabilities, unearned revenue: % of revenue
    flat_pct_revenue = {
        "Accrued_liabilities": "Accrued liabilities",
        "Unearned_revenue": "Unearned revenue",
    }
    for fc_key, hist_key in flat_pct_revenue.items():
        ratio = historical_bs.loc[hist_key, "2025A"] / 11925601
        forecast[fc_key] = pd.Series({
            y: ratio * forecast_is.loc["Revenue", f"{y}E"] for y in years
        })

    # Operating lease liabilities: grow at same rate as lease assets
    last_hist_current_lease = historical_bs.loc["Current operating lease liabilities", "2025A"]
    last_hist_lt_lease = historical_bs.loc["Long-term operating lease liabilities", "2025A"]

    current_lease = {}
    lt_lease = {}
    prev_current = last_hist_current_lease
    prev_lt = last_hist_lt_lease
    prev_rev = 11925601
    for y in years:
        rev = forecast_is.loc["Revenue", f"{y}E"]
        growth = (rev / prev_rev) - 1
        new_current = prev_current * (1 + growth)
        new_lt = prev_lt * (1 + growth)
        current_lease[y] = new_current
        lt_lease[y] = new_lt
        prev_current = new_current
        prev_lt = new_lt
        prev_rev = rev
    forecast["Current_lease_liab"] = pd.Series(current_lease)
    forecast["LT_lease_liab"] = pd.Series(lt_lease)

    # Deferred tax & other long-term liabilities: hold flat
    flat_lt_liab = {
        "Deferred_tax_liab": "Deferred income tax liabilities",
        "Other_lt_liab": "Other long-term liabilities",
    }
    for fc_key, hist_key in flat_lt_liab.items():
        last_val = historical_bs.loc[hist_key, "2025A"]
        forecast[fc_key] = pd.Series({y: last_val for y in years})

    # ===================================================
    # PASS D — Equity
    # ===================================================

    # Common stock: hold flat at 2025A
    forecast["Common_stock"] = pd.Series({
        y: historical_bs.loc["Common stock", "2025A"] for y in years
    })

    # APIC: grow by SBC each year
    apic_balances = {}
    prev_apic = historical_bs.loc["Additional paid-in capital", "2025A"]
    for y in years:
        new_apic = prev_apic + assumptions["sbc"]
        apic_balances[y] = new_apic
        prev_apic = new_apic
    forecast["APIC"] = pd.Series(apic_balances)

    # AOCI: hold flat
    forecast["AOCI"] = pd.Series({
        y: historical_bs.loc["Accumulated other comprehensive loss", "2025A"] for y in years
    })

    # Treasury stock: hold at 0 (retired in 2024)
    forecast["Treasury_stock"] = pd.Series({y: 0.0 for y in years})

    # Retained earnings: prev RE + Net Income − Buybacks
    re_balances = {}
    prev_re = historical_bs.loc["Retained earnings", "2025A"]
    for y in years:
        ni = forecast_is.loc["Net_income", f"{y}E"]
        buyback = assumptions["buybacks"][y]
        new_re = prev_re + ni - buyback
        re_balances[y] = new_re
        prev_re = new_re
    forecast["Retained_earnings"] = pd.Series(re_balances)

    # Convert to DataFrame
    df = pd.DataFrame(forecast).T
    df.columns = [f"{y}E" for y in years]
    return df


if __name__ == "__main__":
    from src.data_loader import load_balance_sheet, load_income_statement
    from src.income_statement import forecast_income_statement
    from src.assumptions import get_assumptions

    historical_bs = load_balance_sheet()
    historical_is = load_income_statement()
    base = get_assumptions("Base")

    forecast_is = forecast_income_statement(historical_is, base)
    forecast_bs = forecast_balance_sheet(historical_bs, forecast_is, base)

    print("=" * 60)
    print("FORECAST BALANCE SHEET (Base case)")
    print("=" * 60)
    print(forecast_bs.round(0))
    print("\nNumber of line items:", forecast_bs.shape[0])