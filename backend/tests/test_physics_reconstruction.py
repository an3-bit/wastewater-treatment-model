"""
Unit Tests for Physics-Reconstructed Inference Mode (Stage 4B).
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from ml.inference import Stage4Surrogate
from ml.physics_checks import BASELINE_POINT


@pytest.fixture
def trained_ann_surrogate():
    models_dir = Path("models/stage4")
    if not (models_dir / "ann___mlp").exists():
        pytest.skip("Trained ANN model artifacts not found in models/stage4/ann___mlp")
    return Stage4Surrogate.load(models_dir, "ann___mlp", is_neural_net=True)


def test_physics_reconstructed_mode_solute_balance_closure(trained_ann_surrogate):
    """Verify that PHYSICS_RECONSTRUCTED mode closes fluid and solute balances to numerical precision."""
    df_in = pd.DataFrame([{
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2000.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }])

    res = trained_ann_surrogate.predict_physics_reconstructed(df_in)

    # Check required columns
    assert "permeate_flow_m3h" in res.columns
    assert "concentrate_flow_m3h" in res.columns
    assert "concentrate_tds_mgL" in res.columns
    assert "diagnostic_concentrate_tds_mgL" in res.columns
    assert "concentrate_tds_discrepancy_pct" in res.columns
    assert "solute_balance_error_kg_s" in res.columns

    # 1. Total flow balance: Qf = Qp + Qr
    qf = 30.0
    qp = float(res["permeate_flow_m3h"].iloc[0])
    qr = float(res["concentrate_flow_m3h"].iloc[0])
    np.testing.assert_allclose(qp + qr, qf, rtol=1e-6)

    # 2. Total solute balance: Qf*Cf = Qp*Cp + Qr*Cr
    cf = 2000.0
    cp = float(res["permeate_tds_mgL"].iloc[0])
    cr = float(res["concentrate_tds_mgL"].iloc[0])
    solute_in = qf * cf
    solute_out = qp * cp + qr * cr
    np.testing.assert_allclose(solute_in, solute_out, rtol=1e-5)
    assert abs(res["solute_balance_error_kg_s"].iloc[0]) < 1e-10


def test_direct_vs_reconstructed_discrepancy_small_in_domain(trained_ann_surrogate):
    """In-domain operating points must show < 2% discrepancy between direct and reconstructed Cr."""
    df_in = pd.DataFrame([BASELINE_POINT])
    res = trained_ann_surrogate.predict_physics_reconstructed(df_in)
    disc_pct = float(res["concentrate_tds_discrepancy_pct"].iloc[0])
    assert disc_pct < 2.0, f"Expected <2% discrepancy at baseline, got {disc_pct:.2f}%"
