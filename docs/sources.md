# Data Sources & References

All financial data in this model is sourced from publicly available filings and verifiable market data. Below are the direct references for every input.

---

## Historical financials (2021A–2025A)

Sourced from Chipotle Mexican Grill 10-K annual filings on SEC EDGAR.

| Fiscal Year | 10-K Filing | Period covered |
|---|---|---|
| 2021A | [10-K for FY2021](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K&dateb=&owner=include&count=40) | Jan 1 – Dec 31, 2021 |
| 2022A | [10-K for FY2022](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K&dateb=&owner=include&count=40) | Jan 1 – Dec 31, 2022 |
| 2023A | [10-K for FY2023](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K&dateb=&owner=include&count=40) | Jan 1 – Dec 31, 2023 |
| 2024A | [10-K for FY2024](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K&dateb=&owner=include&count=40) | Jan 1 – Dec 31, 2024 |
| 2025A | [10-K for FY2025](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K&dateb=&owner=include&count=40) | Jan 1 – Dec 31, 2025 |

All filings can be found at the [SEC EDGAR page for Chipotle Mexican Grill (CIK 0001058090)](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-K).

---

## Market data

| Input | Value | Source / As of |
|---|---|---|
| Current share price | $32.89 | Public market quote, May 2026 |
| Diluted shares outstanding (2025A) | 1,342,616 thousand | CMG 2025 10-K |
| Risk-free rate (10Y Treasury) | 4.20% | U.S. Treasury Yield Curve, May 2026 |
| Equity risk premium | 5.50% | Standard ERP estimate (Damodaran, January 2026) |
| Beta (Base case) | 1.05 | 5-year regression of CMG returns vs. S&P 500 |

---

## Sell-side reference (sanity check)

These are external analyst price targets used purely for context — not inputs to the model.

| Firm | Target | Note |
|---|---|---|
| Guggenheim | $35 | Most bearish published target |
| Sell-side consensus | ~$46 | Mean of major-firm targets |
| Citi | $46 | Bullish target |

---

## Corporate actions adjusted for

The historical model reconciles the following events to ensure clean trend comparison:

- **50-for-1 stock split** (mid-2024) — pre-split share counts and per-share values normalized to post-split equivalents
- **Treasury stock retirement** (2024, $5.2B) — Treasury Stock zeroed out, Retained Earnings reduced by the retirement amount

---

## Notes on simplifications

The Python implementation makes two intentional simplifications relative to the full Sheets model:

1. **ASC 842 operating leases** — Python grows lease assets and liabilities proportional to revenue rather than tracking individual lease schedules. Creates a small balance sheet gap (~$300K on a $10B+ BS, or 0.003%).
2. **Cash flow items zeroed out** — Deferred tax, FX effects, and tax withholding on SBC are set to $0 in the forecast (each is <$50M in history and immaterial to valuation conclusions).

Both simplifications are documented in source code and verified via the test suite.