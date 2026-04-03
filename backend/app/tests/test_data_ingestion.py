"""Tests for data ingestion module — assets, price history, macro indicators."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# All tests mock redis_client to avoid needing a running Redis instance
_redis_mock = AsyncMock()
_redis_mock.hgetall.return_value = {}
_redis_mock.hset.return_value = None
_redis_mock.set.return_value = None
_redis_mock.expire.return_value = None


def _patch_redis():
    """Patch redis_client everywhere it's imported."""
    return patch.multiple(
        "",
        **{},
    )


@pytest.fixture(autouse=True)
def mock_redis():
    """Auto-mock redis_client for all tests in this module."""
    with (
        patch("app.core.redis.redis_client", _redis_mock),
        patch("app.api.v1.macro.redis_client", _redis_mock),
        patch("app.services.market_data.ingestion.redis_client", _redis_mock),
    ):
        _redis_mock.reset_mock()
        _redis_mock.hgetall.return_value = {}
        yield _redis_mock


async def _get_auth_headers(client: AsyncClient, email: str) -> dict:
    """Helper — register + login and return auth headers."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Test@1234", "full_name": "Tester"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Test@1234"},
    )
    return {"Authorization": f"Bearer {login_resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_search_assets_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/assets/search?q=AAPL")
    assert resp.status_code == 403  # No Bearer token


@pytest.mark.asyncio
async def test_search_assets_external(client: AsyncClient) -> None:
    headers = await _get_auth_headers(client, "search@test.com")

    with (
        patch(
            "app.api.v1.assets.search_stock_tickers",
            new_callable=AsyncMock,
            return_value=[
                {
                    "ticker": "AAPL",
                    "name": "Apple Inc.",
                    "exchange": "XNAS",
                    "type": "stock",
                }
            ],
        ),
        patch(
            "app.api.v1.assets.search_crypto_tickers",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        resp = await client.get("/api/v1/assets/search?q=AAPL", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        assert data["results"][0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_load_asset_not_found(client: AsyncClient) -> None:
    headers = await _get_auth_headers(client, "loader@test.com")
    resp = await client.post("/api/v1/assets/FAKE999/load", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_load_asset_and_get_prices(client: AsyncClient) -> None:
    """Test loading an asset with mocked market data, then reading prices."""
    headers = await _get_auth_headers(client, "load2@test.com")

    # Create the asset via search (mocked external API)
    with (
        patch(
            "app.api.v1.assets.search_stock_tickers",
            new_callable=AsyncMock,
            return_value=[
                {
                    "ticker": "MSFT",
                    "name": "Microsoft Corp.",
                    "exchange": "XNAS",
                    "type": "stock",
                }
            ],
        ),
        patch(
            "app.api.v1.assets.search_crypto_tickers",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        await client.get("/api/v1/assets/search?q=MSFT", headers=headers)

    # Load asset with mocked price data
    mock_bars = [
        {"t": 1711929600000, "o": 420.5, "h": 425.0, "l": 418.0, "c": 423.2, "v": 1000000},
        {"t": 1712016000000, "o": 423.2, "h": 428.0, "l": 422.0, "c": 427.1, "v": 1100000},
    ]
    with patch(
        "app.services.market_data.ingestion.fetch_stock_bars",
        new_callable=AsyncMock,
        return_value=mock_bars,
    ):
        resp = await client.post("/api/v1/assets/MSFT/load", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ticker"] == "MSFT"
        assert data["status"] == "loaded"
        assert "2" in data["message"]

    # Verify prices are persisted and retrievable
    resp = await client.get("/api/v1/assets/MSFT/prices", headers=headers)
    assert resp.status_code == 200
    prices = resp.json()
    assert len(prices) == 2
    assert float(prices[0]["close"]) == pytest.approx(423.2, abs=0.01)


@pytest.mark.asyncio
async def test_macro_indicators_empty(client: AsyncClient) -> None:
    """Test macro endpoint returns empty indicators from clean DB."""
    headers = await _get_auth_headers(client, "macro@test.com")
    resp = await client.get("/api/v1/macro", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "database"


@pytest.mark.asyncio
async def test_macro_refresh(client: AsyncClient) -> None:
    """Test macro refresh with mocked FRED data."""
    headers = await _get_auth_headers(client, "macro2@test.com")

    mock_indicators = {
        "T10Y2Y": {
            "indicator_code": "T10Y2Y",
            "indicator_name": "10-Year Treasury Constant Maturity Minus 2-Year",
            "value": -0.42,
            "previous_value": -0.38,
            "direction": "falling",
            "published_at": "2024-04-01T00:00:00",
        }
    }
    with patch(
        "app.services.market_data.ingestion.fetch_all_indicators",
        new_callable=AsyncMock,
        return_value=mock_indicators,
    ):
        resp = await client.post("/api/v1/macro/refresh", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["indicators_updated"] == 1
