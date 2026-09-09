"""
Unit Tests for Physics Consistency and Mass Balance Reconstruction (Stage 4).
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from ml.preprocessing import FEATURE_COLUMNS, ALL_TARGETS
from ml.physics_checks import (
    check_physics_monotonicity,
    evaluate_mass_balance_reconstruction,
    BASELINE_POINT,
)


def test_check_physics_monotonicity():
    # Construct synthetic monotonically increasing recovery with P1
    df_sweep = pd.DataFrame({
        "ml_overall_recovery_pct": np.linspace(50.0, 75.0, 10),
        "ml_average_flux_LMH": np.linspace(15.0, 25.0, 10),
        "ml_SEC_kWh_m3": np.linspace(0.8, 1.2, 10),
        "ml_concentrate_tds_mgL": np.linspace(4000.0, 7000.0, 10),
    })

    flags = check_physics_monotonicity(df_sweep, "stage1_pressure_bar")
    assert flags["recovery_trend"] == "PHYSICS_CONSISTENT"
    assert flags["flux_trend"] == "PHYSICS_CONSISTENT"


def test_mass_balance_reconstruction():
    # Ideal physical data with 0 solute error
    qf = 30.0
    cf = 2000.0
    rec = 70.0
    qp = qf * (rec / 100.0)  # 21.0
    qr = qf - qp            # 9.0
    cp = 10.0               # 10 mg/L
    # (30 * 2000 - 21 * 10) / 9 = (60000 - 210) / 9 = 59790 / 9 = 6643.33 mg/L
    cr = (qf * cf - qp * cp) / qr

    df_inputs = pd.DataFrame([{"feed_flow_m3h": qf, "feed_tds_mgL": cf}])
    df_preds = pd.DataFrame([{
        "overall_recovery_pct": rec,
        "permeate_tds_mgL": cp,
        "concentrate_tds_mgL": cr,
    }])

    res = evaluate_mass_balance_reconstruction(df_preds, df_inputs)
    assert len(res) == 1
    assert abs(res["solute_error_percent"].iloc[0]) < 1e-4
