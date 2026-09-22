"""
Unit-Tests für die Kennzahlenberechnung in src/metrics.py.

Verwenden ausschließlich synthetische Daten (kein Netzwerkzugriff nötig),
damit die Tests deterministisch und offline lauffähig sind.
"""

import numpy as np
import pandas as pd
import pytest

from src.metrics import (
    annualized_return,
    annualized_volatility,
    correlation_matrix,
    portfolio_daily_returns,
    portfolio_summary,
    sharpe_ratio,
)


def test_annualized_return_constant_daily_return():
    # Konstante tägliche Rendite r über 252 Tage -> (1+r)^252 - 1
    r = 0.001
    returns = pd.Series([r] * 252)
    result = annualized_return(returns, periods_per_year=252)
    expected = (1 + r) ** 252 - 1
    assert result == pytest.approx(expected, rel=1e-9)


def test_annualized_return_zero_returns_is_zero():
    returns = pd.Series([0.0] * 100)
    assert annualized_return(returns) == pytest.approx(0.0)


def test_annualized_volatility_scales_with_sqrt_time():
    rng = np.random.default_rng(42)
    daily_std = 0.01
    returns = pd.Series(rng.normal(0, daily_std, 5000))
    result = annualized_volatility(returns, periods_per_year=252)
    expected = daily_std * np.sqrt(252)
    # Stichprobenstreuung -> großzügige Toleranz
    assert result == pytest.approx(expected, rel=0.1)


def test_sharpe_ratio_zero_when_return_equals_risk_free():
    # Rendite exakt gleich risikofreiem Zins -> Sharpe = 0
    rng = np.random.default_rng(1)
    returns = pd.Series(rng.normal(0.0003, 0.01, 1000))
    rf = annualized_return(returns, 252)  # risikofreier Zins = tatsächliche Rendite
    result = sharpe_ratio(returns, risk_free_rate=rf, periods_per_year=252)
    assert result == pytest.approx(0.0, abs=1e-9)


def test_sharpe_ratio_nan_when_volatility_zero():
    returns = pd.Series([0.001] * 50)  # keine Streuung
    result = sharpe_ratio(returns, risk_free_rate=0.0)
    assert np.isnan(result)


def test_portfolio_daily_returns_matches_weighted_average():
    dates = pd.date_range("2024-01-01", periods=3)
    returns = pd.DataFrame(
        {"A": [0.01, 0.02, -0.01], "B": [-0.02, 0.00, 0.03]}, index=dates
    )
    weights = {"A": 0.5, "B": 0.5}
    result = portfolio_daily_returns(returns, weights)
    expected = pd.Series([-0.005, 0.01, 0.01], index=dates)
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_portfolio_daily_returns_raises_when_weights_dont_sum_to_one():
    returns = pd.DataFrame({"A": [0.01, 0.02], "B": [0.00, 0.01]})
    with pytest.raises(ValueError):
        portfolio_daily_returns(returns, {"A": 0.5, "B": 0.4})


def test_portfolio_summary_equal_weight_two_identical_assets():
    # Zwei identische Renditereihen -> Portfolio-Kennzahlen = Einzeltitel-Kennzahlen
    dates = pd.date_range("2024-01-01", periods=100)
    rng = np.random.default_rng(7)
    series = rng.normal(0.0005, 0.012, 100)
    returns = pd.DataFrame({"A": series, "B": series}, index=dates)
    weights = {"A": 0.5, "B": 0.5}

    result = portfolio_summary(returns, weights, risk_free_rate=0.02)
    expected_return = annualized_return(pd.Series(series))
    expected_vol = annualized_volatility(pd.Series(series))

    assert result["Annualisierte Rendite"] == pytest.approx(expected_return, rel=1e-9)
    assert result["Annualisierte Volatilität"] == pytest.approx(expected_vol, rel=1e-9)


def test_correlation_matrix_diagonal_is_one():
    dates = pd.date_range("2024-01-01", periods=50)
    rng = np.random.default_rng(3)
    returns = pd.DataFrame(
        {"A": rng.normal(0, 0.01, 50), "B": rng.normal(0, 0.01, 50)}, index=dates
    )
    corr = correlation_matrix(returns)
    assert corr.loc["A", "A"] == pytest.approx(1.0)
    assert corr.loc["B", "B"] == pytest.approx(1.0)
    assert corr.loc["A", "B"] == corr.loc["B", "A"]
