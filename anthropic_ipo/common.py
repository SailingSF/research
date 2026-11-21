"""Shared chart style and CSV loaders for the analysis notebooks."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA, CHARTS = Path('data'), Path('charts')

# Parchment-and-ink palette (light mode), a nod to Anthropic's look. Categorical slots are used in this fixed order;
# burnt orange is slot 2, so it shows up as an accent, not everywhere. Checked with the dataviz CVD validator.
SERIES = ['#3a6fb0', '#c8602c', '#2e9d8c', '#d6a12a']
POS, NEG = '#3a6fb0', '#9c2a4a'          # diverging poles: money in / money out (claret, kept apart from the orange)
NEUTRAL = '#857e70'                       # totals and history
LIGHT, DARK, PALE = '#a9c1e0', '#1d3b66', '#d8d2c4'   # tint/shade of SERIES[0]; light gray fill on parchment
INK, INK2, MUTED = '#141413', '#4f4a40', '#857e70'
GRID, AXIS, SURFACE = '#e2dccd', '#bfb7a6', '#f2eee3'

plt.rcParams.update({
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
    'figure.dpi': 110, 'savefig.dpi': 200, 'figure.figsize': (9, 5),
    'font.family': 'serif', 'font.serif': ['Charter', 'Georgia', 'Iowan Old Style', 'Times New Roman', 'DejaVu Serif'],
    'font.size': 10.5, 'text.color': INK, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.edgecolor': AXIS, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': GRID, 'grid.linewidth': 0.6,
    'axes.titlesize': 14, 'axes.titleweight': 'normal', 'axes.titlelocation': 'left', 'axes.titlepad': 22,
    'axes.axisbelow': True, 'text.parse_math': False,  # '$' in titles is currency, not math
    'lines.linewidth': 2, 'lines.markersize': 7, 'legend.frameon': False,
})


def load(name):
    return pd.read_csv(DATA / f'{name}.csv')


def wide(df, index='line_item', columns='period'):
    """Long CSV -> line items x periods, in filing order."""
    return df.pivot_table(index=index, columns=columns, values='value', sort=False)


def subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK2, fontsize=10)


def source(fig, text='Source: Anthropic prospectus (Nov 18, 2026); goodatinvesting.com analysis'):
    fig.text(0.01, 0.005, text, color=MUTED, fontsize=8)


def save(fig, name):
    CHARTS.mkdir(exist_ok=True)
    fig.savefig(CHARTS / name, bbox_inches='tight')
