"""yfinance client — free fallback for stock/forex OHLCV data and ticker search.

Used automatically when POLYGON_API_KEY is not configured.
yfinance pulls from Yahoo Finance (no API key required).

Forex notes:
  Yahoo Finance uses "{BASE}{QUOTE}=X" format (e.g. EURUSD=X).
  We store clean tickers (EURUSD) and append =X internally for downloads.
"""

import asyncio
from functools import partial

import yfinance as yf

# Forex pairs are exactly 6 uppercase letters (e.g. EURUSD, GBPJPY).
_FOREX_SUFFIXES = ("=X",)


def _to_yf_ticker(ticker: str) -> str:
    """Convert clean ticker to Yahoo Finance format.

    EURUSD  → EURUSD=X   (6-char all-alpha = forex pair)
    GBPJPY  → GBPJPY=X
    EURUSD=X → EURUSD=X  (idempotent)
    AAPL    → AAPL       (< 6 chars)
    SPY     → SPY
    BTC-USD → BTC-USD    (contains hyphen — crypto/commodity, not forex)
    """
    if any(ticker.endswith(s) for s in _FOREX_SUFFIXES):
        return ticker
    # Only map to =X if it's exactly 6 uppercase alpha chars (classic forex pair)
    # and does NOT contain a hyphen (which would indicate crypto like BTC-USD)
    if len(ticker) == 6 and ticker.isalpha() and "-" not in ticker:
        return f"{ticker}=X"
    return ticker


def _fetch_bars_sync(ticker: str, period: str = "2y") -> list[dict]:
    """Synchronous yfinance download. Wrapped async below."""
    yf_ticker = _to_yf_ticker(ticker)
    df = yf.download(yf_ticker, period=period, interval="1d", auto_adjust=True, progress=False)
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
    """Synchronous yfinance search. Returns stocks, ETFs, and forex pairs."""
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

        # Include stocks, ETFs, and forex currency pairs
        if quote_type not in ("EQUITY", "ETF", "CURRENCY"):
            continue

        if quote_type == "CURRENCY":
            # Strip Yahoo suffix: EURUSD=X → EURUSD
            clean_ticker = ticker.replace("=X", "")
            asset_type = "forex"
        elif quote_type == "ETF":
            clean_ticker = ticker
            asset_type = "etf"
        else:
            clean_ticker = ticker
            asset_type = "stock"

        results.append({
            "ticker": clean_ticker,
            "name": name,
            "exchange": exchange,
            "type": asset_type,
        })

    return results


async def fetch_stock_bars_yf(ticker: str, period: str = "2y") -> list[dict]:
    """Async wrapper — runs yfinance download in a thread pool to avoid blocking.

    Handles stocks (AAPL), ETFs (SPY), and forex pairs (EURUSD → EURUSD=X).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_fetch_bars_sync, ticker, period))


async def search_stock_tickers_yf(query: str, limit: int = 10) -> list[dict]:
    """Async wrapper — runs yfinance search in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_search_ticker_sync, query, limit))
