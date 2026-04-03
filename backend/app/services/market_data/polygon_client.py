"""Polygon.io client — US stocks OHLCV data."""

from datetime import date, timedelta

import httpx

from app.core.config import settings

POLYGON_BASE = "https://api.polygon.io"


async def fetch_stock_bars(
    ticker: str,
    from_date: date | None = None,
    to_date: date | None = None,
    timespan: str = "day",
    limit: int = 500,
) -> list[dict]:
    """Fetch OHLCV bars from Polygon.io for a US stock.

    Returns list of dicts with keys: t, o, h, l, c, v (timestamp, open, high, low, close, volume).
    """
    if to_date is None:
        to_date = date.today()
    if from_date is None:
        from_date = to_date - timedelta(days=365 * 2)  # 2 years default

    url = (
        f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/1/{timespan}"
        f"/{from_date.isoformat()}/{to_date.isoformat()}"
    )
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": limit,
        "apiKey": settings.polygon_api_key,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])
    return [
        {
            "t": bar["t"],  # Unix ms timestamp
            "o": bar["o"],
            "h": bar["h"],
            "l": bar["l"],
            "c": bar["c"],
            "v": bar.get("v", 0),
        }
        for bar in results
    ]


async def search_stock_tickers(query: str, limit: int = 10) -> list[dict]:
    """Search Polygon.io for stock tickers matching a query."""
    url = f"{POLYGON_BASE}/v3/reference/tickers"
    params = {
        "search": query,
        "active": "true",
        "market": "stocks",
        "limit": limit,
        "apiKey": settings.polygon_api_key,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return [
        {
            "ticker": t["ticker"],
            "name": t.get("name", ""),
            "exchange": t.get("primary_exchange", ""),
            "type": "stock",
        }
        for t in data.get("results", [])
    ]
