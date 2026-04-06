"""Strategy endpoints — calculate risk management strategy for an asset."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.asset import Asset
from app.models.strategy import Strategy
from app.models.user import User
from app.services.quant import calculate_kpis
from app.services.risk_manager import MAX_RISK_PCT, RiskManager

router = APIRouter(prefix="/strategies", tags=["strategies"])

_risk_manager = RiskManager()


# ── Request / Response schemas ────────────────────────────────────────────────

class StrategyRequest(BaseModel):
    ticker: str
    direction: str = Field(pattern="^(LONG|SHORT)$")
    capital: float = Field(gt=0, description="Total account capital in USD")
    risk_pct: float = Field(gt=0, le=MAX_RISK_PCT, description="Fraction to risk (max 0.03)")

    @field_validator("ticker")
    @classmethod
    def upper_ticker(cls, v: str) -> str:
        return v.upper()


class StrategyResponse(BaseModel):
    ticker: str
    direction: str
    entry_price: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3_trailing_atr_mult: float
    n_shares: float
    risk_amount: float
    rr_ratio: float
    is_recommended: bool
    atr_used: float
    sl_atr_mult: float
    tp1_pct: float
    tp2_pct: float
    tp3_pct: float
    warning: str | None
    calculated_at: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/calculate", response_model=StrategyResponse)
async def calculate_strategy(
    body: StrategyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Calculate entry, SL, TP1/TP2/TP3, position size and R:R for a ticker."""

    # Resolve asset
    result = await db.execute(select(Asset).where(Asset.ticker == body.ticker))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found. Load it first.")

    # Get current KPIs (need ATR)
    kpis = await calculate_kpis(body.ticker, str(asset.id), db)
    if "error" in kpis:
        raise HTTPException(status_code=422, detail=kpis["error"])

    atr_value: float = kpis["atr_value"]
    entry_price: float = kpis["current_price"]

    # Calculate strategy
    try:
        strat = _risk_manager.calculate_strategy(
            ticker=body.ticker,
            direction=body.direction,
            capital=body.capital,
            risk_pct=body.risk_pct,
            entry_price=entry_price,
            atr_value=atr_value,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None

    # Persist to DB
    now = datetime.now(UTC)
    db.add(
        Strategy(
            user_id=current_user.id,
            asset_id=asset.id,
            ticker=body.ticker,
            direction=strat.direction,
            capital=body.capital,
            risk_pct=body.risk_pct,
            entry_price=strat.entry_price,
            stop_loss=strat.stop_loss,
            tp1=strat.tp1,
            tp2=strat.tp2,
            tp3_trailing_atr_mult=strat.tp3_trailing_atr_mult,
            n_shares=strat.n_shares,
            risk_amount=strat.risk_amount,
            rr_ratio=strat.rr_ratio,
            atr_used=strat.atr_used,
            is_recommended=strat.is_recommended,
            warning=strat.warning,
            calculated_at=now,
        )
    )
    await db.flush()

    return StrategyResponse(
        ticker=strat.ticker,
        direction=strat.direction,
        entry_price=strat.entry_price,
        stop_loss=strat.stop_loss,
        tp1=strat.tp1,
        tp2=strat.tp2,
        tp3_trailing_atr_mult=strat.tp3_trailing_atr_mult,
        n_shares=strat.n_shares,
        risk_amount=strat.risk_amount,
        rr_ratio=strat.rr_ratio,
        is_recommended=strat.is_recommended,
        atr_used=strat.atr_used,
        sl_atr_mult=strat.sl_atr_mult,
        tp1_pct=strat.tp1_pct,
        tp2_pct=strat.tp2_pct,
        tp3_pct=strat.tp3_pct,
        warning=strat.warning,
        calculated_at=now.isoformat(),
    )


@router.get("/{ticker}/last", response_model=StrategyResponse)
async def get_last_strategy(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StrategyResponse:
    """Get the last calculated strategy for a ticker by the current user."""
    ticker = ticker.upper()

    result = await db.execute(
        select(Strategy)
        .where(Strategy.ticker == ticker, Strategy.user_id == current_user.id)
        .order_by(Strategy.calculated_at.desc())
        .limit(1)
    )
    strat = result.scalar_one_or_none()
    if strat is None:
        raise HTTPException(status_code=404, detail="No strategy found for this ticker")

    return StrategyResponse(
        ticker=strat.ticker,
        direction=strat.direction,
        entry_price=strat.entry_price,
        stop_loss=strat.stop_loss,
        tp1=strat.tp1,
        tp2=strat.tp2,
        tp3_trailing_atr_mult=strat.tp3_trailing_atr_mult,
        n_shares=strat.n_shares,
        risk_amount=strat.risk_amount,
        rr_ratio=strat.rr_ratio,
        is_recommended=strat.is_recommended,
        atr_used=strat.atr_used,
        sl_atr_mult=2.5,
        tp1_pct=33.0,
        tp2_pct=33.0,
        tp3_pct=34.0,
        warning=strat.warning,
        calculated_at=strat.calculated_at.isoformat(),
    )
