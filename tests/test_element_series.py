"""
Unit and Integration Tests for Pressure Vessel and Membrane Elements in Series.
"""

import pytest
import numpy as np

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.vessel import PressureVessel, VesselResult


def test_pressure_vessel_series_conservation():
    """
    Verify 3 elements in series inside a PressureVessel:
    1. Overall fluid mass conservation (< 1e-9 m³/s residual)
    2. Overall solute mass conservation (< 1e-9 kg/s residual)
    3. Permeate flow equals sum of element permeate flows
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    vessel = PressureVessel(
        name="Vessel_Test_1",
        num_elements=3,
        element_properties=props,
        element_pressure_drop_bar=0.15
    )

    res = vessel.solve(
        feed_flow_m3_hr=10.0,
        feed_tds_mg_l=2041.0,
        feed_pressure_bar=20.0,
        temperature_celsius=25.0
    )

    assert res.converged is True
    assert len(res.element_results) == 3

    # 1 & 2. Mass and solute residuals
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9
    assert np.isclose(res.water_mass_balance_error_percent, 0.0, atol=1e-6)
    assert np.isclose(res.solute_mass_balance_error_percent, 0.0, atol=1e-6)

    # 3. Permeate flow summation
    sum_elem_qp = sum(e.permeate_flow_m3_hr for e in res.element_results)
    assert np.isclose(res.permeate_flow_m3_hr, sum_elem_qp, atol=1e-6)

    # 4. Solute mass balance in permeate
    sum_elem_solute = sum(e.permeate_flow_m3_s * e.permeate_tds_kg_m3 for e in res.element_results)
    vessel_solute = (res.permeate_flow_m3_hr / 3600.0) * (res.permeate_tds_mg_l * 1e-3)
    assert np.isclose(vessel_solute, sum_elem_solute, atol=1e-9)


def test_monotonic_profiles_along_vessel():
    """
    Verify physical profiles along series elements:
    - Salinity increases monotonically: Cf,1 < Cf,2 < Cf,3
    - Pressure decreases monotonically: Pf,1 > Pf,2 > Pf,3
    - Flux attenuates monotonically: Jw,1 > Jw,2 > Jw,3
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    vessel = PressureVessel(
        name="Vessel_Test_Monotonic",
        num_elements=3,
        element_properties=props,
        element_pressure_drop_bar=0.20
    )

    res = vessel.solve(
        feed_flow_m3_hr=12.0,
        feed_tds_mg_l=2000.0,
        feed_pressure_bar=18.0,
        temperature_celsius=25.0
    )

    e1, e2, e3 = res.element_results

    # Salinity increases
    assert e1.feed_tds_mg_l < e2.feed_tds_mg_l < e3.feed_tds_mg_l
    assert e1.concentrate_tds_mg_l < e2.concentrate_tds_mg_l < e3.concentrate_tds_mg_l

    # Pressure decreases
    assert e1.feed_pressure_bar > e2.feed_pressure_bar > e3.feed_pressure_bar

    # Flux attenuates
    assert e1.water_flux_lmh > e2.water_flux_lmh > e3.water_flux_lmh


def test_vessel_boundary_safeguards():
    """Verify safeguards trigger when feed pressure is insufficient or invalid."""
    vessel = PressureVessel(num_elements=3)
    
    # Non-positive feed flow
    with pytest.raises(ValueError, match="is non-positive"):
        vessel.solve(feed_flow_m3_hr=-5.0, feed_tds_mg_l=2000.0, feed_pressure_bar=15.0)

    # Pressure exceeding 41 bar max
    with pytest.raises(ValueError, match="exceeds maximum allowable limit"):
        vessel.solve(feed_flow_m3_hr=10.0, feed_tds_mg_l=2000.0, feed_pressure_bar=45.0)
