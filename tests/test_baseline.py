"""
Integration and validation tests for the baseline RO membrane model.
"""

import pytest
import numpy as np
import yaml

from ro_model.solver import simulate_ro, solve_membrane_element
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig,
    MembraneElement
)
from ro_model.validation import validate_physical_bounds
from ro_model.units import psi_to_bar, bar_to_pa


def test_baseline_simulation_convergence():
    """
    Verify baseline simulation runs and converges using exact Sowgath et al. (2025) values:
    Qf = 30 m³/h, Cf = 2000 mg/L, Pf = 225 psi (15.5132 bar), T = 25 °C, Am = 37 m².
    """
    res = simulate_ro(
        feed_flow=30.0,
        feed_tds=2000.0,
        pressure=225.0,
        temperature=25.0,
        pressure_unit="psi"
    )
    
    assert res.converged is True
    assert res.feed_flow_m3_hr == 30.0
    assert np.isclose(res.feed_pressure_psi, 225.0, atol=1e-2)
    assert np.isclose(res.feed_pressure_bar, 15.5132, atol=1e-3)
    assert res.feed_tds_mg_l == 2000.0
    assert res.temperature_celsius == 25.0
    
    # Check separation performance
    assert 0.0 < res.water_recovery_fraction < 1.0
    assert 0.0 < res.salt_rejection_fraction < 1.0
    assert res.salt_rejection_percent > 95.0
    
    # Check fluxes
    assert res.water_flux_lmh > 0.0
    assert res.water_flux_m_s > 0.0
    assert res.salt_flux_kg_m2_s > 0.0
    
    # Check osmotic pressures
    assert np.isclose(res.feed_osmotic_pressure_bar, 1.6966, atol=1e-2)
    assert res.membrane_surface_osmotic_pressure_bar >= res.feed_osmotic_pressure_bar
    assert res.permeate_osmotic_pressure_bar < res.feed_osmotic_pressure_bar
    
    # Check energy model
    assert res.hydraulic_power_kw > 0.0
    assert res.pump_electrical_power_kw > res.hydraulic_power_kw
    assert res.sec_kwh_per_m3 > 0.0
    
    # Validate physical checks
    checks = validate_physical_bounds(res)
    for check_name, passed in checks.items():
        assert passed, f"Sanity check '{check_name}' failed."


def test_recovery_and_rejection_formulas():
    """Verify recovery and rejection equations match theoretical definitions."""
    res = simulate_ro(
        feed_flow=30.0,
        feed_tds=2000.0,
        pressure=15.5132,
        temperature=25.0,
        pressure_unit="bar"
    )
    
    expected_wr = res.permeate_flow_m3_s / res.feed_flow_m3_s
    assert np.isclose(res.water_recovery_fraction, expected_wr)
    assert np.isclose(res.water_recovery_percent, expected_wr * 100.0)
    
    expected_sr = 1.0 - (res.permeate_tds_kg_m3 / res.feed_tds_kg_m3)
    assert np.isclose(res.salt_rejection_fraction, expected_sr)
    assert np.isclose(res.salt_rejection_percent, expected_sr * 100.0)


def test_max_pressure_safeguard():
    """Verify error is raised when operating pressure exceeds 41 bar limit."""
    with pytest.raises(ValueError, match="exceeds maximum allowable limit"):
        simulate_ro(
            feed_flow=30.0,
            feed_tds=2000.0,
            pressure=42.0,  # > 41 bar
            pressure_unit="bar"
        )


def test_insufficient_driving_pressure_safeguard():
    """Verify error is raised when feed pressure is lower than osmotic pressure."""
    # Feed TDS 2000 mg/L gives ~1.7 bar osmotic pressure. Pressure of 1.2 bar is insufficient.
    with pytest.raises(ValueError, match="less than feed osmotic pressure"):
        simulate_ro(
            feed_flow=30.0,
            feed_tds=2000.0,
            pressure=1.2,
            pressure_unit="bar"
        )


def test_load_from_yaml():
    """Verify loading baseline parameters from config/baseline.yaml matches defaults."""
    with open("config/baseline.yaml", "r") as f:
        config_data = yaml.safe_load(f)
        
    mem_props = MembraneElementProperties.from_config_dict(config_data)
    sim_cfg = SimulationConfig.from_config_dict(config_data)
    
    assert mem_props.membrane_area_m2 == 37.0
    assert np.isclose(mem_props.Aw_m_pa_s, 9.08e-10)
    assert mem_props.As_m_s == 1.1834e-9
    assert sim_cfg.pump_efficiency == 0.80
    assert sim_cfg.vanthoff_factor == 2.0
    
    res = simulate_ro(
        feed_flow=config_data["source_reported"]["feed_flow"],
        feed_tds=config_data["source_reported"]["feed_concentration"],
        pressure=config_data["source_reported"]["feed_pressure_bar"],
        membrane_properties=mem_props,
        config=sim_cfg
    )
    assert res.converged


def test_manufacturer_validation_acceptance_criteria():
    """
    Verify Stage 1 Manufacturer Validation Run for Toray TML20D-400:
    - Area = 37.0 m²
    - Qf = 11.028 m³/h, Cf = 2000 mg/L NaCl, Pf = 15.5132 bar (225 psi), T = 25 °C
    - Aw = 1.0232e-11 m/(Pa·s) = 1.0232e-6 m/(bar·s)
    - As = 1.1834e-9 m/s
    - k = 5.0e-5 m/s

    Acceptance criteria:
    1. Water flux error <= 5%
    2. Water recovery error <= 5% relative
    3. Salt rejection >= 99.65% (Min spec)
    4. Water balance residual <= 1e-9 m³/s
    5. Solute balance residual <= 1e-9 kg/s
    """
    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,
        As_m_s=1.1834e-9
    )
    cfg = SimulationConfig(
        pump_efficiency=0.80,
        mass_transfer_coefficient=5.0e-5,
        pressure_drop_pa=0.0
    )

    res = simulate_ro(
        feed_flow=11.028,
        feed_tds=2000.0,
        pressure=15.5132,
        pressure_unit="bar",
        temperature=25.0,
        membrane_properties=props,
        config=cfg
    )

    assert res.converged is True

    # Criterion 1: Water flux error <= 5% (nominal: 44.71 LMH)
    flux_err_pct = abs(res.water_flux_lmh - 44.71) / 44.71 * 100.0
    assert flux_err_pct <= 5.0

    # Criterion 2: Recovery error <= 5% relative (nominal: 15.00%)
    rec_err_pct = abs(res.water_recovery_percent - 15.00) / 15.00 * 100.0
    assert rec_err_pct <= 5.0

    # Criterion 3: Salt rejection >= 99.65% (minimum specification)
    assert res.salt_rejection_percent >= 99.65

    # Criteria 4 & 5: Residuals within numerical tolerance
    assert res.water_mass_balance_error_m3_s <= 1.0e-9
    assert res.solute_mass_balance_error_kg_s <= 1.0e-9

