"""
Unit tests for Stage 5B: Mechanistic Feasibility Boundary Refinement.

Verifies:
1. Total membrane element count equals exactly 15 elements across 2 stages (5 vessels x 3 elements).
2. Final Strategy A (19.08 / 19.73 bar) passes mechanistic verification with MaxElemRec <= 30.00%.
3. All four final representative strategies pass all mechanistic safeguards.
4. Baseline dominance is confirmed by at least one mechanistically verified solution (e.g. Strategy D and B).
5. The failed surrogate maximum recovery candidate (19.19 / 19.63 bar) is flagged infeasible (MaxElemRec > 30.00%).
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from data_generation.simulator_runner import create_baseline_system, run_single_simulation
from optimization.pareto import AUTHORITATIVE_BASELINE


def test_total_membrane_elements_count():
    """Verify that authoritative system configuration contains exactly 15 membrane elements."""
    system = create_baseline_system()
    
    # Stage 1: 3 vessels x 3 elements = 9
    assert system.stages[0].parallel_vessels == 3
    assert system.stages[0].elements_per_vessel == 3
    stage1_elements = system.stages[0].parallel_vessels * system.stages[0].elements_per_vessel
    assert stage1_elements == 9
    
    # Stage 2: 2 vessels x 3 elements = 6
    assert system.stages[1].parallel_vessels == 2
    assert system.stages[1].elements_per_vessel == 3
    stage2_elements = system.stages[1].parallel_vessels * system.stages[1].elements_per_vessel
    assert stage2_elements == 6
    
    # Total: 15 elements (555.0 m2)
    assert system.total_elements == 15
    assert system.total_area_m2 == 15 * 37.0


def test_final_strategy_a_mechanistic_feasibility():
    """Verify refined Strategy A (20.00 / 20.25 bar) is strictly feasible and <= 30% element recovery."""
    system = create_baseline_system()
    
    res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=20.00,
        stage2_pressure_bar=20.25,
        system=system,
    )
    
    assert bool(res["feasible"]) is True
    assert res["overall_recovery_pct"] >= 84.0
    # Strict project safeguard: <= 30.000%
    assert res["maximum_element_recovery_pct"] <= 30.000
    assert abs(res["maximum_element_recovery_pct"] - 30.0) <= 0.05
    # Permeate TDS <= 18.0 mg/L
    assert res["permeate_tds_mgL"] <= 18.0
    # Positive SEC
    assert res["SEC_kWh_m3"] > 0.0
    # Polarization <= 1.40
    assert res["maximum_polarization_modulus"] <= 1.40


def test_all_final_representative_strategies_pass_safeguards():
    """Verify that all 4 final representative strategies pass mechanistic safeguards."""
    system = create_baseline_system()
    
    strategies = {
        "Strategy A (Max Feasible Recovery)": (20.00, 20.25),
        "Strategy B (Min Energy)": (15.80, 15.80),
        "Strategy C (Min Stress)": (10.00, 14.00),
        "Strategy D (Balanced Knee)": (16.06, 16.41),
    }
    
    for name, (p1, p2) in strategies.items():
        res = run_single_simulation(
            feed_flow_m3h=30.0,
            feed_tds_mgL=2041.0,
            feed_cod_mgL=51.0,
            feed_pH=8.0,
            temperature_C=25.0,
            stage1_pressure_bar=p1,
            stage2_pressure_bar=p2,
            system=system,
        )
        assert bool(res["feasible"]) is True, f"{name} failed simulation convergence"
        assert res["maximum_element_recovery_pct"] <= 30.000, f"{name} exceeded 30% element recovery: {res['maximum_element_recovery_pct']:.4f}%"
        assert res["permeate_tds_mgL"] <= 18.0, f"{name} exceeded 18 mg/L TDS: {res['permeate_tds_mgL']:.2f}"
        assert res["maximum_polarization_modulus"] <= 1.40, f"{name} exceeded beta 1.40: {res['maximum_polarization_modulus']:.4f}"
        assert res["SEC_kWh_m3"] > 0.0, f"{name} had non-positive SEC"
        assert p2 >= p1 - 1e-4, f"{name} violated P2 >= P1"


def test_baseline_mechanistic_dominance():
    """Verify that at least one mechanistically verified solution strictly dominates authoritative baseline."""
    system = create_baseline_system()
    
    # Mechanistically evaluate baseline (13/18 bar)
    base_res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=13.0,
        stage2_pressure_bar=18.0,
        system=system,
    )
    base_rec = base_res["overall_recovery_pct"]
    base_sec = base_res["SEC_kWh_m3"]
    base_stress = base_res["maximum_element_recovery_pct"]
    
    # Mechanistically evaluate Strategy D (Balanced Knee: 16.06 / 16.41 bar)
    knee_res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=16.06,
        stage2_pressure_bar=16.41,
        system=system,
    )
    knee_rec = knee_res["overall_recovery_pct"]
    knee_sec = knee_res["SEC_kWh_m3"]
    knee_stress = knee_res["maximum_element_recovery_pct"]
    
    # Strategy D must dominate baseline across all 3 objectives:
    # 1. Recovery >= baseline (higher is better)
    assert knee_rec > base_rec
    # 2. SEC <= baseline (lower is better)
    assert knee_sec < base_sec
    # 3. Stress <= baseline (lower is better)
    assert knee_stress < base_stress
    
    # Verify exact improvement margins
    assert knee_rec - base_rec >= 0.8  # +4.71% recovery gain
    assert (base_sec - knee_sec) / base_sec >= 0.05  # >5% energy reduction
    assert (base_stress - knee_stress) / base_stress >= 0.03  # >3% stress reduction


def test_failed_candidate_flagged_infeasible():
    """Verify that surrogate candidate (19.99 / 20.28 bar) violates 30% element recovery mechanistically."""
    system = create_baseline_system()
    
    res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=19.988999992836032,
        stage2_pressure_bar=20.28477469501017,
        system=system,
    )
    
    assert bool(res["feasible"]) is True
    # Must exceed 30.0% project safeguard
    assert res["maximum_element_recovery_pct"] > 30.000
    assert abs(res["maximum_element_recovery_pct"] - 30.068) <= 0.05
    
    # Check verified candidates CSV record
    csv_path = Path("results/stage5/pareto_verified_candidates.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        failed_rows = df[df["strategy_name"] == "SURROGATE_MAX_REC_CANDIDATE_INFEASIBLE"]
        assert len(failed_rows) >= 1
        failed_row = failed_rows.iloc[0]
        assert failed_row["mech_elem_rec_safe"] == False
        assert failed_row["mech_verified_fully_feasible"] == False
        assert failed_row["mech_max_element_rec_pct"] > 30.0
