"""
Membrane Replacement and Degradation Cost Module for Stage 8.

Calculates membrane capital replacement amortization, installation labor, disposal fees,
and stress-adjusted degradation penalties.
"""

from dataclasses import dataclass
from economics.cost_config import EconomicConfig


@dataclass
class MembraneCostResult:
    annual_operating_hours: float
    nominal_lifetime_hours: float
    effective_lifetime_hours: float
    annual_replacement_fraction: float
    element_purchase_cost_kes: float
    labour_cost_kes: float
    disposal_cost_kes: float
    total_annual_membrane_cost_kes: float
    stress_degradation_factor: float


def calculate_membrane_cost(
    annual_operating_hours: float,
    config: EconomicConfig,
    average_max_element_recovery_pct: float = 20.37,
    reference_max_element_recovery_pct: float = 20.37,
) -> MembraneCostResult:
    """
    Calculate annual membrane replacement amortization.
    
    If operating under higher hydraulic recovery stress (max element recovery > 20.37%),
    effective lifetime decreases proportionally according to physical scaling strain.
    """
    nom_life = config.membrane_replacement_interval_hours
    
    # Stress factor based on maximum single-element recovery strain
    stress_ratio = max(0.5, min(2.0, average_max_element_recovery_pct / reference_max_element_recovery_pct))
    eff_life = nom_life / (stress_ratio ** 1.2)  # Non-linear compaction exponent
    
    annual_frac = annual_operating_hours / eff_life

    elem_purchase_total = config.number_of_membrane_elements * config.membrane_element_purchase_cost_kes
    labour_total = config.membrane_replacement_labour_kes
    disposal_total = config.number_of_membrane_elements * config.membrane_disposal_cost_kes

    single_replacement_total = elem_purchase_total + labour_total + disposal_total
    annual_total = single_replacement_total * annual_frac

    return MembraneCostResult(
        annual_operating_hours=annual_operating_hours,
        nominal_lifetime_hours=nom_life,
        effective_lifetime_hours=eff_life,
        annual_replacement_fraction=annual_frac,
        element_purchase_cost_kes=elem_purchase_total * annual_frac,
        labour_cost_kes=labour_total * annual_frac,
        disposal_cost_kes=disposal_total * annual_frac,
        total_annual_membrane_cost_kes=annual_total,
        stress_degradation_factor=stress_ratio,
    )
