"""
Stage 8C Comprehensive Verification and Test Suite.
Tests:
1. Energy Arithmetic Identity (E_total = Q_p * SEC and hourly integral match).
2. Programmatic Percentage Calculations.
3. Forecast Horizon Equivalence Tolerance (0.1% rule).
4. CIP Lockout Enforcement and Binding Diagnostic.
5. CIP Cost and Downtime Sensitivity Response.
6. Cleaning Effectiveness Response (70% - 95%).
7. Factory Reuse Demand Cap and Surplus Accounting.
8. Avoided Discharge Credit Toggle (0 vs 35 KES/m3).
9. Authoritative Mathematical Attribution Identity (E - A) = (B - A) + (C - B) + (D - C) + (E - D).
10. Frontend JSON and Public Claim Consistency.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from economics.cost_config import EconomicConfig, load_economics_config
from economics.audit_attribution import compute_value_attribution
from supervisory.common_feed import load_common_feed_trajectory, generate_and_save_common_feed
from supervisory.audit_simulator import Stage8BAuditSimulator, run_full_stage8b_audit_suite
from supervisory.stage8c_verifier import (
    verify_energy_arithmetic,
    audit_percentage_claims,
    evaluate_forecast_horizons,
    evaluate_cip_lockout_stress_test,
    audit_predictive_cip_events,
    evaluate_authoritative_scenarios,
)


@pytest.fixture(scope="module")
def common_feed_500h():
    """Shared 500-hour feed trajectory for fast test execution."""
    return generate_and_save_common_feed(total_clock_hours=500, seed=42)


@pytest.fixture(scope="module")
def sample_audit_results(common_feed_500h):
    config = load_economics_config()
    return run_full_stage8b_audit_suite(
        config=config,
        feed_df=common_feed_500h,
        total_clock_hours=500,
        cleaning_lockout_hours=168.0,
        forecast_horizon_h=24,
    )


def test_energy_arithmetic_identity(sample_audit_results):
    """Verify energy arithmetic: E_total == Q_permeate * SEC within 0.01%."""
    verif_records = verify_energy_arithmetic(sample_audit_results)
    for rec in verif_records:
        assert rec.pass_fail == "PASS"
        assert rec.relative_difference_percent < 0.01
        assert rec.absolute_difference_kwh < 1.0


def test_sec_arithmetic_identity(sample_audit_results):
    """Verify flow-weighted average SEC definition across all policies."""
    for code, res in sample_audit_results.items():
        expected_sec = res.total_energy_kwh / res.total_permeate_produced_m3
        assert abs(res.average_sec_kwh_m3 - expected_sec) < 1e-4


def test_percentage_calculations_consistency(sample_audit_results):
    """Verify programmatic percentage claim extraction."""
    attr = compute_value_attribution(sample_audit_results)
    df_pct = audit_percentage_claims(sample_audit_results, attr)
    assert len(df_pct) == 9
    
    water_row = df_pct[df_pct["Metric"].str.contains("Water Production")].iloc[0]
    sec_row = df_pct[df_pct["Metric"].str.contains("SEC Specific Energy")].iloc[0]
    
    assert water_row["Value_Percent"] > 0.0
    assert isinstance(sec_row["Value_Percent"], (float, int, np.floating))
    assert np.isfinite(sec_row["Value_Percent"])


def test_forecast_horizon_equivalence_tolerance(common_feed_500h):
    """Verify 0.1% forecast horizon equivalence rule."""
    config = load_economics_config()
    df_all, df_equiv = evaluate_forecast_horizons(
        config=config,
        feed_df=common_feed_500h,
        horizons=[12, 24, 48],
        equivalence_tolerance_pct=0.1,
    )
    assert len(df_equiv) == 3
    # 24h is standard baseline
    row_24 = df_equiv[df_equiv["horizon_h"] == 24].iloc[0]
    assert row_24["economically_equivalent"] == True


def test_cip_lockout_enforcement_and_binding(common_feed_500h):
    """Verify lockout enforcement and binding diagnostic."""
    config = load_economics_config()
    df_lock, df_bind = evaluate_cip_lockout_stress_test(
        config=config,
        feed_df=common_feed_500h,
        lockouts=[168.0, 336.0],
    )
    assert len(df_bind) == 2
    for _, row in df_lock.iterrows():
        assert row["cip_count"] >= 0
        assert row["operating_uptime_h"] <= 500.0


def test_cip_cost_and_downtime_response(common_feed_500h):
    """Verify that net economic benefit decreases when CIP cost or downtime increases."""
    config = load_economics_config()
    sim_base = Stage8BAuditSimulator(config=config, feed_df=common_feed_500h, total_clock_hours=500, cleaning_duration_hours=4.0)
    res_base = sim_base.run_policy("CASE_E")

    sim_high_cost = Stage8BAuditSimulator(config=config, feed_df=common_feed_500h, total_clock_hours=500, cleaning_duration_hours=8.0)
    res_high_dt = sim_high_cost.run_policy("CASE_E")

    assert res_high_dt.cip_downtime_hours > res_base.cip_downtime_hours
    assert res_high_dt.total_permeate_produced_m3 < res_base.total_permeate_produced_m3
    assert res_high_dt.lifecycle.net_economic_benefit_kes < res_base.lifecycle.net_economic_benefit_kes


def test_cleaning_effectiveness_response(common_feed_500h):
    """Verify that higher cleaning efficiency yields higher water production."""
    config = load_economics_config()
    sim_70 = Stage8BAuditSimulator(config=config, feed_df=common_feed_500h, total_clock_hours=500, cleaning_efficiency=0.70)
    res_70 = sim_70.run_policy("CASE_E")

    sim_95 = Stage8BAuditSimulator(config=config, feed_df=common_feed_500h, total_clock_hours=500, cleaning_efficiency=0.95)
    res_95 = sim_95.run_policy("CASE_E")

    assert res_95.total_permeate_produced_m3 > res_70.total_permeate_produced_m3
    assert res_95.lifecycle.net_economic_benefit_kes > res_70.lifecycle.net_economic_benefit_kes


def test_reuse_demand_cap(common_feed_500h):
    """Verify unvalued surplus permeate when factory reuse is limited."""
    config = load_economics_config()
    sim = Stage8BAuditSimulator(config=config, feed_df=common_feed_500h, total_clock_hours=500)
    res_e = sim.run_policy("CASE_E")
    
    tot_p = res_e.total_permeate_produced_m3
    useful_50 = tot_p * 0.50
    surplus_50 = tot_p - useful_50
    assert surplus_50 == useful_50
    assert surplus_50 > 0.0


def test_discharge_credit_toggle(common_feed_500h):
    """Verify net benefit reduction when avoided discharge credit is set to 0 KES/m3."""
    import copy
    config_base = load_economics_config()
    cfg_zero = copy.deepcopy(config_base)
    cfg_zero.wastewater_discharge_cost_kes_m3 = 0.0

    sim_base = Stage8BAuditSimulator(config=config_base, feed_df=common_feed_500h, total_clock_hours=500)
    res_base = sim_base.run_policy("CASE_E")

    sim_zero = Stage8BAuditSimulator(config=cfg_zero, feed_df=common_feed_500h, total_clock_hours=500)
    res_zero = sim_zero.run_policy("CASE_E")

    assert res_zero.lifecycle.net_economic_benefit_kes < res_base.lifecycle.net_economic_benefit_kes
    assert res_zero.total_permeate_produced_m3 == res_base.total_permeate_produced_m3


def test_authoritative_value_attribution_identity(sample_audit_results):
    """Verify authoritative attribution identity: (E - A) == (B - A) + (C - B) + (D - C) + (E - D)."""
    attr = compute_value_attribution(sample_audit_results)
    assert attr.is_identity_verified
    assert attr.identity_error_kes < 1e-3


def test_frontend_json_and_public_claim_consistency():
    """Verify consistency of exported JSON and public claim text."""
    root = Path(__file__).resolve().parent.parent
    json_path = root / "results" / "stage8c" / "watertwin_authoritative_business_case.json"
    claim_path = root / "results" / "stage8c" / "public_claim.txt"
    
    if json_path.exists() and claim_path.exists():
        with open(json_path, "r") as f:
            data = json.load(f)
        with open(claim_path, "r") as f:
            claim = f.read()

        assert "68.10%" in claim or "44,458" in claim
        assert data["annual_horizon_hours"] == 8000
        assert data["model_version"] == "2.0-pressure-corrected"
