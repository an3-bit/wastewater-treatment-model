"""
Unit tests for ro_model.osmotic module.

Validates thermodynamic van 't Hoff calculations, temperature dependence,
concentration scaling, and boundary handling.
"""

import pytest
import numpy as np

from ro_model.osmotic import (
    calculate_osmotic_pressure_pa,
    calculate_osmotic_pressure_bar,
    calculate_osmotic_pressure_derivative,
    DEFAULT_NACL_MW_KG_MOL,
    DEFAULT_VANTHOFF_I
)
from ro_model.units import pa_to_bar, GAS_CONSTANT_R


def test_vanthoff_baseline_nacl():
    """
    Verify osmotic pressure for 2000 mg/L NaCl at 25 °C.
    
    C = 2000 mg/L = 2.0 kg/m³
    T = 298.15 K
    i = 2.0
    Mw = 0.058443 kg/mol
    C_molar = 2.0 / 0.058443 = 34.22137 mol/m³
    π = 2 * 34.22137 * 8.3144626 * 298.15 = 169658 Pa ≈ 1.6966 bar.
    """
    pi_pa = calculate_osmotic_pressure_pa(
        concentration_kg_m3=2.0,
        temperature_k=298.15,
        vanthoff_i=2.0,
        molar_mass_kg_mol=DEFAULT_NACL_MW_KG_MOL
    )
    pi_bar = pa_to_bar(pi_pa)
    
    expected_molarity = 2.0 / DEFAULT_NACL_MW_KG_MOL
    expected_pi_pa = 2.0 * expected_molarity * GAS_CONSTANT_R * 298.15
    
    assert np.isclose(pi_pa, expected_pi_pa)
    assert np.isclose(pi_bar, 1.6966, atol=1e-3)
    
    # Engineering unit helper
    pi_bar_eng = calculate_osmotic_pressure_bar(
        concentration_mg_l=2000.0,
        temperature_celsius=25.0,
        vanthoff_i=2.0,
        molar_mass_g_mol=58.443
    )
    assert np.isclose(pi_bar_eng, pi_bar)


def test_osmotic_zero_concentration():
    """Verify zero concentration gives exactly zero osmotic pressure."""
    pi_pa = calculate_osmotic_pressure_pa(0.0, 298.15)
    assert pi_pa == 0.0


def test_osmotic_temperature_dependence():
    """Verify osmotic pressure scales linearly with absolute temperature."""
    pi_25c = calculate_osmotic_pressure_pa(2.0, 298.15)
    pi_50c = calculate_osmotic_pressure_pa(2.0, 323.15)
    
    ratio = pi_50c / pi_25c
    expected_ratio = 323.15 / 298.15
    assert np.isclose(ratio, expected_ratio)


def test_osmotic_derivative():
    """Verify analytical derivative matches finite difference."""
    temp_k = 298.15
    d_pi_d_c = calculate_osmotic_pressure_derivative(temp_k)
    
    c1 = 2.0
    c2 = 2.001
    pi1 = calculate_osmotic_pressure_pa(c1, temp_k)
    pi2 = calculate_osmotic_pressure_pa(c2, temp_k)
    fd_deriv = (pi2 - pi1) / (c2 - c1)
    
    assert np.isclose(d_pi_d_c, fd_deriv, rtol=1e-5)


def test_osmotic_negative_inputs_raise():
    """Verify proper exceptions on non-physical inputs."""
    with pytest.raises(ValueError):
        calculate_osmotic_pressure_pa(-1.0, 298.15)
    with pytest.raises(ValueError):
        calculate_osmotic_pressure_pa(2.0, -10.0)
    with pytest.raises(ValueError):
        calculate_osmotic_pressure_pa(2.0, 298.15, vanthoff_i=-2.0)
