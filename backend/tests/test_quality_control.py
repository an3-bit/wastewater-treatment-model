"""
Unit tests for Stage 3 Quality Control and Failure Classification.
"""

import pytest
import numpy as np
from data_generation.quality_control import (
    QualityFlag,
    verify_scenario_quality,
)
from data_generation.feasibility import (
    FailureCategory,
    classify_simulation_failure,
)


def test_verify_scenario_quality_pass():
    """Verify that a physically consistent scenario receives QualityFlag.PASS."""
    valid_row = {
        "feasible": 1,
        "feed_flow_m3h": 30.0,
        "permeate_flow_m3h": 21.0,
        "concentrate_flow_m3h": 9.0,
        "feed_tds_mgL": 2041.0,
        "permeate_tds_mgL": 10.0,
        "concentrate_tds_mgL": 6770.0,  # 30*2041 = 61230; 21*10 + 9*6770 = 210 + 60930 = 61140 (close)
        "overall_recovery_pct": 70.0,
        "average_flux_LMH": 37.8,
        "SEC_kWh_m3": 0.85,
        "stage1_pressure_bar": 14.0,
        "stage2_pressure_bar": 20.0,
        "maximum_polarization_modulus": 1.35,
    }
    # Exact solute balance: 30*2041 = 61230; (61230 - 210)/9 = 6780.0
    valid_row["concentrate_tds_mgL"] = (30.0 * 2041.0 - 21.0 * 10.0) / 9.0

    flag, reasons = verify_scenario_quality(valid_row)
    assert flag == QualityFlag.PASS
    assert len(reasons) == 0


def test_verify_scenario_quality_mass_balance_violation():
    """Verify that a mass balance violation triggers QualityFlag.FAIL."""
    invalid_row = {
        "feasible": 1,
        "feed_flow_m3h": 30.0,
        "permeate_flow_m3h": 20.0,
        "concentrate_flow_m3h": 8.0,  # Sum is 28, not 30
        "feed_tds_mgL": 2000.0,
        "permeate_tds_mgL": 10.0,
        "concentrate_tds_mgL": 6000.0,
        "overall_recovery_pct": 66.7,
        "average_flux_LMH": 35.0,
        "SEC_kWh_m3": 0.9,
        "stage1_pressure_bar": 15.0,
        "stage2_pressure_bar": 20.0,
        "maximum_polarization_modulus": 1.2,
    }
    flag, reasons = verify_scenario_quality(invalid_row)
    assert flag == QualityFlag.FAIL
    assert any("Water mass balance error" in r for r in reasons)


def test_classify_simulation_failure_categories():
    """Verify that failure classification properly categorizes various error contexts."""
    # Pressure limit
    cat, _ = classify_simulation_failure(context={"pressure_limit_exceeded": True})
    assert cat == FailureCategory.PRESSURE_LIMIT

    # Element recovery limit
    cat, _ = classify_simulation_failure(ValueError("Single element recovery exceeds limit 0.30"))
    assert cat == FailureCategory.ELEMENT_RECOVERY_LIMIT

    # Osmotic stall
    cat, _ = classify_simulation_failure(ValueError("Osmotic stall: driving pressure insufficient"))
    assert cat == FailureCategory.OSMOTIC_STALL

    # Solver failure
    cat, _ = classify_simulation_failure(RuntimeError("Solver convergence failed after maxiter"))
    assert cat == FailureCategory.SOLVER_FAILURE
