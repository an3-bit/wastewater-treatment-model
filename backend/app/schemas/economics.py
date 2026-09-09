"""
Techno-Economic Schemas (Stage 8C Authoritative Frozen Values)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class WaterBalanceMetrics(BaseModel):
    baseline_permeate_m3: float = 65279.7
    watertwin_permeate_m3: float = 109737.3
    additional_permeate_m3: float = 44457.6
    water_increase_pct: float = 68.10


class EnergyBalanceMetrics(BaseModel):
    baseline_total_kwh: float = 65054.4
    watertwin_total_kwh: float = 102583.2
    total_electricity_change_pct: float = 57.69
    baseline_sec_kwh_m3: float = 0.9965
    watertwin_sec_kwh_m3: float = 0.9348
    sec_reduction_pct: float = 6.19
    energy_interpretation: str = "Total electricity increases (+57.69%) because 68.10% more water is produced. Specific energy consumption decreases (-6.19%)."


class EconomicValues(BaseModel):
    integrated_framework_value_kes_year: float = 4391948.14
    static_optimization_value_kes_year: float = 62203.43
    condition_based_value_kes_year: float = 3902797.57
    prediction_value_kes_year: float = 424164.72
    mpc_value_kes_year: float = 2782.42
    predictive_decision_intelligence_kes_year: float = 426947.14
    treatment_lcow_kes_m3: float = 23.20


class ScenarioDetail(BaseModel):
    name: str
    description: str
    reuse_demand_pct: float
    cip_cost_multiplier: float
    cip_downtime_h: float
    discharge_credit_kes_m3: float
    integrated_value_kes_year: float
    digital_twin_net_benefit_kes_year: float
    treatment_lcow_kes_m3: float


class EconomicSummaryResponse(BaseModel):
    water: WaterBalanceMetrics
    energy: EnergyBalanceMetrics
    economics: EconomicValues
    scenarios_summary: Dict[str, float]
    scientific_caveat: str = "Model-predicted virtual-plant results on synthetic textile wastewater disturbance profiles; requires pilot-scale industrial validation."


class ValueDecompositionItem(BaseModel):
    code: str
    name: str
    formula: str
    value_kes_year: float
    share_pct: float
    classification: str
    commercial_recommendation: str


class ValueDecompositionResponse(BaseModel):
    items: List[ValueDecompositionItem]
    total_integrated_value_kes_year: float = 4391948.14
    pure_prediction_share_pct: float = 9.66
    condition_monitoring_share_pct: float = 88.86
    mpc_share_pct: float = 0.06
    mpc_caveat: str = "MPC contributes marginal value (KES 2,782.42/yr, 0.06%). Commercial focus should remain on Membrane Health, Fouling Prediction, and Predictive CIP."


class EconomicScenariosResponse(BaseModel):
    scenarios: List[ScenarioDetail]
    authoritative_scenario: str = "Base"
    scientific_caveat: str = "Model-predicted virtual-plant results on synthetic industrial disturbance profiles."
