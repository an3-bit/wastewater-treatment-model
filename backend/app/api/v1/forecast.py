"""
Forecast API Endpoints
Provides 24-hour standard horizon forecasts (supporting 6, 12, 24, 48, 72h).
"""

from fastapi import APIRouter, Depends, Query
from app.schemas.forecast import ForecastResponse
from app.services.forecast_service import ForecastService, forecast_service

router = APIRouter()


@router.get(
    "",
    response_model=ForecastResponse,
    summary="Look-Ahead Dynamic State Forecast",
    description="Returns time-series forecast for recovery, permeate flow, SEC, power, water quality, and 6-zone fouling.",
)
async def get_forecast(
    hours: int = Query(default=24, description="Forecast horizon in hours (6, 12, 24, 48, 72). Default: 24 (Stage 8C standard)"),
    service: ForecastService = Depends(lambda: forecast_service),
) -> ForecastResponse:
    return service.get_forecast(horizon_hours=hours)
