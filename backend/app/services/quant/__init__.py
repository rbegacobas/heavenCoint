"""Quant Engine — KPI calculator service.

Computes ATR, SMA, volatility, momentum, trend directions,
confidence ranges, and persists KPI snapshots to DB + Redis.
"""

import math
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.models.kpi_snapshot import KpiSnapshot
from app.models.oscillator_data import OscillatorData
from app.models.price_history import PriceHistory
from app.services.quant.oscillators import (
    OscillatorResult,
    calculate_intentions,
    calculate_netbrute,
    detect_divergence,
)


async def calculate_kpis(ticker: str, asset_id: str, db: AsyncSession) -> dict:
    """Calculate all KPIs for an asset from its price history.

    Returns a dict of computed KPIs (also persisted to DB + Redis).
    """
    # Fetch last 250 bars (need 200 for SMA + buffer)
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.asset_id == asset_id)
        .order_by(PriceHistory.time.asc())
        .limit(250)
    )
    bars = list(result.scalars())

    if len(bars) < 2:
        return {"error": "Insufficient data", "bars_available": len(bars)}

    closes = [float(b.close) for b in bars]
    highs = [float(b.high) for b in bars]
    lows = [float(b.low) for b in bars]
    volumes = [float(b.volume) for b in bars]

    current_price = closes[-1]

    # --- ATR (Average True Range, 14-period) ---
    atr_period = 14
    atr_value = _calculate_atr(highs, lows, closes, atr_period)

    # --- Simple Moving Averages ---
    sma_50 = _sma(closes, 50)
    sma_134 = _sma(closes, 134)
    sma_200 = _sma(closes, 200)

    # --- Trends from SMAs ---
    trend_50d = _trend_from_sma(current_price, sma_50)
    trend_134d = _trend_from_sma(current_price, sma_134)
    trend_200d = _trend_from_sma(current_price, sma_200)
    trend_divergence = (
        len({trend_50d, trend_134d, trend_200d} - {None}) > 1
        and len({t for t in [trend_50d, trend_134d, trend_200d] if t is not None}) > 1
    )

    # --- Volatility (21-day log returns std dev, annualized) ---
    volatility_implied = _calculate_volatility(closes, 21)

    # Volatility change vs 7 days ago
    vol_7d_ago = _calculate_volatility(closes[:-7], 21) if len(closes) > 28 else None
    volatility_change_pct = None
    if vol_7d_ago and vol_7d_ago > 0:
        volatility_change_pct = ((volatility_implied - vol_7d_ago) / vol_7d_ago) * 100

    # Volatility state
    volatility_state = "stable"
    if volatility_change_pct is not None:
        if volatility_change_pct > 10:
            volatility_state = "expansion"
        elif volatility_change_pct < -10:
            volatility_state = "contraction"

    # --- Confidence Range (95%) ---
    daily_std = _daily_std(closes, 21)
    if daily_std:
        price_range_low_95 = current_price - (1.96 * daily_std * current_price / 100)
        price_range_high_95 = current_price + (1.96 * daily_std * current_price / 100)
    else:
        price_range_low_95 = None
        price_range_high_95 = None

    # --- Momentum (12-period rate of change) ---
    momentum_value = None
    momentum_class = "NEUTRAL"
    if len(closes) >= 13:
        momentum_value = closes[-1] - closes[-13]
        if momentum_value > 0:
            momentum_class = "POSITIVE"
        elif momentum_value < 0:
            momentum_class = "NEGATIVE"

    # --- Oscillators (M3) ---
    netbrute: OscillatorResult = calculate_netbrute(highs, lows, closes, volumes)
    intentions: OscillatorResult = calculate_intentions(closes)
    oscillator_divergence = detect_divergence(netbrute, intentions)

    # --- Build KPI dict ---
    kpis = {
        "current_price": current_price,
        "atr_value": atr_value,
        "atr_period": atr_period,
        "volatility_implied": volatility_implied,
        "volatility_change_pct": volatility_change_pct,
        "volatility_state": volatility_state,
        "price_range_low_95": price_range_low_95,
        "price_range_high_95": price_range_high_95,
        "momentum_value": momentum_value,
        "momentum_class": momentum_class,
        "trend_200d": trend_200d,
        "trend_134d": trend_134d,
        "trend_50d": trend_50d,
        "trend_divergence": trend_divergence,
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
        "oscillator_divergence": oscillator_divergence,
    }

    # --- Persist to DB ---
    snapshot = KpiSnapshot(
        time=datetime.now(UTC),
        asset_id=asset_id,
        current_price=Decimal(str(current_price)),
        atr_value=Decimal(str(round(atr_value, 8))),
        atr_period=atr_period,
        volatility_implied=(
            Decimal(str(round(volatility_implied, 4))) if volatility_implied else None
        ),
        volatility_change_pct=(
            Decimal(str(round(volatility_change_pct, 4)))
            if volatility_change_pct is not None
            else None
        ),
        volatility_state=volatility_state,
        price_range_low_95=(
            Decimal(str(round(price_range_low_95, 8))) if price_range_low_95 is not None else None
        ),
        price_range_high_95=(
            Decimal(str(round(price_range_high_95, 8))) if price_range_high_95 is not None else None
        ),
        momentum_value=(
            Decimal(str(round(momentum_value, 4))) if momentum_value is not None else None
        ),
        momentum_class=momentum_class,
        trend_200d=trend_200d,
        trend_134d=trend_134d,
        trend_50d=trend_50d,
        trend_divergence=trend_divergence,
    )
    db.add(snapshot)

    # --- Persist oscillators to DB ---
    now_utc = datetime.now(UTC)
    for osc_type, osc in (("NETBRUTE", netbrute), ("INTENTIONS", intentions)):
        db.add(
            OscillatorData(
                time=now_utc,
                asset_id=asset_id,
                oscillator_type=osc_type,
                value=Decimal(str(round(osc.value, 4))),
                cross_type=osc.cross_type,
                zone=osc.zone,
                observation=osc.observation,
                confidence_level=Decimal(str(round(osc.confidence_level, 2))),
            )
        )

    await db.flush()

    # --- Cache in Redis ---
    redis_data: dict[str, str] = {
        "current_price": str(current_price),
        "atr_value": str(round(atr_value, 8)),
        "atr_period": str(atr_period),
        "volatility_state": volatility_state,
        "momentum_class": momentum_class,
        "trend_divergence": str(trend_divergence).lower(),
        "last_updated": datetime.now(UTC).isoformat(),
    }
    # Add optional fields
    for key in [
        "volatility_implied",
        "volatility_change_pct",
        "price_range_low_95",
        "price_range_high_95",
        "momentum_value",
        "trend_200d",
        "trend_134d",
        "trend_50d",
    ]:
        val = kpis.get(key)
        if val is not None:
            redis_data[key] = str(round(val, 8)) if isinstance(val, int | float) else str(val)

    # Oscillator fields
    redis_data["netbrute_value"] = str(netbrute.value)
    redis_data["netbrute_cross"] = netbrute.cross_type
    redis_data["netbrute_zone"] = netbrute.zone
    redis_data["netbrute_observation"] = netbrute.observation
    redis_data["netbrute_confidence"] = str(netbrute.confidence_level)
    redis_data["intentions_value"] = str(intentions.value)
    redis_data["intentions_cross"] = intentions.cross_type
    redis_data["intentions_zone"] = intentions.zone
    redis_data["intentions_observation"] = intentions.observation
    redis_data["intentions_confidence"] = str(intentions.confidence_level)
    redis_data["oscillator_divergence"] = str(oscillator_divergence).lower()

    await redis_client.hset(f"kpi:{ticker}", mapping=redis_data)
    await redis_client.expire(f"kpi:{ticker}", 60)  # 60s TTL

    return kpis


# ─── Pure calculation helpers ────────────────────────────────────


def _sma(values: list[float], period: int) -> float | None:
    """Simple Moving Average. Returns None if not enough data."""
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def _calculate_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14,
) -> float:
    """Average True Range over `period` bars."""
    true_ranges: list[float] = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0

    # Use SMA for initial ATR, then EMA-style smoothing
    atr = sum(true_ranges[:period]) / period
    for tr in true_ranges[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def _calculate_volatility(closes: list[float], window: int = 21) -> float | None:
    """Annualized volatility from log returns (std dev * sqrt(252))."""
    if len(closes) < window + 1:
        return None
    log_returns = [
        math.log(closes[i] / closes[i - 1])
        for i in range(len(closes) - window, len(closes))
        if closes[i - 1] > 0
    ]
    if len(log_returns) < 2:
        return None
    mean = sum(log_returns) / len(log_returns)
    variance = sum((r - mean) ** 2 for r in log_returns) / (len(log_returns) - 1)
    daily_vol = math.sqrt(variance)
    return daily_vol * math.sqrt(252) * 100  # Annualized percentage


def _daily_std(closes: list[float], window: int = 21) -> float | None:
    """Daily standard deviation of percentage returns."""
    if len(closes) < window + 1:
        return None
    pct_returns = [
        (closes[i] - closes[i - 1]) / closes[i - 1] * 100
        for i in range(len(closes) - window, len(closes))
        if closes[i - 1] > 0
    ]
    if len(pct_returns) < 2:
        return None
    mean = sum(pct_returns) / len(pct_returns)
    variance = sum((r - mean) ** 2 for r in pct_returns) / (len(pct_returns) - 1)
    return math.sqrt(variance)


def _trend_from_sma(price: float, sma: float | None) -> str | None:
    """Determine trend direction from price vs SMA.

    Returns "UP", "DOWN", or "SIDEWAYS" to match frontend TrendDirection enum.
    """
    if sma is None:
        return None
    ratio = price / sma
    if ratio > 1.01:
        return "UP"
    elif ratio < 0.99:
        return "DOWN"
    return "SIDEWAYS"
