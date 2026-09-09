"""
Membrane Health API Endpoints
Provides authoritative 6-zone EKF estimator states and 15-element visualization mapping.
"""

from fastapi import APIRouter, Depends
from app.schemas.membranes import MembraneElementListResponse, MembraneZoneListResponse
from app.services.membrane_service import MembraneService, membrane_service

router = APIRouter()


@router.get(
    "/zones",
    response_model=MembraneZoneListResponse,
    summary="Authoritative 6-Zone EKF States",
    description="Returns the 6 authoritative axial EKF estimator states (S1 Lead, Mid, Tail; S2 Lead, Mid, Tail).",
)
async def get_membrane_zones(
    service: MembraneService = Depends(lambda: membrane_service),
) -> MembraneZoneListResponse:
    return service.get_membrane_zones()


@router.get(
    "/elements",
    response_model=MembraneElementListResponse,
    summary="15 Membrane Elements (Visualization Mapping)",
    description="Returns 15 individual membrane elements mapped from the authoritative 6-zone EKF estimator.",
)
async def get_membrane_elements(
    service: MembraneService = Depends(lambda: membrane_service),
) -> MembraneElementListResponse:
    return service.get_membrane_elements()
