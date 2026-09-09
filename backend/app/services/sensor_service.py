"""
Sensor Service
Service layer for sensor telemetry and historical query resolution.
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.sensors import SensorHistoryResponse, SensorListResponse


class SensorService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def get_sensors(self) -> SensorListResponse:
        return self.engine.get_sensors()

    def get_sensor_history(self, sensor_id: str, hours: float = 24.0) -> SensorHistoryResponse:
        return self.engine.get_sensor_history(sensor_id=sensor_id, hours=hours)


sensor_service = SensorService()
