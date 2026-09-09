"""
Membrane Health Service
Service layer for authoritative 6-zone EKF states and 15-element visualization mapping.
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.membranes import MembraneElementListResponse, MembraneZoneListResponse


class MembraneService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def get_membrane_zones(self) -> MembraneZoneListResponse:
        return self.engine.get_membrane_zones()

    def get_membrane_elements(self) -> MembraneElementListResponse:
        return self.engine.get_membrane_elements()


membrane_service = MembraneService()
