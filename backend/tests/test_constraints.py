"""
Unit tests for constraint checking and margins (src/optimization/constraints.py).
"""

import pytest
import numpy as np

from optimization.constraints import check_candidate_constraints
from ml.domain_guard import OptimizationDomainGuard


@pytest.fixture
def domain_guard():
    return OptimizationDomainGuard.from_training_dataset()


def test_feasible_candidate(domain_guard):
    """Verify clean feasible baseline candidate."""
    state = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "maximum_element_recovery_pct": 23.68,
        "permeate_tds_mgL": 7.23,
        "maximum_polarization_modulus": 1.30,
    }
    rep = check_candidate_constraints(
        p1=13.0,
        p2=18.0,
        predicted_state=state,
        domain_guard=domain_guard,
    )
    assert rep.is_feasible is True
    assert len(rep.violations) == 0
    assert rep.p2_ge_p1_margin_bar == pytest.approx(5.0, abs=1e-4)
    assert rep.max_element_rec_margin_pct == pytest.approx(30.0 - 23.68, abs=1e-2)
    assert rep.permeate_tds_margin_mgL == pytest.approx(18.0 - 7.23, abs=1e-2)


def test_infeasible_p2_lt_p1(domain_guard):
    """Verify rejection when P2 < P1."""
    state = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "maximum_element_recovery_pct": 20.0,
        "permeate_tds_mgL": 8.0,
        "maximum_polarization_modulus": 1.25,
    }
    rep = check_candidate_constraints(
        p1=18.0,
        p2=14.0,
        predicted_state=state,
        domain_guard=domain_guard,
    )
    assert rep.is_feasible is False
    assert any("Stage 2 pressure" in v for v in rep.violations)


def test_infeasible_element_recovery_exceeded(domain_guard):
    """Verify rejection when maximum element recovery > 30%."""
    state = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "maximum_element_recovery_pct": 32.5,
        "permeate_tds_mgL": 8.0,
        "maximum_polarization_modulus": 1.35,
    }
    rep = check_candidate_constraints(
        p1=15.0,
        p2=20.0,
        predicted_state=state,
        domain_guard=domain_guard,
    )
    assert rep.is_feasible is False
    assert any("exceeds 30.0% limit" in v for v in rep.violations)


def test_infeasible_permeate_tds_exceeded(domain_guard):
    """Verify rejection when permeate TDS > 18 mg/L."""
    state = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "maximum_element_recovery_pct": 22.0,
        "permeate_tds_mgL": 19.5,
        "maximum_polarization_modulus": 1.30,
    }
    rep = check_candidate_constraints(
        p1=12.0,
        p2=16.0,
        predicted_state=state,
        domain_guard=domain_guard,
    )
    assert rep.is_feasible is False
    assert any("exceeds 18.0 mg/L" in v for v in rep.violations)
