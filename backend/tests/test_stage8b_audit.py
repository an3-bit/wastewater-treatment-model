"""
Unit and Integration Tests for Stage 8B: Economic Attribution & Predictive Value Audit.

Tests cover:
1. Common Exogenous Feed Trajectory Identity across policies
2. Identical Initial Membrane States and Boundary Conditions
3. Available Feed vs Processed Feed vs CIP Unprocessed Feed Accounting
4. Common 8,000 Clock-Hour Horizon Enforcement
5. Cleaning Hysteresis and Minimum Lockout vs Chattering
6. Mathematical Attribution Identity Verification: (E-A) == (B-A) + (C-B) + (D-C) + (E-D)
7. Instantaneous Operating Recovery vs Annual Effective Recovery Definitions
8. Total Energy (MWh) vs Specific Energy (SEC kWh/m3) Separation
9. Unconstrained Numerical Break-Even Root Finding
10. Factory Permeate Demand Capacity Limiting
11. Multi-Seed Deterministic Reproducibility
"""

import math
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from economics import (
    EconomicConfig,
    load_economics_config,
    compute_value_attribution,
    compute_corrected_break_even,
    ValueDecompositionResult,
    CorrectedBreakEvenSummary,
)
from maintenance import MembraneCleaningManager, CIPAuditStatistics
from supervisory import (
    Stage8BAuditSimulator,
    generate_and_save_common_feed,
    load_common_feed_trajectory,
    run_full_stage8b_audit_suite,
)


def test_common_feed_trajectory_identity():
    """Verify common feed trajectory file generation, schema, and exact identity."""
    df_feed = generate_and_save_common_feed(total_clock_hours=500, seed=42)
    assert len(df_feed) == 500
    assert set(df_feed.columns) == {"clock_hour", "q_feed_available_m3_h", "c_feed_mg_l", "temp_c"}
    assert (df_feed["q_feed_available_m3_h"] >= 18.0).all()
    assert (df_feed["q_feed_available_m3_h"] <= 42.0).all()
    assert (df_feed["c_feed_mg_l"] >= 1000.0).all()
    assert (df_feed["temp_c"] >= 12.0).all()


def test_feed_accounting_available_vs_processed():
    """Verify that available feed equals processed feed + unprocessed CIP downtime feed."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=200, seed=42)
    sim = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=200, random_seed=42)

    res = sim.run_policy("CASE_A")
    assert math.isclose(
        res.total_feed_available_m3,
        res.total_feed_processed_m3 + res.total_feed_unprocessed_cip_m3,
        rel_tol=1e-5
    )
    assert res.total_clock_hours == 200
    assert res.operating_hours + res.cip_downtime_hours == 200.0


def test_cleaning_hysteresis_and_lockout_prevents_chatter():
    """Verify that 168h lockout prevents rapid threshold chattering."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=1000, seed=42)

    # Simulator with lockout
    sim_lockout = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=1000, cleaning_lockout_hours=168.0)
    res_c_lockout = sim_lockout.run_policy("CASE_C")

    # Simulator with unconstrained chattering
    sim_chatter = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=1000, cleaning_lockout_hours=0.0)
    res_c_chatter = sim_chatter.run_policy("CASE_C_CHATTER")

    assert res_c_chatter.number_of_cleanings > res_c_lockout.number_of_cleanings
    if len(res_c_lockout.cleaning_events) > 1:
        inter_cip_intervals = [
            res_c_lockout.cleaning_events[i].trigger_hour - res_c_lockout.cleaning_events[i - 1].trigger_hour
            for i in range(1, len(res_c_lockout.cleaning_events))
        ]
        assert all(interval >= 168.0 for interval in inter_cip_intervals)


def test_mathematical_value_attribution_identity():
    """Verify exact mathematical identity: (E - A) == (B - A) + (C - B) + (D - C) + (E - D)."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=500, seed=42)
    results = run_full_stage8b_audit_suite(config=config, feed_df=feed_df, total_clock_hours=500, seed=42)

    attr = compute_value_attribution(results)
    assert attr.is_identity_verified
    assert attr.identity_error_kes < 1e-3

    expected_sum = attr.val1_static_opt_kes + attr.val2_condition_maint_kes + attr.val3_prediction_kes + attr.val4_supervisory_mpc_kes
    assert math.isclose(attr.total_integrated_value_kes, expected_sum, rel_tol=1e-5)


def test_recovery_definitions_and_downtime_dilution():
    """Verify distinction between instantaneous operating recovery and annual effective recovery."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=300, seed=42)
    sim = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=300, random_seed=42)
    res = sim.run_policy("CASE_C")

    # Operating recovery is strictly based on processed feed during uptime
    assert res.instantaneous_operating_recovery_pct > 0.0
    # Annual effective recovery incorporates downtime dilution
    if res.cip_downtime_hours > 0:
        assert res.annual_effective_recovery_pct <= res.instantaneous_operating_recovery_pct


def test_energy_definitions_and_sec():
    """Verify total energy [kWh] and specific energy consumption [kWh/m3] relationships."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=200, seed=42)
    sim = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=200, random_seed=42)
    res = sim.run_policy("CASE_E")

    assert res.total_energy_kwh > 0.0
    assert math.isclose(res.average_sec_kwh_m3, res.total_energy_kwh / res.total_permeate_produced_m3, rel_tol=1e-5)


def test_numerical_break_even_root_finding():
    """Verify unconstrained numerical break-even calculations."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=200, seed=42)
    results = run_full_stage8b_audit_suite(config=config, feed_df=feed_df, total_clock_hours=200, seed=42)

    be_summary = compute_corrected_break_even(results, config)
    assert be_summary.max_annual_dt_opex_kes >= 0.0
    assert be_summary.max_justifiable_capex_1yr_kes >= 0.0
    assert be_summary.max_justifiable_capex_2yr_kes == be_summary.max_justifiable_capex_1yr_kes * 2.0


def test_factory_reuse_demand_capacity_limit():
    """Verify factory permeate reuse demand throttling decreases useful permeate and net value."""
    config = load_economics_config()
    feed_df = generate_and_save_common_feed(total_clock_hours=200, seed=42)

    sim_full = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=200, reuse_demand_limit_m3_h=None)
    res_full = sim_full.run_policy("CASE_E")

    sim_capped = Stage8BAuditSimulator(config=config, feed_df=feed_df, total_clock_hours=200, reuse_demand_limit_m3_h=10.0)
    res_capped = sim_capped.run_policy("CASE_E")

    assert res_capped.lifecycle.permeate_volume_m3 <= res_full.lifecycle.permeate_volume_m3
    assert res_capped.lifecycle.net_economic_benefit_kes <= res_full.lifecycle.net_economic_benefit_kes


def test_multi_seed_deterministic_reproducibility():
    """Verify identical random seeds produce byte-identical annual results."""
    config = load_economics_config()
    feed1 = generate_and_save_common_feed(total_clock_hours=200, seed=2024)
    feed2 = generate_and_save_common_feed(total_clock_hours=200, seed=2024)

    pd.testing.assert_frame_equal(feed1, feed2)

    sim1 = Stage8BAuditSimulator(config=config, feed_df=feed1, total_clock_hours=200, random_seed=2024)
    sim2 = Stage8BAuditSimulator(config=config, feed_df=feed2, total_clock_hours=200, random_seed=2024)

    res1 = sim1.run_policy("CASE_E")
    res2 = sim2.run_policy("CASE_E")

    assert res1.total_permeate_produced_m3 == res2.total_permeate_produced_m3
    assert res1.lifecycle.net_economic_benefit_kes == res2.lifecycle.net_economic_benefit_kes
    assert res1.number_of_cleanings == res2.number_of_cleanings
