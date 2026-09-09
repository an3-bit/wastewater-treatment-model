"""
Sensitivity, Scenario and Break-Even Analysis Module for Stage 8.

Performs parameter perturbations across water prices, electricity tariffs, CIP costs,
fouling kinetic rates, and digital twin capital expenditures.
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import copy
import numpy as np

from economics.cost_config import EconomicConfig
from economics.lifecycle_cost import calculate_lifecycle_costs, LifecycleCostBreakdown


@dataclass
class SensitivityPoint:
    parameter_name: str
    variation_pct: float
    parameter_value: float
    unit: str
    annual_savings_vs_baseline_kes: float
    annual_savings_vs_fixed_d_kes: float
    digital_twin_lcow_kes_m3: float


@dataclass
class BreakEvenSummary:
    min_water_price_kes_m3: float
    max_electricity_price_kes_kwh: float
    max_annual_dt_opex_kes: float
    max_dt_capex_2yr_payback_kes: float


def run_single_parameter_sensitivity(
    baseline_lifecycle: LifecycleCostBreakdown,
    fixed_d_lifecycle: LifecycleCostBreakdown,
    digital_twin_lifecycle: LifecycleCostBreakdown,
    base_config: EconomicConfig,
    parameter_name: str,
    multipliers: List[float],
) -> List[SensitivityPoint]:
    """
    Evaluate annual economic savings while varying a single economic parameter.
    """
    results: List[SensitivityPoint] = []

    for m in multipliers:
        var_pct = (m - 1.0) * 100.0
        cfg = copy.deepcopy(base_config)

        if parameter_name == "water_purchase_cost":
            cfg.water_purchase_cost_kes_m3 = base_config.water_purchase_cost_kes_m3 * m
            val = cfg.water_purchase_cost_kes_m3
            unit = "KES/m3"
        elif parameter_name == "electricity_rate":
            cfg.electricity_rate_kes_kwh = base_config.electricity_rate_kes_kwh * m
            val = cfg.electricity_rate_kes_kwh
            unit = "KES/kWh"
        elif parameter_name == "cip_chemical_cost":
            cfg.cip_chemical_cost_per_event_kes = base_config.cip_chemical_cost_per_event_kes * m
            val = cfg.cip_chemical_cost_per_event_kes
            unit = "KES/event"
        elif parameter_name == "cleaning_duration":
            cfg.cleaning_duration_hours = base_config.cleaning_duration_hours * m
            val = cfg.cleaning_duration_hours
            unit = "hours"
        elif parameter_name == "digital_twin_opex":
            cfg.digital_twin_annual_opex_kes = base_config.digital_twin_annual_opex_kes * m
            val = cfg.digital_twin_annual_opex_kes
            unit = "KES/year"
        else:
            val = m
            unit = "multiplier"

        # Re-evaluate lifecycles under perturbed config
        dt_res = calculate_lifecycle_costs(
            permeate_volume_m3=digital_twin_lifecycle.permeate_volume_m3,
            feed_volume_m3=digital_twin_lifecycle.feed_volume_m3,
            total_energy_kwh=digital_twin_lifecycle.total_energy_kwh,
            cleaning_times_hours=[0.0] * digital_twin_lifecycle.number_of_cleanings,
            annual_operating_hours=cfg.operating_hours_per_year,
            config=cfg,
            include_digital_twin_opex=True,
        )

        base_res = calculate_lifecycle_costs(
            permeate_volume_m3=baseline_lifecycle.permeate_volume_m3,
            feed_volume_m3=baseline_lifecycle.feed_volume_m3,
            total_energy_kwh=baseline_lifecycle.total_energy_kwh,
            cleaning_times_hours=[0.0] * baseline_lifecycle.number_of_cleanings,
            annual_operating_hours=cfg.operating_hours_per_year,
            config=cfg,
            include_digital_twin_opex=False,
        )

        fixed_d_res = calculate_lifecycle_costs(
            permeate_volume_m3=fixed_d_lifecycle.permeate_volume_m3,
            feed_volume_m3=fixed_d_lifecycle.feed_volume_m3,
            total_energy_kwh=fixed_d_lifecycle.total_energy_kwh,
            cleaning_times_hours=[0.0] * fixed_d_lifecycle.number_of_cleanings,
            annual_operating_hours=cfg.operating_hours_per_year,
            config=cfg,
            include_digital_twin_opex=False,
        )

        saving_vs_base = dt_res.net_economic_benefit_kes - base_res.net_economic_benefit_kes
        saving_vs_fixed_d = dt_res.net_economic_benefit_kes - fixed_d_res.net_economic_benefit_kes

        results.append(
            SensitivityPoint(
                parameter_name=parameter_name,
                variation_pct=var_pct,
                parameter_value=val,
                unit=unit,
                annual_savings_vs_baseline_kes=saving_vs_base,
                annual_savings_vs_fixed_d_kes=saving_vs_fixed_d,
                digital_twin_lcow_kes_m3=dt_res.lcow_total_kes_m3,
            )
        )

    return results


def calculate_break_even_conditions(
    baseline_lifecycle: LifecycleCostBreakdown,
    fixed_d_lifecycle: LifecycleCostBreakdown,
    digital_twin_lifecycle: LifecycleCostBreakdown,
    base_config: EconomicConfig,
) -> BreakEvenSummary:
    """
    Calculate threshold conditions where the digital twin breaks even against alternatives.
    """
    # 1. Max Digital Twin Annual OPEX for positive net benefit vs Fixed D
    # Net_DT(OPEX=0) - Net_FixedD = delta_raw
    dt_zero_opex = calculate_lifecycle_costs(
        permeate_volume_m3=digital_twin_lifecycle.permeate_volume_m3,
        feed_volume_m3=digital_twin_lifecycle.feed_volume_m3,
        total_energy_kwh=digital_twin_lifecycle.total_energy_kwh,
        cleaning_times_hours=[0.0] * digital_twin_lifecycle.number_of_cleanings,
        annual_operating_hours=base_config.operating_hours_per_year,
        config=base_config,
        include_digital_twin_opex=False,
    )
    fixed_d_eval = calculate_lifecycle_costs(
        permeate_volume_m3=fixed_d_lifecycle.permeate_volume_m3,
        feed_volume_m3=fixed_d_lifecycle.feed_volume_m3,
        total_energy_kwh=fixed_d_lifecycle.total_energy_kwh,
        cleaning_times_hours=[0.0] * fixed_d_lifecycle.number_of_cleanings,
        annual_operating_hours=base_config.operating_hours_per_year,
        config=base_config,
        include_digital_twin_opex=False,
    )
    max_opex = max(0.0, dt_zero_opex.net_economic_benefit_kes - fixed_d_eval.net_economic_benefit_kes)
    annual_delta = digital_twin_lifecycle.net_economic_benefit_kes - fixed_d_lifecycle.net_economic_benefit_kes
    max_capex_2yr = max(0.0, annual_delta * 2.0)

    # 2. Min water price where Digital Twin beats Baseline
    # Scan water prices from 0 to 200 KES/m3
    min_water_price = 0.0
    for w_p in np.linspace(0.0, 150.0, 301):
        cfg = copy.deepcopy(base_config)
        cfg.water_purchase_cost_kes_m3 = float(w_p)
        dt_eval = calculate_lifecycle_costs(
            digital_twin_lifecycle.permeate_volume_m3, digital_twin_lifecycle.feed_volume_m3,
            digital_twin_lifecycle.total_energy_kwh, [0.0]*digital_twin_lifecycle.number_of_cleanings,
            cfg.operating_hours_per_year, cfg, include_digital_twin_opex=True,
        )
        base_eval = calculate_lifecycle_costs(
            baseline_lifecycle.permeate_volume_m3, baseline_lifecycle.feed_volume_m3,
            baseline_lifecycle.total_energy_kwh, [0.0]*baseline_lifecycle.number_of_cleanings,
            cfg.operating_hours_per_year, cfg, include_digital_twin_opex=False,
        )
        if dt_eval.net_economic_benefit_kes > base_eval.net_economic_benefit_kes:
            min_water_price = float(w_p)
            break

    # 3. Max electricity price before DT advantage becomes negative
    max_elec_price = 100.0
    for e_p in np.linspace(5.0, 100.0, 191):
        cfg = copy.deepcopy(base_config)
        cfg.electricity_rate_kes_kwh = float(e_p)
        dt_eval = calculate_lifecycle_costs(
            digital_twin_lifecycle.permeate_volume_m3, digital_twin_lifecycle.feed_volume_m3,
            digital_twin_lifecycle.total_energy_kwh, [0.0]*digital_twin_lifecycle.number_of_cleanings,
            cfg.operating_hours_per_year, cfg, include_digital_twin_opex=True,
        )
        fixed_d_eval_p = calculate_lifecycle_costs(
            fixed_d_lifecycle.permeate_volume_m3, fixed_d_lifecycle.feed_volume_m3,
            fixed_d_lifecycle.total_energy_kwh, [0.0]*fixed_d_lifecycle.number_of_cleanings,
            cfg.operating_hours_per_year, cfg, include_digital_twin_opex=False,
        )
        if dt_eval.net_economic_benefit_kes < fixed_d_eval_p.net_economic_benefit_kes:
            max_elec_price = float(e_p)
            break

    return BreakEvenSummary(
        min_water_price_kes_m3=min_water_price,
        max_electricity_price_kes_kwh=max_elec_price,
        max_annual_dt_opex_kes=max_opex,
        max_dt_capex_2yr_payback_kes=max_capex_2yr,
    )
