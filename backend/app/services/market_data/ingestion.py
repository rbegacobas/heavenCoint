"""Data ingestion orchestrator — fetches market data and persists to DB + Redis."""

import logging
from datetime import UTC, datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.models.asset import Asset
from app.models.macro_indicator import MacroIndicator
from app.models.price_history import PriceHistory
from app.services.market_data.binance_client import fetch_crypto_bars
from app.services.market_data.fred_client import fetch_all_indicators
from app.services.market_data.polygon_client import fetch_stock_bars
from app.services.market_data.twelvedata_client import fetch_stock_bars_td
from app.services.market_data.yfinance_client import fetch_stock_bars_yf
from app.services.schwab_client import get_price_history as schwab_get_history
from app.core.redis import redis_client as _redis


async def _schwab_authenticated() -> bool:
    """Return True if a valid Schwab token exists in Redis."""
    token = await _redis.get("schwab:token")
    return token is not None


async def ingest_price_data(ticker: str, asset_id: str, asset_type: str, db: AsyncSession) -> int:
    """Fetch OHLCV data for an asset and persist to price_history.

    Source priority:
      crypto  → Binance (real-time, free)
      forex   → yFinance (15 min delay)
      stocks  → Schwab if authenticated (real-time)
               → Polygon if key configured (real-time)
               → yFinance fallback (15 min delay)
    """
    if asset_type == "crypto":
        try:
            bars = await fetch_crypto_bars(ticker)
            source = "binance"
        except Exception:
            bars = await fetch_stock_bars_yf(ticker)
            source = "yfinance"
    elif asset_type == "forex":
        bars = await fetch_stock_bars_yf(ticker)
        source = "yfinance"
    elif await _schwab_authenticated():
        # Schwab authenticated → real-time institutional data
        bars = await schwab_get_history(ticker)
        if not bars:
            # Schwab failed (e.g. market closed, ticker not found) → fallback
            logger.warning("Schwab returned no data for %s, falling back to yFinance", ticker)
            bars = await fetch_stock_bars_yf(ticker)
            source = "yfinance"
        else:
            source = "schwab"
    elif settings.polygon_api_key:
        bars = await fetch_stock_bars(ticker)
        source = "polygon"
    elif settings.twelvedata_api_key:
        bars = await fetch_stock_bars_td(ticker)
        source = "twelvedata"
    else:
        # Last resort — yfinance (blocked on most cloud VPS IPs)
        bars = await fetch_stock_bars_yf(ticker)
        source = "yfinance"

    if not bars:
        return 0

    # Get the latest existing timestamp for this asset to avoid duplicates
    result = await db.execute(
        select(PriceHistory.time)
        .where(PriceHistory.asset_id == asset_id)
        .order_by(PriceHistory.time.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    count = 0
    for bar in bars:
        bar_time = datetime.fromtimestamp(bar["t"] / 1000, tz=UTC)
        if latest and bar_time <= latest:
            continue

        db.add(
            PriceHistory(
                time=bar_time,
                asset_id=asset_id,
                open=Decimal(str(bar["o"])),
                high=Decimal(str(bar["h"])),
                low=Decimal(str(bar["l"])),
                close=Decimal(str(bar["c"])),
                volume=bar["v"],
                source=source,
            )
        )
        count += 1

    if count > 0:
        await db.flush()

        # Cache latest price in Redis
        last_bar = bars[-1]
        await redis_client.hset(
            f"kpi:{ticker}",
            mapping={
                "current_price": str(last_bar["c"]),
                "last_updated": datetime.now(UTC).isoformat(),
                "data_source": source,
            },
        )
        await redis_client.expire(f"kpi:{ticker}", 300)  # 5 min TTL

    return count


async def ingest_macro_data(db: AsyncSession) -> int:
    """Fetch all FRED macro indicators and persist to DB + Redis.

    Returns the number of indicators updated.
    """
    indicators = await fetch_all_indicators()
    count = 0

    for _series_id, data in indicators.items():
        indicator = MacroIndicator(
            indicator_code=data["indicator_code"],
            indicator_name=data["indicator_name"],
            value=Decimal(str(data["value"])),
            previous_value=Decimal(str(data["previous_value"])) if data["previous_value"] else None,
            direction=data["direction"],
            source="fred",
            published_at=datetime.fromisoformat(data["published_at"]),
        )
        db.add(indicator)
        count += 1

    if count > 0:
        await db.flush()

        # Cache macro summary in Redis
        macro_cache: dict[str, str] = {}
        for series_id, data in indicators.items():
            macro_cache[series_id.lower()] = str(data["value"])
        macro_cache["last_updated"] = datetime.now(UTC).isoformat()

        await redis_client.hset("macro:latest", mapping=macro_cache)
        await redis_client.expire("macro:latest", 3600)  # 1 hour TTL

    return count


async def ensure_asset_exists(
    ticker: str,
    name: str,
    asset_type: str,
    exchange: str | None,
    db: AsyncSession,
) -> Asset:
    """Find or create an asset record. Updates asset_type if it changed. Returns the Asset."""
    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()

    if asset is None:
        decimal_places = 8 if asset_type == "crypto" else 4
        asset = Asset(
            ticker=ticker,
            name=name,
            asset_type=asset_type,
            exchange=exchange,
            decimal_places=decimal_places,
        )
        db.add(asset)
        await db.flush()
        await db.refresh(asset)
    elif asset.asset_type != asset_type:
        # Correct stale asset_type (e.g. forex saved as crypto or stock previously)
        asset.asset_type = asset_type
        await db.flush()

    return asset
