"""Health check endpoint — verifies DB + Redis connectivity."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_factory
from app.core.redis import redis_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    checks: dict[str, str] = {}

    # PostgreSQL
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    # Redis
    try:
        pong = await redis_client.ping()
        checks["redis"] = "ok" if pong else "error"
    except Exception:
        checks["redis"] = "error"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }
