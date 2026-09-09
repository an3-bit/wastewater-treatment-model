"""
Membrane Health & Zoning Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MembraneZone(BaseModel):
    zone_id: str
    stage: int
    position: str  # "Lead", "Middle", "Tail"
    vessels_covered: str
    elements_count: int
    Rf_m_inv: float
    normalized_Rf: float
    permeability_m_pa_s: float
    permeability_decline_percent: float
    health_percent: float
    severity: str  # "HEALTHY", "MODERATE", "SEVERE", "CRITICAL"


class MembraneZoneListResponse(BaseModel):
    zones: List[MembraneZone]
    total_zones: int = 6
    estimator: str = "6-Zone EKF"
    mean_health_percent: float
    max_decline_percent: float
    critical_zone_id: Optional[str] = None


class MembraneElement(BaseModel):
    element_id: str
    stage_id: int
    vessel_id: int
    position_in_vessel: int
    parent_zone_id: str
    estimated_from_zone: bool = True
    health_percent: float
    decline_percent: float
    flux_lmh: float
    salt_rejection_percent: float
    fouling_resistance_m_inv: float
    status: str


class MembraneElementListResponse(BaseModel):
    elements: List[MembraneElement]
    total_elements: int = 15
    mapping_notice: str = "Visualization mapping from authoritative 6-zone EKF estimator. Not 15 independent sensors."
    estimator: str = "6-Zone EKF"
