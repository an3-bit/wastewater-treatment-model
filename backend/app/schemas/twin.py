"""
Twin State & Metadata Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TwinMetadata(BaseModel):
    model_version: str = "2.0-pressure-corrected"
    estimator: str = "6-Zone EKF"
    fouling_zones: int = 6
    display_elements: int = 15
    forecast_horizon_h: int = 24
    status: str = "virtual-plant"
    stage: str = "8C-frozen"
    industrial_validation: bool = False
    economic_model_status: str = "authoritative-frozen"
    data_mode: str = "virtual"
    last_update: datetime = Field(default_factory=datetime.utcnow)
    scientific_caveat: str = "Model-predicted virtual-plant results; requires pilot-scale industrial validation."


class TwinState(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    simulation_time_h: float = 0.0
    feed_flow_m3_h: float = 25.0
    feed_tds_mg_l: float = 3000.0
    temperature_c: float = 25.0
    p1_bar: float = 15.0
    p2_bar: float = 22.0
    p_interstage_bar: float = 14.2
    permeate_flow_m3_h: float = 13.72
    concentrate_flow_m3_h: float = 11.28
    recovery_percent: float = 54.88
    sec_kwh_m3: float = 0.9348
    power_kw: float = 12.82
    permeate_tds_mg_l: float = 85.4
    concentrate_tds_mg_l: float = 6540.0
    salt_rejection_percent: float = 97.15
    overall_permeability_decline_percent: float = 8.45
    membrane_health_score_percent: float = 91.55
    current_operating_policy: str = "Case E: Predictive CIP + Pressure MPC"
    twin_status: str = "OPTIMAL_OPERATION"
    data_quality: str = "GOOD"
    hours_since_cip: float = 48.0


class TwinAdvanceRequest(BaseModel):
    hours: float = Field(default=1.0, ge=0.1, le=168.0, description="Hours of virtual simulation to advance")


class TwinResetRequest(BaseModel):
    reset_to_clean: bool = Field(default=True, description="Reset membranes to clean state (Rf=0)")
    initial_p1_bar: Optional[float] = Field(default=15.0, ge=10.0, le=25.0)
    initial_p2_bar: Optional[float] = Field(default=22.0, ge=12.0, le=30.0)


class TwinAdvanceResponse(BaseModel):
    success: bool
    advanced_hours: float
    current_simulation_time_h: float
    state: TwinState
