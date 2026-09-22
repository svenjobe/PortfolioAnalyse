#!/usr/bin/env python3
"""
Erzeugt Beispiel-Charts/CSV mit SIMULIERTEN Kursverläufen, damit das Repo
auf GitHub sofort Beispieloutput zeigt, ohne dass ein Betrachter das
Skript erst selbst ausführen muss.

WICHTIG: Dies verwendet KEINE echten Marktdaten, sondern per Zufallszahlen
(mit festem Seed, reproduzierbar) simulierte, plausible Kursverläufe
(geometrische Brownsche Bewegung mit realistischen Drift-/Vola-Annahmen
je Ticker). Für eine echte Analyse mit tatsächlichen Marktdaten:

    python analyze.py

Dieses Skript existiert nur, damit `output/` im Repository befüllte
Beispielgrafiken enthält (siehe README, Abschnitt "Beispiel-Output").
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

# Projekt-Root zum Modulpfad hinzufügen, damit "python scripts/generate_demo_output.py"
# unabhängig vom Arbeitsverzeichnis funktioniert.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.data_loader import compute_daily_returns
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

# Plausible annualisierte Drift-/Vola-Annahmen je Ticker (grobe, öffentlich
# bekannte Größenordnungen je Sektor) – rein zur Demonstration.
DEMO_ASSUMPTIONS = {
    "AAPL":    (0.15, 0.28),
    "MSFT":    (0.16, 0.26),
    "NVDA":    (0.35, 0.52),
    "JPM":     (0.10, 0.24),
    "JNJ":     (0.06, 0.16),
    "SAP.DE":  (0.13, 0.27),
    "ALV.DE":  (0.09, 0.20),
    "SIE.DE":  (0.11, 0.25),
    "NESN.SW": (0.05, 0.15),
    "MC.PA":   (0.09, 0.26),
}

# Grobe Sektor-Cluster für eine realistischere Korrelationsstruktur.
CLUSTERS = {
    "AAPL": 0, "MSFT": 0, "NVDA": 0, "SAP.DE": 0,   # Tech
    "JPM": 1, "ALV.DE": 1,                          # Finanzen/Versicherung
    "JNJ": 2,                                       # Gesundheit
    "SIE.DE": 3,                                    # Industrie
    "NESN.SW": 4, "MC.PA": 4,                       # Konsum/Luxus
}


def simulate_prices(tickers: list[str], start, end, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, end)
    n = len(dates)
    n_clusters = len(set(CLUSTERS.values()))

    # Gemeinsamer Markt- + Cluster-Faktor sorgt für realistische Korrelationen
    market_factor = rng.normal(0, 1, n)
    cluster_factors = {c: rng.normal(0, 1, n) for c in range(n_clusters)}

    price_data = {}
    for ticker in tickers:
        mu, sigma = DEMO_ASSUMPTIONS.get(ticker, (0.08, 0.22))
        cluster = CLUSTERS.get(ticker, 0)
        idio = rng.normal(0, 1, n)

        # Renditebeitrag: 40% Markt, 30% Cluster, 30% titelspezifisch
        combined_shock = 0.4 * market_factor + 0.3 * cluster_factors[cluster] + 0.3 * idio
        daily_mu = mu / 252
        daily_sigma = sigma / np.sqrt(252)
        daily_returns = daily_mu + daily_sigma * combined_shock

        prices = 100 * np.cumprod(1 + daily_returns)
        price_data[ticker] = prices

    return pd.DataFrame(price_data, index=dates)


def main() -> None:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    print("Simuliere Beispiel-Kursdaten (KEINE echten Marktdaten) ...")
    prices = simulate_prices(config.TICKERS, config.START_DATE, config.END_DATE)
    daily_returns = compute_daily_returns(prices)

    assets = asset_summary(
        daily_returns,
        risk_free_rate=config.RISK_FREE_RATE,
        periods_per_year=config.TRADING_DAYS_PER_YEAR,
    )
    port_stats = portfolio_summary(
        daily_returns,
        config.WEIGHTS,
        risk_free_rate=config.RISK_FREE_RATE,
        periods_per_year=config.TRADING_DAYS_PER_YEAR,
    )
    port_returns = portfolio_daily_returns(daily_returns, config.WEIGHTS)
    corr = correlation_matrix(daily_returns)

    assets_pct = assets.copy()
    assets_pct["Annualisierte Rendite"] = (assets_pct["Annualisierte Rendite"] * 100).round(2)
    assets_pct["Annualisierte Volatilität"] = (assets_pct["Annualisierte Volatilität"] * 100).round(2)
    assets_pct["Sharpe Ratio"] = assets_pct["Sharpe Ratio"].round(2)
    assets_pct.to_csv(os.path.join(config.OUTPUT_DIR, "demo_asset_metrics.csv"))

    print(assets_pct.to_string())
    print(
        f"\nPortfolio -> Rendite: {port_stats['Annualisierte Rendite']*100:.2f}%  "
        f"Volatilität: {port_stats['Annualisierte Volatilität']*100:.2f}%  "
        f"Sharpe: {port_stats['Sharpe Ratio']:.2f}"
    )

    plot_cumulative_returns(
        port_returns,
        title="Kumulierte Portfoliorendite (Demo, simulierte Daten)",
        outfile=os.path.join(config.OUTPUT_DIR, "cumulative_returns.png"),
    )
    plot_risk_return_scatter(
        assets, port_stats,
        title="Risiko-Rendite-Profil (Demo, simulierte Daten)",
        outfile=os.path.join(config.OUTPUT_DIR, "risk_return_scatter.png"),
    )
    plot_sharpe_bar(
        assets, port_stats,
        title="Sharpe Ratio im Vergleich (Demo, simulierte Daten)",
        outfile=os.path.join(config.OUTPUT_DIR, "sharpe_ratio_comparison.png"),
    )
    plot_correlation_heatmap(
        corr,
        title="Korrelationsmatrix (Demo, simulierte Daten)",
        outfile=os.path.join(config.OUTPUT_DIR, "correlation_heatmap.png"),
    )
    print(f"\nBeispiel-Charts gespeichert in '{config.OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()
