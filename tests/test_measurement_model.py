"""
Unit Tests for Stage 7 Measurement Models and Sensor Sets.
"""

import pytest
import numpy as np

from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import (
    SensorSet,
    SensorClassification,
    ROPlantMeasurementModel,
    SENSOR_SET_MEMBERS,
    ALL_MEASUREMENT_DEFINITIONS,
)


def test_sensor_dimensions():
    """Verify sensor set dimension matches specification."""
    assert len(SENSOR_SET_MEMBERS[SensorSet.CASE_1_MINIMAL]) == 6
    assert len(SENSOR_SET_MEMBERS[SensorSet.CASE_2_STANDARD]) == 10
    assert len(SENSOR_SET_MEMBERS[SensorSet.CASE_3_RICH]) == 13


def test_measurement_forward_operator():
    """Verify observe() produces valid physical outputs."""
    meas_model = ROPlantMeasurementModel(sensor_set=SensorSet.CASE_2_STANDARD)
    st = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)
    u_inputs = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }

    obs = meas_model.observe(st, u_inputs)
    assert len(obs) == 10
    assert np.all(np.isfinite(obs))
    # Feed flow
    assert obs[0] == 30.0
    # Permeate flow > 0
    assert obs[4] > 10.0
    # Permeate TDS < Feed TDS
    assert obs[5] < 100.0


def test_sensor_classification_metadata():
    """Verify every candidate sensor has strict provenance classification."""
    for key, defn in ALL_MEASUREMENT_DEFINITIONS.items():
        assert defn.classification in [
            SensorClassification.COMMON_INDUSTRIAL_SENSOR,
            SensorClassification.OPTIONAL_SENSOR,
            SensorClassification.SYNTHETIC_NOT_DIRECTLY_MEASURED,
        ]
