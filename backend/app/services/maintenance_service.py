"""
Maintenance Service
Service layer for predictive maintenance decisions and CIP event history.
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.maintenance import (
    MaintenanceHistoryResponse,
    MaintenanceRecommendationResponse,
)


class MaintenanceService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def get_recommendation(self) -> MaintenanceRecommendationResponse:
        return self.engine.get_maintenance_recommendation()

    def get_history(self) -> MaintenanceHistoryResponse:
        return self.engine.get_maintenance_history()


maintenance_service = MaintenanceService()
