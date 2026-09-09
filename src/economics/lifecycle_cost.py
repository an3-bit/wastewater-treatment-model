"""
Lifecycle Cost of Water (LCOW) and Net Value Module for Stage 8.

Integrates water valuation, electricity consumption, CIP events, membrane amortization,
and digital twin overheads to compute itemized LCOW and net economic benefit.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

from economics.cost_config import EconomicConfig
from economics.water_value import calculate_water_value, WaterValueResult
from economics.energy_cost import calculate_energy_cost, EnergyCostResult
from economics.cleaning_cost import calculate_annual_cleaning_costs, AnnualCleaningCostResult
from economics.membrane_cost import calculate_membrane_cost, MembraneCostResult


@dataclass
class LifecycleCostBreakdown:
    # Physical Output
    permeate_volume_m3: float
    feed_volume_m3: float
    average_recovery_pct: float
    total_energy_kwh: float
    average_sec_kwh_m3: float
    number_of_cleanings: int

    # Monetary Totals [KES/year]
    gross_water_value_kes: float
    avoided_freshwater_cost_kes: float
    avoided_discharge_cost_kes: float

    energy_cost_kes: float
    cleaning_cost_kes: float
    membrane_cost_kes: float
    digital_twin_opex_kes: float
    total_operating_cost_kes: float

    net_economic_benefit_kes: float

    # Unit Metrics [KES/m3 of Permeate]
    lcow_total_kes_m3: float
    energy_cost_per_m3_kes: float
    cleaning_cost_per_m3_kes: float
    membrane_cost_per_m3_kes: float
    digital_twin_opex_per_m3_kes: float
    net_value_per_m3_kes: float


def calculate_lifecycle_costs(
    permeate_volume_m3: float,
    feed_volume_m3: float,
    total_energy_kwh: float,
    cleaning_times_hours: list,
    annual_operating_hours: float,
    config: EconomicConfig,
    average_max_element_recovery_pct: float = 20.37,
    include_digital_twin_opex: bool = True,
) -> LifecycleCostBreakdown:
    """
    Compute full lifecycle cost breakdown and LCOW for an annual operating scenario.
    """
    perm_vol = max(0.0, float(permeate_volume_m3))
    feed_vol = max(1.0, float(feed_volume_m3))
    avg_rec = (perm_vol / feed_vol) * 100.0
    avg_sec = (total_energy_kwh / perm_vol) if perm_vol > 0 else 0.0

    # 1. Water Value
    w_res = calculate_water_value(perm_vol, config)

    # 2. Energy Cost
    e_res = calculate_energy_cost(total_energy_kwh, perm_vol, config)

    # 3. Cleaning Cost
    c_res = calculate_annual_cleaning_costs(cleaning_times_hours, config)

    # 4. Membrane Cost
    m_res = calculate_membrane_cost(
        annual_operating_hours=annual_operating_hours,
        config=config,
        average_max_element_recovery_pct=average_max_element_recovery_pct,
    )

    # 5. Digital Twin OPEX
    dt_opex = config.digital_twin_annual_opex_kes if include_digital_twin_opex else 0.0

    # 6. Totals
    total_cost = e_res.electricity_cost_kes + c_res.total_cip_cost_kes + m_res.total_annual_membrane_cost_kes + dt_opex
    net_val = w_res.total_water_value_kes - total_cost

    # 7. Unit Breakdown per m3 permeate
    lcow = (total_cost / perm_vol) if perm_vol > 0 else 0.0
    e_unit = (e_res.electricity_cost_kes / perm_vol) if perm_vol > 0 else 0.0
    c_unit = (c_res.total_cip_cost_kes / perm_vol) if perm_vol > 0 else 0.0
    m_unit = (m_res.total_annual_membrane_cost_kes / perm_vol) if perm_vol > 0 else 0.0
    dt_unit = (dt_opex / perm_vol) if perm_vol > 0 else 0.0
    net_unit = (net_val / perm_vol) if perm_vol > 0 else 0.0

    return LifecycleCostBreakdown(
        permeate_volume_m3=perm_vol,
        feed_volume_m3=feed_vol,
        average_recovery_pct=avg_rec,
        total_energy_kwh=total_energy_kwh,
        average_sec_kwh_m3=avg_sec,
        number_of_cleanings=c_res.number_of_cleanings,
        gross_water_value_kes=w_res.total_water_value_kes,
        avoided_freshwater_cost_kes=w_res.avoided_freshwater_value_kes,
        avoided_discharge_cost_kes=w_res.avoided_discharge_value_kes,
        energy_cost_kes=e_res.electricity_cost_kes,
        cleaning_cost_kes=c_res.total_cip_cost_kes,
        membrane_cost_kes=m_res.total_annual_membrane_cost_kes,
        digital_twin_opex_kes=dt_opex,
        total_operating_cost_kes=total_cost,
        net_economic_benefit_kes=net_val,
        lcow_total_kes_m3=lcow,
        energy_cost_per_m3_kes=e_unit,
        cleaning_cost_per_m3_kes=c_unit,
        membrane_cost_per_m3_kes=m_unit,
        digital_twin_opex_per_m3_kes=dt_unit,
        net_value_per_m3_kes=net_unit,
    )
