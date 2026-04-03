"""Macro indicators endpoint — fetch and display FRED data."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.redis import redis_client
from app.models.macro_indicator import MacroIndicator
from app.models.user import User
from app.services.market_data.ingestion import ingest_macro_data

router = APIRouter(prefix="/macro", tags=["macro"])


@router.get("")
async def get_macro_indicators(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Get latest macro indicators. Reads from Redis cache, falls back to DB."""
    # Try Redis cache first
    cached = await redis_client.hgetall("macro:latest")
    if cached:
        return {"source": "cache", "indicators": cached}

    # Fallback: fetch from DB (latest of each indicator)
    from sqlalchemy import func

    subq = (
        select(
            MacroIndicator.indicator_code,
            func.max(MacroIndicator.fetched_at).label("max_fetched"),
        )
        .group_by(MacroIndicator.indicator_code)
        .subquery()
    )

    result = await db.execute(
        select(MacroIndicator).join(
            subq,
            (MacroIndicator.indicator_code == subq.c.indicator_code)
            & (MacroIndicator.fetched_at == subq.c.max_fetched),
        )
    )
    indicators = result.scalars().all()

    return {
        "source": "database",
        "indicators": {
            ind.indicator_code: {
                "name": ind.indicator_name,
                "value": float(ind.value),
                "previous_value": float(ind.previous_value) if ind.previous_value else None,
                "direction": ind.direction,
            }
            for ind in indicators
        },
    }


@router.post("/refresh")
async def refresh_macro_data(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Manually trigger a refresh of all FRED macro indicators."""
    count = await ingest_macro_data(db)
    return {"status": "ok", "indicators_updated": count}
