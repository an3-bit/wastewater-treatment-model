"""
Sensor API Endpoints
Provides 10 standard skid sensor readings and historical time series for charts.
"""

from fastapi import APIRouter, Depends, Query
from app.schemas.sensors import SensorHistoryResponse, SensorListResponse
from app.services.sensor_service import SensorService, sensor_service

router = APIRouter()


@router.get(
    "",
    response_model=SensorListResponse,
    summary="Standard Skid Sensors",
    description="Returns the 10 authoritative standard skid sensors (Qf, Cf, T, P1, Qp, Cp, P2, Pint, Cc, Welec).",
)
async def get_sensors(service: SensorService = Depends(lambda: sensor_service)) -> SensorListResponse:
    return service.get_sensors()


@router.get(
    "/history",
    response_model=SensorHistoryResponse,
    summary="Sensor Telemetry History",
    description="Returns historical time-series data for a specific sensor suitable for frontend charts.",
)
async def get_sensor_history(
    sensor_id: str = Query(default="Qf", description="Sensor ID (e.g., Qf, Cf, T, P1, Qp_total, P2, W_electric)"),
    hours: float = Query(default=24.0, ge=1.0, le=168.0, description="Hours of history to retrieve"),
    service: SensorService = Depends(lambda: sensor_service),
) -> SensorHistoryResponse:
    return service.get_sensor_history(sensor_id=sensor_id, hours=hours)
