"""
data_loader.py

Loads Chipotle Mexican Grill historical financials (2021A-2025A)
from CSV files in the data/ folder.

Source: 10-K filings, SEC EDGAR.
All values in $ thousands.
"""

import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Historical years we want to load
HISTORICAL_YEARS = ["2021A", "2022A", "2023A", "2024A", "2025A"]


def _clean_currency(value):
    """
    Convert a string like '$7,547,061.00' to a float 7547061.0
    Handles blanks, dashes, and parentheses (negative numbers).
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    s = str(value).strip()
    
    # Handle blanks and dashes
    if s in ("", "-", "—", "$-", "$ -"):
        return 0.0
    
    # Handle parentheses for negatives: "(123)" → -123
    is_negative = s.startswith("(") and s.endswith(")")
    if is_negative:
        s = s[1:-1]
    
    # Strip $ and commas
    s = s.replace("$", "").replace(",", "").strip()
    
    try:
        num = float(s)
        return -num if is_negative else num
    except ValueError:
        return 0.0


def _load_csv(filename: str) -> pd.DataFrame:
    """
    Generic CSV loader. Reads the file, skips header rows,
    cleans currency strings, returns historical years only.
    """
    filepath = DATA_DIR / filename
    
    # Read CSV, skipping the first 3 garbage rows (title, units, blank)
    # Row 4 (index 3) becomes the header: "Fiscal Year, 2021A, 2022A, ..."
    df = pd.read_csv(filepath, skiprows=3)
    
    # First column has line item names, rename it
    df = df.rename(columns={df.columns[0]: "LineItem"})
    
    # Drop fully empty rows
    df = df.dropna(how="all")
    df = df[df["LineItem"].notna()]
    
    # Set line item as index, keep only historical year columns
    df = df.set_index("LineItem")
    df = df[HISTORICAL_YEARS]
    
    # Clean all currency strings to floats
    df = df.map(_clean_currency)
    
    return df


def load_income_statement() -> pd.DataFrame:
    """Load historical Income Statement (2021A-2025A)."""
    return _load_csv("historical_is.csv")


def load_balance_sheet() -> pd.DataFrame:
    """Load historical Balance Sheet (2021A-2025A)."""
    return _load_csv("historical_bs.csv")


def load_cash_flow() -> pd.DataFrame:
    """Load historical Cash Flow Statement (2021A-2025A)."""
    return _load_csv("historical_cf.csv")


if __name__ == "__main__":
    print("=" * 60)
    print("INCOME STATEMENT (Historical)")
    print("=" * 60)
    is_df = load_income_statement()
    print(is_df)
    print("\nShape:", is_df.shape)
    print("Revenue 2025A:", is_df.loc["Revenue", "2025A"])

    print("\n" + "=" * 60)
    print("BALANCE SHEET (Historical)")
    print("=" * 60)
    bs_df = load_balance_sheet()
    print(bs_df)
    print("\nShape:", bs_df.shape)

    print("\n" + "=" * 60)
    print("CASH FLOW (Historical)")
    print("=" * 60)
    cf_df = load_cash_flow()
    print(cf_df)
    print("\nShape:", cf_df.shape)