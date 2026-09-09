"""
Maintenance & CIP Recommendation Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MaintenanceRecommendationResponse(BaseModel):
    recommended_action: str  # "CLEAN", "CONTINUE", "MONITOR"
    urgency: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    time_since_last_CIP_h: float
    predicted_time_to_threshold_h: float
    current_decline_percent: float
    predicted_decline_24h_percent: float
    reason_codes: List[str]
    primary_rationale: str
    economic_advantage_kes: float
    lockout_active: bool
    lockout_period_h: float = 168.0
    next_eligible_cleaning_time_h: float
    decision_support_role: str = "Operator Decision Support (Not Autonomous Override)"
    scientific_status: str = "Stage 8C Predictive Techno-Economic Framework"


class MaintenanceEvent(BaseModel):
    event_id: str
    timestamp_h: float
    duration_h: float
    pre_clean_decline_pct: float
    post_clean_decline_pct: float
    estimated_restoration_pct: float
    reason: str
    estimated_cost_kes: float
    downtime_h: float


class MaintenanceHistoryResponse(BaseModel):
    total_cip_count_annual: int
    calendar_baseline_cip_count: int = 12
    condition_based_cip_count: int = 48
    predictive_cip_count: int = 67
    mean_interval_h: float
    history: List[MaintenanceEvent]
