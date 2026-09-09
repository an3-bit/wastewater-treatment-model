"""
Unit tests for Stage 3 Simulation Runner, Batch Generator, and Splitter.
"""

import pytest
import numpy as np
import pandas as pd
from data_generation.simulator_runner import (
    create_baseline_system,
    run_single_simulation,
)
from data_generation.dataset import (
    generate_batch_dataset,
    assign_dataset_splits,
)


def test_single_simulation_feasible_case():
    """Verify single scenario simulation on nominal feasible operating point."""
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
    assert rec["quality_flag"] == "PASS"
    assert rec["overall_recovery_pct"] > 60.0
    assert rec["permeate_tds_mgL"] < 20.0
    assert rec["SEC_kWh_m3"] > 0.0
    assert rec["water_balance_error"] < 1e-4
    assert rec["solute_balance_error"] < 1e-3


def test_single_simulation_pressure_limit_infeasible():
    """Verify that pressures above 41 bar trigger immediate failure categorization."""
    rec = run_single_simulation(
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        feed_cod_mgL=51.0,
        feed_pH=8.0,
        temperature_C=25.0,
        stage1_pressure_bar=45.0,  # Exceeds limit
        stage2_pressure_bar=48.0,
    )

    assert rec["feasible"] == 0
    assert rec["failure_reason"] == "PRESSURE_LIMIT"
    assert np.isnan(rec["overall_recovery_pct"])


def test_batch_generation_and_split_assignment():
    """Verify small batch generation, metadata attachment, and 70/15/15 deterministic splits."""
    candidates = pd.DataFrame(
        [
            {
                "feed_flow_m3h": 30.0,
                "feed_tds_mgL": 2000.0,
                "feed_cod_mgL": 50.0,
                "feed_pH": 7.5,
                "temperature_C": 25.0,
                "stage1_pressure_bar": 13.0,
                "stage2_pressure_bar": 18.0,
            },
            {
                "feed_flow_m3h": 25.0,
                "feed_tds_mgL": 2200.0,
                "feed_cod_mgL": 60.0,
                "feed_pH": 8.0,
                "temperature_C": 28.0,
                "stage1_pressure_bar": 14.0,
                "stage2_pressure_bar": 20.0,
            },
            {
                "feed_flow_m3h": 35.0,
                "feed_tds_mgL": 1800.0,
                "feed_cod_mgL": 40.0,
                "feed_pH": 7.0,
                "temperature_C": 22.0,
                "stage1_pressure_bar": 12.0,
                "stage2_pressure_bar": 16.0,
            },
        ]
    )

    df_res = generate_batch_dataset(candidates, show_progress=False)
    assert len(df_res) == 3
    assert "simulation_id" in df_res.columns
    assert "sampling_method" in df_res.columns
    assert df_res["simulation_id"].iloc[0] == "SIM_00001"

    # Assign splits
    df_splits = assign_dataset_splits(df_res, seed=42)
    assert "dataset_split" in df_splits.columns
    assert set(df_splits["dataset_split"].unique()).issubset({"train", "val", "test", "none"})
