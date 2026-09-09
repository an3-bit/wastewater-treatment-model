"""
Unit tests for Pareto post-processing, non-dominated sorting, and knee selection (src/optimization/pareto.py).
"""

import pytest
import numpy as np
import pandas as pd

from optimization.pareto import (
    find_non_dominated_front,
    select_knee_solution,
    select_representative_solutions,
)


def test_find_non_dominated_front():
    """Verify non-dominated filtering in 3D objective space."""
    # Create candidate points
    # Objective 1: Maximize recovery (f1 = -recovery)
    # Objective 2: Minimize SEC (f2 = SEC)
    # Objective 3: Minimize Max Element Recovery (f3 = MaxElemRec)
    df = pd.DataFrame([
        {"stage1_pressure_bar": 10.0, "stage2_pressure_bar": 14.0, "overall_recovery_pct": 60.0, "SEC_kWh_m3": 0.60, "maximum_element_recovery_pct": 18.0}, # Non-dominated (low SEC, low stress)
        {"stage1_pressure_bar": 13.0, "stage2_pressure_bar": 18.0, "overall_recovery_pct": 70.0, "SEC_kWh_m3": 0.77, "maximum_element_recovery_pct": 23.0}, # Non-dominated (intermediate)
        {"stage1_pressure_bar": 16.0, "stage2_pressure_bar": 24.0, "overall_recovery_pct": 80.0, "SEC_kWh_m3": 1.00, "maximum_element_recovery_pct": 28.0}, # Non-dominated (high recovery)
        {"stage1_pressure_bar": 12.0, "stage2_pressure_bar": 16.0, "overall_recovery_pct": 58.0, "SEC_kWh_m3": 0.85, "maximum_element_recovery_pct": 24.0}, # Strictly dominated by #1 and #2
    ])

    front = find_non_dominated_front(df)
    assert len(front) == 3
    # The dominated candidate (58% recovery, 0.85 SEC) must be excluded
    assert not any(front["overall_recovery_pct"] == 58.0)


def test_select_representative_solutions():
    """Verify selection of Max Recovery, Min SEC, Min Stress, and Knee solutions."""
    df_pareto = pd.DataFrame([
        {"stage1_pressure_bar": 10.0, "stage2_pressure_bar": 14.0, "overall_recovery_pct": 60.0, "SEC_kWh_m3": 0.55, "maximum_element_recovery_pct": 18.0, "permeate_tds_mgL": 10.0},
        {"stage1_pressure_bar": 13.0, "stage2_pressure_bar": 18.0, "overall_recovery_pct": 70.0, "SEC_kWh_m3": 0.75, "maximum_element_recovery_pct": 23.0, "permeate_tds_mgL": 7.0},
        {"stage1_pressure_bar": 16.0, "stage2_pressure_bar": 24.0, "overall_recovery_pct": 80.0, "SEC_kWh_m3": 1.05, "maximum_element_recovery_pct": 28.0, "permeate_tds_mgL": 5.0},
    ])

    reps = select_representative_solutions(df_pareto)

    assert reps["max_recovery"]["overall_recovery_pct"] == 80.0
    assert reps["min_energy"]["SEC_kWh_m3"] == 0.55
    assert reps["min_stress"]["maximum_element_recovery_pct"] == 18.0
    assert "balanced_knee" in reps
    assert "knee_ideal_distance" in reps["balanced_knee"]
