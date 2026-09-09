"""
Health Endpoint
"""

import time
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()
START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API Health & Readiness",
    description="Check the operational health and frozen model version of the WaterTwin API.",
)
async def get_health() -> HealthResponse:
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        model_version=settings.MODEL_VERSION,
        mode=settings.DATA_MODE,
        stage=settings.STAGE_STATUS,
        uptime_seconds=round(uptime, 2),
    )
