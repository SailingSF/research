# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
Research + charts for a goodatinvesting.com post: **"What do you actually own when you buy an AI bond?"**
Core question: do the yields on CoreWeave, Meta (corporate vs. Beignet/Sopaipilla SPVs), SpaceX, and Alphabet
bonds reflect what the bondholder is actually entitled to? The full plan, bond universe, data sources, and
open questions live in @research_plan.md. Read it before starting any analysis step.

## Audience and tone
Same as the previous SpaceX IPO post: technical readers who understand AI/tech but are **not** finance pros.
- Explain the finance (spread, OAS, recovery, credit triangle, Merton, LTV) in plain language; don't explain GPUs or AI.
- Dry, skeptical, willing to say the quiet part out loud. Jokes are garnish, not a substitute for sourced numbers.
- Notebook markdown cells should explain each equation and assumption in plain language.

## Layout
- Follow the plan's split: `01_data_pull.ipynb` → `06_fundamentals.ipynb`, plus `07_meta_spvs.ipynb` (SPV structure), `08_neoclouds.ipynb` (CoreWeave customers, rent, GPU renewal break-even, the equity backstop; Nebius as a funding contrast), `09_trades.ipynb` (priced trade ideas for the post) and `10_gpu_unit_economics.ipynb` (per-GPU rent, resale, payback, margin vs. cost of debt, second life after contracts end, CoreWeave's contract pricing, fleet by chip generation and expected chip lives, Q3 2026 update on contract financing and the holding company's bonds, and the post's "off the razor's edge" chart), one analytical subject each.
  `research.ipynb` is the post's thread: it follows `post_outline.md` section by section, re-checks every number the post uses against the handoff files (`check()` fails if a claim is stale), embeds the post's charts in post order, and saves the one post-only chart (`00_what_the_spread_pays_for.png`). Re-run it after re-running any analysis notebook; update it and the outline when a finding or chart changes.
- Edit the notebooks directly. They are the source; there is no generator script.
- Every analysis notebook follows one reasoning thread:
  - **Opening cell:**
    - the question;
    - a **Short answer**, numbered and citing the § and chart each point comes from;
    - a roadmap table (§ / question / chart);
    - inputs and outputs.
  - **Each section:**
    - heading phrased as a question;
    - why we're asking, then the method in plain language;
    - code, then the chart, displayed inline;
    - **What this shows**, naming the chart file;
    - **Next**, the question it raises.
  - **End:**
    - **Findings, by section**, numbered to match the sections;
    - caveats;
    - open items.
- Every chart in `charts/` is saved by exactly one notebook, in the section that discusses it. Put a chart's reading in the cell right after it, not only in the findings or in chat.
- When a later notebook overturns an earlier result, say so where the earlier claim is made (e.g. "Revised in 06 §7"). Don't leave it only in the later notebook.
- `bonds.csv` (plan §4) is the single source of truth for bond terms. Notebooks read from it; don't hardcode
  coupons, maturities, ratings, or recovery assumptions in cells.
- `issuers.csv` is the same for company-level inputs (shares, debt, liabilities, cash), each with a 10-Q source and date.
- `common.py` holds the shared chart style, cached FRED/equity loaders, Treasury interpolation, and bond price/yield math. Black-Scholes (`bs_call`, `bs_put`) lives there too. Import from it instead of redefining.
- Notebooks hand results forward via `data/spreads.csv` (02), `data/implied_pd.csv`, `data/forward_pd.csv` and `data/yield_buys.csv` (03), `data/merton_inputs.csv` and `data/equity_vs_bond.csv` (05), and `data/fundamentals.csv`, `data/merton_iv.csv` and `data/crash_odds.csv` (06), `data/equity_backstop.csv` (08), `data/trades.csv` and `data/trade_profiles.csv` (09), and `data/gpu_economics.csv` (10). 10's hand-entered GPU prices live in `data/gpu_units.csv` and past GPU retirement dates (Azure, Google) in `data/gpu_lifespans.csv`; its Ornn/GetDeploying rent pulls are cached in `data/gpu_prices/`. 09's bond prices are hand-entered TRACE closes in `data/trade_quotes.csv`. 08's and 10 §6's hand-entered CoreWeave inputs (incl. active power by quarter and management pricing statements) live in `data/neocloud_inputs.csv` and `data/neocloud_customers.csv`. CoreWeave's debt by facility and maturity (contract-repaid loans vs. parent bonds) is in `data/crwv_debt.csv`. Nebius isn't in `issuers.csv`, because 01/05/06 loop over every issuer and expect its stock and options data.
- Options come from Market Data's free plan (key: `MARKETDATA_TOKEN` in `.env`), cached as one snapshot per date in `data/options/`. 09's full Jan 2029 chains are cached separately in `data/options/trades/`, so 01/06 don't pick them up. Each contract costs a credit (10,000 a day), so keep pulls filtered. The free plan serves the previous day's close.
- TRACE prices for any CUSIP: FINRA's bond page (`finra.org/finra-data/fixed-income/bond?symbol=<finra_symbol>&bondType=CORP`) shows the last trade's price, yield and date as page text; read it in Chrome (`document.body.innerText`). The page's `EndOfDayPriceYield` data service hangs when queried directly (Nov 6 and Nov 10). FINRA shows no yield for some 144A lines (SpaceX 2033–56, Beignet); compute it from the price with `common.ytm`. Company financials come from the SEC XBRL API, cached in `data/edgar/companyfacts_*.json`.
- Use a fresh chart style for this post. Don't import the house style from `../spacex_s1`.

## Environment
- Python venv: `~/.venvs/research` (the notebooks' `research` kernel). Use `~/.venvs/research/bin/python`.
  Installed: pandas, matplotlib, seaborn, fredapi, requests. **Not** installed: yfinance, pyarrow, so cache as CSV, not parquet.
- FRED: read the key from the `FRED_API_KEY` env var. Never hardcode it or write it into a notebook output.
- Cache every external pull (FRED, TRACE exports, EDGAR) to disk and load from the cache on re-runs.
  FRED's ICE OAS history can be truncated later, so the cache is the record.
- Run a notebook headlessly (nbconvert isn't installed): `~/.venvs/research/bin/jupyter execute --inplace <nb>.ipynb`

## Data rules
- Most bond prices and yields in the plan are press figures from June–July 2026. Treat them as stale.
  Every hand-entered market number (prices, yields, deal terms, CDS levels) needs an as-of date and a source URL next to it.
- Prefer primary sources (EDGAR filings, TRACE, rating agency rationales) over press. If they conflict, flag it rather than silently picking one.
- When resolving an item in plan §7 ("Open questions"), tick it off in `research_plan.md`.
