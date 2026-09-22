"""
Datenbeschaffung für die Portfolioanalyse via yfinance.

Kapselt den Download von historischen Kursdaten und die Aufbereitung
zu täglichen Renditen. Benötigt eine aktive Internetverbindung.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf


def download_adjusted_close(
    tickers: list[str],
    start: date,
    end: date,
) -> pd.DataFrame:
    """Lädt adjustierte Schlusskurse für eine Liste von Tickern.

    Args:
        tickers: Liste der Ticker-Symbole (Yahoo-Finance-Notation).
        start: Startdatum des Betrachtungszeitraums.
        end: Enddatum des Betrachtungszeitraums.

    Returns:
        DataFrame mit Datumsindex und einer Spalte je Ticker
        (adjustierter Schlusskurs).

    Raises:
        ValueError: Wenn für keinen der Ticker Daten geladen werden konnten.
    """
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,   # Close-Spalte ist bereits dividenden-/split-adjustiert
        progress=False,
        group_by="ticker",
    )

    if raw.empty:
        raise ValueError(
            "Keine Kursdaten erhalten. Bitte Internetverbindung und "
            "Ticker-Symbole prüfen."
        )

    # Bei mehreren Tickern liefert yfinance ein MultiIndex-DataFrame
    # (Ticker, Feld). Wir extrahieren je Ticker die 'Close'-Spalte.
    if isinstance(raw.columns, pd.MultiIndex):
        close = pd.DataFrame({t: raw[t]["Close"] for t in tickers if t in raw.columns.get_level_values(0)})
    else:
        # Einzelner Ticker -> einfaches DataFrame
        close = raw[["Close"]].rename(columns={"Close": tickers[0]})

    close = close.dropna(how="all")
    missing = [t for t in tickers if t not in close.columns]
    if missing:
        print(f"Warnung: Keine Daten für {missing} erhalten – werden ignoriert.")

    return close


def compute_daily_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Berechnet einfache tägliche Renditen aus einer Kurs-Zeitreihe."""
    return price_df.pct_change().dropna(how="all")
