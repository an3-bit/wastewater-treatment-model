"""
Stage 8 and 8B Techno-Economic Analysis Package.
"""

from economics.cost_config import EconomicConfig, EconomicParameter, load_economics_config
from economics.water_value import calculate_water_value, WaterValueResult
from economics.energy_cost import calculate_energy_cost, EnergyCostResult
from economics.cleaning_cost import calculate_single_cip_cost, calculate_annual_cleaning_costs, AnnualCleaningCostResult, CIPEventCost
from economics.membrane_cost import calculate_membrane_cost, MembraneCostResult
from economics.downtime_cost import calculate_downtime_cost, DowntimeCostResult
from economics.lifecycle_cost import calculate_lifecycle_costs, LifecycleCostBreakdown
from economics.economic_kpis import calculate_financial_appraisal, FinancialAppraisalResult
from economics.sensitivity import (
    run_single_parameter_sensitivity,
    calculate_break_even_conditions,
    SensitivityPoint,
    BreakEvenSummary,
)
from economics.audit_attribution import (
    ValueDecompositionResult,
    CorrectedBreakEvenSummary,
    compute_value_attribution,
    compute_corrected_break_even,
)

__all__ = [
    "EconomicConfig",
    "EconomicParameter",
    "load_economics_config",
    "calculate_water_value",
    "WaterValueResult",
    "calculate_energy_cost",
    "EnergyCostResult",
    "calculate_single_cip_cost",
    "calculate_annual_cleaning_costs",
    "AnnualCleaningCostResult",
    "CIPEventCost",
    "calculate_membrane_cost",
    "MembraneCostResult",
    "calculate_downtime_cost",
    "DowntimeCostResult",
    "calculate_lifecycle_costs",
    "LifecycleCostBreakdown",
    "calculate_financial_appraisal",
    "FinancialAppraisalResult",
    "run_single_parameter_sensitivity",
    "calculate_break_even_conditions",
    "SensitivityPoint",
    "BreakEvenSummary",
    "ValueDecompositionResult",
    "CorrectedBreakEvenSummary",
    "compute_value_attribution",
    "compute_corrected_break_even",
]
