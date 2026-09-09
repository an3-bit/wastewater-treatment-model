"""
Simulation Service
Service layer for scenario evaluations using physical RO model bounds.
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.simulation import SimulationRequest, SimulationResult


class SimulationService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def run_simulation(self, req: SimulationRequest) -> SimulationResult:
        return self.engine.run_scenario_simulation(req)


simulation_service = SimulationService()
