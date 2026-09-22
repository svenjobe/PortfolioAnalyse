"""
Visualisierungen für die Portfolioanalyse (matplotlib).

Farbgebung folgt einem festen, farbfehlsichtigkeitssicheren Schema:
- Kategorial: Blau (#2a78d6) für Einzeltitel, Orange (#eb6834) als
  Hervorhebung für das Portfolio.
- Divergierend (Korrelation, -1..+1): Blau <-> Rot mit neutralem Grau
  bei 0.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# --- Farbpalette --------------------------------------------------------
BLUE = "#2a78d6"
ORANGE = "#eb6834"
RED = "#e34948"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
SURFACE = "#fcfcfb"

DIVERGING_CMAP = LinearSegmentedColormap.from_list(
    "blue_red_diverging", [BLUE, "#f0efec", RED]
)


def _style_axis(ax) -> None:
    """Wendet ein einheitliches, zurückhaltendes Erscheinungsbild an."""
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRIDLINE)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.title.set_color(INK_PRIMARY)
    ax.xaxis.label.set_color(INK_SECONDARY)
    ax.yaxis.label.set_color(INK_SECONDARY)


def plot_cumulative_returns(
    portfolio_returns: pd.Series,
    title: str = "Kumulierte Portfoliorendite",
    outfile: str | None = None,
):
    """Linienchart der kumulierten Portfoliorendite über die Zeit."""
    cumulative = (1 + portfolio_returns).cumprod() - 1

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
    ax.plot(cumulative.index, cumulative.values * 100, color=BLUE, linewidth=2)
    ax.fill_between(cumulative.index, cumulative.values * 100, 0, color=BLUE, alpha=0.08)
    ax.axhline(0, color=GRIDLINE, linewidth=1)
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=12)
    ax.set_ylabel("Kumulierte Rendite (%)")
    _style_axis(ax)
    fig.tight_layout()
    if outfile:
        fig.savefig(outfile, facecolor=SURFACE)
    return fig


def plot_risk_return_scatter(
    asset_summary_df: pd.DataFrame,
    portfolio_stats: dict,
    title: str = "Risiko-Rendite-Profil",
    outfile: str | None = None,
):
    """Streudiagramm: Volatilität (x) vs. annualisierte Rendite (y).

    Jeder Punkt ist per Direktbeschriftung identifiziert (kein Farb-Overload
    bei 10+ Einzeltiteln) - das Portfolio wird als hervorgehobener Punkt
    dargestellt.
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    x = asset_summary_df["Annualisierte Volatilität"] * 100
    y = asset_summary_df["Annualisierte Rendite"] * 100
    ax.scatter(x, y, s=70, color=BLUE, zorder=3, edgecolor="white", linewidth=0.8)
    for ticker, xi, yi in zip(asset_summary_df.index, x, y):
        ax.annotate(
            ticker,
            (xi, yi),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=8.5,
            color=INK_SECONDARY,
        )

    port_x = portfolio_stats["Annualisierte Volatilität"] * 100
    port_y = portfolio_stats["Annualisierte Rendite"] * 100
    ax.scatter(
        [port_x], [port_y], s=160, color=ORANGE, zorder=4,
        edgecolor="white", linewidth=1.2, marker="D",
    )
    ax.annotate(
        "Portfolio",
        (port_x, port_y),
        textcoords="offset points",
        xytext=(8, 6),
        fontsize=9.5,
        fontweight="bold",
        color=INK_PRIMARY,
    )

    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=12)
    ax.set_xlabel("Annualisierte Volatilität (%)")
    ax.set_ylabel("Annualisierte Rendite (%)")
    _style_axis(ax)
    fig.tight_layout()
    if outfile:
        fig.savefig(outfile, facecolor=SURFACE)
    return fig


def plot_sharpe_bar(
    asset_summary_df: pd.DataFrame,
    portfolio_stats: dict,
    title: str = "Sharpe Ratio im Vergleich",
    outfile: str | None = None,
):
    """Balkendiagramm der Sharpe Ratio je Einzeltitel, Portfolio hervorgehoben."""
    combined = asset_summary_df["Sharpe Ratio"].copy()
    combined["Portfolio"] = portfolio_stats["Sharpe Ratio"]
    combined = combined.sort_values(ascending=True)

    colors = [ORANGE if idx == "Portfolio" else BLUE for idx in combined.index]

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    bars = ax.barh(combined.index, combined.values, color=colors, height=0.6)
    for bar, value in zip(bars, combined.values):
        ax.annotate(
            f"{value:.2f}",
            (value, bar.get_y() + bar.get_height() / 2),
            textcoords="offset points",
            xytext=(5 if value >= 0 else -5, 0),
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=8.5,
            color=INK_SECONDARY,
        )

    ax.axvline(0, color=GRIDLINE, linewidth=1)
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=12)
    ax.set_xlabel("Sharpe Ratio")
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRIDLINE)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9)
    ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.title.set_color(INK_PRIMARY)
    fig.tight_layout()
    if outfile:
        fig.savefig(outfile, facecolor=SURFACE)
    return fig


def plot_correlation_heatmap(
    corr_df: pd.DataFrame,
    title: str = "Korrelationsmatrix der täglichen Renditen",
    outfile: str | None = None,
):
    """Heatmap der Korrelationsmatrix (divergierend Blau <-> Rot, Grau bei 0)."""
    fig, ax = plt.subplots(figsize=(8, 7), dpi=150)
    im = ax.imshow(corr_df.values, cmap=DIVERGING_CMAP, vmin=-1, vmax=1)

    ax.set_xticks(range(len(corr_df.columns)))
    ax.set_yticks(range(len(corr_df.index)))
    ax.set_xticklabels(corr_df.columns, rotation=45, ha="right", fontsize=8.5, color=INK_SECONDARY)
    ax.set_yticklabels(corr_df.index, fontsize=8.5, color=INK_SECONDARY)

    for i in range(len(corr_df.index)):
        for j in range(len(corr_df.columns)):
            value = corr_df.values[i, j]
            text_color = "white" if abs(value) > 0.6 else INK_PRIMARY
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=7, color=text_color)

    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=12)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Korrelationskoeffizient")
    fig.patch.set_facecolor(SURFACE)
    fig.tight_layout()
    if outfile:
        fig.savefig(outfile, facecolor=SURFACE)
    return fig
