from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


def _fallback_price(symbol: str) -> float:
    seed = sum(ord(ch) for ch in symbol)
    random.seed(seed)
    return round(random.uniform(80, 320), 2)


def get_stock_quote(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    try:
        history = ticker.history(period="2d")
        if history.empty:
            raise ValueError("No history available")
        current = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else current
        return {
            "symbol": symbol,
            "current_price": round(current, 2),
            "previous_close": round(previous_close, 2),
            "source": "live",
        }
    except Exception:
        price = _fallback_price(symbol)
        return {
            "symbol": symbol,
            "current_price": price,
            "previous_close": round(price * 0.99, 2),
            "source": "fallback",
        }


def get_historical_prices(symbol: str, period: str = "6mo", interval: str = "1d") -> dict:
    ticker = yf.Ticker(symbol)
    try:
        history = ticker.history(period=period, interval=interval)
        if history.empty:
            raise ValueError("No historical data available")
        history = history.reset_index()
        return {
            "labels": [dt.strftime("%Y-%m-%d") for dt in history["Date"]],
            "prices": [round(float(p), 2) for p in history["Close"]],
            "source": "live",
        }
    except Exception:
        base = _fallback_price(symbol)
        dates = pd.date_range(datetime.today() - timedelta(days=120), periods=120, freq="D")
        generated = [round(base + (idx * 0.08) + ((idx % 7) - 3) * 0.6, 2) for idx in range(120)]
        return {
            "labels": [dt.strftime("%Y-%m-%d") for dt in dates],
            "prices": generated,
            "source": "fallback",
        }
