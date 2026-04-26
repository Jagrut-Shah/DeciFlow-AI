"""
API v1 Router — Mounts all versioned endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.decisions import router as decisions_router
from app.api.v1.endpoints.pipeline import router as pipeline_router
from app.api.v1.endpoints.system import router as system_router
from app.api.v1.endpoints.simulation import router as simulation_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.data import router as data_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(decisions_router, prefix="/decisions", tags=["Decisions"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(simulation_router, prefix="/simulation", tags=["Simulation"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(data_router, prefix="/data", tags=["Data"])
