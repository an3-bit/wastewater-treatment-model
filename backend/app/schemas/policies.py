"""
Policy Comparison Schemas (Stage 8C Authoritative Table 15)
"""

from typing import List
from pydantic import BaseModel, Field


class PolicyItem(BaseModel):
    policy_code: str
    policy_name: str
    architecture: str
    p1_bar: float
    p2_bar: float
    permeate_m3: float
    effective_recovery_pct: float
    total_energy_kwh: float
    sec_kwh_m3: float
    cip_count: int
    cip_downtime_h: float
    operating_uptime_h: float
    treatment_lcow_kes_m3: float
    net_annual_benefit_kes: float
    incremental_value_vs_baseline_kes: float
    policy_type: str
    deployable: bool
    oracle: bool = False
    theoretical_upper_bound: bool = False


class PolicyComparisonResponse(BaseModel):
    policies: List[PolicyItem]
    total_policies: int
    authoritative_recommended_policy: str = "CASE_E"
    oracle_notice: str = "Case F (Oracle) represents a theoretical upper bound with perfect disturbance preview and is not deployable in real time."
