"""KPI endpoints — get computed quantitative metrics for an asset."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.redis import redis_client
from app.models.asset import Asset
from app.models.user import User
from app.services.quant import calculate_kpis

router = APIRouter(prefix="/kpis", tags=["kpis"])


@router.get("/{ticker}")
async def get_kpis(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Get current KPIs for a ticker. Reads from Redis, recalculates if stale."""
    ticker = ticker.upper()

    # Try Redis cache first (must have full KPI data, not just ingestion partial cache)
    cached = await redis_client.hgetall(f"kpi:{ticker}")
    if cached and "atr_value" in cached:
        return {
            "ticker": ticker,
            "source": "cache",
            "is_stale": False,
            "price": {
                "current": float(cached["current_price"]),
                "range_low_95": float(cached.get("price_range_low_95", 0)),
                "range_high_95": float(cached.get("price_range_high_95", 0)),
            },
            "atr": {
                "value": float(cached["atr_value"]),
                "period": int(cached["atr_period"]),
            },
            "volatility": {
                "implied": float(cached.get("volatility_implied", 0)),
                "change_pct": float(cached.get("volatility_change_pct", 0)),
                "state": cached["volatility_state"],
            },
            "momentum": {
                "value": float(cached.get("momentum_value", 0)),
                "class": cached["momentum_class"],
            },
            "trends": {
                "d200": cached.get("trend_200d"),
                "d134": cached.get("trend_134d"),
                "d50": cached.get("trend_50d"),
                "divergence": cached["trend_divergence"] == "true",
            },
            "last_updated": cached.get("last_updated"),
            "data_source": cached.get("data_source", "unknown"),
        }

    # Not cached — compute from DB
    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    kpis = await calculate_kpis(ticker, str(asset.id), db)

    if "error" in kpis:
        raise HTTPException(status_code=422, detail=kpis["error"])

    return {
        "ticker": ticker,
        "source": "calculated",
        "is_stale": False,
        "price": {
            "current": kpis["current_price"],
            "range_low_95": kpis.get("price_range_low_95"),
            "range_high_95": kpis.get("price_range_high_95"),
        },
        "atr": {
            "value": kpis["atr_value"],
            "period": kpis["atr_period"],
        },
        "volatility": {
            "implied": kpis.get("volatility_implied"),
            "change_pct": kpis.get("volatility_change_pct"),
            "state": kpis["volatility_state"],
        },
        "momentum": {
            "value": kpis.get("momentum_value"),
            "class": kpis["momentum_class"],
        },
        "trends": {
            "d200": kpis.get("trend_200d"),
            "d134": kpis.get("trend_134d"),
            "d50": kpis.get("trend_50d"),
            "divergence": kpis["trend_divergence"],
        },
        "data_source": kpis.get("data_source", "yfinance"),
    }


@router.post("/{ticker}/refresh")
async def refresh_kpis(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Force recalculation of KPIs for a ticker."""
    ticker = ticker.upper()

    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    kpis = await calculate_kpis(ticker, str(asset.id), db)

    if "error" in kpis:
        raise HTTPException(status_code=422, detail=kpis["error"])

    return {"ticker": ticker, "status": "recalculated", "kpis": kpis}
