"""Monte Carlo of Anthropic's revenue, cash flows and value per share: 06's forecast and 08's valuation in one module.

Same model and same default numbers as 06_forecast.ipynb (revenue curves, costs) and 08_valuation.ipynb (extension
to 2040, discounting, per share), which explain the reasoning. 09_playground.ipynb checks that run() reproduces both,
and is the place to change inputs:

    import montecarlo as mc
    res = mc.run(beta=1.5, rev_per_compute=(1.8, 3.0))
    mc.summary(res)

All money is in $ millions, per-share values in dollars, rates as decimals.
"""
import numpy as np
import pandas as pd

from common import load, wide

_K = load('kpis').drop_duplicates('metric').set_index('metric').value
_X = load('valuation_inputs').set_index('item').value            # outside data, written by 08

# Every input, in plain English. Where each number comes from:
#   [S-1]        a fact in Anthropic's filing: audited financials, or a figure the company states
#   [Anthropic]  the company's own estimate or framing in the S-1: unaudited, and written to sell the stock
#   [Ours]       our assumption, where the S-1 is silent. We give a range and say why
#   [Market]     outside market data (Treasury yields, Damodaran), stored in data/valuation_inputs.csv
# A pair (low, high) is a range: each of the 20,000 simulated worlds draws its own value from it.
# Shares are decimals (0.25 = 25%); money is $ millions.
# Groups 1-4 all move value per share (09 §2 shows each one's swing); group 5 is off by default (10 §4); group 6 is plumbing.
PARAMS = dict(
    # --- 1. How big can Anthropic get? ----------------------------------------------------------------------------
    # Revenue ceiling (today's $) = $40T of knowledge-work wages x AI's share of them x Anthropic's share of AI.
    # [Anthropic] "the work that knowledge workers perform represented more than $40 trillion in economic value
    #   globally in 2025", the company's own estimate from government wage data. It calls this the opportunity
    #   but never says how much of it AI will capture, or Anthropic's share. Those two numbers are ours.
    ai_share_of_wages=(0.015, 0.08),     # [Ours] Share of those wages that ends up as spending on AI: $0.6-3.2T a year,
                                         #   or about $50-270 a month for each of the >1B knowledge workers the S-1
                                         #   expects by 2028. Yardstick [S-1]: cloud computing took 20 years to reach
                                         #   $1.9T, ~5% of $40T. Each doubling (2% -> 4% -> 8%) is equally likely.
    anthropic_share_of_ai=(0.30, 0.55),  # [Ours] Anthropic's slice of that AI spend: it stays the leading vendor, from
                                         #   first among several labs and cloud giants to about half the market. The S-1
                                         #   gives no market share. (15-35% gave a ~$37 median; 35-60%, ~$65.)
    # Together: a ceiling of ~$180B-$1.8T a year, ~$590B in the middle (9x today's ~$64B run-rate). Two checks:
    #   Anthropic's own compute contracts are sized for ~$236-304B (Q3 vs Q2 efficiency; 09 §6 values them at
    #   ~$18-45 a share), below ~88-97% of worlds; the $83 IPO price needs ~$730B at 2x efficiency (09 §4).
    ceiling=None,                        # Shortcut: set the ceiling range yourself, e.g. (400e3, 900e3) = $400-900B a
                                         #   year. Replaces the two lines above.
    ceiling_growth=_K['it_spend_cagr_2006_2025'] / 100,  # [S-1] The ceiling itself rises ~7% a year, as IT spending
                                         #   did from 2006 to 2025.

    # --- 2. What does it cost to serve that revenue? -------------------------------------------------------------
    rev_per_compute=(1.5, 2.5),          # Revenue earned per $1 spent on compute (chips, cloud, data centers).
                                         #   [S-1] $1.72 in Q3-2026, $2.08 in Q2-2026. [Ours] 1.5-2.5: cheaper chips
                                         #   vs price cuts. Compute can't fall below the take-or-pay contracts [S-1].
    cash_opex_pct=0.25,                  # [Ours] Everything else paid in cash (sales, partner fees, salaries, offices),
                                         #   as a share of revenue, to 2030. [S-1] Q3-2026 was ~28% (03).
    opex_end=0.25,                       # [Ours] Where that share ends up by last_year, falling in a straight line from
                                         #   2031. 0.25 = no savings from scale; big software companies get lower (08 §5).

    # --- 3. What is a dollar of future cash worth today? ---------------------------------------------------------
    # Discount rate = risk-free rate + beta x equity risk premium (~10.5%; 08 §1).
    risk_free=_X['risk_free_rate'] / 100,              # [Market] What a US Treasury bond pays.
    erp=_X['equity_risk_premium'] / 100,               # [Market] Extra yearly return stocks are priced to earn over
                                                       #   Treasuries (Damodaran).
    beta=_X['beta_software_system_app'],               # [Market] How much riskier than the average stock: listed
                                                       #   software's 1.25. Anthropic has no trading history yet.
    discount_rate=None,                  # Shortcut: set the rate directly, e.g. 0.09. Replaces the three lines above.
    terminal_growth=0.03,                # [Ours] Growth every year after last_year, forever. Kept below the risk-free
                                         #   rate: no company outgrows the economy for ever.
    last_year=2040,                      # [Ours] Last year forecast year by year; a perpetuity covers the rest (08 §2).

    # --- 4. Other costs. Margins end up thin (~10%), so each 1% of revenue they take, every year, is ~$5 a share
    sbc_new_grants_pct=0.04,             # [Ours] Stock pay for future grants, as a share of revenue, counted as a cost.
                                         #   [S-1] Q3-2026 was 6.3% including grants already made (those are in the
                                         #   16.4B share count, so not charged again).
    donations_pct=0.03,                  # [Ours] Charitable donations and donation matching, share of revenue. [S-1]
                                         #   9M-2026 was 6%, lumpy, and the company says it will grow.
    capex_pct=0.04,                      # [Ours] Equipment Anthropic buys and owns, share of revenue. Most of its compute
                                         #   is rented and already in group 2. [S-1] 9M-2026 was 8.7%, partly prepaid rent.
    tax_rate=0.21,                       # [Ours] The US federal rate, on profits only. Ignores past losses that would shelter
                                         #   tax (cautious).

    # --- 5. A breakthrough the forecast leaves out (off by default) ----------------------------------------------
    # Groups 1-4 value Anthropic as a company selling AI to knowledge workers. The bull case for the stock is bigger:
    # a breakthrough (AGI, a cancer cure, a room-temperature superconductor) worth far more than any wage bill.
    prize_chance=0.0,                    # [Ours] Chance it happens and Anthropic's shareholders get the payoff. Each world
                                         #   draws yes or no. 0 = off, as in 06/08. 10 §3 backs out what $83 implies.
    prize_value=10e6,                    # [Ours] The payoff to shareholders, in today's money ($M): $10T, the "AGI prize"
                                         #   of the SpaceX post. Added on top of the world's own value.

    # --- 6. Plumbing: little or no effect on value per share -----------------------------------------------------
    cash_yield=0.04,                     # [Ours] Interest earned on the cash pile. Only affects whether cash runs out.
    n_worlds=20_000,                     # How many worlds to draw.
    seed=6,                              # Fixes the random draws, so every run gives the same numbers.
    speed_noise=1.0,                     # How fast each world approaches its ceiling is fitted to the last six
                                         #   quarters of growth (06 §2), with some randomness: 1 = the fit's own uncertainty,
                                         #   0 = none. Barely moves value (09 §3).
)

# --- Facts from data/ (S-1 and 02-04), fixed across runs ---
_R = wide(load('real_earnings'), index='metric')
_HIST = ['Q1-2025', 'Q2-2025', 'Q3-2025', 'Q4-2025', 'Q1-2026', 'Q2-2026', 'Q3-2026']
_quarterly = _R.loc['revenue', _HIST].copy()
_quarterly[_HIST[4:]] = _R.loc['clean_revenue', _HIST[4:]]       # 2026: net of policy-violator revenue (02 §3)
_run_rate = _quarterly * 4
GROWTH = np.log(_run_rate).diff().dropna()                        # log q/q growth
START = _run_rate.shift(1).dropna()                               # run-rate each quarter's growth started from
RUN_NOW = _run_rate['Q3-2026']                                    # forecast starts here, ~$64B a year

_bs = wide(load('balance_sheet'))['2026-09-30']
CASH = _bs[['Cash and cash equivalents', 'Short-term investments']].sum()
_opt = load('stock_options').set_index('event').loc['Balance as of September 30, 2026']
STRIKE_PROCEEDS = _opt.shares_k * 1e3 * _opt.wavg_exercise_price_usd / 1e6
FD_SHARES = load('dilution').query("scenario == 'today'").shares_k.sum() * 1e3   # 04: ~16.4B fully diluted
_COMMIT = load('compute_schedule').set_index('year').sum(axis=1)                 # 03: take-or-pay compute by year
_BACKLOG = _K['rsu_unrecognized_sbc'] - _K['rsu_sbc_catchup_at_ipo'] + _K['option_unrecognized_sbc']
IPO = (_X['ipo_price_low'], _X['ipo_price_high'])      # the marketed range
IPO_PRICE = _X['ipo_price']                                # where it priced (prospectus, Nov 18)


def fit_speed(ceiling):
    """06 §2: least-squares Gompertz speed (and its standard error) for each ceiling ($M a year), through the origin."""
    ceiling = np.atleast_1d(np.asarray(ceiling, dtype=float))
    gap = np.log(ceiling[:, None] / START.values[None, :])
    speed = (gap * GROWTH.values).sum(axis=1) / (gap ** 2).sum(axis=1)
    resid = GROWTH.values - speed[:, None] * gap
    se = np.sqrt((resid ** 2).sum(axis=1) / (len(GROWTH) - 1) / (gap ** 2).sum(axis=1))
    return speed, se


def draw_worlds(p):
    """06 §5: one row per world with its ceiling, speed and revenue per compute dollar. Same draw order as 06."""
    rng = np.random.default_rng(p['seed'])
    n = p['n_worlds']
    w = pd.DataFrame({'ai_share_of_wages': np.exp(rng.uniform(*np.log(p['ai_share_of_wages']), n)),
                      'anthropic_share_of_ai': rng.uniform(*p['anthropic_share_of_ai'], n),
                      'rev_per_compute': rng.uniform(*p['rev_per_compute'], n)})
    w['ceiling'] = _K['knowledge_work_value'] * w.ai_share_of_wages * w.anthropic_share_of_ai
    if p['ceiling'] is not None:
        w['ceiling'] = np.exp(rng.uniform(*np.log(p['ceiling']), n))
    speed, se = fit_speed(w.ceiling.values)
    w['speed'] = rng.normal(speed, se * p['speed_noise']).clip(0.02, 0.9)
    w['prize_hit'] = rng.uniform(size=n) < p['prize_chance']      # drawn last, so the draws above match 06
    return w


def fixed_worlds(ceiling, rev_per_compute):
    """Worlds with chosen inputs (numbers or equal-length arrays) and no randomness: speed = the fitted speed."""
    c, rpc = np.broadcast_arrays(np.atleast_1d(ceiling).astype(float), np.atleast_1d(rev_per_compute).astype(float))
    return pd.DataFrame({'ceiling': c, 'rev_per_compute': rpc, 'speed': fit_speed(c)[0]})


def _periods(last_year):
    years = ['Q4-2026'] + [str(y) for y in range(2027, last_year + 1)]
    quarters = [f'Q{(i + 2) % 4 + 1}-{2026 + (i + 2) // 4}' for i in range(1, 4 * (last_year - 2030) + 18)]
    year_of = ['Q4-2026' if q == 'Q4-2026' else q[-4:] for q in quarters]
    return years, quarters, year_of


def simulate(worlds, p):
    """Revenue, costs, cash and value for each world (06 §6-7, 08 §2-3). Returns a dict of tables:
    'worlds' (inputs + headline outputs, one row per world) and per-year tables (worlds x periods)."""
    years, quarters, year_of = _periods(p['last_year'])
    assert (worlds.ceiling > RUN_NOW).all(), 'every ceiling must sit above today’s ~$64B run-rate'

    # Revenue: each quarter closes `speed` of the log gap to a ceiling that grows ceiling_growth a year (06 §1)
    rr, path = RUN_NOW, []
    for t in range(1, len(quarters) + 1):
        ceiling_now = worlds.ceiling.values * (1 + p['ceiling_growth']) ** (t / 4)
        rr = rr * np.exp(worlds.speed.values * np.log(ceiling_now / rr))
        path.append(rr)
    revenue = (pd.DataFrame(path, index=quarters) / 4).groupby(year_of).sum().T[years]
    revenue.index = worlds.index

    # Costs (06 §7; opex fades to opex_end after 2030, 08 §5)
    n_late = p['last_year'] - 2030
    opex = pd.Series([p['cash_opex_pct']] * (len(years) - n_late)
                     + list(np.linspace(p['cash_opex_pct'], p['opex_end'], n_late + 1)[1:]), index=years)
    commit = pd.Series([_COMMIT.get(2026 if y == 'Q4-2026' else int(y), 0.0) for y in years], index=years)
    sbc_existing = pd.Series(0.0, index=years)                    # grants already in the 16.4B count
    sbc_existing[['Q4-2026', '2027', '2028', '2029']] = [_K['rsu_sbc_catchup_at_ipo']] + [_BACKLOG / 3] * 3
    compute = revenue.div(worlds.rev_per_compute, axis=0).clip(lower=commit, axis=1)   # take-or-pay floor
    sbc = sbc_existing + p['sbc_new_grants_pct'] * revenue
    donations = p['donations_pct'] * revenue
    real_oi = revenue.mul(1 - opex, axis=1) - compute - sbc - donations
    owner_fcf = real_oi - p['tax_rate'] * real_oi.clip(lower=0) - p['capex_pct'] * revenue

    # Cash, rolled forward with interest (06 §7): FCF = owner FCF + stock comp + donations + interest
    cash, cash_end = pd.Series(CASH, index=worlds.index), {}
    for y in years:
        cash = cash + owner_fcf[y] + sbc[y] + donations[y] + cash * p['cash_yield'] * (0.25 if y == 'Q4-2026' else 1)
        cash_end[y] = cash
    cash_end = pd.DataFrame(cash_end)

    # Value (08 §2-3): owner FCF with existing grants added back, mid-period discounting, Gordon terminal value
    r = p['discount_rate'] if p['discount_rate'] is not None else p['risk_free'] + p['beta'] * p['erp']
    g = p['terminal_growth']
    cf = owner_fcf + sbc_existing
    t = pd.Series([0.125] + [int(y) + 0.5 - 2026.75 for y in years[1:]], index=years)
    pv = cf / (1 + r) ** t
    last = years[-1]
    v = pd.DataFrame({'pv_2026_2030': pv[years[:5]].sum(axis=1), 'pv_2031_last': pv[years[5:]].sum(axis=1),
                      'terminal': cf[last] * (1 + g) / (r - g) / (1 + r) ** t[last],
                      'cash_and_strikes': CASH + STRIKE_PROCEEDS,
                      # breakthrough: yes/no per drawn world; fixed worlds get its expected value
                      'prize': worlds.get('prize_hit', p['prize_chance']) * p['prize_value']})
    v['equity'] = v.sum(axis=1).clip(lower=0)                   # limited liability
    v['per_share'] = v.equity * 1e6 / FD_SHARES

    out = worlds.assign(revenue_2030=revenue['2030'], revenue_last=revenue[last],
                        owner_fcf_margin_last=owner_fcf[last] / revenue[last],
                        lowest_cash=cash_end.min(axis=1), **v)
    return dict(worlds=out, revenue=revenue, compute=compute, real_operating_income=real_oi,
                owner_fcf=owner_fcf, cash_end=cash_end, discount_rate=r, params=p)


def run(**overrides):
    """Draw worlds and simulate them. Any PARAMS key can be overridden, e.g. run(beta=1.5, opex_end=0.15)."""
    unknown = set(overrides) - set(PARAMS)
    assert not unknown, f'unknown inputs: {unknown}'
    ranges = {'ai_share_of_wages', 'anthropic_share_of_ai', 'rev_per_compute', 'ceiling'}   # drawn per world
    wrong = {k for k, v in overrides.items() if isinstance(v, (tuple, list)) != (k in ranges) and v is not None}
    assert not wrong, (f'{wrong}: only {sorted(ranges)} take a (low, high) range; every other input is one number, '
                       f'e.g. beta=1.6. To compare cases, run once per value.')
    p = {**PARAMS, **overrides}
    return simulate(draw_worlds(p), p)


def contract_worlds(p=None):
    """09 §6: the world Anthropic's own compute contracts are sized for, one per S-1 efficiency (Q3-2026 and Q2-2026
    revenue per compute $). Its ceiling is the one whose 2029 revenue = committed 2029 compute x that efficiency.
    No randomness. Returns {label: simulate() result for that one world}."""
    p = {**PARAMS, **(p or {})}
    q = wide(load('quarterly_income_statement'))
    rpc = (q.loc['Revenue'] / q.loc['Compute and infrastructure'])[['Q3-2026', 'Q2-2026']]
    grid = np.geomspace(RUN_NOW * 1.2, 3e6, 400)                     # candidate ceilings, $M a year
    out = {}
    for quarter, r in rpc.items():
        rev_2029 = simulate(fixed_worlds(grid, r), p)['revenue']['2029'].values
        k = np.interp(_COMMIT[2029] * r, rev_2029, grid)              # 2029 revenue rises with the ceiling
        out[f'Contracts at {r:.2f}x ({quarter})'] = simulate(fixed_worlds(k, r), p)
    return out


def public_benefit_multiple(per_share, price=IPO_PRICE):
    """Share-count multiple from the Public Benefit Fund's top-ups if the stock climbs from the IPO price to per_share:
    [S-1] up to 2% more shares each time the price rises 50% above the last milestone. Assumes the maximum every time.
    ponytail: one pass, so the top-ups don't feed back into the price that triggers them (slightly overstates steps)."""
    step, top_up = _K['public_benefit_price_step_pct'] / 100, _K['public_benefit_issuance_pct'] / 100
    steps = np.floor(np.log(np.maximum(per_share, price) / price) / np.log(1 + step))
    return (1 + top_up) ** steps


def summary(res, pcts=(0.10, 0.25, 0.50, 0.75, 0.90)):
    """Percentiles of the headline outputs ($B, $ per share, margins), plus the odds of clearing the IPO range and price."""
    w = res['worlds']
    cols = {'ceiling': 'ceiling today, $B', 'revenue_2030': 'revenue 2030, $B', 'revenue_last': 'revenue last year, $B',
            'owner_fcf_margin_last': 'owner FCF margin, last year', 'lowest_cash': 'lowest cash, $B',
            'equity': 'equity value, $B', 'per_share': 'value per share, $'}
    t = w[list(cols)].quantile(list(pcts)).rename(columns=cols, index=lambda q: f'P{q * 100:.0f}').T
    t.loc[[c for c in cols.values() if c.endswith('$B')]] /= 1000
    print(f"discount rate {res['discount_rate']:.2%}; mean value per share ${w.per_share.mean():.2f}; "
          f"worlds worth ≥ ${IPO_PRICE:.0f} (IPO price): {(w.per_share >= IPO_PRICE).mean():.0%}; "
          f"run out of cash: {(w.lowest_cash < 0).mean():.1%}")
    return t.round(2)
