"""
Unit tests for Stage 3B Dataset Curation, Classification, and Safeguards.
"""

import pytest
import numpy as np
import pandas as pd
from data_generation.curation import (
    OperatingClassification,
    OODClassification,
    classify_scenario,
    compute_safeguard_sensitivities,
    compute_recovery_bands,
    curate_stage3_datasets,
)
from data_generation.simulator_runner import run_single_simulation


def test_classify_scenario_taxonomy():
    """Verify that scenarios are accurately mapped to the 4-tier taxonomy."""
    # Feasible & safe
    row_acceptable = {"feasible": 1, "maximum_element_recovery_pct": 22.5}
    assert classify_scenario(row_acceptable) == OperatingClassification.ENGINEERING_ACCEPTABLE

    # Feasible but boundary stress (> 30%)
    row_stress = {"feasible": 1, "maximum_element_recovery_pct": 35.0}
    assert classify_scenario(row_stress) == OperatingClassification.BOUNDARY_STRESS

    # Exactly at safeguard threshold
    row_boundary = {"feasible": 1, "maximum_element_recovery_pct": 30.0}
    assert classify_scenario(row_boundary) == OperatingClassification.ENGINEERING_ACCEPTABLE

    # Infeasible
    row_infeasible = {"feasible": 0, "maximum_element_recovery_pct": np.nan}
    assert classify_scenario(row_infeasible) == OperatingClassification.INFEASIBLE


def test_baseline_operating_point_classification():
    """Verify that the Stage 2 baseline operating point is firmly ENGINEERING_ACCEPTABLE."""
    rec = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=13.0,
        stage2_pressure_bar=18.0,
    )
    assert rec["feasible"] == 1
    assert rec["maximum_element_recovery_pct"] <= 30.0
    assert classify_scenario(rec) == OperatingClassification.ENGINEERING_ACCEPTABLE


def test_curation_dataset_creation_and_preservation(tmp_path):
    """Verify that curation preserves raw files and correctly partitions acceptable vs boundary."""
    df_raw_feasible = pd.DataFrame([
        {"simulation_id": "SIM_001", "feed_flow_m3h": 30.0, "maximum_element_recovery_pct": 20.0, "feasible": 1},
        {"simulation_id": "SIM_002", "feed_flow_m3h": 30.0, "maximum_element_recovery_pct": 28.0, "feasible": 1},
        {"simulation_id": "SIM_003", "feed_flow_m3h": 30.0, "maximum_element_recovery_pct": 32.0, "feasible": 1},
        {"simulation_id": "SIM_004", "feed_flow_m3h": 30.0, "maximum_element_recovery_pct": 45.0, "feasible": 1},
    ])
    df_raw_all = df_raw_feasible.copy()

    # Save mock files to tmp_path
    df_raw_all.to_csv(tmp_path / "stage3_all_scenarios.csv", index=False)
    df_raw_feasible.to_csv(tmp_path / "stage3_feasible_scenarios.csv", index=False)

    results = curate_stage3_datasets(raw_data_dir=str(tmp_path), max_element_recovery_threshold=30.0)
    df_acc = results["engineering_acceptable"]
    df_bnd = results["boundary_stress"]

    assert len(df_acc) == 2
    assert len(df_bnd) == 2
    assert (df_acc["maximum_element_recovery_pct"] <= 30.0).all()
    assert (df_bnd["maximum_element_recovery_pct"] > 30.0).all()
    assert set(df_acc["dataset_split"].unique()).issubset({"train", "val", "test"})


def test_safeguard_sensitivities_monotonicity():
    """Verify that sensitivity table counts increase monotonically with threshold."""
    df_mock = pd.DataFrame({
        "maximum_element_recovery_pct": [15.0, 22.0, 28.0, 33.0, 40.0]
    })
    sens_df = compute_safeguard_sensitivities(df_mock, thresholds=[20.0, 25.0, 30.0, 35.0])
    counts = sens_df["Accepted Scenarios"].to_list()
    assert counts == sorted(counts)
    assert counts[0] == 1  # <= 20%
    assert counts[1] == 2  # <= 25%
    assert counts[2] == 3  # <= 30%
    assert counts[3] == 4  # <= 35%
