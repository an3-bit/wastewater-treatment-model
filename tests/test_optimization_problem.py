"""
Unit tests for ROOperatingOptimizationProblem (src/optimization/problem.py).
"""

import pytest
import numpy as np
import pandas as pd

from optimization.problem import ROOperatingOptimizationProblem
from ml.domain_guard import OptimizationDomainGuard


def test_problem_initialization():
    """Verify default problem dimensions, bounds, and constraint setup."""
    guard = OptimizationDomainGuard.from_training_dataset()
    prob = ROOperatingOptimizationProblem(domain_guard=guard)

    assert prob.n_var == 2
    assert prob.n_obj == 3
    assert prob.n_ieq_constr == 3  # Case A default
    assert prob.xl[0] == pytest.approx(guard.bounds.p1_min, rel=1e-3)
    assert prob.xu[0] == pytest.approx(guard.bounds.p1_max, rel=1e-3)
    assert prob.xl[1] == pytest.approx(guard.bounds.p2_min, rel=1e-3)
    assert prob.xu[1] == pytest.approx(guard.bounds.p2_max, rel=1e-3)


def test_problem_case_b_polarization():
    """Verify Case B problem initialization with 4 inequality constraints."""
    prob = ROOperatingOptimizationProblem(enforce_polarization_limit=True)
    assert prob.n_ieq_constr == 4


def test_problem_evaluation():
    """Verify vectorized evaluation returns correct objective and constraint shapes."""
    prob = ROOperatingOptimizationProblem()
    x = np.array([
        [13.0, 18.0],
        [15.0, 20.0],
        [18.0, 15.0],  # Infeasible P2 < P1
    ])
    out = {}
    prob._evaluate(x, out)

    assert "F" in out
    assert "G" in out
    assert out["F"].shape == (3, 3)
    assert out["G"].shape == (3, 3)

    # First solution (13/18 bar) should be feasible: P1 - P2 = -5 <= 0
    assert out["G"][0, 0] == pytest.approx(-5.0, abs=1e-4)

    # Third solution (18/15 bar) should violate P2 >= P1: P1 - P2 = +3 > 0
    assert out["G"][2, 0] == pytest.approx(3.0, abs=1e-4)


def test_problem_evaluate_full_state():
    """Verify evaluate_full_state returns DataFrame with all 7 targets and conserved quantities."""
    prob = ROOperatingOptimizationProblem()
    p1 = np.array([13.0, 14.0])
    p2 = np.array([18.0, 19.0])
    df_state = prob.evaluate_full_state(p1, p2)

    assert isinstance(df_state, pd.DataFrame)
    assert len(df_state) == 2
    assert "overall_recovery_pct" in df_state.columns
    assert "SEC_kWh_m3" in df_state.columns
    assert "maximum_element_recovery_pct" in df_state.columns
    assert "permeate_flow_m3h" in df_state.columns
    assert "concentrate_flow_m3h" in df_state.columns
    assert "concentrate_tds_mgL" in df_state.columns
    assert "solute_balance_error_kg_s" in df_state.columns
    assert np.all(df_state["solute_balance_error_kg_s"] == 0.0)
