"""
Unit tests verifying clean initial condition (t = 0) equivalence with authoritative steady-state model.
"""

import pytest
import numpy as np

from data_generation.simulator_runner import run_single_simulation, create_baseline_system
from fouling.model import FoulingParameters
from fouling.dynamics import DynamicROSimulator


def test_t0_clean_identity_authoritative_baseline():
    """Verify that at t=0, the dynamic model reproduces the 13/18 bar baseline within numerical tolerance."""
    # Steady state run
    ss_res = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=13.0,
        stage2_pressure_bar=18.0,
    )

    # Dynamic run at t=0
    sim = DynamicROSimulator()
    dyn_res = sim.simulate(
        strategy_name="BASELINE",
        initial_p1_bar=13.0,
        initial_p2_bar=18.0,
        horizon_hours=0.0,
        time_step_hours=1.0,
    )

    state0 = dyn_res.states[0]

    # Check overall metrics
    assert abs(state0.instantaneous_recovery_pct - ss_res["overall_recovery_pct"]) < 1e-5
    assert abs(state0.instantaneous_sec_kwh_m3 - ss_res["SEC_kWh_m3"]) < 1e-5
    assert abs(state0.instantaneous_permeate_flow_m3_h - ss_res["permeate_flow_m3h"]) < 1e-5
    assert abs(state0.instantaneous_permeate_tds_mg_l - ss_res["permeate_tds_mgL"]) < 1e-5
    assert abs(state0.instantaneous_concentrate_tds_mg_l - ss_res["concentrate_tds_mgL"]) < 1e-5

    # Check clean resistance & permeability
    assert state0.average_permeability_ratio == 1.0
    assert state0.average_permeability_decline_pct == 0.0
    for est in state0.element_states:
        assert est.r_f_m_inv == 0.0
        assert est.permeability_ratio == 1.0


def test_t0_clean_identity_all_representative_strategies():
    """Verify t=0 clean equivalence across all 4 Stage 5 representative strategies."""
    strategies = {
        "Strategy A (Max Feasible Recovery)": (19.08, 19.73),
        "Strategy B (Min Energy)": (15.30, 15.30),
        "Strategy C (Min Stress)": (10.00, 14.00),
        "Strategy D (Balanced Knee)": (15.05, 15.80),
    }

    sim = DynamicROSimulator()

    for name, (p1, p2) in strategies.items():
        ss_res = run_single_simulation(
            feed_flow_m3h=30.0,
            feed_tds_mgL=2041.0,
            feed_cod_mgL=51.0,
            feed_pH=8.0,
            temperature_C=25.0,
            stage1_pressure_bar=p1,
            stage2_pressure_bar=p2,
        )

        dyn_res = sim.simulate(
            strategy_name=name,
            initial_p1_bar=p1,
            initial_p2_bar=p2,
            horizon_hours=0.0,
            time_step_hours=1.0,
        )

        state0 = dyn_res.states[0]
        assert abs(state0.instantaneous_recovery_pct - ss_res["overall_recovery_pct"]) < 1e-5
        assert abs(state0.instantaneous_sec_kwh_m3 - ss_res["SEC_kWh_m3"]) < 1e-5
        assert abs(state0.instantaneous_permeate_flow_m3_h - ss_res["permeate_flow_m3h"]) < 1e-5
