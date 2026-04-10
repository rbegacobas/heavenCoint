"""Twelve Data client — reliable stock OHLCV and search for cloud deployments.

Free tier: 800 API calls/day, 8 calls/minute.
Requires TWELVEDATA_API_KEY in environment.
Sign up free: https://twelvedata.com/

Used as fallback when POLYGON_API_KEY is not set.
Preferred over yfinance because Yahoo Finance blocks most cloud VPS IPs.
"""

import logging
from datetime import datetime, timedelta

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.twelvedata.com"


def _is_configured() -> bool:
    return bool(settings.twelvedata_api_key)


def _to_td_symbol(ticker: str) -> str:
    """Convert internal ticker format to Twelve Data symbol format.

    EUR-USD → EUR/USD  (forex hyphen → slash)
    EURUSD  → EUR/USD  (6-char forex → slash)
    NVDA    → NVDA     (stocks unchanged)
    """
    t = ticker.upper()
    if "-" in t and len(t) == 7:  # EUR-USD style
        return t.replace("-", "/")
    if len(t) == 6 and t.isalpha():  # EURUSD style
        return f"{t[:3]}/{t[3:]}"
    return t


async def fetch_stock_bars_td(ticker: str, period_days: int = 365 * 2) -> list[dict]:
    """Download OHLCV bars from Twelve Data.

    Returns list of dicts with keys: t (unix ms), o, h, l, c, v
    """
    if not _is_configured():
        return []

    # Calculate start date
    start_date = (datetime.utcnow() - timedelta(days=period_days)).strftime("%Y-%m-%d")

    params = {
        "symbol": _to_td_symbol(ticker),
        "interval": "1day",
        "start_date": start_date,
        "outputsize": 5000,
        "apikey": settings.twelvedata_api_key,
        "format": "JSON",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(f"{_BASE}/time_series", params=params)
            r.raise_for_status()
            data = r.json()

        if data.get("status") == "error":
            logger.warning("Twelve Data error for %s: %s", ticker, data.get("message"))
            return []

        values = data.get("values", [])
        bars = []
        for v in values:
            try:
                dt = datetime.strptime(v["datetime"], "%Y-%m-%d")
                bars.append({
                    "t": int(dt.timestamp() * 1000),
                    "o": float(v["open"]),
                    "h": float(v["high"]),
                    "l": float(v["low"]),
                    "c": float(v["close"]),
                    "v": int(float(v.get("volume", 0))),
                })
            except (KeyError, ValueError):
                continue

        # API returns newest-first, sort ascending
        bars.sort(key=lambda x: x["t"])
        logger.info("Twelve Data: fetched %d bars for %s", len(bars), ticker)
        return bars

    except Exception as e:
        logger.warning("Twelve Data fetch failed for %s: %s", ticker, e)
        return []


async def search_stock_tickers_td(query: str, limit: int = 10) -> list[dict]:
    """Search tickers via Twelve Data symbol_search endpoint."""
    if not _is_configured():
        return []

    params = {
        "symbol": query,
        "outputsize": limit,
        "apikey": settings.twelvedata_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{_BASE}/symbol_search", params=params)
            r.raise_for_status()
            data = r.json()

        results = []
        for item in data.get("data", [])[:limit]:
            instrument_type = item.get("instrument_type", "").lower()
            if instrument_type not in ("common stock", "etf", "index"):
                continue
            asset_type = "etf" if instrument_type == "etf" else "stock"
            results.append({
                "ticker": item.get("symbol", ""),
                "name": item.get("instrument_name", item.get("symbol", "")),
                "exchange": item.get("exchange", ""),
                "type": asset_type,
            })
        return results

    except Exception as e:
        logger.warning("Twelve Data search failed for %s: %s", query, e)
        return []
