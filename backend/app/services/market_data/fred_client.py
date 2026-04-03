"""FRED client — Federal Reserve Economic Data (macro indicators)."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

FRED_BASE = "https://api.stlouisfed.org/fred"

# Key indicators for the platform
INDICATOR_SERIES = {
    "T10Y2Y": "Treasury 10Y-2Y Spread (Recession Indicator)",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index (CPI)",
    "GDP": "Gross Domestic Product",
    "FEDFUNDS": "Federal Funds Rate",
    "DGS10": "10-Year Treasury Yield",
    "UMCSENT": "Consumer Sentiment Index",
    "DCOILWTICO": "WTI Crude Oil Price",
}


async def fetch_series_latest(series_id: str, limit: int = 2) -> list[dict]:
    """Fetch latest observations for a FRED series.

    Returns list of dicts with keys: date, value.
    """
    url = f"{FRED_BASE}/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    observations = data.get("observations", [])
    return [
        {
            "date": obs["date"],
            "value": float(obs["value"]) if obs["value"] != "." else None,
        }
        for obs in observations
    ]


async def fetch_all_indicators() -> dict[str, dict]:
    """Fetch latest values for all key macro indicators.

    Returns dict keyed by series_id with name, value, previous_value, direction.
    """
    results: dict[str, dict] = {}

    for series_id, name in INDICATOR_SERIES.items():
        try:
            obs = await fetch_series_latest(series_id, limit=2)
            if not obs or obs[0]["value"] is None:
                continue

            current = obs[0]["value"]
            previous = obs[1]["value"] if len(obs) > 1 and obs[1]["value"] is not None else None

            if previous is not None:
                if current > previous:
                    direction = "positive"
                elif current < previous:
                    direction = "negative"
                else:
                    direction = "stable"
            else:
                direction = "stable"

            results[series_id] = {
                "indicator_code": series_id,
                "indicator_name": name,
                "value": current,
                "previous_value": previous,
                "direction": direction,
                "published_at": obs[0]["date"],
            }
        except Exception:
            logger.warning("Failed to fetch FRED series %s", series_id)
            continue

    return results
