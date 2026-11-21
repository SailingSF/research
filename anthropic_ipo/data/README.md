# Anthropic S-1 — extracted CSVs

All files are written by `01_extract_s1.ipynb` from the S-1/A (Amendment No. 1, filed 2026-11-02,
accession 0001628280-26-068676). Don't hand-edit them; fix the notebook and re-run it.

## Conventions
- Long format: `line_item, period, period_type, unit, value`.
- `value` in **millions USD** unless `unit` says otherwise (`pct`, `usd_per_share`, `thousands_shares`, `count`).
- Parentheses → negative. `—` → 0. `*` (below the 10% disclosure threshold) → empty.
- Periods: `FY2023`–`FY2025` (years to Dec 31), `9M-2025` / `9M-2026` (nine months to Sep 30),
  `Q1-2025`…`Q3-2026`, balance-sheet dates `2024-12-31`, `2025-12-31`, `2026-09-30`.
  `period_type`: `year` | `ytd_9m` | `quarter` | `instant`.
- **10-for-1 split on 2026-09-17.** Common shares, options and EPS are post-split. Preferred share counts
  and issue prices are pre-split; each preferred share converts into 10 common.

## Files
| File | What | S-1 table |
|---|---|---|
| `income_statement.csv` | Consolidated P&L (natural expense lines: compute, personnel, S&M+partnerships, other), EPS, share count | F-pages |
| `quarterly_income_statement.csv` | Same P&L, Q1-2025 → Q3-2026 | MD&A |
| `balance_sheet.csv` | 3 dates | F-pages |
| `cash_flow.csv` | `section` = operating adjustments / working capital / investing / financing | F-pages |
| `comprehensive_income.csv` | OCI | F-pages |
| `non_gaap.csv` | `measure` = `adjusted_operating_income` / `adjusted_net_income`; reconciliation lines, annual + quarterly | MD&A |
| `revenue_breakdown.csv` | `dimension` = `geography` (US / International) / `pricing_model` (consumption / subscription) | Note 2 |
| `opex_by_function.csv` | Cost of revenue / R&D / S&M / G&A view of the same opex | Note |
| `customer_concentration.csv` | Anonymised customers ≥10% of revenue or receivables | Note 2 |
| `balance_sheet_detail.csv` | `schedule` = ppe / prepaid_current / other_assets_noncurrent / payables_accruals | Notes |
| `flow_detail.csv` | `schedule` = lease_cost / other_income_expense / supplemental_cash_flow / tax_provision / credit_loss_allowance | Notes |
| `contractual_obligations.csv` | Leases + **$314B compute purchase commitments** by year due, as of 2026-09-30 | MD&A |
| `convertible_notes_outstanding.csv` | Amazon 2023/2024 rollover notes: principal, conversion price, Class N shares on conversion (wide) | MD&A |
| `note_facilities_2026.csv` | Undrawn 2026 facilities: Google $20B, Amazon $15B, Broadcom $42B (wide) | MD&A |
| `fair_value_rollforward.csv` | Level 3 roll-forward by instrument (convertible notes, warrants, partner financing, donation matching, SAFEs) | Note 4 |
| `deferred_revenue_rollforward.csv` | Deferred revenue roll-forward | Note 3 |
| `preferred_stock.csv` | By series at 2025-12-31 and 2026-09-30: shares (thousands, pre-split), issue price, carrying value, liquidation preference, `issue_price_per_common_usd` | Note |
| `share_counts.csv` | `schedule` = common_reserved_as_converted (by series, options/RSUs, pools) / antidilutive_excluded | Notes |
| `stock_options.csv` | Option roll-forward (wide) | Note |
| `kpis.csv` | **Hand-entered** narrative KPIs (customer tiers, NRR, RPO, headcount…) with `approx` flag and source quote | prose / `mda2ba.jpg` |

## Derived (written by analysis notebooks, not the S-1 extractor)
| File | Written by | What |
|---|---|---|
| `real_earnings.csv` | `02_real_earnings.ipynb` | metric × period: revenue, clean revenue, GAAP / adjusted / real operating income, SBC, donations, CFO, FCF, operating FCF, owner FCF |
| `compute_schedule.csv` | `03_growth_vs_compute.ipynb` | Estimated compute-commitment payments by year and layer. Totals tie to the S-1's $895.4B; the yearly spread outside the S-1 table is **our estimate** |
| `projections.csv` | `03_growth_vs_compute.ipynb` | scenario × period × metric (revenue, compute, real operating income, owner FCF, FCF, cash) |
| `dilution.csv` | `04_gaap_loss_and_dilution.ipynb` | Shares by source: `today` (fully diluted at 2026-09-30), `today_reserved`, and new shares through 2030 by scenario; `pct_of_fd` is % of today's count |
| `token_economics.csv` | `05_token_economics.ipynb` | For each usage multiple `m` (list-price $ of tokens per $1 of subscription fee) and API discount `d`: implied serving cost per $1 of list price `c`, API / subscription gross margin, API margin after channel fees (9M-2026) |
| `forecast.csv` | `06_forecast.ipynb` | metric × period × percentile (P10–P90) from 20,000 simulated worlds: revenue, compute, real operating income/margin, owner FCF/margin, FCF, cash |
| `forecast_worlds.csv` | `06_forecast.ipynb` | One row per simulated world (20,000): ceiling, speed, revenue per compute $, Q4-2030 run-rate, revenue and owner FCF by year |
| `valuation.csv` | `08_valuation.ipynb` | P10–P90 and mean (`percentile` = `mean`) of DCF value components ($M) and value per share on today's ~16.4B fully diluted shares, with the discount rate and terminal growth used |
| `valuation_inputs.csv` | `08_valuation.ipynb` | **Not from the S-1.** Risk-free rate, equity risk premium, industry betas (Damodaran), IPO price range (S-1/A No. 2, primary), $83 IPO price, shares offered, underwriters' option, private placement, net proceeds and shares outstanding after (final prospectus 424B4, primary), ANT's day-one open (press), Oct-2026 Run-Rate Revenue (FWP), each with `as_of`, `source_url`, `reliability` |
| `comps_spacex.csv` | `10_spacex_and_prize.ipynb` | **Not from the S-1.** SpaceX (SPCX): Nov-18 close (same day as Anthropic's pricing), 10-Q shares, cash, securities, debt, revenue (total, SI and its Advertising / Solutions & Infrastructure split, Connectivity), Customer B's share of revenue, cash flow (asserted against cached XBRL in `source_docs/spacex/`), stock comp, interest income and lease principal for owner FCF, FY2025 from its S-1, Cursor's $60B deal value (8-K), Damodaran aerospace and wireless-telecom betas, and the SpaceX post's original DCF per share (10 re-values the post's forecasts and asserts it still reproduces these); each with `as_of`, `source_url`, `reliability` |
| `compute_capacity.csv` | `07_chip_mix.ipynb` | Announced compute capacity per deal (MW, contracted and online by end-2026), chip family, rented/leased/owned. **Outside data** (releases, press, our estimates), with `as_of`, `source_url`, `reliability` |
| `external.csv` | `05_token_economics.ipynb` | **Not from the S-1.** API list prices, plan prices, measured subscription usage and analyst margin estimates, each with `as_of`, `source_url`, `reliability` (primary / measured / analyst / press) |

## Not extracted (blank in this amendment)
Offering size and price, pro forma capitalization, dilution, beneficial-ownership percentages, lock-up release
share counts, Run-Rate Revenue as of Oct 31 2026. Re-run on the priced amendment.

## Gotchas
- **Convertible notes are carried at fair value** ($130.5B at 2026-09-30) against $6.2B of principal. The
  fair-value change ($94B in 9M-2026) drives almost all of the GAAP net loss.
- `opex_by_function.csv` and the income statement are two cuts of the same total; don't add them.
