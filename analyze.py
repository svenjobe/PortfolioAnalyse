#!/usr/bin/env python3
"""
Portfolioanalyse: Rendite, Volatilität und Sharpe Ratio für ein
10-Aktien-Portfolio (pandas + yfinance).

Verwendung:
    python analyze.py

Benötigt eine aktive Internetverbindung, da historische Kursdaten live
über yfinance (Yahoo Finance) geladen werden. Ergebnisse (CSV + Charts)
werden im Ordner `output/` abgelegt.
"""

from __future__ import annotations

import os

from src import config
from src.data_loader import compute_daily_returns, download_adjusted_close
from src.metrics import (
    asset_summary,
    correlation_matrix,
    portfolio_daily_returns,
    portfolio_summary,
)
from src.visualize import (
    plot_correlation_heatmap,
    plot_cumulative_returns,
    plot_risk_return_scatter,
    plot_sharpe_bar,
)


def main() -> None:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    print(f"Lade Kursdaten für {len(config.TICKERS)} Titel "
          f"({config.START_DATE} bis {config.END_DATE}) ...")
    prices = download_adjusted_close(config.TICKERS, config.START_DATE, config.END_DATE)
    daily_returns = compute_daily_returns(prices)

    print("Berechne Kennzahlen je Einzeltitel ...")
    assets = asset_summary(
        daily_returns,
        risk_free_rate=config.RISK_FREE_RATE,
        periods_per_year=config.TRADING_DAYS_PER_YEAR,
    )
    assets_pct = assets.copy()
    assets_pct["Annualisierte Rendite"] = (assets_pct["Annualisierte Rendite"] * 100).round(2)
    assets_pct["Annualisierte Volatilität"] = (assets_pct["Annualisierte Volatilität"] * 100).round(2)
    assets_pct["Sharpe Ratio"] = assets_pct["Sharpe Ratio"].round(2)
    print(assets_pct.to_string())

    print("\nBerechne Portfolio-Kennzahlen (gewichtet) ...")
    port_stats = portfolio_summary(
        daily_returns,
        config.WEIGHTS,
        risk_free_rate=config.RISK_FREE_RATE,
        periods_per_year=config.TRADING_DAYS_PER_YEAR,
    )
    print(
        f"  Annualisierte Rendite:      {port_stats['Annualisierte Rendite'] * 100:6.2f} %\n"
        f"  Annualisierte Volatilität:  {port_stats['Annualisierte Volatilität'] * 100:6.2f} %\n"
        f"  Sharpe Ratio:                {port_stats['Sharpe Ratio']:6.2f}"
    )

    # Ergebnisse speichern -------------------------------------------------
    assets_pct.to_csv(os.path.join(config.OUTPUT_DIR, "asset_metrics.csv"))
    with open(os.path.join(config.OUTPUT_DIR, "portfolio_metrics.csv"), "w") as f:
        f.write("Kennzahl,Wert\n")
        f.write(f"Annualisierte Rendite (%),{port_stats['Annualisierte Rendite'] * 100:.2f}\n")
        f.write(f"Annualisierte Volatilität (%),{port_stats['Annualisierte Volatilität'] * 100:.2f}\n")
        f.write(f"Sharpe Ratio,{port_stats['Sharpe Ratio']:.2f}\n")

    port_returns = portfolio_daily_returns(daily_returns, config.WEIGHTS)
    corr = correlation_matrix(daily_returns)

    print("\nErstelle Charts ...")
    plot_cumulative_returns(
        port_returns, outfile=os.path.join(config.OUTPUT_DIR, "cumulative_returns.png")
    )
    plot_risk_return_scatter(
        assets, port_stats, outfile=os.path.join(config.OUTPUT_DIR, "risk_return_scatter.png")
    )
    plot_sharpe_bar(
        assets, port_stats, outfile=os.path.join(config.OUTPUT_DIR, "sharpe_ratio_comparison.png")
    )
    plot_correlation_heatmap(
        corr, outfile=os.path.join(config.OUTPUT_DIR, "correlation_heatmap.png")
    )

    print(f"\nFertig. Ergebnisse liegen in '{config.OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()
