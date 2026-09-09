"""
Twin API Endpoints
Provides system metadata, current digital twin state, and virtual plant demo clock control.
"""

from fastapi import APIRouter, Depends
from app.schemas.twin import (
    TwinAdvanceRequest,
    TwinAdvanceResponse,
    TwinMetadata,
    TwinResetRequest,
    TwinState,
)
from app.services.twin_service import TwinService, twin_service

router = APIRouter()


@router.get(
    "/metadata",
    response_model=TwinMetadata,
    summary="System Metadata",
    description="Returns frozen model parameters, estimator architecture, and validation status.",
)
async def get_metadata(service: TwinService = Depends(lambda: twin_service)) -> TwinMetadata:
    return service.get_metadata()


@router.get(
    "/state",
    response_model=TwinState,
    summary="Current Digital Twin State",
    description="Returns full telemetry, flows, pressures, water qualities, and membrane health metrics.",
)
async def get_current_state(service: TwinService = Depends(lambda: twin_service)) -> TwinState:
    return service.get_current_state()


@router.post(
    "/advance",
    response_model=TwinAdvanceResponse,
    summary="Advance Virtual Simulation",
    description="Advance the virtual plant time and fouling accumulation by specified hours (Demo Clock).",
)
async def advance_simulation(
    req: TwinAdvanceRequest,
    service: TwinService = Depends(lambda: twin_service),
) -> TwinAdvanceResponse:
    return service.advance_simulation(req)


@router.post(
    "/reset",
    response_model=TwinState,
    summary="Reset Virtual Simulation",
    description="Reset virtual plant state to clean baseline or initial conditions.",
)
async def reset_simulation(
    req: TwinResetRequest,
    service: TwinService = Depends(lambda: twin_service),
) -> TwinState:
    return service.reset_simulation(req)
