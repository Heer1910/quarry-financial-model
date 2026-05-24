"""
income_statement.py

Forecasts Chipotle's Income Statement for 2026E-2030E
based on assumptions (Base / Bull / Bear) and revenue drivers.

Logic mirrors the Sheets model column-by-column.
"""

import pandas as pd
from src.assumptions import FORECAST_YEARS


def calculate_revenue(historical_is: pd.DataFrame, assumptions: dict) -> pd.Series:
    """
    Build the revenue line from store count and AUV.
    
    Revenue = avg_store_count × AUV
    
    Returns a pandas Series indexed by forecast year.
    """
    # Historical 2025A store count (ending) and AUV
    # We need these as the starting point for the forecast
    store_count_2025 = 4042  # 2025A ending store count
    auv_2025 = 3070.44  # 2025A AUV in $K (per store)

    # Build year-by-year
    revenue = {}
    prev_store_count = store_count_2025
    prev_auv = auv_2025

    for year in FORECAST_YEARS:
        # Store count math
        openings = assumptions["openings"][year]
        closures = assumptions["closures"][year]
        ending_count = prev_store_count + openings + closures
        avg_count = (prev_store_count + ending_count) / 2

        # AUV math
        new_auv = prev_auv * (1 + assumptions["auv_growth"][year])

        # Revenue in $K (avg_count × AUV in $K already gives $K)
        revenue[year] = avg_count * new_auv

        # Update for next year
        prev_store_count = ending_count
        prev_auv = new_auv

    return pd.Series(revenue, name="Revenue")


def forecast_income_statement(
    historical_is: pd.DataFrame,
    assumptions: dict,
) -> pd.DataFrame:
    """
    Forecast Income Statement for 2026E-2030E.
    
    Returns a DataFrame with rows = line items, columns = forecast years.
    """
    # Calculate revenue first (driver of everything else)
    revenue = calculate_revenue(historical_is, assumptions)

    # Build forecast as a dict, one line item at a time
    forecast = {}
    forecast["Revenue"] = revenue

    # Cost of revenue items (% of revenue)
    forecast["Food_bev_pkg"] = revenue * assumptions["food_bev_pkg_pct"]
    forecast["Labor"] = revenue * assumptions["labor_pct"]
    forecast["Occupancy"] = pd.Series(
        {y: revenue[y] * assumptions["occupancy_pct"][y] for y in FORECAST_YEARS}
    )
    forecast["Other_opex"] = revenue * assumptions["other_opex_pct"]
    forecast["GA"] = revenue * assumptions["ga_pct"]
    forecast["DA"] = revenue * assumptions["da_pct"]

    # Pre-opening: openings × $K per store
    forecast["Pre_opening"] = pd.Series({
        y: assumptions["openings"][y] * assumptions["preopening_per_store"]
        for y in FORECAST_YEARS
    })

    # Impairment: flat assumption
    forecast["Impairment"] = pd.Series({
        y: assumptions["impairment"] for y in FORECAST_YEARS
    })

    # Total operating expenses (sum of all the above except revenue)
    opex_items = ["Food_bev_pkg", "Labor", "Occupancy", "Other_opex", 
                  "GA", "DA", "Pre_opening", "Impairment"]
    forecast["Total_opex"] = sum(forecast[item] for item in opex_items)

    # Operating income = Revenue - Total opex
    forecast["Operating_income"] = revenue - forecast["Total_opex"]

    # Other income: flat $75M based on 2025A normalized level
    forecast["Other_income"] = pd.Series({y: 75000 for y in FORECAST_YEARS})

    # Pretax income
    forecast["Pretax_income"] = forecast["Operating_income"] + forecast["Other_income"]

    # Tax
    forecast["Tax_expense"] = forecast["Pretax_income"] * assumptions["tax_rate"]

    # Net income
    forecast["Net_income"] = forecast["Pretax_income"] - forecast["Tax_expense"]

    # Convert dict to DataFrame
    df = pd.DataFrame(forecast).T
    df.columns = [f"{y}E" for y in FORECAST_YEARS]
    return df


if __name__ == "__main__":
    from src.data_loader import load_income_statement
    from src.assumptions import get_assumptions

    historical = load_income_statement()
    base_assumptions = get_assumptions("Base")

    forecast = forecast_income_statement(historical, base_assumptions)

    print("=" * 60)
    print("FORECAST INCOME STATEMENT (Base case)")
    print("=" * 60)
    print(forecast.round(0))
    print("\n2030E Revenue:", round(forecast.loc["Revenue", "2030E"]))
    print("2030E Net Income:", round(forecast.loc["Net_income", "2030E"]))