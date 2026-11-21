# Research Plan: What Do You Actually Own When You Buy an AI Bond?

*Working title for goodatinvesting.com. Research plan drafted Oct 24, 2026.*

---

## 1. The thesis

AI infrastructure is being funded with debt, but "a bond" means very different things depending on who issued it and what it's secured by. The question for the post: **do the yields on these bonds actually reflect the risk of what the bondholder is entitled to?**

### Original framing
- **CoreWeave**: your bond is backed by a GPU with tangible value.
- **Meta**: your bond is backed by the incredibly profitable businesses of Facebook and Instagram.
- **SpaceX**: your bond reflects a massively indebted company that can never pay down its debt with its profitable but smaller space and connectivity business.
- **Google**: chose to sell equity instead of issuing debt.

### Refined framing (after initial research)
In at least two of the three cases, the bond doesn't give you a claim on the thing in the original framing. That gap is the hook.

| Issuer | Instrument | What you actually own | Status mid-2026 |
|---|---|---|---|
| **CoreWeave** | $8.5B IG-rated delayed-draw term loan (Mar 2026) | Secured by GPUs **plus a customer contract**, reportedly Meta contracts worth ≥$19B | Investment grade |
| **CoreWeave** | Senior unsecured notes (2031/2032) | CoreWeave's unsecured promise to pay | Traded at 76.5–81¢, yielding 15–16% |
| **Meta** | Meta Platforms corporate bonds (e.g. ~$30B Oct 2025) | Senior unsecured claim on Meta, i.e. Facebook/Instagram cash flows | Use as a baseline |
| **Meta / Blue Owl** | Beignet Investor LLC: $27B, 6.581%, due 2049 (Hyperion, Louisiana) | **Not Meta.** An SPV (80% Blue Owl, 20% Meta). Meta pays rent, renewable every 4 years. If Meta leaves, the data center is sold and Meta covers any shortfall (residual value guarantee). | A+ at issue; record low ~94.4¢ while Meta stock rallied |
| **Meta / BlackRock** | Sopaipilla (El Paso, ~$12B, 2026) | Same SPV structure | Investors demanded ~0.4 pts more than Hyperion |
| **SpaceX** | $25B senior unsecured notes, 5 tranches (5/7/10/20/30yr), Jun 2026 | Unsecured claim on SpaceX | IG from all 3 agencies; 10yr set ~50bp over Intel at the same rating |
| **Alphabet** | Existing corporate bonds | Claim on a company that raised ~$84.75B of equity **and** ~$52B of bonds in H1 2026 (see first-pass findings) | Control group (AA+ baseline) |

### First-pass findings (Oct 24, 2026) that change the framing
Sources and links are in §7. Market levels are press quotes with dates in `quotes.csv`. FRED snapshot on Oct 22: 10yr 4.96%, 30yr 5.29%; OAS A 75bp, BBB 111bp, B 346bp, CCC 1,340bp.

1. **CoreWeave: the contract is the collateral, and the company says so.** The DDTL 4.0 rating is "supported by a long-term customer contract with an investment-grade AI enterprise." After stabilization the loan is sized off contract cash flow (1.2x DSCR) and can reach **~102% of what the GPUs cost**. Strip out the contract and the hardware alone can't cover the loan, even on day one. Same company, two claims: the subsidiary loan is **A3**, the parent is **B+/Ba3** (six notches lower). The parent's unsecured 9.75% 2031s traded at 78–83 (~15–16% yield) in mid-Oct. That's ~10pp over Treasuries, between the B (3.5pp) and CCC (13.4pp) averages.
2. **Meta SPVs: you own a 4-year lease plus a conditional, declining, capped guarantee.** You don't own a Meta bond. The market prices the gap: Meta corporate 2036s priced at T+90 in April, while Sopaipilla priced at ~T+287 in July with a one-notch-lower rating. Beignet is at ~91–92¢ (~7.5%).
3. **SpaceX: net cash today, burning fast, thin covenants.** At Sep 30: $89.9B cash + securities vs. $38.0B debt, so **~$52B net cash**. But 9-month free cash flow was about −$35B (OCF $13.1B, capex $48.1B). At that pace net cash is gone in roughly 1–1.5 years, not by 2029–31. The notes have no subsidiary guarantees, no CoC put, and a lien carve-out that lets new GPU debt jump ahead. The 2036s widened from ~140bp at issue to ~193bp (BBB average: 111bp); the 2056s are at ~83¢.
4. **Alphabet is not the "equity, not debt" control group.** It did both: $51.8B of bonds in H1 2026 *and* the $84.75B "equity raise." Of that raise, ~$30B of the $40B ATM goes to an "administrative change" in how it pays employee stock-comp taxes, and $15B is mandatory convertible preferred. Reframe as "the AA+ hyperscaler that still borrows at T+43 to T+83, and also sold stock."
5. **Anthropic/Broadcom is a TPU SPV, not GPU-backed.** It's a third structure: a supplier-guaranteed lease SPV. Good for a sidebar comparing who backstops what.

### Control group decision (Oct 25)
**Apple is the control. Alphabet moves into the treatment group** as "the AI spender with a fortress balance sheet." Apple (AA+/Aaa) has issued no bonds in 2026 (its last deal was May 2025, $4.5B to fund buybacks). Alphabet borrowed ~$52B in H1 to fund capex. The post reads as a ladder: Apple → Alphabet → Meta corporate → Meta SPVs → SpaceX → CoreWeave. Each bond is compared with its rating bucket's ICE OAS **on the same date**, which strips out market-wide moves.

### Spread findings (`02_spreads.ipynb`, updated Oct 25 with Oct 23 TRACE closes)
**Most robust measure:** the change in excess spread (bond spread minus its rating-bucket average) since the bond was issued. It's the same bond at the same maturity, so the bucket's maturity mix cancels out.

| Bond | Excess at issue | Excess now (Oct 23) | Change |
|---|---|---|---|
| Apple 2030 / 2035 (control) | −28 / −8 | −49 / −39 | **−21 / −31** (tightened) |
| Alphabet 2031 / 2036 / 2056 | −6 / +14 / +34 | −12 / +17 / +57 | −6 / +3 / +23 |
| Meta 2031 / 2036 / 2056 | +1 / +38 / +80 | +15 / +41 / +137 | +14 / +3 / **+57** |
| Beignet 2049 | +136 | +139 | +3 (*was +30 before the Oct 26 accrued-interest fix; bullet basis. Amortizing basis in 07: +35bp raw vs. Meta's own +48bp*) |
| Sopaipilla 2048 (Jul) | +172 | +162 | −10 (was priced wide from day one) |
| SpaceX 2036 | +47 | +146 | **+99** |

Levels on Oct 23 (no issue comparison): SpaceX 2031 230bp over Treasuries; CoreWeave unsecured **992–1,052bp** (79–85¢, 14.7–15.3%), vs. a single-B average of 346bp and a CCC average of ~1,340bp.

- **Beignet has converged on Sopaipilla.** On the proper amortizing basis (07), both trade ~260–270bp over Treasuries at a ~14.5-year average life, within ~6bp of each other. The market prices the two Meta SPV structures the same.
- **The control behaves like a control.** Apple tightened against AA bonds while every AI spender widened. Alphabet barely moved except at the long end, Meta widened most at 30 years, and SpaceX widened most of all.
- **Beignet: mostly rates (revised Oct 26).** Of the 9.5-point price fall since issue, ~8.2 points is rates and ~1.3 is credit/structure (05 §5). An earlier "two-thirds rates" read came from a yield solver that ignored accrued interest; fixed in `common.py`. Beignet closed at **90.515 on Oct 23**, a new low.
- **SpaceX 2036 fell 2.7 points on Oct 23 alone** (to 88.72, a 7.52% yield). All four quoted tranches now trade 130–175bp over the BBB average.
- **CoreWeave unsecured** fell further between Oct 15 (Morningstar: 83 on the 9.75% 2031s) and Oct 23 (FINRA: 81.25).
- **Junk widened; the CCC bucket blew out.** From Aug 22 to Oct 22: CCC ~1,040 → 1,340bp, B 288 → 346bp, BB 158 → 210bp, while IG barely moved (81 → 89bp, mid-range for 3 years). *(Corrected Oct 31: earlier text said BB and B "barely moved" and IG was "near 3-year lows".)*

### Maturity ("duration") adjustment: first attempt (Oct 25, `02_spreads.ipynb` §6)
**Problem.** Rating averages (ICE OAS) blend all maturities, roughly 7–10 years on average. Long bonds pay more just for being long: on Oct 22, IG 1–3y = 59bp vs. 15y+ = 107bp. So raw excess spread overstates long bonds and understates short ones.

| | Approach | Result |
|---|---|---|
| A | Same bond, change since issue | Maturity cancels out. **Use this for "did it get worse?" claims.** |
| B | Scale each rating average by the IG maturity curve (`rating OAS × IG OAS[maturity] / IG OAS[all]`) | Moves levels 10–25bp (Alphabet 2036: +17 → +3; SpaceX 2036: +146 → +123). **Doesn't change the order or the story.** Changes since issue move by <12bp. Untested assumption: every rating's curve has the same shape. HY (CoreWeave) not adjusted (no HY-by-maturity data on FRED). |
| C | Compare bonds of similar maturity side by side | At ~30y: Apple 54 → Alphabet 122 → Meta 202 → SpaceX 282bp. (The SPVs are ~15-year average-life bonds, so they belong in the 10–15y group instead: see 07.) **Cleanest chart candidate for the post.** |
| D | Rating × maturity benchmarks (ICE sub-indices like "A 7–10y", or a spread curve fitted to many TRACE bonds per rating) | **Later step.** Needs data we don't have. |

### Key nuances to resolve
- **CoreWeave**: Is the collateral value coming from the **GPU** or the **Meta contract**? Hypothesis: the contract does most of the work. The spread between the secured loan and the unsecured notes is the market's price for "GPU + contract."
- **Meta**: The equity and SPV bond markets disagreed. Beignet hit its low on the same day Meta stock rallied 9%. Why?
- **SpaceX**: With ~$100.8B of cash post-IPO, it's arguably **net cash today**. The bear case is trajectory. S&P projects cash burn through 2029–2030, and Oppenheimer projects up to $400B of net debt by 2031. The bond is a bet on burn rate.
- **Alphabet**: What spread does a company earn by *not* levering up?
- **Optional fourth structure**: Anthropic's reported ~$35B GPU-backed financing guaranteed by Broadcom (June 2026), a guarantor-backed structure.

---

## 2. Research questions

1. What is the spread over Treasuries for each bond, and how does it compare with its rating bucket?
2. What annual default probability does each spread imply?
3. What exactly is each bondholder entitled to: seniority, collateral, guarantees, covenants, recovery in default?
4. For GPU-backed debt, does the collateral value stay above the loan balance as GPUs depreciate?
5. Do equity markets and bond markets agree on each company's risk?
6. Net: are any of these bonds mispriced relative to what they actually own?

---

## 3. Data sources

### Treasury curve (free)
- **FRED** via `fredapi`: `DGS1`, `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`
- **Treasury.gov** daily par yield curve CSVs as a backup or cross-check

### Market-wide credit spreads (free)
ICE BofA option-adjusted spread series on FRED:
- **IG master**: `BAMLC0A0CM`
- **IG by rating**: `BAMLC0A1CAAA` (AAA), `BAMLC0A2CAA` (AA), `BAMLC0A3CA` (A), `BAMLC0A4CBBB` (BBB)
- **HY master**: `BAMLH0A0HYM2`
- **HY by rating**: `BAMLH0A1HYBB` (BB), `BAMLH0A2HYB` (B), `BAMLH0A3HYC` (CCC & lower)
- History on these may be truncated on FRED, so pull and cache early.

### Individual bond prices and yields
- **FINRA TRACE**: Fixed Income Data / Bond Center lookup by CUSIP. 144A trades (SpaceX notes, Beignet) are disseminated.
- **Brokerage bond search** (Schwab) for spot quotes. Check whether the Schwab Trader API returns fixed income; it probably doesn't.
- **OpenFIGI** to map CUSIP, ISIN, and FIGI.
- **CDS**: not freely available. Use levels reported in the press as reference points.

### Bond terms and legal docs
- **SEC EDGAR**
  - 10-K / 10-Q debt footnotes (maturity schedules, rates, collateral)
  - Indentures: Exhibit 4.x
  - Credit agreements: Exhibit 10.x (CoreWeave's loan facilities)
  - 8-Ks announcing note issuances (Meta, SpaceX, CoreWeave)
- **Rating agency reports**: S&P / Moody's rating rationales (free with registration). These are critical for 144A deals like Beignet, whose offering memos aren't public.
- **Press**: Bloomberg, FT, Reuters for deal terms and secondary trading levels.

### Phase 6 data sources (checked Oct 26, 2026)
- **Options (IV for Merton, IV term structure for "when is the risk"):** [Market Data](https://www.marketdata.app/pricing/). The free tier has 100 credits a day, 24h-delayed chains with `iv`/greeks, and charges 1 credit per contract (filter by `expiration` and `strikeLimit`). Starter is $30 for one month: 10k credits a day, and historical chains at 1 credit per 1,000 contracts, but historical chains return **no IV**, so we'd back it out with Black-Scholes. AAPL works with no key. The API reads its key from a `MARKETDATA_TOKEN` env var. Longest listed expiry is ~Jan 2029 (~2.2y), so Merton's T=5 needs an extrapolation or a T≈2 run. SPCX has Dec 2028 / Jan 2028 expiries (press). Alternative: Alpha Vantage Premium at $49.99/mo has `HISTORICAL_OPTIONS` with IV and greeks back to 2008.
- **Fundamentals:** SEC XBRL API (`data.sec.gov/api/xbrl/companyfacts`), free, primary, needs a User-Agent.
- **Consensus estimates:** Alpha Vantage `EARNINGS_ESTIMATES` (free key) has revenue and EPS only. No cheap source for capex/FCF consensus, so use company guidance plus press-reported S&P/Oppenheimer projections.
- **SpaceX CDS:** priced by ICE / S&P (institutional only). Press levels: 5y ~110bp in June → record ~195–197bp on Oct 7, 2026 ([Advisor Perspectives](https://www.advisorperspectives.com/articles/2026/10/07/spacex-credit-risk-gauge-record-high-fundraising-reports), [IFR](https://www.ifre.com/people-and-markets/2451735/spacex-cds-takes-off-as-bonds-stumble)). There's no cheap term structure, so short-dated SPCX options are the cheap way to see years 0–2.
- **TRACE history:** FINRA historical data costs $2,000/yr plus setup, so skip it. Use FINRA Bond Center per-bond trade history, exported manually.

### Fundamentals
- 10-K / 10-Q / S-1 for cash, debt, FCF, capex, interest expense
- Reuse the SpaceX S-1 CSVs from the existing `spacex_ipo_analysis` repo
- Reuse the GPU rental price curve (H100 decay, by-generation pricing) from the SpaceX post

---

## 4. Bond universe: the term sheet to build

One row per instrument, saved as `bonds.csv`:

| Field | Notes |
|---|---|
| `cusip` / `isin` | from EDGAR / FINRA / OpenFIGI |
| `issuer_entity` | parent, subsidiary, or SPV (exact legal name) |
| `ultimate_credit` | whose cash actually pays (e.g. Beignet → Meta rent) |
| `seniority` | senior secured, senior unsecured, subordinated |
| `secured` | Y/N |
| `collateral` | GPUs, contracts, real estate, none |
| `guarantor` | parent guarantee, residual value guarantee, third party (Broadcom) |
| `coupon`, `maturity`, `amortization` | |
| `call_features` | make-whole, par call |
| `change_of_control` | |
| `covenants` | maintenance vs. incurrence; LTV / DSCR tests |
| `rating` | S&P / Moody's / Fitch at issue and current |
| `issue_size` | |
| `144A` | Y/N |
| `assumed_recovery` | for the PD calculation |

**Initial universe:**
- CoreWeave: GPU-backed DDTL(s), senior unsecured notes (2030/2031/2032), convertibles
- Meta: 2–3 corporate bonds across the curve (e.g. 10yr, 30yr)
- Beignet Investor LLC 6.581% 2049
- Sopaipilla (if priced and trading)
- SpaceX: all 5 tranches of the June 2026 senior notes
- Alphabet: 2–3 bonds matched on maturity to the above
- Benchmark: Intel bond at the same rating and maturity as the SpaceX 10yr
- Optional: Oracle (another heavily levered AI capex story)

---

## 5. Notebook analysis plan

### `01_data_pull.ipynb`
- Pull the Treasury curve and ICE OAS series from FRED; cache to parquet/CSV
- Load TRACE price/yield history per CUSIP (manual export or scrape → CSV)
- Build `bonds.csv` term sheet

### `02_spreads.ipynb`
- Interpolate the Treasury curve to each bond's maturity (cubic spline or linear)
- **G-spread** = bond YTM − interpolated Treasury yield
- Chart each bond's spread vs. its rating bucket's OAS over time. Who trades wide or tight relative to their rating?
- Headline chart: **Same issuer, different claim**. CoreWeave secured vs. unsecured; Meta corporate vs. Beignet.

### `03_implied_default.ipynb`
- Credit triangle: `spread ≈ PD × (1 − R)` → `PD ≈ spread / (1 − R)`
- Recovery assumptions: senior unsecured ~40%, secured ~60–70%, SPV with RVG depends on the Meta guarantee
- Cumulative default probability to maturity: `1 − (1 − PD)^T`
- Headline chart: **Market-implied default odds by bond**. This is the credit version of the "Bayesian priors" chart from the SpaceX post.
- Sensitivity table: implied PD across a range of recovery assumptions

**Phase 3 findings (Oct 23 TRACE; built Oct 25).** Chart: `charts/03_implied_default_odds.png`. Results are saved to `data/implied_pd.csv` for 05/06.
- Headline metric: **5-year** implied default odds, using the same window for every bond so maturities are comparable. Each bond is compared with two benchmarks:
  - its rating bucket's OAS, put through the same formula at R = 40%;
  - S&P's historical 5-year default rate for its exact notch (2024 study, table 26, cached in `data/sp/`).
- 5-year implied odds:

  | Bond | 5-year implied odds | Note |
  |---|---|---|
  | Apple 2035 | 2% | |
  | Alphabet 2036 | 7% | |
  | Meta 2036 | 9% | |
  | Meta 2056 | 16% | |
  | Beignet / Sopaipilla | 24% / 26% | R = 60%; bullet basis |
  | SpaceX | 18–22% | |
  | CoreWeave | 60–62% | |

- **Every bond's implied odds are 5–75× history.** That's the risk/liquidity premium, so the within-rating comparison is the one that means something. Apple sits *below* its bucket (it's short-dated), and everyone else sits above it.
- **The SPV recovery paradox.** A *higher* recovery assumption makes the same spread imply *more* defaults. At 40% recovery, Beignet's odds (18.5%) roughly match Meta's own 2056 bond (16%). At 60% they're ~24%. Either the market expects to recover less than the building-plus-RVG story suggests, or it sees more default risk than Meta itself carries. We can't tell which from the price alone.
- **CoreWeave is priced like CCC, not B+.** At 0% recovery its 5-year implied odds are 43%, against S&P's CCC/C history of 46.5% and B+ history of 12.9%. No recovery assumption reconciles the price with a B+ rating.
- Known limits:
  - The PD is assumed constant every year.
  - The same maturity effect as in 02 applies: long bonds look riskier.
  - Beignet is treated as a bullet.

### `04_gpu_collateral_ltv.ipynb` (the CoreWeave chart)
- Model the loan balance over time from its amortization schedule
- Model collateral value over time with the GPU rental decay curve from the SpaceX post (H100: ~$8 → $2.85 → ~$2/hr), and as resale value under 3-year vs. 5-year useful-life assumptions
- Plot **LTV over time**: does the collateral fall below the loan balance, and when?
- Separate the GPU value from the contract value: what's the contracted cash flow (Meta) vs. the hardware's standalone worth?
- Scenario: Meta doesn't renew. What's left?

### `05_equity_vs_bond.ipynb`
- **Merton / distance-to-default** model: market cap, equity volatility (from options IV), and debt face value → implied asset value, asset vol, and default probability
- Compare equity-implied PD with bond-implied PD for each issuer
- Highlight disagreements, especially Meta stock vs. Beignet bond prices

**Phase 5 findings (Oct 23 prices; built Oct 25).**

Charts:
- `charts/05_equity_vs_bond.png`
- `charts/05_meta_vs_beignet.png`

Inputs:
- New `issuers.csv` holds shares, debt, liabilities and cash from the latest 10-Qs, with sources. Phase 6 reuses it.
- Stock prices come from Yahoo's chart endpoint, cached in `data/equity/` by 01.
- Volatility is **realised**, not option-implied (Yahoo options need a login session).
- Merton runs on a 5-year horizon, with D = debt face value. Sensitivity is tested against total liabilities and 3-month volatility.

Results:

| Issuer | Stock-implied spread | Spread paid (~5y bond) |
|---|---|---|
| Apple | 0bp | 16bp |
| Alphabet | 0bp | 53bp |
| Meta | 0.4bp (≤12bp in all variants) | 80bp |
| SpaceX | 80bp (range 24–157bp) | 230bp |
| CoreWeave | 1,437bp (range 1,437–1,981bp) | 1,052bp |

- Big tech spreads are almost entirely not about default.
- **Beignet's 24% implied odds are about 240× what Meta's stock implies for Meta**, so the market isn't pricing Meta's credit in Beignet.
- **The stock market is more pessimistic about CoreWeave than its bondholders are**, and the unsecured notes are junior, so they look underpaid.
- **Meta vs. Beignet:**
  - Since issue, both are down ~10%. Beignet's −9.5 pts splits into **−8.2 from rates** and −1.3 from credit/structure (revised Oct 26 after the accrued-interest fix). Its record lows were mostly the Treasury market.
  - From early September to mid-October, Meta rallied ~25% while Beignet hit record lows around 91. Then Meta fell 13% in the week of Oct 15–23.

Open items:
- Option-implied volatility → moved to phase 6.
- [ ] Fuller Beignet TRACE trade history; the chart has only 5 points.
- [x] SpaceX volatility rests on 92 trading days since its Jun 12 IPO. Resolved in 06: option IV is 55% (vs. 83% realised), and the stock-implied spread falls to ~1bp.

### `06_fundamentals.ipynb` (built Oct 26)

Charts:
- `charts/06_iv_term_structure.png`
- `charts/06_spacex_runway.png`
- `charts/06_risk_scatter.png`

Data:
- `data/options/{T}_2026-10-23.csv` (Market Data, free plan).
- `data/edgar/companyfacts_*.json` (SEC XBRL).
- `data/spcx_fy2025_s1.csv`.
- `data/spcx_funding.csv`.
- Output `data/fundamentals.csv`. Handoffs now also include `data/merton_inputs.csv` (05) and `data/forward_pd.csv` (03). `merton()` moved to `common.py`.

**Findings (Oct 23 close):**
- **The pause test (revised Oct 26): stop growing, keep replacing what wears out.**
  - Method: upkeep capex = fleet cost ÷ stated useful life (`data/fleet.csv`, from the 10-K/10-Q/424B4), or D&A if higher. Cash = latest quarter's operating cash flow × 4, matching today's fleet. Years = debt ÷ (run-rate OCF − upkeep).
  - Results:
    - Apple 0.7 yrs, Alphabet 0.8, Meta 0.8. Fleet replacement is 15–25% above D&A for Alphabet and Meta.
    - SpaceX 1.6 at run-rate, 27 on TTM.
    - **CoreWeave fails**: run-rate OCF of ~$2.7B vs. ~$6.3B to replace its GPUs. It has $15B due by end-2028 vs. $5.5B cash, and $103.7B of contract backlog (41% within 2 years).
- **SpaceX by segment (`data/spcx_segments.csv`, `charts/06_spacex_segments.png`), Q3 annualised:**
  - **AI:** EBITDA ~$20B vs. capex ~$66B (84% of the total; ~$10B upkeep, ~$56B growth).
  - **Connectivity (Starlink):** ~$14B EBITDA vs. ~$6B capex. ~$4B of that replaces satellites (5-year broadband life, 3-year mobile; the constellation de-orbits without them).
  - **Space:** ~$1B EBITDA vs. ~$6B capex (Starship).
  - **The GPUs are the whole cash burn.** Runway scenario "stop new GPUs, keep launching": never runs out (+~$4B/qtr).
  - The AI segment only covered its own upkeep from Q3 (TTM −$3B), so the self-funding claim rests on Q3's AI revenue ($7.6B/qtr) holding.
- **IV vs. realised:**
  - Apple 29/24, Alphabet 37/31, Meta 43/43, SpaceX 55/83, CoreWeave 86/95.
  - Merton on IV: **CoreWeave's stock-implied 5y spread is 1,054bp vs. its bond's 1,052bp.** The 05 gap was a realised-vol artifact.
  - SpaceX's stock-implied spread is ~1bp, so its 230bp is not equity-wipeout risk.
- **Option-implied tail by Jan 2029:**
  - CoreWeave: P(≥75% fall) 32%, P(≥90%) 22%, vs. ~30% bond-implied.
  - SpaceX: 10% and 3%, vs. ~7.5% bond-implied.
- **Timing** (annual rate of a ≥50% fall, year 1 vs. years 1–2.2, shape relative to Apple):
  - SpaceX: flat, 14%/14% (0.64×), matching the flat bond curve.
  - CoreWeave: front-loaded (0.33×); bonds don't show it (1.11×).
  - Meta: same as Apple (0.93×), while its bond curve is back-loaded (1.53×), probably a long-bond premium.
- **SpaceX runway** (liquidity ~$95B at Sep 30):
  - Consensus FCF (−61/−110/−66): needs new money by **Dec 2027**, even with the $40B Apollo lease; a ~$90B gap by end-2028.
  - Q3 run-rate: mid-2029.
  - Stop new GPUs (keep launching satellites, building Starship): never.
  - **Its risk is financing risk from ~2027**, consistent with both flat curves.

Open (06):
- [x] Consensus (Oct 26), now named:
  - Revenue (TIKR via Yahoo): 2026 $45.9B, 2027 $132B, 2028 $249B. LSEG had ~$110B for 2027 pre-earnings.
  - Capex (S&P Global MI preview, Oct 19): $69.9B for 2026, $194.3B for FY2028. Debt $350B by FY2029.
  - The FCF consensus (−61/−110/−66) is still unattributed, and all of these predate the Oct 20 guidance.
  - **Company guidance (Q3 call, Oct 20):** Q4 capex $35–40B; 2.5–3 GW by end-2026; ~13 GW by end-2027 ("surprised if less"); Q1 2027 revenue $33–37B; $100B ARR by year-end; pricing "slightly above" $30–50/W; ~50/50 internal/external; prefers spot pricing.
  - Built into 06 §4b (`data/spcx_ai_inputs.csv`, `charts/06_spacex_ai_model.png`):
    - **Revenue per GW per year:** Q3 actual $19.5B; guidance-implied ~$26B; consensus-implied ~$12.5B (half of management's); CoreWeave's contracted rate ~$8B.
    - **Cost:** at $40B/GW, 2027 capex is ~$425B.
    - **Outside money needed by end-2028:** ~$190B (management pricing) / ~$390B (consensus pricing) / ~$455B (CoreWeave pricing); ~$105–630B across $35–50B/GW.
    - **If the build stops at 20 GW,** FCF is +$100–320B a year from 2029.
- [ ] Apollo lease: fixed rate and tranche schedule. Not public as of Oct 26; set at pricing before the expected year-end close. Earlier FT reporting described $10B of loans + $30B of IG debt; the 8-K's finance-lease structure takes precedence. Watch for an 8-K.
- [ ] CoreWeave Q3 10-Q: **not filed as of Oct 26**; expected ~Nov 10. When it lands, refresh TTM, cash, the maturity table, the pause test, and `fleet.csv`.
  - Interim, primary (Q2 8-K, Aug 11): 1.5 GW active, ~3.7 GW contracted, $104B backlog + >$25B signed in early Q3.
  - Interim, call guidance via press: Q3 revenue $3.45–3.6B, capex $11.5–13.5B; FY revenue $12.4–13.2B, capex $35–39B; >1.85 GW by year-end.
- [ ] IV history: only if a SpaceX IV-vs-spread time series earns a chart. Market Data Starter is $30 for one month.
- [x] SpaceX AI revenue durability. Short-dated: backlog $63.0B at Sep 30 (10-Q), 67% within one year, 27% in 1–3 years; $17.5B deferred (prepaid). Customer B (AI segment) was 34.5% of Q3 consolidated revenue. Musk prefers 'effectively the spot market rate'. AI revenue tracks spot GPU prices (H100: −~20%/yr once mature).
- [ ] Replacement cost vs. historical cost: V3 satellites and newer GPUs are cheaper per unit of capacity, so fleet ÷ life errs high. Contested GPU lives (5–6 years) err the other way.

### `07_meta_spvs.ipynb` (added Oct 26): Beignet and Sopaipilla structure

Charts:
- `charts/07_spv_premium.png`: structure premium over Meta's own curve, Oct 2025 vs. now.
- `charts/07_meta_exposure.png`: what Meta reports vs. what it's on the hook for.
- `charts/07_spv_vs_meta_scenarios.png`: Beignet's loss if Meta walks vs. extra coupon earned over Meta's bonds.

Data:
- `data/meta_spv_exposure.csv`: 10-Q Note 5.
- `data/meta_spv_facts.csv`: structure facts with sources.
- `data/meta_curve_2025-10-30.csv`: Meta's Oct 2025 term sheet.

**Structure (10-Q primary unless noted):**
- Each venture is 80% owned by its partner (Blue Owl in Louisiana, BlackRock GIP/HPS in Texas) and 20% by Meta.
- Development cost is ~$27B (Louisiana) and ~$14B (Texas).
- Leases start in 2029 (Louisiana) and 2028 (Texas), with 4-year initial terms renewable up to 20 years.
- Meta provides residual value guarantees *to the Ventures*: ~$28.1B (Louisiana) and ~$13.4B (Texas), declining, covering the first 16 years, and conditional on undisclosed "other conditions."
- The last 4 years are covered by a termination fee instead (IFR).
- Meta isn't the primary beneficiary because the partner controls "remarketing," so the ventures aren't consolidated.
- Meta's disclosed max exposure is $68.4B.
- Meta took ~$3B and $1.04B of cash out at formation.
- S&P rates both A+ (Meta −1 notch, "absence of a direct asset pledge"). Fitch rates Sopaipilla AA-.
- Sopaipilla's property insurance is ~$450M against a ~$14B campus, and Meta can terminate after a delay of more than 18 months (BigGo citing S&P; single secondary source).

**Findings (Oct 23 TRACE):**
- **Amortizing, not bullet.** Weighted average life is ~14.7y (Beignet) and ~14.5y (Sopaipilla), modelled as interest-only to lease start, then level payments. True spreads at average life are **267bp / 261bp**. Beignet at issue models to 232bp, vs. the press's "T+225."
- **The structure premium over Meta's own curve at the same life is ~130–150bp and hasn't grown.**
  - Beignet: +149bp at issue → +136bp now.
  - Sopaipilla: +131bp now.
  - Meta's own ~15y spread widened 83 → 131bp, more than Beignet did. **Beignet's slide is Meta-wide widening plus rates, not the structure.**
- **The RVG is sized to the bonds** (1.03× / 1.07×). Estimated rent covers modelled debt service 1.26–1.29×. S&P cites 1.12× for Beignet.
- **The premium can't plausibly be all default risk.** At R = 60% it would imply ~40% odds over the bonds' life that Meta walks *and* the guarantee fails. It's mostly illiquidity (144A, PIMCO ~$18B of $27.3B), index exclusion, complexity, and the casualty gap.
- **For Meta:** ~$0.5B a year of extra coupon buys ~$40B off balance sheet (~48% of its $84B of reported debt), a walk-away option every 4 years, and ~$4B of upfront cash. Twenty years of rent, if renewed, is ~$92B, more than Meta's reported debt.
- **Where the SPV loses but Meta is fine (§6, per $100 vs. a same-life Meta bond).**
  - Meta walks at renewal 1 (2033) and the RVG doesn't reach bondholders: −32 (campus at 50% of cost) / −57 (25%).
  - Catastrophe before the lease with Meta terminating free: ~−85.
  - RVG works but shrinks linearly (hypothetical): −4 to −16.
  - The extra coupon (~20 points over the bonds' life) only covers walks in the 2040s. **The SPV holder is short Meta's option to walk.**
- **Where the SPV beats Meta.**
  - If Meta defaults, SPV recovery is 100% if Meta keeps the campus, 56–77% if it rejects the lease (42–77% if the claim is capped at 3 years of rent), vs. 40% on Meta's own bonds.
  - Meta can't dilute the SPV, and new SPVs subordinate Meta's own bonds.
  - Principal returns before Meta's back-loaded risk.

**Open (07):**
- [ ] Who receives the RVG: the JV (10-Q, Les Barclays reading of S&P) vs. "sized so the bonds are repaid" (IFR). Needs the offering memorandum or S&P's report (RatingsDirect; the S&P annual review of Beignet Investor LLC is dated Oct 22, 2026).
- [ ] Actual amortization schedules (offering memoranda, S&P/Fitch). Sopaipilla coupon frequency is assumed semiannual.
- [ ] Do the notes have registration rights? This determines index eligibility.
- [ ] Confirm Sopaipilla's insurance limits and the 18-month termination right from a primary source (Fitch rating action commentary or S&P presale). Does Beignet have the same clause?
- [ ] Bankruptcy remoteness: true-sale / non-consolidation opinions, and whether the RVG claim is capped like a lease claim (§502(b)(6)).
- [ ] The RVG decline schedule and its "other conditions."

---

### `08_neoclouds.ipynb` (added Oct 31): what CoreWeave's survival depends on, with Nebius as a contrast

Reframes "what does success rely on?" for the post. Data: `data/neocloud_inputs.csv` and `data/neocloud_customers.csv` (CoreWeave Q2 10-Q/8-K, DDTL deck, Nebius Q2 6-K cached in `data/edgar/nbis_6k_2026-08-12_*`). Charts: `08_customers.png`, `08_rent_vs_contracts.png`, `08_renewal_breakeven.png`, `08_funding_mix.png`.

**Findings (Q2 filings):**
- **Customers:** the named contracts are Meta ≤$35B (AA-), OpenAI ~$22B and Jane Street $6B (private). The other ~$40B is Microsoft, Anthropic and others, undisclosed. Every AI-model customer is also building its own capacity or buying non-Nvidia chips (Meta campuses/MTIA; OpenAI Stargate and Broadcom chips; Anthropic TPUs/Trainium; Microsoft Maia and other neoclouds).
- **Rent outlasts the customers:**
  - $29.1B of leases are running (12 years left on average), and $35.5B more are signed but not started (7–16 year terms).
  - Contracts average ~5 years, and 80% of the backlog is used up by mid-2030.
  - From 2031 on: ~$45B of rent against ~$21B of contracted revenue.
- **Renewal break-even (one batch of equipment):**
  - On company-average economics (18¢ of cash a year per $1 of equipment, 68% debt-funded, 9.5% interest), a 5-year contract leaves lenders ~1% short. They're whole if old GPUs earn ≥46% of their old revenue afterwards, i.e. prices fall ≤14% a year. H100s fell ~19% a year.
  - Shareholders need ~94% (7-year life) or ~75% (8-year).
  - The Meta contract behind the DDTL (30¢ a year per $1) repays its loan with ~$57 per $100 to spare.
  - **CoreWeave fails on a GPU rental price, not a level of AI spend.**
- **Paid-off GPUs (§3b, `08_paid_off_gpu.png`):**
  - Depreciation doesn't matter to bondholders; cash running costs do. CoreWeave's 41% is 20% fixed rent (Q2 lease cost) plus 21% other.
  - The same old H100 nets ~$7 (all non-rent costs) to ~$69 (power only) per $100 of first-year revenue over years 6–10. SpaceX, which owns its halls, keeps that. CoreWeave pays ~$100 of rent on the space over those years, so it nets ~−$94.
  - 06's upkeep figure for SpaceX is therefore a ceiling (noted in 06 §2).
- **Nebius:**
  - Lenders funded 34% (CoreWeave: 71%); debt ÷ revenue is about the same (~3.5×).
  - Cash $8.0B vs. debt $8.5B; convertible notes at 1.25–2.625%; top 3 customers 59%; RPO $37.5B.
  - No straight bonds, so no spread ladder; included as a funding contrast only.

Open (08):
- [ ] ATM sales (35M-share program, Sep 17 2026) and Sep 30 cash incl. the $4.2B 2033 convertible: from the Q3 10-Q; refresh 08 §5.
- [ ] Read Nvidia's $6.3B capacity order from the Sep 2025 8-K (press-only in 08 §5).
- [ ] Refresh with CoreWeave's Q3 10-Q (~Nov 10) and Nebius's Q3 6-K.
- [x] GPU rental price history beyond H100 (Blackwell spot and contract). Done in 10 §1: A100/H100/H200/B200 executed (Ornn) and list (GetDeploying) prices, Nov 2026. Contract prices from a primary source still open (10).
- [ ] Microsoft's remaining commitment to CoreWeave (undisclosed).
- [ ] SpaceX's non-rent running costs and power price (Colossus on-site gas); GPU failure rates by age. Both are assumed in §3b.

### `10_gpu_unit_economics.ipynb` (added Nov 9): per-GPU economics, from a reader's question

A reader asked for the bottom-up view: rent, resale, payback per GPU, and operating margin vs. cost of debt. Data: `data/gpu_units.csv` (hand-entered prices with sources), `data/gpu_rent_history.csv`, cached Ornn and GetDeploying pulls in `data/gpu_prices/`, SEC XBRL for CoreWeave, Equinix and Digital Realty. Charts: `10_rent_history.png`, `10_new_vs_used.png`, `10_payback.png`, `10_margins.png`, `10_second_life.png`, `10_contracts.png`, `10_chip_lives.png`, `10_q3_leverage.png`, `10_escape.png`.

**Findings (Nov 9 2026):**
- **H100 rent fell ~80% from the 2023 peak to early 2026, then rose** (~$2.50 spot, ~$3.10 executed now). From Jan 2024 it is roughly flat, not −19% a year. **Revises 08 §3** (noted there).
- Used H100 ~75% of a new card; a used card is ~60% of an H100 system's all-in cost.
- One GPU at today's prices pays back in ~0.8–1.8 years at 90% utilization; CoreWeave as a whole ~5.5 years, because its contracts work out to ~$1.35–2.10 per GPU-hour.
- CoreWeave: −2% operating margin, interest 25% of revenue, ~9.5% borrowing cost. Per $1 of equipment: 18¢ cash, 17¢ wear-out, 1.5¢ left vs. 6.4¢ interest. Equinix 23% / Digital Realty 16% margins on ~3% debt; at Equinix's margin, CoreWeave's equipment earns ~7%.
- **Second life (§5):** a ~6½-year-old A100 still earns ~30¢/yr per $1 it cost, the same as CoreWeave's new equipment under contract (31¢). If CoreWeave's chips do likewise after their contracts end, its equipment returns ~9.4%/yr over 8 years (90% utilized; ~5% at 60% or at the 2026 low) vs. 9.5% debt, and lenders are repaid by ~year 6 (2030–32, when the unsecured notes mature). Burnout at contract end: −3%/yr, and lenders are never repaid. An 8-year accounting life alone would turn Q2's −2% margin into ~+12%.
- **Contract prices (§6):**
  - ~$64B of ~$89B of contracts with known amounts were signed Mar 2025–Apr 2026, near the price bottom. Meta's $21B was signed in Mar 2026, when a 36-month B200 reservation was ~$2.79/hr; it's ~$7.16 now.
  - CoreWeave earns ~$9M per MW of power a year; new Q3 3–6-month contracts ~$40M per MW. Pricing is cost-plus, with no disclosed discounts. CoreWeave traded the upside for take-or-pay financing.
  - Meta's contracts are fixed to 2031–32. Old chips re-contract well: H100s at ~95% of their original price, and an A100 contract runs to 2029.
  - Shareholders: ~15%/yr over a 10-year life at A100-like second-life rents, against −48% with burnout.
  - 08 §3b revised.
- **Chip lives (§7, `10_chip_lives.png`, added Nov 10):**
  - CoreWeave's 1.5 GW at Jun 2026, estimated from active power by quarter and install dates: GB300 52%, GB200 22%, H100 16%, H200 8%, Ampere 2%.
  - Azure/Google retired K80/P40/P100/V100 at 7.0–9.5 years from launch (median 8.3). V100s are still listed by 17 providers at 9.4 years.
  - Retirement runs from launch, and CoreWeave installs late, so the fleet gets ~2.5 years after its ~5-year contracts at the median life (1.2–3.6 across the range).
  - Second life of the Jun 2026 fleet: ~$9B today (12% discount; ~$5B glut, ~$14B at a 10-year life) vs. a ~$30B market value (revised to ~$16B in §8). The cash per $1 is about what the contracts paid; the gain is that none of it goes to lenders.
- **After Q3 (§8, `10_q3_leverage.png`, added Nov 10):**
  - Q3: revenue per MW ~$9.2M, adjusted EBITDA margin 62%, GAAP operating margin +6%. Debt +$11B to $46.9B (83% of net equipment).
  - New 4–5-year contracts at $20–25M per MW cover loan payments ~3× (old book 1.2×), and lenders cap loans at 70–100% of cost. So higher prices mean faster repayment, not more debt per MW.
  - DDTL 5.5 ($2.6B) is the exception: 3-year contracts against 5-year debt.
  - Parent bonds due in single payments, ~$21B in 2030–33, roughly equal the base-case second-life cash of the Jun 2026 fleet in those years.
  - Management's 2027–28 renewal plan implies ~$5.15 per GPU-hour.
  - "Active power" is IT load (CFO).
- **Off the razor's edge (§9, `10_escape.png`, added Nov 10):** if CoreWeave signed nothing after Q3, the old contracts leave ~$10B for CoreWeave, Inc. over 2027–33 against ~$32B it owes (old book alone: −$18B by 2033). Q3's contracts (~$19B left) and the second life (~$27B) leave ~$29B by 2033 (~$16B at glut prices). "Parent" = CoreWeave, Inc.: subsidiaries borrow the DDTLs (guaranteed by CoreWeave, Inc. except DDTL 4.0); the unsecured notes and converts are CoreWeave, Inc.'s.

Open (10):
- [ ] Refresh with CoreWeave's Q3 10-Q.
- [ ] Longer executed-price history, and primary-source multi-year contract prices.
- [ ] GPU liquidation/auction prices as a check on dealer quotes.
- [x] Q3 release and call (Nov 10): revenue per MW, pricing/renewal disclosures (10 §8); "active power" is IT load. The 10-Q itself is still to come.
- [ ] Multi-year old-chip (A100/V100) rent history to test §5's second-life assumption.
- [ ] CoreWeave fleet by generation (undisclosed; §7 estimates it) and first post-contract renewals/retirements.
- [ ] DDTL 5.5 advance rate and re-lease criteria; actual 2027 renewal prices against the ~$5.15/GPU-hour implied by management's plan.
- [ ] Decide whether the post's CoreWeave section (outline: "loses ~19% of its rental value every year") should be reframed around 10 §1.

### Re-price to Nov 10, 2026 (all notebooks)
- Bonds: TRACE last trades for all 21 bonds read from each FINRA bond page (`quotes.csv`, `data/trade_quotes.csv`); FINRA's data API hung, as on Nov 6. Options: Market Data Nov 9 close (01 snapshot + 09 Jan 2029 chains). Stocks: Yahoo to Nov 10. FRED to Nov 9; SOFR cached (`data/fred/SOFR.csv`).
- Fixed: 06 now saves `data/merton_iv.csv` and `data/crash_odds.csv` (they had been stale since Nov 1); 06/08/09/research as-of dates are no longer hard-coded; 09 accepts bond quotes up to 3 days after the option date.
- Every notebook's text, `research.ipynb`'s checks, `post_outline.md` and `post.md` updated to the new numbers. Biggest moves: CoreWeave stock-implied spread ~1,136bp vs. bond ~1,041bp (was 1,054 vs. 1,052); options odds of a ≥75% CoreWeave fall 37% (was 32%); Meta SPV premium ~110–125bp, narrowed from ~149bp at issue (was "~130–150, hasn't grown"); SpaceX 2036 +108bp since issue; all 09 trades re-priced (CoreWeave $49, SpaceX $142).
- [ ] Not re-done: 01 doesn't refresh SEC XBRL (its request header carries a personal email); company financials stay Q2 until the CoreWeave 10-Q.
- [ ] **Nov 11:** CoreWeave stock up ~20% intraday after Q3 (to ~$60). Q3 10-Q not on EDGAR yet (checked 2 pm ET; last year's came Nov 13). Re-price 05/06/08/09/10 and the post once Nov 11 options (Market Data serves them Nov 12) and Nov 11 TRACE closes are out; the Nov 10 numbers mix with nothing until then.
- [x] **CoreWeave note ratings:** issue ratings are B (S&P) / B1 (Moody's), one notch below the B+/Ba3 issuer, last rated Oct 20 2026 per FINRA bond pages (read Nov 11). `bonds.csv` updated; 03's history marker moves B+ → B (5-yr history 12.9% → 14.7%, price implies ~4.0–4.2× instead of ~4.5–4.8×). 02's bucket was already B.

## 6. Expected charts for the post

1. Treasury curve + IG/HY spread history (context: where credit spreads are now)
2. Same issuer, different claim: CoreWeave secured vs. unsecured spreads
3. Meta stock vs. Beignet bond price (the divergence)
4. SpaceX tranches vs. same-rated peers (Intel) across the curve
5. Market-implied default probability by bond
6. CoreWeave GPU collateral LTV over time
7. Equity-implied vs. bond-implied default risk
8. "Do yields reflect risk?" summary scatter

---

## 7. Open questions / to verify

- [x] Current TRACE prices for all bonds (Oct 25). Every bond has an Oct 23 TRACE last trade: CoreWeave, SpaceX 2031, and Sopaipilla from FINRA Bond Center (144A lines); the rest from TradingView's FINRA feed. FINRA symbols are in `bonds.csv` → `finra_symbol`. Last trades are single prints, so levels are approximate. **Refresh routine:** open each FINRA bond page, record last trade price/yield/date in `quotes.csv`. Daily closes by date are in FINRA's `EndOfDayPriceYield` dataset (used for 09's Oct 30 prices).
- [x] Missing CUSIPs (144A). SpaceX `84615QAA1/AC7/AE3/AG8/AJ2` (2031/33/36/46/56). Beignet `076912AA2` (Reg S `USU06930AA60`; matures May 30 2049; **quarterly** coupon). Sopaipilla `83577VAA8` (7.534%, Nov 30 2048, $12.547B). CoreWeave 144A CUSIPs (from FINRA): `21873SAB4` (9.25% 2030), `21873SAC2` (9.00% 2031), `21873SAG3` (9.75% 2031), `21873SAK4` (9.625% 2032). FINRA also lists 3 converts: 1.75% Dec-2031, **1.75% Oct-2032** (the $4B 2032 convert), and 2.875% Apr-2033. CoreWeave 9.625% matures **Jul 15 2032** (was Jul 1).
- [x] CoreWeave DDTL terms. From the [DDTL 4.0 deck](https://s205.q4cdn.com/133937190/files/doc_presentations/2026/Mar/2026-03-DDTL-4-Overview.pdf): monthly amortization after stabilization, fully repaid by Mar 2032; sized at 90% loan-to-cost during install, then 1.2x DSCR (up to ~102% LTC); 1.15x minimum DSCR from mid-2027; first lien on GPUs, the customer contract, and DC leases. *Still open:* what happens if the customer terminates (needs the credit agreement exhibit to the Mar 2026 8-K).
- [x] CoreWeave total debt. **$35.55B principal at 2026-06-30** ($31.8B recourse + $3.7B non-recourse), from the [Q2 10-Q](https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm) debt note. The ~$17B–$50B range is timing plus whether leases are included. A $4.2B 2033 convert (Sep 2026) is after this date and unverified.
- [x] Beignet RVG mechanics. Per Meta's [Q3 10-Q](https://www.sec.gov/Archives/edgar/data/1326801/000162828026066773/meta-20260930.htm): the RVG goes to the JV, not the bondholders. It pays only the shortfall between fair value and a threshold that **declines over time**, and only if Meta terminates or doesn't renew *and* "certain other conditions are met." Covers the first 16 years. Hyperion threshold ~$28.1B at Dec 2025, against $27.3B of Beignet notes. Combined max RVG for both ventures is $41.5B at Sep 30 2026. Meta books $0 liability ("not probable"). *Still open:* the "other conditions," and the threshold's decline schedule.
- [x] SpaceX indenture ([Ex. 4.1](https://www.sec.gov/Archives/edgar/data/1181412/000162828026045763/exhibit41-closing8xkjune20.htm)). **No subsidiary guarantors. No change-of-control put.** Covenants are limited to liens (with carve-outs, including purchase-money liens for financing new property, which is exactly how GPU debt would be secured) and a merger covenant. Make-whole call; par call 1–6 months before maturity. All tranches mature Jul 15.
- [x] Sopaipilla priced. Late Jul 2026, ~$12.55B (one source says $12.3B), **7.534% yield, ~T+287.5bp**, S&P A+ (one source also cites Fitch AA-), 2048 maturity. Coupon and CUSIP not yet found.
- [x] Alphabet 2026 debt. **Yes, a lot.** $20B USD (Feb, 7 tranches 2029–2066, T+27 to T+95), £5.5B incl. a 100-year bond, C$8.5B (May), plus euros: $51.8B issued in H1 per the Q2 10-Q, with LT debt at $98.2B. A reported $25B USD deal in Aug 2026 is unverified.
- [x] Anthropic / Broadcom. **It's TPUs, not GPUs.** An Apollo/Blackstone SPV buys Google TPUs and leases them to Anthropic. Broadcom backstops the senior tranches (reported 80%+ of the first $35B). Senior priced ~5.75% (IG); a $4.5B subordinated tranche priced 8.5%. Later reports of $42B / $60B packages are easy to conflate. Enough for a sidebar, not a full section.

### New open questions (first pass)
- [ ] CoreWeave unsecured note recovery: ~$25B of secured or subsidiary debt sits ahead of ~$10B of unsecured notes, so a 40% recovery assumption is probably generous.
- [ ] CoreWeave issuer ratings (B+ S&P / Ba3 Moody's) come from press only. Confirm with the agencies.
- [ ] Morningstar cites "secured 7.125% 2030 notes" yielding ~7.17%. These aren't in CoreWeave's 10-Q debt table. Identify the issuer (a data-center SPV?).
- [ ] Beignet yield conflict: ~6.95% (FT via NAI500, undated) vs. 7.55% at 91¢ (Reuters, Sep 28).
- [x] Meta 5.55% 2064 at 7.48% (Benzinga). It looked too wide, but TRACE shows Meta's 2056 at 7.31% (~200bp), so it's consistent.
- [x] SpaceX's proposed ~$40B Apollo-led GPU-backed debt. **8-K Oct 26:** a binding commitment for a ~$40B **master finance lease**. An Apollo-managed lessor owns the GPU pods; rent is 1/20 of cost per quarter plus a fixed rate; schedules start H1 2027 and run ~5–5.25 years. The lessor owns the GPUs, so it ranks ahead of the notes on them, with no lien test needed. Payments straddle the $7B Jul 2031 maturity.
- [ ] SpaceX "Other financings" (failed sale-leasebacks on AI infrastructure) grew from $4.6B to $13.0B in 9 months. What are they?
- [ ] Intel benchmark bond (same rating and maturity as the SpaceX 10yr) not yet added to `bonds.csv`.
- [ ] SPV recovery (60% in `bonds.csv`) drives Beignet/Sopaipilla's implied odds; 40% makes them look like Meta corporate. Need the RVG "other conditions" and threshold schedule, or an S&P presale recovery rating, to pin it down.
- [x] Term structure of PD, first pass (03 §6, `charts/03_default_timing.png`). Forward default rates are bootstrapped from each issuer's bonds, net of Apple's spread at the same maturity. Bonds less than 2 years apart are skipped.
  - **Meta is back-loaded:** 1.0% → 1.6% → 2.9% → 3.6% per year.
  - **Alphabet:** 0.6% → 1.2%, then flat.
  - **SpaceX is flat** at 3.5–4.1% from day one, then 3.3% for 2046–56.
  - **CoreWeave:** 15% → 16.5%, with no view past 2032.
  - *Still open:* SpaceX's flat curve could be (a) default risk concentrated in years 3–5, before the Jul 2031 maturity, or (b) near-term non-default premia (downgrade risk, priming by secured GPU debt, 144A illiquidity). Separating them needs a shorter SpaceX instrument (bridge loan, CP, CDS) or a burn-rate model (06).
  - The SPVs have only one maturity each, so they can't be bootstrapped.

---

## 8. Sources found so far

- SpaceX notes offering: https://qz.com/spacex-bond-sale-senior-notes-ipo-ai-062226
- SpaceX bridge loan / Oppenheimer projection: https://mbiz.heraldcorp.com/article/10784436
- SpaceX pricing vs. Intel: https://en.fnnews.com/news/202606241815035124
- CoreWeave $8.5B GPU loan: https://news.bloomberglaw.com/capital-markets/coreweave-raises-8-5-billion-gpu-loan-backed-by-meta-deal
- CoreWeave unsecured notes trading levels: https://cryptobriefing.com/coreweave-debt-stress-private-credit-ai/
- Hyperion / Beignet structure: https://marcellus.in/story/short-read-three-ai-megadeals-are-breaking-new-ground-on-wall-street/
- Hyperion lease renewal mechanics: https://www.kvpr.org/2025-12-05/meta-is-building-a-massive-data-center-why-its-fueling-fears-of-an-ai-bubble
- Beignet record low: https://protos.com/metas-ai-bond-just-hit-a-record-low-as-its-stock-soared/
- El Paso / Sopaipilla pricing, Anthropic GPU financing: https://finance.technews.tw/2026/07/24/meta-faces-higher-borrowing-costs-in-latest-12bn-data-centre-financing/
- Alphabet equity raise: https://datacenterdynamics.com/en/news/googles-parent-company-alphabet-seeks-80-billion-for-ai-build-out/
- S&P 2024 Annual Global Corporate Default and Rating Transition Study (Mar 27 2025), cumulative default rates by notch: https://www.spglobal.com/ratings/en/research/articles/250327-default-transition-and-recovery-2024-annual-global-corporate-default-and-rating-transition-study-13452126 (PDF via S&P Maalot: https://maalot.co.il/Publications/FTS20250331162126.pdf)
- Previous post (tone, GPU rental curve): https://goodatinvesting.com/website/spacex-ipo/