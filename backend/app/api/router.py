"""Central API router.

All feature routers are aggregated here and mounted under ``settings.API_STR``.
"""

from fastapi import APIRouter

from app.api.routes import auth, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
