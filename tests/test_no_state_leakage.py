"""
Unit Tests for Strict Anti-Leakage Isolation (Stage 7).
Ensures hidden ground-truth membrane properties are never accessible to estimator inputs.
"""

import pytest
from state_estimation.measurement_model import (
    SensorSet,
    SENSOR_SET_MEMBERS,
    PROHIBITED_MEASUREMENTS,
    ALL_MEASUREMENT_DEFINITIONS,
)


def test_no_hidden_states_in_sensor_sets():
    """Verify that no prohibited true states appear in any active sensor set."""
    for s_set, member_list in SENSOR_SET_MEMBERS.items():
        for sensor_name in member_list:
            for prohibited in PROHIBITED_MEASUREMENTS:
                assert prohibited not in sensor_name.lower(), (
                    f"DATA LEAKAGE VIOLATION: Prohibited quantity '{prohibited}' "
                    f"found in active sensor set '{s_set.value}' (sensor: '{sensor_name}')!"
                )


def test_measurement_dictionary_isolation():
    """Verify that true Rf, Aeff, beta, Cm are strictly excluded from measurement definitions."""
    for key, defn in ALL_MEASUREMENT_DEFINITIONS.items():
        assert "rf" not in key.lower()
        assert "aeff" not in key.lower()
        assert "polarization" not in key.lower()
        assert "surface_tds" not in key.lower()
