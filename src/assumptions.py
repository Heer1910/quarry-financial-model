"""
assumptions.py

Stores forecast assumptions for Chipotle financial model.
Three scenarios: Base, Bull, Bear.

Each assumption is keyed by year (2026-2030) where applicable.
"""

# Forecast years
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]

# ---------------------------------------------------------
# MARKET INPUTS — shared across all scenarios
# These are external data points, not scenario-dependent.
# Updated: May 2026
# ---------------------------------------------------------
MARKET_INPUTS = {
    "diluted_shares_2025": 1342616,    # 2025A diluted shares outstanding ($K)
    "current_price": 32.89,            # CMG share price as of May 2026
    "current_price_date": "May 2026",  # Used for display in dashboard
}

# --------------------------------------------------------------------
# BASE CASE - matches the current Sheets model
# --------------------------------------------------------------------

BASE = {
    # Revenue drivers
    "openings": {2026: 320, 2027: 335, 2028: 350, 2029: 365, 2030: 380},
    "closures": {2026: -20, 2027: -20, 2028: -20, 2029: -20, 2030: -20},
    "auv_growth": {2026: 0.020, 2027: 0.025, 2028: 0.025, 2029: 0.025, 2030: 0.020},

    # Cost structure
    "food_bev_pkg_pct": 0.295,
    "labor_pct": 0.250,
    "occupancy_pct": {2026: 0.051, 2027: 0.051, 2028: 0.050, 2029: 0.050, 2030: 0.050},
    "other_opex_pct": 0.145,
    "ga_pct": 0.055,
    "da_pct": 0.030,

    # Pre-opening and impairment ($k)
    "preopening_per_store": 160,
    "impairment": 30000,

    # Working capital (days/%)
    "dso_days": 5,
    "dio_days": 5,
    "dpo_days": 23,
    "other_current_pct": 0.020,

    # CapEx ($k per store + maintenance % of revenue)
    "capex_per_store": 1950,
    "maintenance_capex_pct": 0.020,

    # Tax
    "tax_rate": 0.235,

    # Buybacks
    "buybacks": {2026: 1500000, 2027: 1700000, 2028: 1900000, 2029: 1900000, 2030: 1900000},

    # SBC ($k)
    "sbc": 150000,

    # Diluted shares (thousands)
    "diluted_shares": {2026: 1309000, 2027: 1275000, 2028: 1241000, 2029:1207000, 2030: 1173000},

    # DCF inputs
    "beta": 1.05,
    "terminal_growth": 0.025,
    "risk_free_rate": 0.042,
    "equity_risk_premium": 0.055,
    "after_tax_cost_of_debt": 0.035,
    "equity_weight": 0.95,
    "debt_weight": 0.05,
}


# ---------------------------------------------------------
# BULL CASE — aggressive recovery scenario
# Overrides only the assumptions that differ from BASE
# ---------------------------------------------------------

BULL = {
    **BASE,
    "openings": {2026: 360, 2027: 385, 2028: 410, 2029: 435, 2030: 460},
    "auv_growth": {2026: 0.040, 2027: 0.045, 2028: 0.040, 2029: 0.035, 2030: 0.030},
    "food_bev_pkg_pct": 0.285,
    "labor_pct": 0.240,
    "ga_pct": 0.050,
    "beta": 0.90,
    "terminal_growth": 0.030,
    # Bull case: management accelerates buybacks given strong cash generation
    "buybacks": {2026: 1700000, 2027: 2000000, 2028: 2200000, 2029: 2200000, 2030: 2200000},
}


# ---------------------------------------------------------
# BEAR CASE — structural decline scenario
# ---------------------------------------------------------

BEAR = {
    **BASE,
    "openings": {2026: 280, 2027: 290, 2028: 300, 2029: 310, 2030: 320},
    "auv_growth": {2026: 0.000, 2027: 0.010, 2028: 0.015, 2029: 0.015, 2030: 0.015},
    "food_bev_pkg_pct": 0.305,
    "labor_pct": 0.260,
    "ga_pct": 0.060,
    "beta": 1.20,
    "terminal_growth": 0.020,
    # Bear case: management pulls back on buybacks when growth disappoints
    "buybacks": {2026: 800000, 2027: 900000, 2028: 1000000, 2029: 1000000, 2030: 1000000},
}

# ---------------------------------------------------------
# Helper function to grab the right scenario
# ---------------------------------------------------------
def get_assumptions(scenario: str = "Base") -> dict:
    scenario = scenario.capitalize()
    if scenario == "Base":
        return BASE
    elif scenario == "Bull":
        return BULL
    elif scenario == "Bear":
        return BEAR
    else:
        raise ValueError(f"Unknown scenario: {scenario}. Must be Base, Bull, or Bear.")
