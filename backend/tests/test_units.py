"""
Unit tests for ro_model.units module.

Tests bi-directional conversions across pressure, flow, concentration, flux,
permeability, temperature, and energy units.
"""

import pytest
import numpy as np

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    psi_to_pa,
    pa_to_psi,
    psi_to_bar,
    bar_to_psi,
    m3_per_hr_to_m3_per_s,
    m3_per_s_to_m3_per_hr,
    m3_per_day_to_m3_per_s,
    m3_per_s_to_m3_per_day,
    l_per_hr_to_m3_per_s,
    m3_per_s_to_l_per_hr,
    mg_per_l_to_kg_per_m3,
    kg_per_m3_to_mg_per_l,
    conc_to_molarity,
    molarity_to_conc,
    m_per_s_to_lmh,
    lmh_to_m_per_s,
    aw_bar_to_pa,
    aw_pa_to_bar,
    celsius_to_kelvin,
    kelvin_to_celsius,
    watts_to_kw,
    kw_to_watts,
    specific_energy_j_to_kwh_per_m3,
)


def test_pressure_conversions():
    """Verify pressure conversions between bar, Pa, and psi."""
    # 1 bar = 100,000 Pa
    assert bar_to_pa(1.0) == 100000.0
    assert pa_to_bar(100000.0) == 1.0
    
    # 225 psi ≈ 15.5132 bar
    p_pa = psi_to_pa(225.0)
    p_bar = psi_to_bar(225.0)
    assert np.isclose(p_bar, 15.5132, atol=1e-3)
    assert np.isclose(pa_to_psi(p_pa), 225.0)
    assert np.isclose(bar_to_psi(p_bar), 225.0)


def test_flow_conversions():
    """Verify volumetric flow rate conversions."""
    # 30 m³/h = 30 / 3600 m³/s
    q_s = m3_per_hr_to_m3_per_s(30.0)
    assert np.isclose(q_s, 30.0 / 3600.0)
    assert np.isclose(m3_per_s_to_m3_per_hr(q_s), 30.0)
    
    # m³/day conversions
    q_day_s = m3_per_day_to_m3_per_s(36.0)
    assert np.isclose(m3_per_s_to_m3_per_day(q_day_s), 36.0)
    
    # L/h conversions
    q_l_s = l_per_hr_to_m3_per_s(3600.0)
    assert np.isclose(m3_per_s_to_l_per_hr(q_l_s), 3600.0)


def test_concentration_and_molarity():
    """Verify concentration and molarity conversions."""
    # 2000 mg/L = 2.0 kg/m³ = 2.0 g/L
    c_kg_m3 = mg_per_l_to_kg_per_m3(2000.0)
    assert np.isclose(c_kg_m3, 2.0)
    assert np.isclose(kg_per_m3_to_mg_per_l(c_kg_m3), 2000.0)
    
    # NaCl molarity: 2.0 kg/m³ / 0.05844 kg/mol ≈ 34.223 mol/m³
    mw_nacl = 0.058443
    molarity = conc_to_molarity(2.0, mw_nacl)
    assert np.isclose(molarity, 2.0 / mw_nacl)
    assert np.isclose(molarity_to_conc(molarity, mw_nacl), 2.0)
    
    with pytest.raises(ValueError):
        conc_to_molarity(2.0, -0.05)


def test_flux_conversions():
    """Verify water flux conversions between m/s and LMH."""
    # 1 m/s = 3.6e6 LMH
    flux_m_s = 1.0e-5
    flux_lmh = m_per_s_to_lmh(flux_m_s)
    assert np.isclose(flux_lmh, 36.0)
    assert np.isclose(lmh_to_m_per_s(36.0), 1.0e-5)


def test_permeability_conversions():
    """Verify Aw conversions between m/(bar·s) and m/(Pa·s)."""
    aw_bar = 9.08e-5  # m/(bar·s)
    aw_pa = aw_bar_to_pa(aw_bar)
    assert np.isclose(aw_pa, 9.08e-10)
    assert np.isclose(aw_pa_to_bar(aw_pa), 9.08e-5)


def test_temperature_conversions():
    """Verify temperature conversions between °C and K."""
    assert celsius_to_kelvin(25.0) == 298.15
    assert kelvin_to_celsius(298.15) == 25.0
    assert celsius_to_kelvin(0.0) == 273.15


def test_energy_conversions():
    """Verify power and energy unit conversions."""
    assert watts_to_kw(5000.0) == 5.0
    assert kw_to_watts(5.0) == 5000.0
    
    # 3.6e6 J/m³ = 1 kWh/m³
    assert np.isclose(specific_energy_j_to_kwh_per_m3(3.6e6), 1.0)
