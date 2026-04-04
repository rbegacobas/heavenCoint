"""Asset endpoints — search, load, get price history."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.models.user import User
from app.schemas.asset import (
    AssetLoadResponse,
    AssetSearchResponse,
    AssetSearchResult,
    PriceBar,
)
from app.services.market_data.binance_client import search_crypto_tickers
from app.services.market_data.ingestion import ensure_asset_exists, ingest_price_data
from app.services.market_data.polygon_client import search_stock_tickers
from app.services.market_data.yfinance_client import search_stock_tickers_yf

router = APIRouter(prefix="/assets", tags=["assets"])

logger = logging.getLogger(__name__)


@router.get("/search", response_model=AssetSearchResponse)
async def search_assets(
    q: str = Query(min_length=1, max_length=20),
    asset_type: str | None = Query(default=None, pattern="^(stock|crypto|etf|forex)$"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Search assets by ticker or name. Queries both local DB and external APIs."""
    results: list[AssetSearchResult] = []

    # 1. Search local DB first
    query = select(Asset).where(
        Asset.is_active.is_(True),
        (Asset.ticker.ilike(f"%{q}%")) | (Asset.name.ilike(f"%{q}%")),
    )
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    query = query.limit(10)

    db_result = await db.execute(query)
    for asset in db_result.scalars():
        results.append(AssetSearchResult.model_validate(asset))

    # 2. If less than 5 local results, also search external APIs
    if len(results) < 5:
        if asset_type in (None, "stock"):
            try:
                external = (
                    await search_stock_tickers(q, limit=5)
                    if settings.polygon_api_key
                    else await search_stock_tickers_yf(q, limit=5)
                )
                for item in external:
                    if not any(r.ticker == item["ticker"] for r in results):
                        # Persist to local DB for future lookups
                        # item["type"] can be "stock", "etf", or "forex"
                        asset = await ensure_asset_exists(
                            ticker=item["ticker"],
                            name=item["name"],
                            asset_type=item.get("type", "stock"),
                            exchange=item.get("exchange"),
                            db=db,
                        )
                        results.append(AssetSearchResult.model_validate(asset))
            except Exception:
                logger.warning("Stock search API failed for query: %s", q)

        if asset_type in (None, "crypto"):
            try:
                external = await search_crypto_tickers(q, limit=5)
                for item in external:
                    if not any(r.ticker == item["ticker"] for r in results):
                        asset = await ensure_asset_exists(
                            ticker=item["ticker"],
                            name=item["name"],
                            asset_type="crypto",
                            exchange="BINANCE",
                            db=db,
                        )
                        results.append(AssetSearchResult.model_validate(asset))
            except Exception:
                logger.warning("Crypto search API failed for query: %s", q)

    return {"results": results[:10], "count": len(results[:10])}


@router.post("/{ticker}/load", response_model=AssetLoadResponse)
async def load_asset(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Load an asset into the dashboard — triggers price data ingestion."""
    ticker = ticker.upper()

    # Find the asset in DB
    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found. Search first with GET /assets/search",
        )

    # Ingest price data
    try:
        bars_count = await ingest_price_data(
            ticker=ticker,
            asset_id=str(asset.id),
            asset_type=asset.asset_type,
            db=db,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch market data: {e}",
        ) from None

    # Store active ticker in Redis user session
    from app.core.redis import redis_client

    await redis_client.set(
        f"session:{current_user.id}",
        f'{{"active_ticker":"{ticker}","asset_id":"{asset.id}"}}',
        ex=86400,  # 24h TTL
    )

    return {
        "ticker": ticker,
        "asset_id": asset.id,
        "status": "loaded",
        "message": f"Loaded {bars_count} new price bars for {ticker}",
    }


@router.get("/{ticker}/prices", response_model=list[PriceBar])
async def get_prices(
    ticker: str,
    limit: int = Query(default=200, le=1000),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[PriceHistory]:
    """Get historical price bars for an asset."""
    ticker = ticker.upper()

    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    prices_result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.asset_id == asset.id)
        .order_by(PriceHistory.time.desc())
        .limit(limit)
    )
    prices = list(prices_result.scalars())
    prices.reverse()  # Chronological order
    return prices
