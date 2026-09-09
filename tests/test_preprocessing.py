"""
Unit Tests for Preprocessing and Anti-Leakage Isolation (Stage 4).
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from ml.preprocessing import (
    PreprocessingPipeline,
    FEATURE_COLUMNS,
    ALL_TARGETS,
    PRIMARY_TARGETS,
    SECONDARY_TARGETS,
)


@pytest.fixture
def sample_data():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "feed_flow_m3h": np.random.uniform(20, 40, n),
        "feed_tds_mgL": np.random.uniform(1500, 3000, n),
        "temperature_C": np.random.uniform(20, 35, n),
        "stage1_pressure_bar": np.random.uniform(10, 20, n),
        "stage2_pressure_bar": np.random.uniform(14, 28, n),
        "overall_recovery_pct": np.random.uniform(40, 80, n),
        "permeate_tds_mgL": np.random.uniform(2, 10, n),
        "concentrate_tds_mgL": np.random.uniform(3000, 10000, n),
        "average_flux_LMH": np.random.uniform(10, 30, n),
        "SEC_kWh_m3": np.random.uniform(0.5, 1.5, n),
        "maximum_element_recovery_pct": np.random.uniform(15, 29, n),
        "maximum_polarization_modulus": np.random.uniform(1.05, 1.25, n),
    })
    return df


def test_preprocessing_pipeline_fit_transform(sample_data):
    pipe = PreprocessingPipeline()
    assert not pipe.fitted

    pipe.fit(sample_data)
    assert pipe.fitted
    assert len(pipe.target_scalers) == len(ALL_TARGETS)

    # Transform features
    X_scaled = pipe.transform_features(sample_data)
    assert X_scaled.shape == (len(sample_data), 5)
    np.testing.assert_allclose(X_scaled.mean(axis=0), 0.0, atol=1e-7)
    np.testing.assert_allclose(X_scaled.std(axis=0), 1.0, atol=1e-7)


def test_target_inverse_transform(sample_data):
    pipe = PreprocessingPipeline().fit(sample_data)

    for tgt in ALL_TARGETS:
        y_scaled = pipe.transform_target(sample_data, tgt)
        y_recon = pipe.inverse_transform_target(y_scaled, tgt)
        np.testing.assert_allclose(y_recon, sample_data[tgt].to_numpy(), rtol=1e-5, atol=1e-5)


def test_unfitted_pipeline_raises():
    pipe = PreprocessingPipeline()
    dummy_df = pd.DataFrame({"feed_flow_m3h": [30.0]})
    with pytest.raises(RuntimeError):
        pipe.transform_features(dummy_df)
