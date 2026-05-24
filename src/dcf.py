"""
dcf.py

Discounted Cash Flow valuation for Chipotle.

Calculates:
- Unlevered Free Cash Flow (UFCF) for each forecast year
- WACC from CAPM
- Terminal Value via Gordon Growth
- Present value of UFCFs + PV of Terminal Value = Enterprise Value
- Equity Value = EV - Net Debt
- Implied share price = Equity Value / Diluted shares
"""

import pandas as pd
from src.assumptions import FORECAST_YEARS


def calculate_ufcf(
    forecast_is: pd.DataFrame,
    forecast_bs: pd.DataFrame,
    historical_bs: pd.DataFrame,
    assumptions: dict,
) -> pd.DataFrame:
    """
    Build the UFCF for each forecast year.

    UFCF = EBIT × (1 - tax rate) + D&A - CapEx - ΔNWC
    """
    rows = {}
    years = FORECAST_YEARS

    # EBIT = Operating income
    rows["EBIT"] = pd.Series({
        y: forecast_is.loc["Operating_income", f"{y}E"] for y in years
    })

    # Tax rate (flat assumption)
    rows["Tax_rate"] = pd.Series({y: assumptions["tax_rate"] for y in years})

    # NOPAT = EBIT × (1 - tax)
    rows["NOPAT"] = rows["EBIT"] * (1 - assumptions["tax_rate"])

    # Add back D&A
    rows["DA"] = pd.Series({
        y: forecast_is.loc["DA", f"{y}E"] for y in years
    })

    # CapEx (positive number, will subtract below)
    rows["CapEx"] = pd.Series({
        y: (
            assumptions["openings"][y] * assumptions["capex_per_store"]
            + assumptions["maintenance_capex_pct"] * forecast_is.loc["Revenue", f"{y}E"]
        ) for y in years
    })

    # Change in NWC = (current NWC) − (prior NWC)
    # NWC = AR + Inventory + Prepaid − AP − Accrued payroll − Accrued liab − Unearned rev
    def _nwc(year):
        if year == 2025:
            ar = historical_bs.loc["Accounts receivable", "2025A"]
            inv = historical_bs.loc["Inventory", "2025A"]
            prepaid = historical_bs.loc["Prepaid expenses and other current assets", "2025A"]
            ap = historical_bs.loc["Accounts payable", "2025A"]
            payroll = historical_bs.loc["Accrued payroll and benefits", "2025A"]
            accrued = historical_bs.loc["Accrued liabilities", "2025A"]
            unearned = historical_bs.loc["Unearned revenue", "2025A"]
        else:
            ar = forecast_bs.loc["Accounts_receivable", f"{year}E"]
            inv = forecast_bs.loc["Inventory", f"{year}E"]
            prepaid = forecast_bs.loc["Prepaid_other_ca", f"{year}E"]
            ap = forecast_bs.loc["Accounts_payable", f"{year}E"]
            payroll = forecast_bs.loc["Accrued_payroll", f"{year}E"]
            accrued = forecast_bs.loc["Accrued_liabilities", f"{year}E"]
            unearned = forecast_bs.loc["Unearned_revenue", f"{year}E"]
        return (ar + inv + prepaid) - (ap + payroll + accrued + unearned)

    nwc_changes = {}
    prev_nwc = _nwc(2025)
    for y in years:
        current_nwc = _nwc(y)
        nwc_changes[y] = current_nwc - prev_nwc
        prev_nwc = current_nwc
    rows["Change_in_NWC"] = pd.Series(nwc_changes)

    # UFCF = NOPAT + D&A - CapEx - ΔNWC
    rows["UFCF"] = rows["NOPAT"] + rows["DA"] - rows["CapEx"] - rows["Change_in_NWC"]

    df = pd.DataFrame(rows).T
    df.columns = [f"{y}E" for y in years]
    return df


def calculate_wacc(assumptions: dict) -> float:
    """
    WACC = (E/V) × Cost of Equity + (D/V) × Cost of Debt × (1 - tax)
    
    Cost of Equity (CAPM) = Rf + Beta × ERP
    """
    cost_of_equity = (
        assumptions["risk_free_rate"]
        + assumptions["beta"] * assumptions["equity_risk_premium"]
    )
    wacc = (
        assumptions["equity_weight"] * cost_of_equity
        + assumptions["debt_weight"] * assumptions["after_tax_cost_of_debt"]
    )
    return wacc


def run_dcf(
    forecast_is: pd.DataFrame,
    forecast_bs: pd.DataFrame,
    forecast_cf: pd.DataFrame,
    historical_bs: pd.DataFrame,
    assumptions: dict,
) -> dict:
    """
    Run the full DCF and return a dict of key results.
    """
    years = FORECAST_YEARS

    # Step 1: Build UFCF
    ufcf_df = calculate_ufcf(forecast_is, forecast_bs, historical_bs, assumptions)
    ufcfs = ufcf_df.loc["UFCF"].values  # array of 5 UFCFs

    # Step 2: Calculate WACC
    wacc = calculate_wacc(assumptions)

    # Step 3: Discount factors (mid-year convention: 0.5, 1.5, 2.5, 3.5, 4.5)
    discount_periods = [0.5, 1.5, 2.5, 3.5, 4.5]
    discount_factors = [(1 + wacc) ** -p for p in discount_periods]

    # Step 4: PV of explicit forecast UFCFs
    pv_ufcfs = [ufcf * df for ufcf, df in zip(ufcfs, discount_factors)]
    sum_pv_ufcfs = sum(pv_ufcfs)

    # Step 5: Terminal value (Gordon growth)
    g = assumptions["terminal_growth"]
    terminal_ufcf = ufcfs[-1] * (1 + g)
    terminal_value = terminal_ufcf / (wacc - g)
    pv_terminal = terminal_value * discount_factors[-1]  # discount at year 5 factor

    # Step 6: Enterprise Value
    enterprise_value = sum_pv_ufcfs + pv_terminal

    # Step 7: Net Debt (negative = net cash position)
    # Net Debt = Total debt - Cash - ST investments - LT investments
    cash_2025 = historical_bs.loc["Cash and equivalents", "2025A"]
    st_inv = historical_bs.loc["Short-term investments", "2025A"]
    lt_inv = historical_bs.loc["Long-term investments", "2025A"]
    total_debt = 0  # Chipotle has no traditional debt
    net_debt = total_debt - cash_2025 - st_inv - lt_inv

    # Step 8: Equity Value
    equity_value = enterprise_value - net_debt

    # Step 9: Implied share price
    # Use 2025A diluted shares — most recent actual count
    # From your Sheets: B44 in Assumptions tab (2021 = 1,425,550 post-split)
    # 2025A shares from Sheets: F44
    diluted_shares_2025 = 1342616  # 2025A diluted shares (thousands), from Sheets

    implied_price = equity_value / diluted_shares_2025  # both in thousands; result is $/share

    # Current price for comparison
    current_price = 32.89

    return {
        "ufcf_df": ufcf_df,
        "ufcfs": list(ufcfs),
        "wacc": wacc,
        "discount_factors": discount_factors,
        "pv_ufcfs": pv_ufcfs,
        "sum_pv_ufcfs": sum_pv_ufcfs,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "net_debt": net_debt,
        "equity_value": equity_value,
        "diluted_shares": diluted_shares_2025,
        "implied_price": implied_price,
        "current_price": current_price,
        "upside_pct": (implied_price / current_price) - 1,
    }


if __name__ == "__main__":
    from src.data_loader import load_balance_sheet, load_cash_flow, load_income_statement
    from src.income_statement import forecast_income_statement
    from src.balance_sheet import forecast_balance_sheet
    from src.cash_flow import forecast_cash_flow, plug_cash_into_bs
    from src.assumptions import get_assumptions

    historical_bs = load_balance_sheet()
    historical_cf = load_cash_flow()
    historical_is = load_income_statement()

    for scenario in ["Bear", "Base", "Bull"]:
        assumptions = get_assumptions(scenario)
        forecast_is = forecast_income_statement(historical_is, assumptions)
        forecast_bs = forecast_balance_sheet(historical_bs, forecast_is, assumptions)
        forecast_cf = forecast_cash_flow(
            historical_bs, historical_cf, forecast_is, forecast_bs, assumptions
        )
        forecast_bs_final = plug_cash_into_bs(forecast_bs, forecast_cf)

        results = run_dcf(forecast_is, forecast_bs_final, forecast_cf, historical_bs, assumptions)

        print(f"\n{'=' * 60}")
        print(f"DCF VALUATION — {scenario.upper()} CASE")
        print("=" * 60)
        print(f"WACC:                {results['wacc']:.2%}")
        print(f"Terminal growth:     {assumptions['terminal_growth']:.2%}")
        print(f"Sum of PV UFCFs:     ${results['sum_pv_ufcfs']:>15,.0f}K")
        print(f"PV of Terminal:      ${results['pv_terminal']:>15,.0f}K")
        print(f"Enterprise Value:    ${results['enterprise_value']:>15,.0f}K")
        print(f"Net Debt:            ${results['net_debt']:>15,.0f}K")
        print(f"Equity Value:        ${results['equity_value']:>15,.0f}K")
        print(f"Diluted Shares (K):   {results['diluted_shares']:>15,}")
        print(f"Implied Price:       ${results['implied_price']:>15,.2f}")
        print(f"Current Price:       ${results['current_price']:>15,.2f}")
        print(f"Upside / (Downside): {results['upside_pct']:>15.1%}")