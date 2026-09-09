"""
Maintenance API Endpoints
Provides decision-support cleaning recommendations and historical CIP logs.
"""

from fastapi import APIRouter, Depends
from app.schemas.maintenance import (
    MaintenanceHistoryResponse,
    MaintenanceRecommendationResponse,
)
from app.services.maintenance_service import (
    MaintenanceService,
    maintenance_service,
)

router = APIRouter()


@router.get(
    "/recommendation",
    response_model=MaintenanceRecommendationResponse,
    summary="Predictive Maintenance Recommendation",
    description="Returns decision-support cleaning action (CLEAN, CONTINUE, MONITOR) based on Stage 8C predictive optimization.",
)
async def get_maintenance_recommendation(
    service: MaintenanceService = Depends(lambda: maintenance_service),
) -> MaintenanceRecommendationResponse:
    return service.get_recommendation()


@router.get(
    "/history",
    response_model=MaintenanceHistoryResponse,
    summary="Maintenance & CIP History",
    description="Returns historical CIP cleaning records, downtime, and restoration statistics.",
)
async def get_maintenance_history(
    service: MaintenanceService = Depends(lambda: maintenance_service),
) -> MaintenanceHistoryResponse:
    return service.get_history()
