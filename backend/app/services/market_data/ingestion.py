"""Data ingestion orchestrator — fetches market data and persists to DB + Redis."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.models.asset import Asset
from app.models.macro_indicator import MacroIndicator
from app.models.price_history import PriceHistory
from app.services.market_data.binance_client import fetch_crypto_bars
from app.services.market_data.fred_client import fetch_all_indicators
from app.services.market_data.polygon_client import fetch_stock_bars


async def ingest_price_data(ticker: str, asset_id: str, asset_type: str, db: AsyncSession) -> int:
    """Fetch OHLCV data for an asset and persist to price_history.

    Returns the number of bars persisted.
    """
    if asset_type == "crypto":
        bars = await fetch_crypto_bars(ticker)
        source = "binance"
    else:
        bars = await fetch_stock_bars(ticker)
        source = "polygon"

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
    """Find or create an asset record. Returns the Asset."""
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

    return asset
