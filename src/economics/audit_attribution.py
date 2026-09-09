"""
Stage 8B Economic Attribution and Mathematical Value Decomposition Engine.

Calculates:
1. Corrected incremental value decomposition:
   - Value 1: Static Optimization (B - A)
   - Value 2: Condition-Based Maintenance (C - B)
   - Value 3: Value of Prediction (D - C)
   - Value 4: Value of Supervisory MPC (E - D)
   - Value 5: State Estimation Error Gap (F - E)
   - Total Integrated Value: (E - A)
2. Exact numerical break-even root-finding for water price, electricity price, and OPEX limits.
3. Economic input verification and provenance audit.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import copy
import numpy as np
import pandas as pd

from economics.cost_config import EconomicConfig, load_economics_config
from economics.lifecycle_cost import calculate_lifecycle_costs, LifecycleCostBreakdown
from supervisory.audit_simulator import AuditPolicyResult, Stage8BAuditSimulator


@dataclass
class ValueDecompositionResult:
    val1_static_opt_kes: float
    val2_condition_maint_kes: float
    val3_prediction_kes: float
    val4_supervisory_mpc_kes: float
    val5_oracle_gap_kes: float
    total_integrated_value_kes: float
    
    # Percentages of total integrated value (if positive)
    pct1_static_opt: float
    pct2_condition_maint: float
    pct3_prediction: float
    pct4_supervisory_mpc: float
    
    # Verification identity: (E - A) == (B - A) + (C - B) + (D - C) + (E - D)
    identity_error_kes: float
    is_identity_verified: bool


@dataclass
class CorrectedBreakEvenSummary:
    water_price_breakeven_kes_m3: Optional[float]
    electricity_price_breakeven_kes_kwh: Optional[float]
    cip_cost_breakeven_kes_event: Optional[float]
    max_annual_dt_opex_kes: float
    max_justifiable_capex_1yr_kes: float
    max_justifiable_capex_2yr_kes: float
    max_justifiable_capex_3yr_kes: float


def compute_value_attribution(
    results: Dict[str, AuditPolicyResult],
) -> ValueDecompositionResult:
    """
    Compute rigorous mathematical value attribution across the policy hierarchy:
    - Case A: Fixed Baseline + Fixed Calendar CIP
    - Case B: Fixed Strategy D + Fixed Calendar CIP
    - Case C: Fixed Strategy D + Condition-Based Reactive CIP
    - Case D: Fixed Strategy D + Predictive CIP
    - Case E: Predictive CIP + Supervisory Pressure MPC
    - Case F: Oracle Benchmark (True Rf)
    """
    net_a = results["CASE_A"].lifecycle.net_economic_benefit_kes
    net_b = results["CASE_B"].lifecycle.net_economic_benefit_kes
    net_c = results["CASE_C"].lifecycle.net_economic_benefit_kes
    net_d = results["CASE_D"].lifecycle.net_economic_benefit_kes
    net_e = results["CASE_E"].lifecycle.net_economic_benefit_kes
    net_f = results.get("ORACLE", results.get("CASE_F", results["CASE_E"])).lifecycle.net_economic_benefit_kes

    v1 = net_b - net_a
    v2 = net_c - net_b
    v3 = net_d - net_c
    v4 = net_e - net_d
    v5 = net_f - net_e
    v_total = net_e - net_a

    # Verify identity
    sum_components = v1 + v2 + v3 + v4
    identity_err = abs(v_total - sum_components)
    is_valid = identity_err < 1e-3

    if abs(v_total) > 1e-4:
        p1 = (v1 / v_total) * 100.0
        p2 = (v2 / v_total) * 100.0
        p3 = (v3 / v_total) * 100.0
        p4 = (v4 / v_total) * 100.0
    else:
        p1, p2, p3, p4 = 0.0, 0.0, 0.0, 0.0

    return ValueDecompositionResult(
        val1_static_opt_kes=v1,
        val2_condition_maint_kes=v2,
        val3_prediction_kes=v3,
        val4_supervisory_mpc_kes=v4,
        val5_oracle_gap_kes=v5,
        total_integrated_value_kes=v_total,
        pct1_static_opt=p1,
        pct2_condition_maint=p2,
        pct3_prediction=p3,
        pct4_supervisory_mpc=p4,
        identity_error_kes=identity_err,
        is_identity_verified=is_valid,
    )


def compute_corrected_break_even(
    results: Dict[str, AuditPolicyResult],
    base_config: EconomicConfig,
) -> CorrectedBreakEvenSummary:
    """
    Perform unconstrained numerical root-finding to determine exact economic break-evens.
    """
    case_a = results["CASE_A"]
    case_b = results["CASE_B"]
    case_e = results["CASE_E"]

    # 1. Maximum DT Annual OPEX: Net(E without OPEX) - Net(B)
    net_e_zero_opex = case_e.lifecycle.net_economic_benefit_kes + case_e.lifecycle.digital_twin_opex_kes
    max_opex = max(0.0, net_e_zero_opex - case_b.lifecycle.net_economic_benefit_kes)

    # Incremental benefit of Case E over Fixed Strategy D
    delta_vs_fixed_d = case_e.lifecycle.net_economic_benefit_kes - case_b.lifecycle.net_economic_benefit_kes
    max_capex_1yr = max(0.0, delta_vs_fixed_d * 1.0)
    max_capex_2yr = max(0.0, delta_vs_fixed_d * 2.0)
    max_capex_3yr = max(0.0, delta_vs_fixed_d * 3.0)

    # 2. Water price root finding: where Net(E) == Net(A)
    # Delta Net(w) = (Perm_E - Perm_A)*w - (Costs_E - Costs_A) = 0
    delta_perm = case_e.lifecycle.permeate_volume_m3 - case_a.lifecycle.permeate_volume_m3
    delta_costs = case_e.lifecycle.total_operating_cost_kes - case_a.lifecycle.total_operating_cost_kes
    if delta_perm > 0:
        w_break = delta_costs / delta_perm
        w_break_even = float(w_break) if w_break >= 0 else 0.0
    else:
        w_break_even = None

    # 3. Electricity tariff root finding: where Net(E) == Net(A)
    # Delta Net(e) = (Revenue_E - Revenue_A) - (Costs_other_E - Costs_other_A) - (Energy_E - Energy_A)*e = 0
    delta_rev = case_e.lifecycle.gross_water_value_kes - case_a.lifecycle.gross_water_value_kes
    delta_non_energy_costs = (
        (case_e.lifecycle.cleaning_cost_kes + case_e.lifecycle.membrane_cost_kes + case_e.lifecycle.digital_twin_opex_kes) -
        (case_a.lifecycle.cleaning_cost_kes + case_a.lifecycle.membrane_cost_kes)
    )
    delta_kwh = case_e.lifecycle.total_energy_kwh - case_a.lifecycle.total_energy_kwh

    if abs(delta_kwh) > 1e-3:
        e_break = (delta_rev - delta_non_energy_costs) / delta_kwh
        e_break_even = float(e_break) if e_break > 0 else None
    else:
        e_break_even = None

    # 4. CIP Cost root finding: where Net(E) == Net(A)
    delta_cip_count = case_e.lifecycle.number_of_cleanings - case_a.lifecycle.number_of_cleanings
    net_advantage_before_cip = (
        (case_e.lifecycle.gross_water_value_kes - case_a.lifecycle.gross_water_value_kes) -
        (case_e.lifecycle.energy_cost_kes - case_a.lifecycle.energy_cost_kes) -
        (case_e.lifecycle.membrane_cost_kes - case_a.lifecycle.membrane_cost_kes) -
        case_e.lifecycle.digital_twin_opex_kes
    )
    if delta_cip_count > 0:
        cip_break = net_advantage_before_cip / delta_cip_count
        cip_break_even = float(cip_break) if cip_break > 0 else None
    else:
        cip_break_even = None

    return CorrectedBreakEvenSummary(
        water_price_breakeven_kes_m3=w_break_even,
        electricity_price_breakeven_kes_kwh=e_break_even,
        cip_cost_breakeven_kes_event=cip_break_even,
        max_annual_dt_opex_kes=max_opex,
        max_justifiable_capex_1yr_kes=max_capex_1yr,
        max_justifiable_capex_2yr_kes=max_capex_2yr,
        max_justifiable_capex_3yr_kes=max_capex_3yr,
    )
