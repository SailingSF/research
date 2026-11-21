# CLAUDE.md

## What this is
Research + charts for a goodatinvesting.com blog post on the **Anthropic IPO**, built from Anthropic's Form S-1.
Same format as the earlier SpaceX IPO post (`../spacex_s1`): sourced numbers first, narrative second.

Source filing: final prospectus (424B4), filed 2026-11-19 (CIK 2130357, accession 0001628280-26-074944), priced at $83 on Nov 18,
https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm
Financials cover FY2023–FY2025, nine months to Sep 30 2025/2026, and Q1-2025 → Q3-2026; they're identical to S-1/A No. 1's
(Nov 2). Offering terms live in `data/valuation_inputs.csv` (08). ANT began trading Nov 19 (opened $111.50).
SpaceX's Q3 10-Q is cached at `source_docs/spacex/spcx_10q_2026q3.htm` (+ `.txt` for grep).

## Audience and tone
Technical readers who understand AI deeply but are **not** finance pros.
- Explain the finance (fair-value marks, convertible notes, liquidation preference, dilution, non-GAAP add-backs,
  purchase commitments, multiples); don't explain models, tokens, or GPUs.
- Dry, skeptical, willing to say the quiet part out loud. Jokes are garnish, not a substitute for sourced numbers.
- Be fair to the company: the S-1 facts first, then the critique.

## Layout
```
anthropic_ipo/
├── CLAUDE.md
├── research.ipynb          <- the post's thread (create when the outline exists)
├── 01_extract_s1.ipynb     <- S-1 -> data/*.csv, plus reconciliation checks
├── 0N_<subject>.ipynb      <- one analytical subject each (e.g. growth, compute economics, cap table, valuation)
├── data/                   <- extracted CSVs; see data/README.md for every file and its conventions
├── charts/                 <- PNGs, each saved by exactly one notebook
└── source_docs/            <- the S-1 HTML, a greppable s1_full.txt, and chart images from the filing
```
- `research.ipynb` follows the blog post section by section, re-checks every number the post uses against `data/`,
  and embeds the charts in post order. Re-run it after re-running any analysis notebook.
- Edit notebooks directly. They are the source; there is no generator script.
- Every analysis notebook follows one reasoning thread:
  - **Opening cell:** the question; a numbered **Short answer** citing the § and chart for each point; a roadmap
    table (§ / question / chart); inputs and outputs.
  - **Each section:** heading phrased as a question; why we're asking and the method in plain language; code, then
    the chart inline; **What this shows**, naming the chart file; **Next**, the question it raises.
  - **End:** **Findings, by section**; caveats; open items.
- Markdown cells explain each equation and assumption in plain language.
- Every chart in `charts/` is saved by exactly one notebook, in the section that discusses it. Put a chart's reading
  in the cell right after it.
- When a later notebook overturns an earlier result, say so where the earlier claim is made.
- `montecarlo.py` is 06's simulation + 08's valuation as one module (`mc.PARAMS`, `mc.run(**changes)`, `mc.fixed_worlds`, `mc.contract_worlds()` for 09 §6's contracts view, `mc.public_benefit_multiple()` for 09 §7). Its defaults must
  match 06's `A`/`MC` and 08's `V` (`prize_chance` defaults to 0, so the breakthrough input is off unless set): change an assumption in both places, and 09 §1 asserts they still agree.
- `common.py` holds the chart style (reference dataviz palette), `load()`/`wide()` CSV helpers and `save()`. Import from it.
- Notebooks so far: `02_real_earnings.ipynb` (GAAP loss anatomy; real revenue, operating income, FCF) and
  `03_growth_vs_compute.ipynb` (compute commitment schedule, revenue scenarios, path to real profitability, cash runway),
  `04_gaap_loss_and_dilution.ipynb` (net loss = marks; fully diluted share count ~16.4B; new shares after the IPO by scenario),
  `05_token_economics.ipynb` (serving cost per $ of revenue; subscription vs API margins by usage multiple; cost per token).
  `06_forecast.ipynb` (what the $895B of compute commitments is, by partner and in context; Gompertz revenue curves: ceiling from the S-1 TAM, speed fitted to the quarters; Monte Carlo of revenue, real operating margin, FCF to 2030).
  `07_chip_mix.ipynb` (announced MW by chip family and deal, online by year; $ per MW-year by deal (spot vs multi-year vs owned); vs the MW that 06's revenue percentiles need; rented vs leased vs owned; outside data, reads `data/forecast.csv`).
  `08_valuation.ipynb` (DCF of every 06 world on today's ~16.4B shares: CAPM rate, curves extended to 2040 + 3% perpetuity; value per share vs rounds and IPO range; sensitivity; reverse DCF).
  `09_playground.ipynb` (change any input in one `P` dict; checks `montecarlo.py` reproduces 06/08; works back from the IPO price: which worlds, one dial at a time, ceiling × efficiency map; §6 values the revenue Anthropic's own compute contracts can serve; §7 what grants, donations and Public Benefit top-ups cost per share).
  `10_spacex_and_prize.ipynb` (EV/revenue vs SpaceX at $83; price vs each post's DCF and the contracts view; implied chance of a $10T breakthrough; Kelly position size vs your breakthrough odds).
  `research.ipynb` follows `outline.md` section by section: `check()` asserts each number the post quotes against `data/` or `montecarlo.py`, then shows the charts.
  Hand-offs: 02 → `data/real_earnings.csv`; 03 → `data/compute_schedule.csv`, `data/projections.csv`; 04 → `data/dilution.csv`;
  05 → `data/token_economics.csv`, `data/external.csv` (outside data: list prices, plan prices, measured subscription usage); 06 → `data/forecast.csv`, `data/forecast_worlds.csv` (per-world detail for 08); 07 → `data/compute_capacity.csv` (outside data, each row with `as_of`, `source_url`, `reliability`);
  08 → `data/valuation.csv` (P10–P90 and `mean`; the post's headline is the mean), `data/valuation_inputs.csv` (outside data: rates, ERP, betas, IPO terms and the $83 price);
  10 → `data/comps_spacex.csv` (outside data: SPCX price, 10-Q balance sheet/revenue/cash flow checked against cached XBRL in `source_docs/spacex/`, Cursor deal value, industry betas, the SpaceX post's DCF). 10 §2 imports `../spacex_s1/analysis/dcf.py` and re-values its forecasts on 08's rules (Sep-30 balance sheet, Cursor at deal value, stock comp + 21% tax as costs, CAPM with revenue-weighted beta).
  06's assumptions live only in its `A` (costs, same values as 03) and `MC` (Monte Carlo ranges) dicts.
- **Per-share numbers use the ~16.4B fully diluted count from 04**, never the 2.1B EPS denominator.
  03's assumptions live only in its `A` and `SCENARIOS` dicts.
- **"Real" definitions (use these everywhere):** real operating income = GAAP operating income + Bartz (one-off);
  stock comp and share-paid donations stay as costs. Clean revenue = reported − 6% (5–7%) policy-violator revenue, 2026 only.
  FCF = CFO − PP&E − equipment prepayments − finance-lease principal; operating FCF = FCF − interest income;
  owner FCF = operating FCF − SBC − donations. The company's "Adjusted" figures add back SBC and donations: quote them, don't adopt them.
- Use a fresh chart style for this post. Don't import the SpaceX house style.

## Data rules
- `data/*.csv` is the single source of truth for S-1 numbers. Notebooks read from it; don't hardcode filed figures in cells.
  Fix extraction problems in `01_extract_s1.ipynb`, never by hand-editing a CSV.
- Hand-entered narrative numbers live in `kpis.csv` with an `approx` flag (`~`, `>`, `<`) and the source quote.
  Keep the flag when you use them ("more than 11,900", not "11,900").
- **10-for-1 split (2026-09-17):** preferred counts/prices in `preferred_stock.csv` are pre-split; each converts into 10 common.
  Use `issue_price_per_common_usd` when comparing round prices to a per-share IPO price.
- **GAAP net loss is mostly a valuation mark.** The fair-value change on convertible notes and other instruments
  ($94B + $10B in 9M-2026) tracks Anthropic's own rising valuation. Say so whenever net loss appears.
- Two cuts of opex exist (natural lines in the income statement, functional lines in `opex_by_function.csv`). Don't mix them.
- Anything not from the S-1 (peer multiples, private marks, market prices, press) goes in a separate CSV with
  `as_of`, `source_url` and a `reliability` flag, and stays out of the reconciliation checks.
- Prefer primary sources (EDGAR) over press. If they conflict, flag it rather than silently picking one.

## Environment
- Python venv: `~/.venvs/research`; the notebooks use its `python3` kernel. Installed: pandas, matplotlib,
  requests, beautifulsoup4, jupyter. Not installed: lxml (so no `pd.read_html`; the extractor parses with bs4).
- Run a notebook headlessly: `~/.venvs/research/bin/jupyter execute --inplace <nb>.ipynb`
- EDGAR requests need a contact User-Agent: set `SEC_USER_AGENT` in `.env` (gitignored) (sec.gov only).
  Cache every download in `source_docs/` and load from the cache on re-runs.
- Search the filing's narrative with `grep -n ... source_docs/s1_full.txt`.
- Git exists only to open-source the research later; no need to commit as you go.
