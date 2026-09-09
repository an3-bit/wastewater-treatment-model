"""
Unit Tests for Virtual Sensor Threshold Forecasting (Stage 7).
"""

import pytest
import numpy as np

from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.forecasting import VirtualSensorForecaster
from fouling.model import RM_AUTHORITATIVE_M_INV


def test_virtual_sensor_forecast():
    """Verify forward projection correctly computes decline trajectory and thresholds."""
    forecaster = VirtualSensorForecaster(max_horizon_hours=168.0, dt_hours=2.0)
    st0 = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)

    u_forecast = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }

    res = forecaster.forecast(st0, u_forecast, current_time_hours=0.0)

    assert len(res.forecast_timestamps_hours) > 1
    assert len(res.predicted_decline_pct_trajectory) == len(res.forecast_timestamps_hours)
    assert res.predicted_decline_pct_trajectory[0] == 0.0
    assert res.predicted_decline_pct_trajectory[-1] > 0.0

    # Monotonicity of projected decline
    diffs = np.diff(res.predicted_decline_pct_trajectory)
    assert np.all(diffs >= 0.0)

    # Threshold ordering
    if res.predicted_t5_hours is not None and res.predicted_t10_hours is not None:
        assert res.predicted_t5_hours < res.predicted_t10_hours
    if res.predicted_t10_hours is not None and res.predicted_t15_hours is not None:
        assert res.predicted_t10_hours < res.predicted_t15_hours
