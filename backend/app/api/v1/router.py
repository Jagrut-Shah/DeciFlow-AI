"""
API v1 Router — Mounts all versioned endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.decisions import router as decisions_router
from app.api.v1.endpoints.pipeline import router as pipeline_router
from app.api.v1.endpoints.system import router as system_router

api_router = APIRouter()

api_router.include_router(decisions_router, prefix="/decisions", tags=["Decisions"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
