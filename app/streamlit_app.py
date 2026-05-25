"""
streamlit_app.py

Interactive dashboard for the Chipotle financial model.
Run locally: streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

# Make src/ importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from src.main import run_full_model


# ===================================================
# Page config
# ===================================================
st.set_page_config(
    page_title="Quarry — Chipotle Financial Model",
    page_icon="🌯",
    layout="wide",
)


# ===================================================
# Header
# ===================================================
st.title("🌯 Quarry - Chipotle Mexican Grill Financial Model")
st.markdown(
    "A three-statement financial model and DCF valuation for **Chipotle Mexican Grill** "
    "(NYSE: CMG), built in Python and Google Sheets."
)
st.markdown("---")


# ===================================================
# Sidebar — Scenario selector
# ===================================================
st.sidebar.header("📊 Scenario")
scenario = st.sidebar.radio(
    "Choose a valuation scenario:",
    options=["Base", "Bull", "Bear"],
    index=0,
    help="Bull = aggressive recovery. Base = current trajectory. Bear = structural decline.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "Built by **Heer Patel** as part of the Quarry portfolio project.\n\n"
    "[GitHub repo](https://github.com/Heer1910/quarry-financial-model) · "
    "[Portfolio](https://heer1910.github.io)"
)


# ===================================================
# Run the model for the chosen scenario
# ===================================================
with st.spinner(f"Running {scenario} case..."):
    results = run_full_model(scenario)

dcf = results["dcf"]
assumptions = results["assumptions"]


# ===================================================
# HERO: Implied share price
# ===================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Implied Share Price",
        value=f"${dcf['implied_price']:.2f}",
    )

with col2:
    st.metric(
        label="Current Share Price",
        value=f"${dcf['current_price']:.2f}",
    )

with col3:
    upside = dcf['upside_pct']
    st.metric(
        label="Upside / (Downside)",
        value=f"{upside:.1%}",
        delta=f"{upside:.1%}",
        delta_color="normal" if upside >= 0 else "inverse",
    )


# ===================================================
# Scenario comparison (always shows all three)
# ===================================================
st.markdown("### Scenario Comparison")

scenarios_data = []
for s in ["Bear", "Base", "Bull"]:
    r = run_full_model(s)
    scenarios_data.append({
        "Scenario": s,
        "Implied Price": f"${r['dcf']['implied_price']:.2f}",
        "Upside/(Downside)": f"{r['dcf']['upside_pct']:.1%}",
        "WACC": f"{r['dcf']['wacc']:.2%}",
        "Terminal Growth": f"{r['assumptions']['terminal_growth']:.1%}",
    })

st.dataframe(
    pd.DataFrame(scenarios_data).set_index("Scenario"),
    use_container_width=True,
)

bull_price = run_full_model('Bull')['dcf']['implied_price']
st.info(
    f"💡 **Key insight:** All three scenarios imply CMG trades above intrinsic value. "
    f"Even the Bull case (aggressive recovery, 4 - 4.5% AUV growth, WACC 8.9%) implies "
    f"only \\${bull_price:.2f} - still below the current \\$32.89."
)


# ===================================================
# DCF Breakdown
# ===================================================
st.markdown("---")
st.markdown(f"### DCF Breakdown - {scenario} Case")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Cost of Capital (WACC)**")
    st.write(f"- Risk-free rate: {assumptions['risk_free_rate']:.2%}")
    st.write(f"- Equity risk premium: {assumptions['equity_risk_premium']:.2%}")
    st.write(f"- Beta: {assumptions['beta']:.2f}")
    st.write(f"- Cost of equity: {(assumptions['risk_free_rate'] + assumptions['beta'] * assumptions['equity_risk_premium']):.2%}")
    st.write(f"- After-tax cost of debt: {assumptions['after_tax_cost_of_debt']:.2%}")
    st.write(f"- WACC: {dcf['wacc']:.2%}")

with col2:
    st.markdown("**Valuation Bridge**")
    st.write(f"- Sum of PV UFCFs: **${dcf['sum_pv_ufcfs']/1000:,.0f}M**")
    st.write(f"- PV of Terminal Value: **${dcf['pv_terminal']/1000:,.0f}M**")
    st.write(f"- Enterprise Value: **${dcf['enterprise_value']/1000:,.0f}M**")
    st.write(f"- Net Debt: **${dcf['net_debt']/1000:,.0f}M**")
    st.write(f"- Equity Value: **${dcf['equity_value']/1000:,.0f}M**")
    st.write(f"- Diluted Shares: **{dcf['diluted_shares']/1000:,.0f}M**")


# ===================================================
# UFCF Build
# ===================================================
st.markdown("### Unlevered Free Cash Flow Build")
ufcf_df = dcf["ufcf_df"]

# Format for display
ufcf_display = ufcf_df.copy()
for col in ufcf_display.columns:
    if col != "Tax_rate":
        ufcf_display[col] = ufcf_display[col].apply(lambda x: f"${x:,.0f}")
ufcf_display.loc["Tax_rate"] = ufcf_df.loc["Tax_rate"].apply(lambda x: f"{x:.1%}")

st.dataframe(ufcf_display, use_container_width=True)


# ===================================================
# Forecast Financial Statements (collapsible)
# ===================================================
st.markdown("---")
st.markdown("### Forecast Financial Statements")

with st.expander("📈 Income Statement (2026E–2030E)"):
    is_display = results["forecast_is"].copy()
    for col in is_display.columns:
        is_display[col] = is_display[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(is_display, use_container_width=True)

with st.expander("📊 Balance Sheet (2026E–2030E)"):
    bs_display = results["forecast_bs"].copy()
    for col in bs_display.columns:
        bs_display[col] = bs_display[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(bs_display, use_container_width=True)

with st.expander("💰 Cash Flow Statement (2026E–2030E)"):
    cf_display = results["forecast_cf"].copy()
    for col in cf_display.columns:
        cf_display[col] = cf_display[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(cf_display, use_container_width=True)


# ===================================================
# Footer
# ===================================================
st.markdown("---")
st.markdown(
    "**Data source:** Chipotle 10-K filings (2021–2025), SEC EDGAR · "
    "**Current price as of:** May 2026 · "
    "**Model:** [GitHub](https://github.com/Heer1910/quarry-financial-model)"
)
