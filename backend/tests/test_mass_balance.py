"""
Unit tests for mass and solute balance conservation across diverse operating regimes.
"""

import pytest
import numpy as np

from ro_model.solver import simulate_ro
from ro_model.membrane import MembraneElementProperties, SimulationConfig


@pytest.mark.parametrize("feed_flow", [15.0, 30.0, 45.0])
@pytest.mark.parametrize("feed_tds", [500.0, 2000.0, 5000.0])
@pytest.mark.parametrize("feed_pressure_bar", [12.0, 15.5132, 25.0, 35.0])
def test_mass_and_solute_conservation(feed_flow, feed_tds, feed_pressure_bar):
    """
    Verify that total fluid mass balance and solute mass balance are strictly conserved
    across multiple flow, salinity, and pressure conditions.
    """
    result = simulate_ro(
        feed_flow=feed_flow,
        feed_tds=feed_tds,
        pressure=feed_pressure_bar,
        temperature=25.0,
        pressure_unit="bar"
    )
    
    assert result.converged, f"Simulation did not converge: {result.solver_message}"
    
    # 1. Total Water Mass Balance: Qf = Qp + Qr
    q_f = result.feed_flow_m3_s
    q_p = result.permeate_flow_m3_s
    q_r = result.concentrate_flow_m3_s
    
    water_residual = abs(q_f - (q_p + q_r))
    assert water_residual < 1.0e-9, f"Water balance residual too large: {water_residual} m³/s"
    assert result.water_mass_balance_error_percent < 1.0e-4
    
    # 2. Total Solute Mass Balance: Qf * Cf = Qp * Cp + Qr * Cr
    c_f = result.feed_tds_kg_m3
    c_p = result.permeate_tds_kg_m3
    c_r = result.concentrate_tds_kg_m3
    
    solute_feed = q_f * c_f
    solute_outlets = (q_p * c_p) + (q_r * c_r)
    solute_residual = abs(solute_feed - solute_outlets)
    
    assert solute_residual < 1.0e-9, f"Solute balance residual too large: {solute_residual} kg/s"
    assert result.solute_mass_balance_error_percent < 1.0e-4


def test_mass_balance_modes_a_and_b():
    """Verify mass balance conservation holds in both Mode A and Mode B CP calculations."""
    for mode in ["mode_a", "mode_b"]:
        cfg = SimulationConfig(cp_mode=mode)
        res = simulate_ro(
            feed_flow=30.0,
            feed_tds=2000.0,
            pressure=15.5132,
            config=cfg
        )
        assert res.converged
        assert res.water_mass_balance_error_percent < 1.0e-4
        assert res.solute_mass_balance_error_percent < 1.0e-4
