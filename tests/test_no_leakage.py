"""
Unit Tests for Strict Anti-Leakage Isolation (Stage 4).
"""

import pytest
import numpy as np
import pandas as pd
from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS


def test_anti_leakage_statistics():
    """Verify that fit statistics are calculated strictly on train data and not on test data."""
    # Create two distinct distributions for train and test
    df_train = pd.DataFrame({
        "feed_flow_m3h": [20.0, 25.0, 30.0],
        "feed_tds_mgL": [1500.0, 2000.0, 2500.0],
        "temperature_C": [20.0, 25.0, 30.0],
        "stage1_pressure_bar": [10.0, 12.0, 14.0],
        "stage2_pressure_bar": [15.0, 18.0, 21.0],
        "overall_recovery_pct": [50.0, 60.0, 70.0],
        "permeate_tds_mgL": [5.0, 6.0, 7.0],
        "concentrate_tds_mgL": [4000.0, 5000.0, 6000.0],
        "average_flux_LMH": [15.0, 20.0, 25.0],
        "SEC_kWh_m3": [0.8, 1.0, 1.2],
        "maximum_element_recovery_pct": [20.0, 22.0, 24.0],
        "maximum_polarization_modulus": [1.1, 1.15, 1.2],
    })

    df_test = pd.DataFrame({
        "feed_flow_m3h": [35.0, 40.0],
        "feed_tds_mgL": [2800.0, 3000.0],
        "temperature_C": [32.0, 35.0],
        "stage1_pressure_bar": [16.0, 18.0],
        "stage2_pressure_bar": [24.0, 26.0],
        "overall_recovery_pct": [75.0, 80.0],
        "permeate_tds_mgL": [8.0, 9.0],
        "concentrate_tds_mgL": [7000.0, 8000.0],
        "average_flux_LMH": [28.0, 30.0],
        "SEC_kWh_m3": [1.4, 1.6],
        "maximum_element_recovery_pct": [26.0, 28.0],
        "maximum_polarization_modulus": [1.22, 1.25],
    })

    pipeline = PreprocessingPipeline().fit(df_train)

    # Input scaler mean must match train mean exactly
    expected_train_mean = df_train[FEATURE_COLUMNS].mean().to_numpy()
    np.testing.assert_allclose(pipeline.input_scaler.mean_, expected_train_mean, rtol=1e-6)

    # Transform test set and ensure it uses train statistics
    X_test_scaled = pipeline.transform_features(df_test)
    expected_X_test_scaled = (df_test[FEATURE_COLUMNS].to_numpy() - pipeline.input_scaler.mean_) / pipeline.input_scaler.scale_
    np.testing.assert_allclose(X_test_scaled, expected_X_test_scaled, rtol=1e-6)
