"""
Unit Tests for Unscented Kalman Filter (UKF) Functionality (Stage 7).
"""

import pytest
import numpy as np

from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import SensorSet, ROPlantMeasurementModel
from state_estimation.noise import NoiseLevel, SensorNoiseModel
from state_estimation.ukf import UnscentedKalmanFilter


def test_ukf_single_step():
    """Verify UKF step executes unscented transform, bounds state, and maintains valid covariance."""
    ukf = UnscentedKalmanFilter(
        representation=StateRepresentation.AXIAL_6_ZONE,
        sensor_set=SensorSet.CASE_2_STANDARD,
        noise_level=NoiseLevel.NOMINAL,
    )
    st0 = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)
    ukf.initialize(st0)

    u_inputs = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }

    meas_model = ROPlantMeasurementModel(sensor_set=SensorSet.CASE_2_STANDARD)
    y_true = meas_model.observe(st0, u_inputs)
    noise_model = SensorNoiseModel(noise_level=NoiseLevel.NOMINAL, random_seed=456)
    y_meas = noise_model.add_noise(y_true, ukf.sensor_keys)

    res = ukf.step(
        y_measured=y_meas,
        u_inputs=u_inputs,
        time_hours=1.0,
        delta_t_hours=1.0,
        true_state_for_benchmark=st0,
    )

    assert res.step_index == 0
    assert np.all(res.posterior_state.values >= 0.0)
    np.testing.assert_allclose(res.posterior_covariance, res.posterior_covariance.T, atol=1e-6)
    eigs = np.linalg.eigvalsh(res.posterior_covariance)
    assert np.all(eigs > 0.0)
    assert res.nis >= 0.0
