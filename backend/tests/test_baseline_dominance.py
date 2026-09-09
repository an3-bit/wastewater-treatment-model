"""
Unit tests for baseline dominance analysis (src/optimization/pareto.py).
"""

import pytest
import numpy as np
import pandas as pd

from optimization.pareto import evaluate_baseline_dominance, AUTHORITATIVE_BASELINE


def test_baseline_non_dominated():
    """Verify that a Pareto front with mutual trade-offs classifies baseline as NON_DOMINATED."""
    # Baseline: R=65.4543%, SEC=0.824396, MaxElemRec=21.2441%
    df_pareto = pd.DataFrame([
        {"overall_recovery_pct": 55.0, "SEC_kWh_m3": 0.60, "maximum_element_recovery_pct": 15.0}, # Better SEC and stress, worse recovery
        {"overall_recovery_pct": 75.0, "SEC_kWh_m3": 0.95, "maximum_element_recovery_pct": 25.0}, # Better recovery, worse SEC and stress
    ])

    res = evaluate_baseline_dominance(df_pareto)
    assert res["baseline_status"] == "NON_DOMINATED"
    assert res["n_candidates_dominating_baseline"] == 0
    assert res["n_candidates_dominated_by_baseline"] == 0


def test_baseline_dominated():
    """Verify that a candidate with strictly better recovery and lower SEC & stress dominates baseline."""
    df_pareto = pd.DataFrame([
        {"overall_recovery_pct": 72.0, "SEC_kWh_m3": 0.70, "maximum_element_recovery_pct": 20.0}, # Dominates baseline across all 3
    ])

    res = evaluate_baseline_dominance(df_pareto)
    assert res["baseline_status"] == "DOMINATED"
    assert res["n_candidates_dominating_baseline"] == 1


def test_baseline_dominating():
    """Verify when baseline strictly dominates an inferior candidate."""
    df_pareto = pd.DataFrame([
        {"overall_recovery_pct": 60.0, "SEC_kWh_m3": 0.95, "maximum_element_recovery_pct": 25.0}, # Inferior in all 3
    ])

    res = evaluate_baseline_dominance(df_pareto)
    assert res["baseline_status"] == "DOMINATING"
    assert res["n_candidates_dominated_by_baseline"] == 1
