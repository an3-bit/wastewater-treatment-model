"""
Forecast Schemas for WaterTwin AI
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    time_offset_h: float
    recovery_percent: float
    permeate_flow_m3_h: float
    sec_kwh_m3: float
    power_kw: float
    permeate_tds_mg_l: float
    permeability_decline_percent: float
    stage1_decline_percent: float
    stage2_decline_percent: float
    zone_rf_m_inv: Dict[str, float]


class ForecastConfidence(BaseModel):
    horizon_hours: int
    is_standard_horizon: bool
    confidence_level_percent: float = 95.0
    flux_uncertainty_band_pct: float = 2.5
    fouling_uncertainty_band_pct: float = 3.8
    notes: str = "Uncertainty bounds based on validated EKF covariance and feed disturbance bounds."


class ForecastResponse(BaseModel):
    horizon_hours: int
    step_hours: float
    standard_horizon_note: str = "24h is the authoritative Stage 8C frozen standard horizon."
    confidence: ForecastConfidence
    trajectory: List[ForecastPoint]
    predicted_threshold_crossing_h: Optional[float] = None
