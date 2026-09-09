"""
Twin Service
Service layer for digital twin metadata, state queries, and virtual simulation advance/reset.
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.twin import TwinAdvanceRequest, TwinAdvanceResponse, TwinMetadata, TwinResetRequest, TwinState


class TwinService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def get_metadata(self) -> TwinMetadata:
        return self.engine.get_metadata()

    def get_current_state(self) -> TwinState:
        return self.engine.get_state()

    def advance_simulation(self, req: TwinAdvanceRequest) -> TwinAdvanceResponse:
        return self.engine.advance(hours=req.hours)

    def reset_simulation(self, req: TwinResetRequest) -> TwinState:
        return self.engine.reset(
            reset_to_clean=req.reset_to_clean,
            initial_p1=req.initial_p1_bar or 18.0,
            initial_p2=req.initial_p2_bar or 25.0,
        )


twin_service = TwinService()
