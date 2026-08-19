"""Central API router.

All feature routers are aggregated here and mounted under ``settings.API_STR``.
"""

from fastapi import APIRouter

from app.api.routes import auth, event, health,inventory

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(event.router, tags=["events"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(support_desk.router, tags=["discussion"])
api_router.include_router(bounty.router, tags=["bounties"])
