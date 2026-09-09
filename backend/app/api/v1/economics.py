"""
Economics API Endpoints
Provides authoritative Stage 8C frozen techno-economic metrics, value decomposition, and scenarios.
"""

from fastapi import APIRouter, Depends
from app.schemas.economics import (
    EconomicScenariosResponse,
    EconomicSummaryResponse,
    ValueDecompositionResponse,
)
from app.services.economics_service import EconomicsService, economics_service

router = APIRouter()


@router.get(
    "/summary",
    response_model=EconomicSummaryResponse,
    summary="Authoritative Techno-Economic Summary",
    description="Returns Stage 8C frozen water impact (+68.10%), energy balance (+57.69% total kWh, -6.19% SEC), and net value (KES 4.39M/yr).",
)
async def get_economic_summary(
    service: EconomicsService = Depends(lambda: economics_service),
) -> EconomicSummaryResponse:
    return service.get_summary()


@router.get(
    "/value-decomposition",
    response_model=ValueDecompositionResponse,
    summary="Mathematical Value Attribution Waterfall",
    description="Returns exact value decomposition: Static (B-A), Condition (C-B), Prediction (D-C), MPC (E-D), Integrated (E-A).",
)
async def get_value_decomposition(
    service: EconomicsService = Depends(lambda: economics_service),
) -> ValueDecompositionResponse:
    return service.get_value_decomposition()


@router.get(
    "/scenarios",
    response_model=EconomicScenariosResponse,
    summary="Economic Sensitivity Scenarios",
    description="Returns Conservative (KES 1.86M/yr), Base (KES 4.39M/yr), and Favourable (KES 4.68M/yr) scenario evaluations.",
)
async def get_scenarios(
    service: EconomicsService = Depends(lambda: economics_service),
) -> EconomicScenariosResponse:
    return service.get_scenarios()
