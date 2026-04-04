"""Oscillators endpoint — NetBrute and Intenciones per asset.

Reads from Redis (populated by QuantEngine after /assets/{ticker}/load).
Falls back to recalculating from DB if cache is empty.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.redis import redis_client
from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.models.user import User
from app.services.quant.oscillators import (
    calculate_intentions,
    calculate_netbrute,
    detect_divergence,
)

router = APIRouter(prefix="/oscillators", tags=["oscillators"])


def _oscillator_from_cache(cached: dict, prefix: str) -> dict | None:
    """Extract one oscillator's fields from a Redis hash."""
    key = f"{prefix}_value"
    if key not in cached:
        return None
    return {
        "value": float(cached[key]),
        "cross_type": cached.get(f"{prefix}_cross", "NONE"),
        "zone": cached.get(f"{prefix}_zone", ""),
        "observation": cached.get(f"{prefix}_observation", ""),
        "confidence_level": float(cached.get(f"{prefix}_confidence", 0)),
    }


@router.get("/{ticker}")
async def get_oscillators(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Get NetBrute and Intenciones oscillators for a ticker.

    Reads from Redis cache (populated by /assets/{ticker}/load).
    Recalculates from DB if cache has expired.
    """
    ticker = ticker.upper()

    # Try Redis cache first
    cached = await redis_client.hgetall(f"kpi:{ticker}")
    netbrute_cached = _oscillator_from_cache(cached, "netbrute") if cached else None
    intentions_cached = _oscillator_from_cache(cached, "intentions") if cached else None

    if netbrute_cached and intentions_cached:
        divergence = cached.get("oscillator_divergence", "false") == "true"
        return {
            "ticker": ticker,
            "source": "cache",
            "netbrute": netbrute_cached,
            "intentions": intentions_cached,
            "divergence": divergence,
            "last_updated": cached.get("last_updated"),
        }

    # Not cached — recalculate from DB
    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found. Load it first.")

    bars_result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.asset_id == asset.id)
        .order_by(PriceHistory.time.asc())
        .limit(250)
    )
    bars = list(bars_result.scalars())

    if len(bars) < 15:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient price history ({len(bars)} bars, need at least 15).",
        )

    highs = [float(b.high) for b in bars]
    lows = [float(b.low) for b in bars]
    closes = [float(b.close) for b in bars]
    volumes = [float(b.volume) for b in bars]

    netbrute = calculate_netbrute(highs, lows, closes, volumes)
    intentions = calculate_intentions(closes)
    divergence = detect_divergence(netbrute, intentions)

    return {
        "ticker": ticker,
        "source": "calculated",
        "netbrute": {
            "value": netbrute.value,
            "cross_type": netbrute.cross_type,
            "zone": netbrute.zone,
            "observation": netbrute.observation,
            "confidence_level": netbrute.confidence_level,
        },
        "intentions": {
            "value": intentions.value,
            "cross_type": intentions.cross_type,
            "zone": intentions.zone,
            "observation": intentions.observation,
            "confidence_level": intentions.confidence_level,
        },
        "divergence": divergence,
        "last_updated": None,
    }
