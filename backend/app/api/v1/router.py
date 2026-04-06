"""V1 API router — aggregates all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.kpis import router as kpis_router
from app.api.v1.macro import router as macro_router
from app.api.v1.oscillators import router as oscillators_router
from app.api.v1.strategies import router as strategies_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(assets_router)
api_router.include_router(macro_router)
api_router.include_router(kpis_router)
api_router.include_router(oscillators_router)
api_router.include_router(strategies_router)
