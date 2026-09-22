"""
Zentrale Konfiguration für die Portfolioanalyse.

Alle Parameter (Ticker, Gewichte, Zeitraum, risikofreier Zins) sind hier
gebündelt, damit sie an einer Stelle angepasst werden können.
"""

from __future__ import annotations

from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Portfolio-Zusammensetzung
# ---------------------------------------------------------------------------
# Bewusst diversifiziertes Beispielportfolio über Sektoren und Regionen
# hinweg (US-Tech, US-Finanzen/Gesundheit, DACH-Standardwerte, Frankreich).
# Ticker folgen der Yahoo-Finance-Notation (".DE" = Xetra, ".SW" = SIX,
# ".PA" = Euronext Paris).
TICKERS: list[str] = [
    "AAPL",    # Apple – US Technologie
    "MSFT",    # Microsoft – US Technologie
    "NVDA",    # Nvidia – US Halbleiter
    "JPM",     # JPMorgan Chase – US Finanzen
    "JNJ",     # Johnson & Johnson – US Gesundheit
    "SAP.DE",  # SAP SE – Deutschland, Software
    "ALV.DE",  # Allianz SE – Deutschland, Versicherung
    "SIE.DE",  # Siemens AG – Deutschland, Industrie
    "NESN.SW", # Nestlé SA – Schweiz, Konsumgüter
    "MC.PA",   # LVMH – Frankreich, Luxusgüter
]

# Gleichgewichtetes Portfolio (10 % je Position). Kann durch ein beliebiges
# dict {Ticker: Gewicht} ersetzt werden, Summe sollte 1.0 ergeben.
WEIGHTS: dict[str, float] = {ticker: 1.0 / len(TICKERS) for ticker in TICKERS}

# ---------------------------------------------------------------------------
# Betrachtungszeitraum
# ---------------------------------------------------------------------------
END_DATE: date = date.today()
START_DATE: date = END_DATE - timedelta(days=5 * 365)  # letzte 5 Jahre

# ---------------------------------------------------------------------------
# Risikokennzahlen
# ---------------------------------------------------------------------------
# Näherungswert für den risikofreien Zins (z. B. Rendite kurzlaufender
# Staatsanleihen). Sollte bei Bedarf an die aktuelle Zinslandschaft
# angepasst werden.
RISK_FREE_RATE: float = 0.02  # 2 % p.a.

# Handelstage pro Jahr für die Annualisierung.
TRADING_DAYS_PER_YEAR: int = 252

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
OUTPUT_DIR: str = "output"
