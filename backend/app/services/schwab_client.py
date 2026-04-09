"""Schwab / Thinkorswim API client.

Handles OAuth2 authentication and provides methods for:
- Market data (quotes, price history)
- Order management (preview, place, cancel, list)

Token lifecycle:
  - Access token:  30 minutes (auto-refreshed transparently)
  - Refresh token: 7 days (requires manual re-login after expiry)

Tokens are persisted in Redis under key "schwab:token" so they survive
backend restarts without requiring re-authentication.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

import schwab
from schwab.auth import Client

from app.core.config import settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

REDIS_TOKEN_KEY = "schwab:token"
REDIS_TOKEN_TTL = 7 * 24 * 3600  # 7 days (refresh token lifetime)


# ── Token persistence helpers ─────────────────────────────────────────────────

async def _save_token(token: dict) -> None:
    """Persist token dict to Redis."""
    await redis_client.set(REDIS_TOKEN_KEY, json.dumps(token), ex=REDIS_TOKEN_TTL)


async def _load_token() -> dict | None:
    """Load token dict from Redis. Returns None if not found."""
    raw = await redis_client.get(REDIS_TOKEN_KEY)
    if raw is None:
        return None
    return json.loads(raw)


async def _delete_token() -> None:
    await redis_client.delete(REDIS_TOKEN_KEY)


# ── Client factory ────────────────────────────────────────────────────────────

async def get_schwab_client() -> Client | None:
    """Return an authenticated Schwab client, or None if not authenticated.

    Loads the saved token from Redis and creates a client with automatic
    token refresh. Returns None if no token is stored yet.
    """
    token = await _load_token()
    if token is None:
        return None

    try:
        client = schwab.auth.client_from_token_file(
            token_path=None,  # we manage tokens ourselves
            api_key=settings.schwab_app_key,
            app_secret=settings.schwab_secret,
            token=token,
            token_write_func=lambda t: _save_token_sync(t),
        )
        return client
    except Exception as exc:
        logger.warning("Failed to create Schwab client from token: %s", exc)
        return None


def _save_token_sync(token: dict) -> None:
    """Synchronous token write callback required by schwab-py internals.

    schwab-py calls this synchronously on every token refresh. We schedule
    the async Redis write as a fire-and-forget background task.
    """
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_save_token(token))
    except RuntimeError:
        # No running loop (shouldn't happen in FastAPI context)
        asyncio.run(_save_token(token))


# ── OAuth2 flow ───────────────────────────────────────────────────────────────

def get_auth_url() -> str:
    """Return the Schwab OAuth2 authorization URL.

    The user must open this URL in their browser, log in with their
    Schwab/Thinkorswim credentials, and then be redirected to the
    callback URL with an authorization code.
    """
    oauth = schwab.auth.OAuth2Client(
        client_id=settings.schwab_app_key,
        client_secret=settings.schwab_secret,
    )
    url, _ = oauth.create_authorization_url(
        "https://api.schwabapi.com/v1/oauth/authorize",
        redirect_uri=settings.schwab_callback_url,
    )
    return url


async def exchange_code_for_token(redirected_url: str) -> dict:
    """Exchange the OAuth2 authorization code for access + refresh tokens.

    Args:
        redirected_url: The full callback URL that Schwab redirected to,
                        e.g. "https://127.0.0.1?code=xxx&session=yyy"

    Returns:
        Token dict with access_token, refresh_token, expiry info.

    Raises:
        ValueError: If the exchange fails.
    """
    try:
        client = await schwab.auth.client_from_received_url_async(
            api_key=settings.schwab_app_key,
            app_secret=settings.schwab_secret,
            callback_url=settings.schwab_callback_url,
            received_url=redirected_url,
            token_write_func=_save_token,
        )
        token = await _load_token()
        return token or {}
    except Exception as exc:
        raise ValueError(f"Token exchange failed: {exc}") from exc


# ── Status ────────────────────────────────────────────────────────────────────

async def get_connection_status() -> dict[str, Any]:
    """Return current Schwab connection status.

    Returns a dict with:
      - connected: bool
      - token_age_days: float | None
      - refresh_expires_in_days: float | None
      - needs_relogin: bool
    """
    token = await _load_token()
    if token is None:
        return {
            "connected": False,
            "token_age_days": None,
            "refresh_expires_in_days": None,
            "needs_relogin": True,
        }

    # schwab-py stores creation_timestamp in the token metadata
    creation_ts = token.get("creation_timestamp")
    if creation_ts:
        age_seconds = datetime.now(UTC).timestamp() - creation_ts
        age_days = age_seconds / 86400
        remaining_days = max(0.0, 7.0 - age_days)
    else:
        age_days = None
        remaining_days = None

    needs_relogin = remaining_days is not None and remaining_days < 0.5

    return {
        "connected": True,
        "token_age_days": round(age_days, 2) if age_days is not None else None,
        "refresh_expires_in_days": round(remaining_days, 2) if remaining_days is not None else None,
        "needs_relogin": needs_relogin,
    }


# ── Market data ───────────────────────────────────────────────────────────────

async def get_quote(ticker: str) -> dict[str, Any] | None:
    """Fetch real-time quote for a ticker from Schwab.

    Returns None if not authenticated or ticker not found.
    """
    client = await get_schwab_client()
    if client is None:
        return None

    try:
        resp = await client.get_quote(ticker)
        resp.raise_for_status()
        data = resp.json()
        quote = data.get(ticker, {})
        ref = quote.get("reference", {})
        quote_data = quote.get("quote", {})
        return {
            "ticker": ticker,
            "last": quote_data.get("lastPrice"),
            "bid": quote_data.get("bidPrice"),
            "ask": quote_data.get("askPrice"),
            "volume": quote_data.get("totalVolume"),
            "open": quote_data.get("openPrice"),
            "high": quote_data.get("highPrice"),
            "low": quote_data.get("lowPrice"),
            "close": quote_data.get("closePrice"),
            "description": ref.get("description"),
            "exchange": ref.get("exchange"),
        }
    except Exception as exc:
        logger.warning("Schwab get_quote(%s) failed: %s", ticker, exc)
        return None


async def get_price_history(
    ticker: str,
    period_type: str = "year",
    period: int = 1,
    frequency_type: str = "daily",
    frequency: int = 1,
) -> list[dict] | None:
    """Fetch OHLCV daily bars from Schwab.

    Returns list of bars in format compatible with existing ingestion pipeline:
    [{"t": ms_timestamp, "o": open, "h": high, "l": low, "c": close, "v": volume}]

    Returns None if not authenticated.
    """
    client = await get_schwab_client()
    if client is None:
        return None

    try:
        pt = Client.PriceHistory.PeriodType[period_type.upper()]
        ft = Client.PriceHistory.FrequencyType[frequency_type.upper()]

        resp = await client.get_price_history(
            ticker,
            period_type=pt,
            period=period,
            frequency_type=ft,
            frequency=frequency,
            need_extended_hours_data=False,
        )
        resp.raise_for_status()
        raw = resp.json()

        candles = raw.get("candles", [])
        return [
            {
                "t": c["datetime"],  # already in ms
                "o": c["open"],
                "h": c["high"],
                "l": c["low"],
                "c": c["close"],
                "v": c["volume"],
            }
            for c in candles
        ]
    except Exception as exc:
        logger.warning("Schwab get_price_history(%s) failed: %s", ticker, exc)
        return None
