"""
Scenario Simulation Schemas
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    feed_flow_m3_h: float = Field(default=25.0, ge=10.0, le=40.0, description="Feed volumetric flow rate (m³/h)")
    feed_tds_mg_l: float = Field(default=3000.0, ge=500.0, le=8000.0, description="Feed TDS concentration (mg/L)")
    temperature_c: float = Field(default=25.0, ge=10.0, le=45.0, description="Feed temperature (°C)")
    p1_bar: float = Field(default=15.0, ge=10.0, le=25.0, description="Stage 1 Feed Pressure (bar)")
    p2_bar: float = Field(default=22.0, ge=12.0, le=30.0, description="Stage 2 Feed Pressure (bar)")
    forecast_horizon_h: int = Field(default=24, ge=1, le=72, description="Simulation forecast horizon in hours")
    economic_scenario: str = Field(default="Base", description="Economic scenario (Base, Conservative, Favourable)")


class SimulationWarning(BaseModel):
    code: str
    message: str
    severity: str  # "INFO", "WARNING", "CRITICAL"


class SimulationResult(BaseModel):
    feasible: bool
    feed_flow_m3_h: float
    feed_tds_mg_l: float
    temperature_c: float
    p1_bar: float
    p2_bar: float
    permeate_flow_m3_h: float
    concentrate_flow_m3_h: float
    recovery_percent: float
    sec_kwh_m3: float
    power_kw: float
    permeate_tds_mg_l: float
    concentrate_tds_mg_l: float
    salt_rejection_percent: float
    fouling_metrics: Dict[str, float]
    estimated_daily_value_kes: float
    constraint_status: Dict[str, bool]
    warnings: List[SimulationWarning]
    execution_time_ms: float
