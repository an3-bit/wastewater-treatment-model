"""
Unit Tests for Stage 7 State Representations & Dynamic State Transitions.
"""

import pytest
import numpy as np

from state_estimation.state_model import (
    StateRepresentation,
    StateVector,
    StateTransitionModel,
)
from fouling.model import RM_AUTHORITATIVE_M_INV, AW_AUTHORITATIVE_M_PA_S


def test_state_vector_conversions():
    """Verify lossless conversion between 15-element array and reduced representations."""
    # 1. Full 15-Element
    rf_15 = np.linspace(1e12, 1.5e13, 15)
    st15 = StateVector.from_15_element_array(rf_15, representation=StateRepresentation.FULL_15_ELEMENT)
    np.testing.assert_allclose(st15.to_15_element_array(), rf_15)

    # 2. Axial 6-Zone
    st6 = StateVector.from_15_element_array(rf_15, representation=StateRepresentation.AXIAL_6_ZONE)
    assert st6.values.shape == (6,)
    expanded_15 = st6.to_15_element_array()
    assert expanded_15.shape == (15,)
    # Verify symmetry in Stage 1 (vessels 1, 2, 3 should have identical elements)
    np.testing.assert_allclose(expanded_15[0], expanded_15[3])
    np.testing.assert_allclose(expanded_15[1], expanded_15[4])
    np.testing.assert_allclose(expanded_15[2], expanded_15[5])

    # 3. Lumped 2-Stage
    st2 = StateVector.from_15_element_array(rf_15, representation=StateRepresentation.LUMPED_2_STAGE)
    assert st2.values.shape == (2,)
    expanded_2_15 = st2.to_15_element_array()
    assert expanded_2_15.shape == (15,)
    # Stage 1 all equal
    np.testing.assert_allclose(expanded_2_15[0:9], st2.values[0])
    # Stage 2 all equal
    np.testing.assert_allclose(expanded_2_15[9:15], st2.values[1])


def test_permeability_and_decline_conversions():
    """Verify conversion to Aw and decline percentage."""
    st = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)
    aw_15 = st.to_effective_permeabilities_15(temperature_celsius=25.0)
    # Clean Aw should equal baseline Aw
    np.testing.assert_allclose(aw_15, AW_AUTHORITATIVE_M_PA_S, rtol=1e-4)

    decline = st.to_permeability_decline_pct_15(temperature_celsius=25.0)
    np.testing.assert_allclose(decline, 0.0, atol=1e-6)

    # Set Rf = Rm -> Permeability should halve (Aw = Aw_clean / 2, decline = 50%)
    st_half = StateVector(values=np.ones(6) * RM_AUTHORITATIVE_M_INV, representation=StateRepresentation.AXIAL_6_ZONE)
    aw_half = st_half.to_effective_permeabilities_15(temperature_celsius=25.0)
    np.testing.assert_allclose(aw_half, AW_AUTHORITATIVE_M_PA_S / 2.0, rtol=1e-4)
    decline_half = st_half.to_permeability_decline_pct_15(temperature_celsius=25.0)
    np.testing.assert_allclose(decline_half, 50.0, atol=1e-4)


def test_state_transition_monotonicity():
    """Verify forward state transition integrates positive growth."""
    transition_model = StateTransitionModel(representation=StateRepresentation.AXIAL_6_ZONE)
    st0 = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)
    u_inputs = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }

    st1 = transition_model.predict_next_state(st0, u_inputs, delta_t_hours=1.0)
    assert np.all(st1.values >= st0.values)
    assert np.all(st1.values > 0.0)
