"""
Unit tests for core fouling data structures, conversions, and calibration routines.
"""

import pytest
import numpy as np

from fouling.model import (
    FoulingParameters,
    calculate_water_viscosity,
    calculate_clean_membrane_resistance,
    resistance_to_permeability,
)
from fouling.calibration import calibrate_fouling_rate_constant
from fouling.cleaning import apply_cleaning_event


def test_viscosity_and_clean_resistance():
    """Verify physical temperature scaling of water viscosity and Darcy clean resistance."""
    # At 25 C: mu ~ 8.90e-4 Pa.s
    mu25 = calculate_water_viscosity(25.0)
    assert 8.8e-4 < mu25 < 9.0e-4

    # At 20 C: mu should be higher (~1.00e-3 Pa.s)
    mu20 = calculate_water_viscosity(20.0)
    assert mu20 > mu25

    # R_m from Aw = 1.0232e-11 m/(Pa.s)
    rm25 = calculate_clean_membrane_resistance(1.0232e-11, 25.0)
    assert 1.0e14 < rm25 < 1.2e14

    # Invert back to permeability
    aw_back = resistance_to_permeability(rm25, 25.0)
    assert abs(aw_back - 1.0232e-11) < 1e-15


def test_fouling_calibration():
    """Verify that calibrate_fouling_rate_constant hits target 15% decline at 625 L/m2."""
    calib = calibrate_fouling_rate_constant(
        target_decline_pct=15.0,
        target_cum_volume_l_m2=625.0,
        benchmark_recovery_pct=60.0,
    )

    assert calib.calibrated_r_spec > 0.0
    assert abs(calib.achieved_permeability_decline_pct - 15.0) < 1e-6
    assert calib.residual_abs_error_pct < 1e-6
    assert calib.identifiability_status == "EXACTLY_IDENTIFIED_SINGLE_PARAMETER"


def test_cleaning_event_restoration():
    """Verify that chemical cleaning event properly reduces Rf according to eta_clean."""
    sim_params = FoulingParameters.create_default(cleaning_efficiency=0.90)
    from fouling.model import ElementFoulingState

    # Create dummy fouled element state with Rf = 1e13
    elem = ElementFoulingState(
        stage_index=1,
        element_index=1,
        global_element_id="Stage1_Vessel1_Elem1",
        r_f_m_inv=1.0e13,
        r_total_m_inv=sim_params.r_m_m_inv + 1.0e13,
        permeability_ratio=sim_params.r_m_m_inv / (sim_params.r_m_m_inv + 1.0e13),
    )

    restored = apply_cleaning_event([elem], cleaning_efficiency=0.90, parameters=sim_params)
    assert len(restored) == 1
    # 90% removed => 10% remains => Rf = 1e12
    assert abs(restored[0].r_f_m_inv - 1.0e12) < 1e6
    assert restored[0].permeability_ratio > elem.permeability_ratio
