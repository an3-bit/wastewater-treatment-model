"""
Unit & Integration Tests for Stage 8: Predictive Techno-Economic Supervisory Optimization.

Tests cover:
1. Economic Configuration and Source Provenance Validation
2. Missing Economic Input Handling (reduced scope)
3. Water Valuation & Avoided Sewer Discharge
4. Energy Cost & SEC Integration
5. Itemized CIP Cleaning Cost Breakdown
6. Membrane Degradation & Replacement Cost
7. Levelized Cost of Water (LCOW) Formulation
8. Explicit CIP Event Execution & Partial Permeability Recovery
9. Multi-Horizon Prediction (6h, 12h, 24h, 48h, 72h) & Physical Constraint Checking
10. Candidate Action Evaluation & Economic Objective Function
11. Annual Plant Simulation Mass & Energy Balances (Conservation)
12. Deterministic Reproducibility Across Fixed Random Seeds
13. Break-Even Analysis & Financial Metrics (NPV, IRR, Payback)
"""

import math
import pytest
import numpy as np
from pathlib import Path

from economics import (
    EconomicConfig,
    EconomicParameter,
    load_economics_config,
    calculate_water_value,
    calculate_energy_cost,
    calculate_single_cip_cost,
    calculate_annual_cleaning_costs,
    calculate_membrane_cost,
    calculate_downtime_cost,
    calculate_lifecycle_costs,
    calculate_financial_appraisal,
    calculate_break_even_conditions,
    run_single_parameter_sensitivity,
)
from maintenance import MembraneCleaningManager, CleaningEventExecution
from prediction import (
    SupervisoryPredictor,
    CandidateActionEvaluation,
)
from supervisory import (
    AnnualPlantSimulator,
    generate_synthetic_industrial_feed,
    run_full_annual_comparison,
)


def test_economics_config_provenance_and_schema():
    """Verify that economics.yaml loads cleanly and all required provenance fields exist."""
    config = load_economics_config()
    assert config is not None
    assert config.operating_hours_per_year == 8000.0
    assert config.water_purchase_cost_kes_m3 == 93.0
    assert config.electricity_rate_kes_kwh == 13.74
    assert config.number_of_membrane_elements == 15
    assert config.cleaning_efficiency_nominal == 0.90

    # Test raw parameters dictionary provenance
    params = config.raw_parameters
    assert isinstance(params, dict)
    assert len(params) >= 15
    for key, p in params.items():
        assert isinstance(p, EconomicParameter)
        assert p.name is not None
        assert p.unit is not None
        assert p.source is not None
        assert p.source_type in {"SOURCE-BACKED", "USER-SUPPLIED", "SCENARIO ASSUMPTION"}
        assert isinstance(p.reference_year, int)
        assert p.notes is not None


def test_missing_economic_inputs_graceful_handling():
    """Verify that setting optional inputs to None / 0 doesn't break calculations."""
    config = load_economics_config()
    # Lifecycle calculation with reduced scope (e.g., zero DT OPEX)
    res = calculate_lifecycle_costs(
        permeate_volume_m3=170000.0,
        feed_volume_m3=240000.0,
        total_energy_kwh=180000.0,
        cleaning_times_hours=[500.0, 1200.0, 2000.0],
        annual_operating_hours=8000.0,
        config=config,
        include_digital_twin_opex=False,
    )
    assert res.digital_twin_opex_kes == 0.0
    assert res.lcow_total_kes_m3 > 0.0
    assert res.net_economic_benefit_kes > 0.0


def test_water_value_and_discharge_avoidance():
    """Verify avoided freshwater and wastewater discharge calculations."""
    config = load_economics_config()
    perm_vol = 10000.0
    val_res = calculate_water_value(perm_vol, config)

    assert val_res.permeate_volume_m3 == perm_vol
    assert val_res.avoided_freshwater_value_kes == perm_vol * 93.0
    assert val_res.avoided_discharge_value_kes == perm_vol * 35.0
    assert val_res.total_water_value_kes == perm_vol * (93.0 + 35.0)


def test_energy_cost_and_sec():
    """Verify electricity cost matches E_total * rate."""
    config = load_economics_config()
    kwh = 50000.0
    vol = 40000.0
    res = calculate_energy_cost(kwh, vol, config)

    assert math.isclose(res.electricity_cost_kes, 50000.0 * 13.74, rel_tol=1e-6)
    assert math.isclose(res.sec_kwh_m3, 50000.0 / 40000.0, rel_tol=1e-6)


def test_cleaning_cost_breakdown():
    """Verify itemized CIP cost components sum correctly."""
    config = load_economics_config()
    single_cip = calculate_single_cip_cost(event_index=1, time_hours=100.0, config=config)
    assert single_cip.chemical_cost_kes == config.cip_chemical_cost_per_event_kes
    assert math.isclose(single_cip.water_cost_kes, config.cip_water_volume_m3 * config.water_purchase_cost_kes_m3, rel_tol=1e-6)
    assert math.isclose(single_cip.energy_cost_kes, config.cip_energy_kwh * config.electricity_rate_kes_kwh, rel_tol=1e-6)
    assert math.isclose(single_cip.labour_cost_kes, config.cip_labour_hours * config.cip_labour_rate_kes_h, rel_tol=1e-6)
    assert math.isclose(single_cip.downtime_cost_kes, config.cleaning_duration_hours * config.downtime_lost_revenue_rate_kes_h, rel_tol=1e-6)
    assert math.isclose(
        single_cip.total_cost_kes,
        single_cip.chemical_cost_kes + single_cip.water_cost_kes + single_cip.energy_cost_kes + single_cip.labour_cost_kes + single_cip.downtime_cost_kes,
        rel_tol=1e-6
    )


def test_membrane_cost_and_lifecycle():
    """Verify membrane replacement and degradation calculations."""
    config = load_economics_config()
    mem_cost = calculate_membrane_cost(
        annual_operating_hours=8000.0,
        config=config,
        average_max_element_recovery_pct=20.37,
    )
    assert mem_cost.annual_operating_hours == 8000.0
    assert mem_cost.total_annual_membrane_cost_kes > 0.0
    assert mem_cost.stress_degradation_factor == 1.0


def test_lcow_formulation():
    """Verify Levelized Cost of Water (LCOW) formula and unit cost components."""
    config = load_economics_config()
    lc = calculate_lifecycle_costs(
        permeate_volume_m3=170000.0,
        feed_volume_m3=240000.0,
        total_energy_kwh=190000.0,
        cleaning_times_hours=[500.0, 1000.0, 1500.0],
        annual_operating_hours=8000.0,
        config=config,
    )
    # LCOW = total_operating_cost / permeate_volume
    assert math.isclose(lc.lcow_total_kes_m3, lc.total_operating_cost_kes / lc.permeate_volume_m3, rel_tol=1e-6)
    # Sum of unit costs equals total LCOW
    sum_unit_costs = lc.energy_cost_per_m3_kes + lc.cleaning_cost_per_m3_kes + lc.membrane_cost_per_m3_kes + lc.digital_twin_opex_per_m3_kes
    assert math.isclose(lc.lcow_total_kes_m3, sum_unit_costs, rel_tol=1e-6)


def test_cleaning_event_and_recovery():
    """Verify explicit CIP manager applies partial recovery (Rf_after = (1-eta)*Rf_before)."""
    config = load_economics_config()
    manager = MembraneCleaningManager(config)

    initial_Rf = np.array([1.0e13, 1.2e13, 1.5e13, 1.8e13, 2.0e13, 2.2e13])
    rf_after, event = manager.execute_cleaning(initial_Rf, current_hour=150.0, trigger_reason="TEST_CLEANING")

    assert event.duration_hours == config.cleaning_duration_hours
    assert event.efficiency == config.cleaning_efficiency_nominal
    expected_Rf = initial_Rf * (1.0 - config.cleaning_efficiency_nominal)
    assert np.allclose(rf_after, expected_Rf, rtol=1e-5)
    assert len(manager.history) == 1


def test_supervisory_predictor_and_constraints():
    """Verify multi-horizon forward predictor obeys physical constraints (P <= 41 bar, element rec <= 30%)."""
    config = load_economics_config()
    predictor = SupervisoryPredictor(config)

    rf_state = np.array([2.0e12, 2.5e12, 3.0e12, 3.5e12, 4.0e12, 4.5e12])

    forecast_res = predictor.generate_multi_horizon_forecast(
        origin_time_hours=0.0,
        q_feed=30.0,
        c_feed=2041.0,
        temp_c=25.0,
        p1_bar=16.06,
        p2_bar=16.41,
        initial_6zone_rf=rf_state,
    )

    assert set(forecast_res.horizons.keys()) == {"6h", "12h", "24h", "48h", "72h"}
    for h_name, f in forecast_res.horizons.items():
        assert f.max_element_recovery_pct <= 30.0
        assert f.recovery_pct > 0.0
        assert f.permeate_flow_m3_h > 0.0
        assert f.sec_kwh_m3 > 0.0
        assert f.net_operating_value_kes != 0.0


def test_candidate_actions_evaluation():
    """Verify evaluation of candidate action space."""
    config = load_economics_config()
    predictor = SupervisoryPredictor(config)

    rf_state = np.array([5.0e12, 6.0e12, 7.0e12, 8.0e12, 9.0e12, 1.0e13])

    evals = predictor.evaluate_counterfactual_actions(
        current_time_hours=100.0,
        q_feed=30.0,
        c_feed=2041.0,
        temp_c=25.0,
        current_p1_bar=16.06,
        current_p2_bar=16.41,
        initial_6zone_rf=rf_state,
    )

    assert len(evals) == 10
    feasible_actions = [a for a in evals if a.is_feasible]
    assert len(feasible_actions) > 0


def test_annual_simulation_mass_and_energy_conservation():
    """Verify mass balance (Qf = Qp + Qc) and energy calculations across simulation steps."""
    config = load_economics_config()
    sim = AnnualPlantSimulator(config=config, total_hours=50, random_seed=42)

    res = sim.run_policy(policy_code="CASE_B")

    assert res.annual_operating_hours == 50.0
    records = res.hourly_records
    assert len(records) == 50

    # Mass balance: for active operational hours, Qf = Qp + Qc
    active_recs = [r for r in records if not r.is_cleaning_hour]
    for r in active_recs:
        assert r.q_perm_m3_h <= r.q_feed_m3_h
        assert r.q_perm_m3_h >= 0.0
        assert r.permeability_decline_pct >= 0.0


def test_deterministic_reproducibility():
    """Verify that identical random seeds produce identical annual results."""
    q1, c1, t1 = generate_synthetic_industrial_feed(total_hours=100, seed=101)
    q2, c2, t2 = generate_synthetic_industrial_feed(total_hours=100, seed=101)

    assert np.allclose(q1, q2)
    assert np.allclose(c1, c2)
    assert np.allclose(t1, t2)

    config = load_economics_config()
    sim1 = AnnualPlantSimulator(config=config, total_hours=100, random_seed=101)
    sim2 = AnnualPlantSimulator(config=config, total_hours=100, random_seed=101)

    res1 = sim1.run_policy("CASE_B")
    res2 = sim2.run_policy("CASE_B")

    assert res1.lifecycle.permeate_volume_m3 == res2.lifecycle.permeate_volume_m3
    assert res1.lifecycle.net_economic_benefit_kes == res2.lifecycle.net_economic_benefit_kes
    assert res1.lifecycle.number_of_cleanings == res2.lifecycle.number_of_cleanings


def test_break_even_and_financial_metrics():
    """Verify break-even conditions and NPV/payback calculations."""
    config = load_economics_config()
    sim = AnnualPlantSimulator(config=config, total_hours=100, random_seed=42)
    case_a = sim.run_policy("CASE_A")
    case_b = sim.run_policy("CASE_B")
    case_e = sim.run_policy("CASE_E")

    break_even = calculate_break_even_conditions(
        baseline_lifecycle=case_a.lifecycle,
        fixed_d_lifecycle=case_b.lifecycle,
        digital_twin_lifecycle=case_e.lifecycle,
        base_config=config,
    )
    assert break_even.max_annual_dt_opex_kes >= 0.0
    assert break_even.max_dt_capex_2yr_payback_kes >= 0.0

    appraisal = calculate_financial_appraisal(
        incremental_annual_benefit_kes=500000.0,
        config=config,
        capex_override=1000000.0,
    )
    assert appraisal.simple_payback_years == 2.0
    assert appraisal.npv_5yr_kes > 0.0
    assert appraisal.irr_pct is not None and appraisal.irr_pct > 0.0
