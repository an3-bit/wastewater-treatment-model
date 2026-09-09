"""
Unit tests for dynamic fluid and solute mass conservation across time-stepping simulations.
"""

import pytest
import numpy as np

from fouling.dynamics import DynamicROSimulator


def test_dynamic_mass_balance_mode_a():
    """Verify exact fluid and solute mass balance across 168h in Mode A (Fixed Pressure)."""
    sim = DynamicROSimulator()
    res = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=168.0,
        time_step_hours=2.0,
        operating_mode="MODE_A_FIXED_PRESSURE",
    )

    for state in res.states:
        # Water mass balance
        q_f = 30.0
        q_p = state.instantaneous_permeate_flow_m3_h
        q_r = state.instantaneous_concentrate_flow_m3_h
        water_err_pct = abs(q_f - (q_p + q_r)) / q_f * 100.0
        assert water_err_pct < 1e-4, f"Water balance violated at t={state.time_hours}h: {water_err_pct}%"

        # Solute mass balance
        c_f = 2041.0
        c_p = state.instantaneous_permeate_tds_mg_l
        c_r = state.instantaneous_concentrate_tds_mg_l
        solute_err_pct = abs((q_f * c_f) - (q_p * c_p + q_r * c_r)) / (q_f * c_f) * 100.0
        assert solute_err_pct < 1e-4, f"Solute balance violated at t={state.time_hours}h: {solute_err_pct}%"

    assert res.max_dynamic_water_error_pct < 1e-4
    assert res.max_dynamic_solute_error_pct < 1e-4


def test_dynamic_mass_balance_mode_b():
    """Verify exact fluid and solute mass balance across 72h in Mode B (Production-Maintaining Pressure)."""
    sim = DynamicROSimulator()
    res = sim.simulate(
        strategy_name="MIN_ENERGY",
        initial_p1_bar=15.30,
        initial_p2_bar=15.30,
        horizon_hours=72.0,
        time_step_hours=2.0,
        operating_mode="MODE_B_MAINTAIN_PRODUCTION",
    )

    for state in res.states:
        q_f = 30.0
        q_p = state.instantaneous_permeate_flow_m3_h
        q_r = state.instantaneous_concentrate_flow_m3_h
        water_err_pct = abs(q_f - (q_p + q_r)) / q_f * 100.0
        assert water_err_pct < 1e-4

        c_f = 2041.0
        c_p = state.instantaneous_permeate_tds_mg_l
        c_r = state.instantaneous_concentrate_tds_mg_l
        solute_err_pct = abs((q_f * c_f) - (q_p * c_p + q_r * c_r)) / (q_f * c_f) * 100.0
        assert solute_err_pct < 1e-4
