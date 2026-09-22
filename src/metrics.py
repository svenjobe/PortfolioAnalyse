"""
Kennzahlenberechnung: annualisierte Rendite, Volatilität und Sharpe Ratio
für Einzeltitel sowie für ein gewichtetes Portfolio.

Alle Funktionen arbeiten auf täglichen (einfachen) Renditen und
annualisieren über die Anzahl der Handelstage pro Jahr (Standard: 252).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_return(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualisierte (geometrische) Rendite aus täglichen Renditen."""
    compounded_growth = (1 + daily_returns).prod()
    n_periods = daily_returns.count()
    if n_periods == 0:
        return np.nan
    return compounded_growth ** (periods_per_year / n_periods) - 1


def annualized_volatility(daily_returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualisierte Volatilität (Standardabweichung) aus täglichen Renditen."""
    return daily_returns.std(ddof=1) * np.sqrt(periods_per_year)


def sharpe_ratio(
    daily_returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Annualisierte Sharpe Ratio.

    Sharpe = (annualisierte Rendite - risikofreier Zins) / annualisierte Volatilität
    """
    ann_return = annualized_return(daily_returns, periods_per_year)
    ann_vol = annualized_volatility(daily_returns, periods_per_year)
    if ann_vol == 0 or np.isnan(ann_vol):
        return np.nan
    return (ann_return - risk_free_rate) / ann_vol


def asset_summary(
    daily_returns: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    """Kennzahlen-Tabelle (Rendite, Volatilität, Sharpe) je Einzeltitel."""
    rows = []
    for ticker in daily_returns.columns:
        series = daily_returns[ticker].dropna()
        rows.append(
            {
                "Ticker": ticker,
                "Annualisierte Rendite": annualized_return(series, periods_per_year),
                "Annualisierte Volatilität": annualized_volatility(series, periods_per_year),
                "Sharpe Ratio": sharpe_ratio(series, risk_free_rate, periods_per_year),
            }
        )
    return pd.DataFrame(rows).set_index("Ticker")


def portfolio_daily_returns(daily_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Gewichtete tägliche Portfoliorendite aus Einzeltitel-Renditen."""
    aligned_weights = pd.Series(weights).reindex(daily_returns.columns).fillna(0.0)
    if not np.isclose(aligned_weights.sum(), 1.0):
        raise ValueError(f"Gewichte summieren sich auf {aligned_weights.sum():.4f}, erwartet 1.0")
    return daily_returns.mul(aligned_weights, axis=1).sum(axis=1)


def portfolio_summary(
    daily_returns: pd.DataFrame,
    weights: dict[str, float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> dict:
    """Kennzahlen für das Gesamtportfolio (gewichtete Renditen)."""
    port_returns = portfolio_daily_returns(daily_returns, weights)
    return {
        "Annualisierte Rendite": annualized_return(port_returns, periods_per_year),
        "Annualisierte Volatilität": annualized_volatility(port_returns, periods_per_year),
        "Sharpe Ratio": sharpe_ratio(port_returns, risk_free_rate, periods_per_year),
    }


def correlation_matrix(daily_returns: pd.DataFrame) -> pd.DataFrame:
    """Korrelationsmatrix der täglichen Renditen (Diversifikationsindikator)."""
    return daily_returns.corr()
