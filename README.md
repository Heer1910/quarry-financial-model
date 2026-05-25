# Quarry — Chipotle Mexican Grill Financial Model

🌐 **[Live Demo →](https://quarry-cmg-model.streamlit.app)** · 📂 [GitHub Repo](https://github.com/Heer1910/quarry-financial-model)

A complete three-statement financial model and DCF valuation for Chipotle Mexican Grill (NYSE: CMG), built in both Google Sheets and Python.

**Implied share price:** $19.40 (Base case) vs. current $32.89 → **41% downside**

![Dashboard](docs/screenshots/01_dashboard_hero.png)

---

## Key findings

| Scenario | Implied Price | Upside/(Downside) | Story |
|---|---|---|---|
| Bear | $13.07 | -60.3% | Structural decline thesis |
| Base | $19.40 | -41.0% | Steady-state, no recovery |
| Bull | $29.76 | -9.5% | Aggressive recovery still below market |

**Conclusion:** Even the bull case shows modest downside. The market is pricing CMG beyond an aggressive-recovery scenario, suggesting the stock is fully valued to overvalued.

![Bull case toggled](docs/screenshots/03_bull_case.png)

*Scenarios update in real-time via the sidebar toggle.*

---

## What this project demonstrates

- **Financial modeling fundamentals:** historical balance sheet reconciliation across 5 years (treasury stock retirement, 50-for-1 stock split, materiality adjustments), three-statement linking, DCF valuation with WACC and terminal value, scenario analysis
- **Python proficiency:** translating Excel logic to pandas DataFrames, modular code architecture, proper IS→BS→CF circular linking
- **Data pipelines:** loading historical 10-K data from CSV files, cleaning currency strings, structured data validation
- **Deployment:** interactive Streamlit dashboard hosted on Streamlit Community Cloud

---

## Project structure

```
quarry-financial-model/
├── app/
│   └── streamlit_app.py        # Interactive dashboard
├── data/                       # Historical 10-K data (2021A-2025A) as CSV
│   ├── historical_is.csv
│   ├── historical_bs.csv
│   └── historical_cf.csv
├── docs/
│   └── screenshots/            # Project visuals
├── src/                        # Model logic
│   ├── assumptions.py          # Bull/Base/Bear scenario inputs
│   ├── data_loader.py          # CSV → pandas DataFrames
│   ├── income_statement.py     # IS forecast (2026E-2030E)
│   ├── balance_sheet.py        # BS forecast with cash plug
│   ├── cash_flow.py            # CF forecast + circular link to BS
│   ├── dcf.py                  # DCF valuation
│   └── main.py                 # Orchestrator
├── tests/
├── requirements.txt
└── README.md
```

---

## How to run

```bash
# Clone the repo
git clone https://github.com/Heer1910/quarry-financial-model.git
cd quarry-financial-model

# Set up environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the full model (CLI output)
python3 -m src.main

# OR launch the interactive Streamlit dashboard
streamlit run app/streamlit_app.py
```

---

## Methodology

**Historical period (2021A-2025A):** Sourced from Chipotle 10-K filings on SEC EDGAR. Balance sheet reconciles to zero across all five years after adjusting for the 50-for-1 stock split (mid-2024) and treasury stock retirement ($5.2B).

**Forecast period (2026E-2030E):** Five-year forward forecast driven by:
- Store count (openings, closures) and AUV growth
- Cost ratios as % of revenue (food/bev, labor, occupancy, G&A, D&A)
- Working capital days (DSO, DIO, DPO)
- CapEx per new store + maintenance % of revenue

**DCF:** Unlevered free cash flow with mid-year convention, terminal value via Gordon Growth, WACC from CAPM (Rf 4.20%, ERP 5.50%, Beta 1.05 Base).

**Scenarios:** Single-dropdown toggle in Sheets, `get_assumptions(scenario)` function in Python. Bear/Base/Bull differ on store openings, AUV growth, cost ratios, beta, and terminal growth.

### DCF build

![DCF breakdown](docs/screenshots/02_dcf_breakdown.png)

---

## Excel vs. Python

The same model exists in two forms. Output matches within $0.04 per share across all scenarios.

### Google Sheets — Assumptions tab

![Sheets assumptions](docs/screenshots/04_sheets_assumptions.png)

### Google Sheets — DCF tab

![Sheets DCF](docs/screenshots/05_sheets_dcf.png)

### Python — modular implementation

![Python DCF code](docs/screenshots/06_code_dcf.png)

This dual implementation demonstrates the ability to translate financial logic between tools — a key skill in real FP&A and equity research workflows.

---

## Data sources

- Chipotle Mexican Grill 10-K filings (2021–2025), SEC EDGAR
- Current share price: $32.89 (May 2026)
- Sell-side targets: Guggenheim $35, consensus ~$46, Citi $46

---

## Author

**Heer Patel** — Data Science + Finance, University of Illinois Chicago (May 2026)
[Portfolio](https://heer1910.github.io) · [LinkedIn](https://www.linkedin.com/in/heer1910)