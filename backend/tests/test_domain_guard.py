"""
Unit Tests for Optimization Domain Guard, Proximity Indicator, and Mechanistic Verification (Stage 4B).
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from ml.domain_guard import (
    OptimizationDomainGuard,
    DomainBounds,
    DomainProximityStatus,
)
from ml.verification import verify_candidate_with_mechanistic_model
from ml.inference import Stage4Surrogate
from ml.physics_checks import BASELINE_POINT


@pytest.fixture
def domain_guard():
    csv_path = Path("data/generated/stage3_engineering_acceptable.csv")
    if not csv_path.exists():
        pytest.skip(f"{csv_path} not found")
    return OptimizationDomainGuard.from_training_dataset(csv_path)


@pytest.fixture
def trained_ann_surrogate():
    models_dir = Path("models/stage4")
    if not (models_dir / "ann___mlp").exists():
        pytest.skip("Trained ANN model artifacts not found in models/stage4/ann___mlp")
    return Stage4Surrogate.load(models_dir, "ann___mlp", is_neural_net=True)


def test_domain_guard_valid_baseline(domain_guard):
    is_valid, violations = domain_guard.validate_inputs(BASELINE_POINT)
    assert is_valid, f"Baseline point should be valid, but got violations: {violations}"
    assert len(violations) == 0


def test_domain_guard_rejects_p2_less_than_p1(domain_guard):
    invalid_candidate = dict(BASELINE_POINT)
    invalid_candidate["stage1_pressure_bar"] = 18.0
    invalid_candidate["stage2_pressure_bar"] = 14.0  # P2 < P1

    is_valid, violations = domain_guard.validate_inputs(invalid_candidate)
    assert not is_valid
    assert any("less than Stage 1 pressure" in v for v in violations)


def test_domain_guard_rejects_out_of_bounds(domain_guard):
    # Flow out of bounds (e.g. 50 m3/h > 40 m3/h max)
    invalid_candidate = dict(BASELINE_POINT)
    invalid_candidate["feed_flow_m3h"] = 55.0

    is_valid, violations = domain_guard.validate_inputs(invalid_candidate)
    assert not is_valid
    assert any("feed_flow_m3h" in v for v in violations)


def test_domain_guard_rejects_excessive_pressure(domain_guard):
    invalid_candidate = dict(BASELINE_POINT)
    invalid_candidate["stage2_pressure_bar"] = 45.0  # > 41 bar max membrane limit

    is_valid, violations = domain_guard.validate_inputs(invalid_candidate)
    assert not is_valid
    assert any("exceeds maximum allowable 41 bar" in v for v in violations)


def test_domain_guard_safeguard_30pct(domain_guard):
    is_valid_safe, _ = domain_guard.validate_predicted_state(25.0)
    assert is_valid_safe

    is_valid_unsafe, msg = domain_guard.validate_predicted_state(32.5)
    assert not is_valid_unsafe
    assert "exceeds 30.0% safeguard limit" in msg


def test_domain_proximity_status(domain_guard):
    # Baseline is strictly IN_DOMAIN
    status_base, z_base = domain_guard.evaluate_proximity_status(BASELINE_POINT)
    assert status_base == DomainProximityStatus.IN_DOMAIN

    # Far OOD point
    ood_candidate = {
        "feed_flow_m3h": 50.0,
        "feed_tds_mgL": 4000.0,
        "temperature_C": 40.0,
        "stage1_pressure_bar": 25.0,
        "stage2_pressure_bar": 35.0,
    }
    status_ood, z_ood = domain_guard.evaluate_proximity_status(ood_candidate)
    assert status_ood == DomainProximityStatus.OUT_OF_DOMAIN
    assert z_ood > 3.5


def test_verify_candidate_with_mechanistic_model(trained_ann_surrogate, domain_guard):
    audit = verify_candidate_with_mechanistic_model(
        candidate=BASELINE_POINT,
        surrogate=trained_ann_surrogate,
        domain_guard=domain_guard,
    )

    assert audit["domain_guard_valid"] is True
    assert audit["mechanistic_feasible"] is True
    assert "error_matrix" in audit

    # Check that baseline errors are small (<1% relative error for all targets)
    for tgt, errs in audit["error_matrix"].items():
        assert errs["direct_rel_error_pct"] < 1.0, f"Target {tgt} direct error too high: {errs['direct_rel_error_pct']:.2f}%"
        assert errs["recon_rel_error_pct"] < 1.0, f"Target {tgt} recon error too high: {errs['recon_rel_error_pct']:.2f}%"
