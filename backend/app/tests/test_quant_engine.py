"""Tests for M2 Quant Engine — KPI calculations and endpoints."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.services.quant import (
    _calculate_atr,
    _calculate_volatility,
    _sma,
    _trend_from_sma,
)

# Redis mock
_redis_mock = AsyncMock()
_redis_mock.hgetall.return_value = {}
_redis_mock.hset.return_value = None
_redis_mock.set.return_value = None
_redis_mock.expire.return_value = None


@pytest.fixture(autouse=True)
def mock_redis():
    with (
        patch("app.core.redis.redis_client", _redis_mock),
        patch("app.api.v1.kpis.redis_client", _redis_mock),
        patch("app.services.quant.redis_client", _redis_mock),
    ):
        _redis_mock.reset_mock()
        _redis_mock.hgetall.return_value = {}
        yield _redis_mock


async def _get_auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Test@1234", "full_name": "Tester"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Test@1234"},
    )
    return {"Authorization": f"Bearer {login_resp.json()['access_token']}"}


async def _create_asset_with_prices(
    db: AsyncSession, ticker: str = "TEST", num_bars: int = 50
) -> Asset:
    """Insert an asset with synthetic price history for testing."""
    asset = Asset(
        ticker=ticker,
        name=f"{ticker} Corp",
        asset_type="stock",
        exchange="TEST",
        decimal_places=4,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)

    base_price = 100.0
    now = datetime.now(UTC)
    for i in range(num_bars):
        # Simulate slight price movements
        offset = (i % 10) - 5  # oscillates between -5 and +4
        price = base_price + offset + (i * 0.1)
        bar = PriceHistory(
            time=now - timedelta(days=num_bars - i),
            asset_id=asset.id,
            open=Decimal(str(price - 0.5)),
            high=Decimal(str(price + 1.0)),
            low=Decimal(str(price - 1.0)),
            close=Decimal(str(price)),
            volume=1000000 + i * 1000,
            source="test",
        )
        db.add(bar)
    await db.flush()

    return asset


# ─── Unit tests for pure calculation helpers ─────────────────


def test_sma_basic():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert _sma(values, 3) == pytest.approx(40.0)  # (30+40+50)/3
    assert _sma(values, 5) == pytest.approx(30.0)


def test_sma_insufficient_data():
    assert _sma([10.0, 20.0], 5) is None


def test_atr_basic():
    highs = [110.0, 112.0, 111.0, 113.0, 115.0]
    lows = [100.0, 102.0, 101.0, 103.0, 105.0]
    closes = [105.0, 108.0, 106.0, 110.0, 112.0]
    atr = _calculate_atr(highs, lows, closes, period=3)
    assert atr > 0


def test_volatility_basic():
    # 30 prices with slight variations
    closes = [100.0 + (i * 0.1) for i in range(30)]
    vol = _calculate_volatility(closes, window=21)
    assert vol is not None
    assert vol > 0


def test_volatility_insufficient_data():
    assert _calculate_volatility([100.0, 101.0], window=21) is None


def test_trend_from_sma():
    assert _trend_from_sma(110.0, 100.0) == "bullish"
    assert _trend_from_sma(90.0, 100.0) == "bearish"
    assert _trend_from_sma(100.5, 100.0) == "neutral"
    assert _trend_from_sma(100.0, None) is None


# ─── Integration tests ───────────────────────────────────────


@pytest.mark.asyncio
async def test_kpi_endpoint_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/kpis/AAPL")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_kpi_endpoint_not_found(client: AsyncClient) -> None:
    headers = await _get_auth_headers(client, "kpi1@test.com")
    resp = await client.get("/api/v1/kpis/NONEXIST", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_kpi_calculation(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test full KPI calculation with synthetic data."""
    headers = await _get_auth_headers(client, "kpi2@test.com")

    # Create asset with enough price history
    asset = await _create_asset_with_prices(db_session, "KPITEST", num_bars=50)

    resp = await client.get(f"/api/v1/kpis/{asset.ticker}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["ticker"] == "KPITEST"
    assert data["source"] == "calculated"
    assert "price" in data
    assert data["price"]["current"] > 0
    assert "atr" in data
    assert data["atr"]["value"] > 0
    assert data["atr"]["period"] == 14
    assert "volatility" in data
    assert data["volatility"]["state"] in ("expansion", "contraction", "stable")
    assert "momentum" in data
    assert data["momentum"]["class"] in ("positive", "negative", "neutral")
    assert "trends" in data

    # Verify Redis was called to cache the KPI
    _redis_mock.hset.assert_called()


@pytest.mark.asyncio
async def test_kpi_refresh(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test force recalculation of KPIs."""
    headers = await _get_auth_headers(client, "kpi3@test.com")
    asset = await _create_asset_with_prices(db_session, "REFTEST", num_bars=30)

    resp = await client.post(f"/api/v1/kpis/{asset.ticker}/refresh", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "REFTEST"
    assert data["status"] == "recalculated"
    assert "kpis" in data
    assert data["kpis"]["current_price"] > 0
