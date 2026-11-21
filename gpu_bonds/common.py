"""Shared helpers for the notebooks: chart style, cached FRED/equity loaders, bond math."""
from math import erf, sqrt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- chart style (fresh for this post) ----
INK, INK2, MUTED, GRID, AXIS, SURFACE = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#fcfcfb'
BOND = '#2a78d6'                          # "the bond"
RAMP = ['#86b6ef', '#2a78d6', '#104281']  # ordinal blue: safer → riskier
EQUITY = '#d4762a'                        # "the stock" (only used where bond and stock appear together)

plt.rcParams.update({
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
    'font.family': ['Helvetica Neue', 'Arial', 'sans-serif'], 'font.size': 10,
    'text.color': INK, 'axes.labelcolor': INK2, 'xtick.color': MUTED, 'ytick.color': INK2,
    'axes.edgecolor': AXIS, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
    'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
    'legend.frameon': False, 'lines.linewidth': 1.4,
})


def source_note(fig, text, fontsize=7.5):
    """Source line under the chart, wrapped to the figure's width.

    A single long line makes savefig(bbox_inches='tight') widen the image to fit it,
    leaving blank space to the right of the plot. Wrapping keeps the note inside the
    figure's width; it sits just below the figure, and 'tight' grows the image downward.
    """
    import textwrap
    chars = int(fig.get_figwidth() * 72 / (fontsize * 0.52))   # ~average character width
    fig.text(0.01, 0, textwrap.fill(text, chars), fontsize=fontsize, color=MUTED, ha='left', va='top')


# ---- cached data (written by 01_data_pull) ----
TENORS = {'DGS1': 1, 'DGS2': 2, 'DGS3': 3, 'DGS5': 5, 'DGS7': 7, 'DGS10': 10, 'DGS20': 20, 'DGS30': 30}


def load(sid):
    return pd.read_csv(f'data/fred/{sid}.csv', index_col=0, parse_dates=True)[sid]


def load_equity(ticker):
    return pd.read_csv(f'data/equity/{ticker}.csv', index_col=0, parse_dates=True)


ust = pd.concat([load(s) for s in TENORS], axis=1, sort=True).ffill()


def treasury_yield(date, years):
    """Treasury yield (%) at `years` on `date`, linear between tenors, flat beyond 30y."""
    row = ust.loc[:date].iloc[-1]
    return float(np.interp(years, list(TENORS.values()), row.values))


# ---- bond math (semiannual bullet, clean price) ----
def bond_price(y_pct, coupon, years):
    """Clean price: PV of remaining cash flows minus accrued interest (quotes are clean)."""
    n = max(int(np.ceil(years * 2)), 1)
    t = years * 2 - np.arange(n)[::-1]          # half-years to each payment, last one = maturity
    y = y_pct / 100
    dirty = (coupon / 2 / (1 + y / 2) ** t).sum() + 100 / (1 + y / 2) ** t[-1]
    accrued = coupon / 2 * (1 - t[0])           # share of the current coupon period already elapsed
    return dirty - accrued


def ytm(price, coupon, years, lo=-50.0, hi=100.0):
    """Yield (%) that reprices the bond to clean `price`, by bisection (price falls as yield rises)."""
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if bond_price(mid, coupon, years) > price else (lo, mid)
    return mid


def norm_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


assert abs(ytm(bond_price(6.0, 5.0, 10), 5.0, 10) - 6.0) < 1e-6
assert abs(bond_price(5.0, 5.0, 7) - 100) < 1e-9
assert abs(bond_price(5.0, 5.0, 7.3) - 100) < 0.02      # par bond between coupon dates is ~100 clean


# ---- Merton (1974): default risk implied by the stock ----
def merton(E, sig_E, D, r, T):
    """Back out asset value V and asset vol from equity value E and equity vol (Merton 1974)."""
    disc = D * np.exp(-r * T)
    def call(V, s):
        d1 = (np.log(V / D) + (r + s * s / 2) * T) / (s * np.sqrt(T))
        return V * norm_cdf(d1) - disc * norm_cdf(d1 - s * np.sqrt(T)), d1
    sig_V = sig_E * E / (E + D)
    for _ in range(500):
        lo, hi = E, E + disc                       # E <= call value <= V, so V lies in [E, E + D e^-rT]
        for _ in range(200):
            V = (lo + hi) / 2
            lo, hi = (lo, V) if call(V, sig_V)[0] > E else (V, hi)
        d1 = call(V, sig_V)[1]
        new = sig_E * E / (norm_cdf(d1) * V)
        if abs(new - sig_V) < 1e-12: break
        sig_V = new
    d2 = d1 - sig_V * np.sqrt(T)
    spread = -np.log(norm_cdf(d2) + V / disc * norm_cdf(-d1)) / T
    return {'V': V, 'sig_V': sig_V, 'DD': d2, 'pd': norm_cdf(-d2), 'spread_bp': spread * 1e4}

# check: the solution must reprice the stock and its volatility
_m = merton(30, 0.8, 35, 0.04, 5)
_d1 = _m['DD'] + _m['sig_V'] * np.sqrt(5)
assert abs(_m['V'] * norm_cdf(_d1) - 35 * np.exp(-0.2) * norm_cdf(_m['DD']) - 30) < 1e-6
assert abs(norm_cdf(_d1) * _m['sig_V'] * _m['V'] - 0.8 * 30) < 1e-6



# ---- Black-Scholes option prices (no dividends) ----
def bs_call(S, K, T, r, s):
    """European call: S spot, K strike, T years, r continuous rate, s volatility."""
    d1 = (np.log(S / K) + (r + s * s / 2) * T) / (s * np.sqrt(T))
    return S * norm_cdf(d1) - K * np.exp(-r * T) * norm_cdf(d1 - s * np.sqrt(T))


def bs_put(S, K, T, r, s):
    """European put, by put-call parity."""
    return bs_call(S, K, T, r, s) - S + K * np.exp(-r * T)


assert abs(bs_call(100, 100, 1, 0.0, 0.2) - 7.9656) < 1e-3          # textbook at-the-money value
