"""
Simulation API Endpoints
Provides interactive scenario evaluations using physical model bounds.
"""

from fastapi import APIRouter, Depends
from app.schemas.simulation import SimulationRequest, SimulationResult
from app.services.simulation_service import SimulationService, simulation_service

router = APIRouter()


@router.post(
    "/run",
    response_model=SimulationResult,
    summary="Run Scenario Simulation",
    description="Simulate RO plant operating state, hydraulic recovery, specific energy consumption, and fouling rates for candidate setpoints.",
)
async def run_simulation(
    req: SimulationRequest,
    service: SimulationService = Depends(lambda: simulation_service),
) -> SimulationResult:
    return service.run_simulation(req)
