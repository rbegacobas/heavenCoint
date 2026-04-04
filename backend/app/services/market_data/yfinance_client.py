"""yfinance client — free fallback for stock OHLCV data and ticker search.

Used automatically when POLYGON_API_KEY is not configured.
yfinance pulls from Yahoo Finance (no API key required).
"""

import asyncio
from functools import partial

import yfinance as yf


def _fetch_bars_sync(ticker: str, period: str = "2y") -> list[dict]:
    """Synchronous yfinance download. Wrapped async below."""
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if df.empty:
        return []

    bars = []
    for ts, row in df.iterrows():
        # yfinance may return MultiIndex columns when downloading single ticker
        try:
            o = float(row["Open"].iloc[0]) if hasattr(row["Open"], "iloc") else float(row["Open"])
            h = float(row["High"].iloc[0]) if hasattr(row["High"], "iloc") else float(row["High"])
            lo = float(row["Low"].iloc[0]) if hasattr(row["Low"], "iloc") else float(row["Low"])
            c = (
                float(row["Close"].iloc[0]) if hasattr(row["Close"], "iloc")
                else float(row["Close"])
            )
            v = int(row["Volume"].iloc[0]) if hasattr(row["Volume"], "iloc") else int(row["Volume"])
        except (KeyError, TypeError, ValueError):
            continue

        bars.append({
            "t": int(ts.timestamp() * 1000),  # Unix ms — same format as Polygon/Binance
            "o": o,
            "h": h,
            "l": lo,
            "c": c,
            "v": v,
        })

    return bars


def _search_ticker_sync(query: str, limit: int = 10) -> list[dict]:
    """Synchronous yfinance search."""
    try:
        search = yf.Search(query, max_results=limit)
        quotes = search.quotes
    except Exception:
        return []

    results = []
    for q in quotes[:limit]:
        ticker = q.get("symbol", "")
        name = q.get("longname") or q.get("shortname") or ticker
        exchange = q.get("exchange", "")
        quote_type = q.get("quoteType", "EQUITY").upper()

        # Only stocks/ETFs (skip futures, options, etc.)
        if quote_type not in ("EQUITY", "ETF"):
            continue

        results.append({
            "ticker": ticker,
            "name": name,
            "exchange": exchange,
            "type": "etf" if quote_type == "ETF" else "stock",
        })

    return results


async def fetch_stock_bars_yf(ticker: str, period: str = "2y") -> list[dict]:
    """Async wrapper — runs yfinance download in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_fetch_bars_sync, ticker, period))


async def search_stock_tickers_yf(query: str, limit: int = 10) -> list[dict]:
    """Async wrapper — runs yfinance search in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_search_ticker_sync, query, limit))
