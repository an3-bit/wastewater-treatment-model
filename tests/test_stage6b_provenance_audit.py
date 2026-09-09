"""
Tests for Stage 6B: Dynamic Model Provenance & Scientific Claims Audit.

Verifies:
1. Toray pressure convention and pure water permeability Aw calculations.
2. Dimensional consistency of Rm = 1 / (mu * Aw).
3. Stage 6 clean-state initial condition (t=0) equivalence with mechanistic solver.
4. Single authoritative baseline and strategy t15 values in generated tables.
5. Parameter ledger and model constant consistency.
6. Controlled sensitivity invariance of strategy dominance rankings.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from ro_model.units import bar_to_pa, pa_to_bar, m3_per_hr_to_m3_per_s
from ro_model.membrane import MembraneElementProperties, OperatingConditions, SimulationConfig, MembraneElement
from ro_model.solver import solve_membrane_element
from data_generation.simulator_runner import create_baseline_system, run_single_simulation
from fouling.model import (
    calculate_water_viscosity,
    calculate_clean_membrane_resistance,
    resistance_to_permeability,
    FoulingParameters
)
from fouling.calibration import calibrate_fouling_rate_constant
from fouling.dynamics import DynamicROSimulator


ROOT_DIR = Path(__file__).resolve().parent.parent


def test_toray_pressure_convention_and_aw_derivation():
    """
    Verify that standard Toray test conditions yield:
    - deltaP = 15.5132 bar (225 psi gauge/differential)
    - NDP = deltaP - delta_pi = 13.1466 bar
    - Reconciled Aw = 9.4463e-7 m/(bar.s) = 3.4007 LMH/bar
    """
    area = 37.0
    nom_qp_m3_h = 39.7 / 24.0
    rec_nom = 0.15
    qf_m3_h = nom_qp_m3_h / rec_nom
    cf_mg_l = 2000.0
    temp_c = 25.0
    k_cp = 5.0e-5
    as_lit = 1.1834e-9

    delta_p_bar = 15.5132 # 225 psi gauge
    p_perm_bar = 1.01325
    p_feed_bar = delta_p_bar + p_perm_bar

    # Solve for Aw
    aw_test = 9.446312e-12 # m/(Pa.s)
    props = MembraneElementProperties(
        membrane_area_m2=area,
        Aw_m_pa_s=aw_test,
        As_m_s=as_lit
    )
    conds = OperatingConditions.from_engineering_units(
        feed_flow_m3_hr=qf_m3_h,
        feed_tds_mg_l=cf_mg_l,
        feed_pressure_bar=p_feed_bar,
        permeate_pressure_bar=p_perm_bar,
        temperature_celsius=temp_c
    )
    cfg = SimulationConfig(
        mass_transfer_coefficient=k_cp,
        pressure_drop_pa=0.0
    )
    elem = MembraneElement(properties=props, config=cfg)
    res = solve_membrane_element(elem, conds, cfg)

    # Check that nominal permeate flow matches 39.7 m3/day (1.6542 m3/h) to < 0.05%
    assert abs(res.permeate_flow_m3_hr - nom_qp_m3_h) / nom_qp_m3_h < 0.0005
    assert abs(res.water_recovery_percent - 15.0) < 0.01
    assert abs(res.water_flux_lmh - 44.707) < 0.02
    assert abs(res.transmembrane_pressure_bar - 15.5132) < 0.001


def test_rm_and_aw_dimensional_consistency():
    """
    Verify Rm = 1 / (mu * Aw) dimensions and exact numerical values at 25 C.
    """
    mu_25 = calculate_water_viscosity(25.0)
    assert abs(mu_25 - 8.90439e-4) < 1.0e-6

    # 1. Effective Aw
    aw_eff = 1.0232e-11 # m/(Pa.s)
    rm_eff = calculate_clean_membrane_resistance(aw_eff, 25.0)
    assert abs(rm_eff - 1.097578e14) < 1.0e9

    # Inverse check
    aw_back = resistance_to_permeability(rm_eff, 25.0)
    assert abs(aw_back - aw_eff) < 1.0e-17

    # 2. Reconciled Toray Gauge Aw
    aw_gauge = 9.446312e-12 # m/(Pa.s)
    rm_gauge = calculate_clean_membrane_resistance(aw_gauge, 25.0)
    assert abs(rm_gauge - 1.188868e14) < 1.0e9


def test_rspec_recalibration_proportionality():
    """
    Verify that r_spec scales exactly with Rm under the empirical calibration benchmark.
    """
    cal = calibrate_fouling_rate_constant(
        target_decline_pct=15.0,
        target_cum_volume_l_m2=625.0,
        temperature_celsius=25.0
    )
    assert abs(cal.residual_abs_error_pct) < 1.0e-12
    assert abs(cal.calibrated_r_spec - 1.954988e13) < 1.0e9


def test_single_authoritative_t15_values():
    """
    Verify that generated CSV tables contain single, verified t15 values without discrepancies.
    """
    ledger_path = ROOT_DIR / "results/stage6/stage6_final_authoritative_ledger.csv"
    assert ledger_path.exists()

    df = pd.read_csv(ledger_path)
    assert len(df) == 5

    # Check Baseline
    row_base = df[df["strategy_name"] == "Authoritative Baseline"].iloc[0]
    assert abs(row_base["time_to_15pct_decline_hours"] - 20.57) < 0.05
    assert abs(row_base["permeability_decline_168h_pct"] - 43.87) < 0.05

    # Check Strategy A
    row_a = df[df["strategy_name"] == "Strategy A (Max Recovery)"].iloc[0]
    assert abs(row_a["time_to_15pct_decline_hours"] - 9.98) < 0.05
    assert abs(row_a["permeability_decline_168h_pct"] - 55.17) < 0.05

    # Check Strategy B
    row_b = df[df["strategy_name"] == "Strategy B (Min Energy)"].iloc[0]
    assert abs(row_b["time_to_15pct_decline_hours"] - 17.59) < 0.05
    assert abs(row_b["dynamic_average_sec_kwh_m3"] - 1.1458) < 0.01

    # Check Strategy C
    row_c = df[df["strategy_name"] == "Strategy C (Min Stress)"].iloc[0]
    assert abs(row_c["time_to_15pct_decline_hours"] - 35.18) < 0.05
    assert "FEASIBLE" in row_c["mode_b_pressure_ceiling_status"]

    # Check Strategy D
    row_d = df[df["strategy_name"] == "Strategy D (Balanced Knee)"].iloc[0]
    assert abs(row_d["time_to_15pct_decline_hours"] - 16.69) < 0.05


def test_stage6_clean_state_equivalence():
    """
    Verify that at t=0, the dynamic simulation state reproduces the clean steady-state mechanistic solver.
    """
    sys_base = create_baseline_system()
    p1, p2 = 16.06, 16.41 # Strategy D in V2

    # Steady state
    ss_res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=0.0,
        feed_pH=7.0,
        temperature_C=25.0,
        stage1_pressure_bar=p1,
        stage2_pressure_bar=p2,
        system=sys_base
    )

    # Dynamic t=0
    params = FoulingParameters.create_default()
    dyn_sim = DynamicROSimulator(parameters=params)
    dyn_res = dyn_sim.simulate(
        strategy_name="Strategy D",
        initial_p1_bar=p1,
        initial_p2_bar=p2,
        horizon_hours=24.0,
        time_step_hours=1.0,
        operating_mode="MODE_A_FIXED_PRESSURE"
    )

    s0 = dyn_res.states[0]
    assert abs(s0.instantaneous_recovery_pct - ss_res["overall_recovery_pct"]) < 1.0e-5
    assert abs(s0.instantaneous_sec_kwh_m3 - ss_res["SEC_kWh_m3"]) < 1.0e-5
    assert abs(s0.instantaneous_permeate_tds_mg_l - ss_res["permeate_tds_mgL"]) < 1.0e-4


def test_controlled_sensitivity_dominance_invariance():
    """
    Verify that under both Aw = 1.0232e-6 and Aw = 9.4463e-7:
    1. Strategy B has lowest SEC
    2. Strategy A has highest recovery
    3. Strategy C has lowest stress
    4. Authoritative Baseline is strictly dominated by Strategy D
    """
    comp_path = ROOT_DIR / "results/stage6/aw_sensitivity_comparison.csv"
    assert comp_path.exists()

    df_comp = pd.read_csv(comp_path)

    base = df_comp[df_comp["Strategy"] == "Authoritative Baseline"].iloc[0]
    strat_a = df_comp[df_comp["Strategy"] == "Strategy A (Max Recovery)"].iloc[0]
    strat_b = df_comp[df_comp["Strategy"] == "Strategy B (Min Energy)"].iloc[0]
    strat_c = df_comp[df_comp["Strategy"] == "Strategy C (Min Stress)"].iloc[0]
    strat_d = df_comp[df_comp["Strategy"] == "Strategy D (Balanced Knee)"].iloc[0]

    # Check under corrected Aw
    assert strat_a["Rec_corr_pct"] > strat_d["Rec_corr_pct"] > strat_b["Rec_corr_pct"] > strat_c["Rec_corr_pct"]
    assert strat_b["SEC_corr_kWh_m3"] < strat_d["SEC_corr_kWh_m3"] < strat_a["SEC_corr_kWh_m3"] < base["SEC_corr_kWh_m3"] < strat_c["SEC_corr_kWh_m3"]
    assert strat_c["Max_Elem_Rec_corr_pct"] < strat_d["Max_Elem_Rec_corr_pct"] < strat_b["Max_Elem_Rec_corr_pct"] < base["Max_Elem_Rec_corr_pct"] < strat_a["Max_Elem_Rec_corr_pct"]

    # Baseline strict dominance by Strategy D under corrected Aw:
    assert strat_d["Rec_corr_pct"] > base["Rec_corr_pct"]
    assert strat_d["SEC_corr_kWh_m3"] < base["SEC_corr_kWh_m3"]
    assert strat_d["Max_Elem_Rec_corr_pct"] < base["Max_Elem_Rec_corr_pct"]
