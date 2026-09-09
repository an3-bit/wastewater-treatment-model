"""
Unit Tests for Stage 4 Inference and Model Serialization.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS
from ml.inference import Stage4Surrogate
from ml.train import train_linear_regression


@pytest.fixture
def sample_dataset():
    np.random.seed(42)
    n = 50
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


def test_stage4_surrogate_prediction(sample_dataset, tmp_path):
    lr_models = train_linear_regression(sample_dataset)
    surrogate = Stage4Surrogate(
        model_name="Linear_Regression",
        models=lr_models,
        is_neural_net=False,
    )

    # 1. Predict with DataFrame
    preds_df = surrogate.predict(sample_dataset)
    assert len(preds_df) == len(sample_dataset)
    for tgt in ALL_TARGETS:
        assert tgt in preds_df.columns

    # 2. Predict with Dict (scalar)
    single_dict = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2000.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }
    preds_dict = surrogate.predict(single_dict)
    assert len(preds_dict) == 1
    assert "overall_recovery_pct" in preds_dict.columns

    # 3. Test Save and Load
    saved_path = surrogate.save(tmp_path / "models")
    loaded_surrogate = Stage4Surrogate.load(saved_path, model_name="Linear_Regression", is_neural_net=False)
    preds_loaded = loaded_surrogate.predict(sample_dataset)

    np.testing.assert_allclose(preds_df.to_numpy(), preds_loaded.to_numpy(), rtol=1e-6)
