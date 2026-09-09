"""
Unit and Integration Tests for ROStage with Parallel Pressure Vessels.
"""

import pytest
import numpy as np

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.stage import ROStage, StageResult


def test_stage_parallel_vessels_conservation():
    """
    Verify ROStage with 4 parallel pressure vessels (each with 3 elements):
    - Mass conservation (< 1e-9 m³/s residual)
    - Solute conservation (< 1e-9 kg/s residual)
    - Total permeate flow = M * vessel permeate flow
    - Total concentrate flow = M * vessel concentrate flow
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    num_vessels = 4
    stage = ROStage(
        name="Stage_1_Test",
        parallel_vessels=num_vessels,
        elements_per_vessel=3,
        element_properties=props,
        element_pressure_drop_bar=0.15
    )

    feed_q_hr = 30.0  # m³/h
    feed_tds = 2041.0 # mg/L
    feed_p = 20.0     # bar

    res = stage.solve(
        feed_flow_m3_hr=feed_q_hr,
        feed_tds_mg_l=feed_tds,
        feed_pressure_bar=feed_p,
        temperature_celsius=25.0
    )

    assert res.converged is True
    assert res.parallel_vessels == num_vessels
    assert res.total_elements == 12
    assert res.total_membrane_area_m2 == 12 * 37.0

    # Parallel scaling checks
    v_res = res.vessel_result
    assert np.isclose(res.permeate_flow_m3_hr, v_res.permeate_flow_m3_hr * num_vessels)
    assert np.isclose(res.concentrate_flow_m3_hr, v_res.concentrate_flow_m3_hr * num_vessels)
    assert np.isclose(res.permeate_tds_mg_l, v_res.permeate_tds_mg_l)
    assert np.isclose(res.concentrate_tds_mg_l, v_res.concentrate_tds_mg_l)

    # Residuals
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9
    assert np.isclose(res.water_mass_balance_error_percent, 0.0, atol=1e-6)
    assert np.isclose(res.solute_mass_balance_error_percent, 0.0, atol=1e-6)

    # Energy
    assert res.hydraulic_power_kw > 0.0
    assert res.electrical_power_kw > res.hydraulic_power_kw
    assert res.sec_kwh_per_m3 > 0.0


def test_invalid_stage_parameters():
    """Verify safeguards trigger for invalid vessel counts."""
    with pytest.raises(ValueError, match="parallel_vessels must be >= 1"):
        stage = ROStage(parallel_vessels=0)
        stage.solve(feed_flow_m3_hr=30.0, feed_tds_mg_l=2000.0, feed_pressure_bar=15.0)
