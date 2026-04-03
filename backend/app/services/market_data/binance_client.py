"""Binance client — crypto OHLCV data."""

import httpx

BINANCE_BASE = "https://api.binance.com"

# Map our ticker format (BTC-USD) to Binance format (BTCUSDT)
_TICKER_MAP = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "BNB-USD": "BNBUSDT",
    "XRP-USD": "XRPUSDT",
    "ADA-USD": "ADAUSDT",
    "DOGE-USD": "DOGEUSDT",
    "DOT-USD": "DOTUSDT",
    "AVAX-USD": "AVAXUSDT",
    "MATIC-USD": "MATICUSDT",
}


def to_binance_symbol(ticker: str) -> str:
    """Convert our ticker format to Binance symbol."""
    return _TICKER_MAP.get(ticker, ticker.replace("-", ""))


async def fetch_crypto_bars(
    ticker: str,
    interval: str = "1d",
    limit: int = 500,
) -> list[dict]:
    """Fetch OHLCV klines from Binance for a crypto pair.

    Returns list of dicts with keys: t, o, h, l, c, v.
    """
    symbol = to_binance_symbol(ticker)
    url = f"{BINANCE_BASE}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return [
        {
            "t": kline[0],  # Open time (unix ms)
            "o": float(kline[1]),
            "h": float(kline[2]),
            "l": float(kline[3]),
            "c": float(kline[4]),
            "v": int(float(kline[5])),
        }
        for kline in data
    ]


async def search_crypto_tickers(query: str, limit: int = 10) -> list[dict]:
    """Search available crypto pairs matching the query."""
    url = f"{BINANCE_BASE}/api/v3/exchangeInfo"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    query_upper = query.upper()
    results = []
    for sym in data.get("symbols", []):
        if sym["status"] != "TRADING" or not sym["symbol"].endswith("USDT"):
            continue
        base = sym["baseAsset"]
        if query_upper in base or query_upper in sym["symbol"]:
            results.append(
                {
                    "ticker": f"{base}-USD",
                    "name": f"{base}/USD",
                    "exchange": "BINANCE",
                    "type": "crypto",
                }
            )
            if len(results) >= limit:
                break

    return results
