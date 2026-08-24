"""Central API router.

All feature routers are aggregated here and mounted under ``settings.API_STR``.
"""

from fastapi import APIRouter

from app.api.routes import ai, auth, bounty, event, health, inventory, student, support_desk

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(student.router, tags=["students"])
api_router.include_router(event.router, tags=["events"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(support_desk.router, tags=["discussion"])
api_router.include_router(bounty.router, tags=["bounties"])
api_router.include_router(ai.router, tags=["ai"])
