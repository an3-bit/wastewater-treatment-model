"""
FastAPI Backend Integration & Regression Tests
Validates all REST API endpoints against frozen Stage 8C authoritative scientific results.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["model_version"] == "2.0-pressure-corrected"
    assert data["mode"] in ["virtual", "virtual-plant"]
    assert data["stage"] == "8C-frozen"


def test_twin_metadata_endpoint():
    res = client.get("/api/v1/twin/metadata")
    assert res.status_code == 200
    data = res.json()
    assert data["model_version"] == "2.0-pressure-corrected"
    assert data["estimator"] == "6-Zone EKF"
    assert data["fouling_zones"] == 6
    assert data["display_elements"] == 15
    assert data["forecast_horizon_h"] == 24
    assert data["industrial_validation"] is False


def test_twin_state_and_advance():
    res = client.get("/api/v1/twin/state")
    assert res.status_code == 200
    state = res.json()
    assert state["feed_flow_m3_h"] == 25.0
    assert state["feed_tds_mg_l"] == 3000.0
    assert state["p1_bar"] > 0
    assert state["recovery_percent"] > 0
    assert state["sec_kwh_m3"] > 0
    assert 0 <= state["membrane_health_score_percent"] <= 100

    # Test Advance
    adv_res = client.post("/api/v1/twin/advance", json={"hours": 4.0})
    assert adv_res.status_code == 200
    adv_data = adv_res.json()
    assert adv_data["success"] is True
    assert adv_data["advanced_hours"] == 4.0

    # Test Reset
    reset_res = client.post("/api/v1/twin/reset", json={"reset_to_clean": True, "initial_p1_bar": 18.0, "initial_p2_bar": 25.0})
    assert reset_res.status_code == 200
    reset_state = reset_res.json()
    assert reset_state["simulation_time_h"] == 0.0


def test_sensors_endpoint():
    res = client.get("/api/v1/sensors")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] == 10
    sensor_ids = {s["id"] for s in data["sensors"]}
    expected_ids = {"Qf", "Cf", "T", "P1", "Qp_total", "Cp_total", "P2", "P_interstage", "C_concentrate", "W_electric"}
    assert sensor_ids == expected_ids

    # Test Sensor History
    hist_res = client.get("/api/v1/sensors/history?sensor_id=Qp_total&hours=12")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["sensor_id"] == "Qp_total"
    assert len(hist_data["history"]) > 0


def test_membranes_zones_and_element_mapping():
    # Test Zones
    res_zones = client.get("/api/v1/membranes/zones")
    assert res_zones.status_code == 200
    data_zones = res_zones.json()
    assert data_zones["total_zones"] == 6
    assert len(data_zones["zones"]) == 6
    for z in data_zones["zones"]:
        assert z["stage"] in [1, 2]
        assert z["position"] in ["Lead", "Middle", "Tail"]
        assert 0 <= z["health_percent"] <= 100

    # Test Elements
    res_elem = client.get("/api/v1/membranes/elements")
    assert res_elem.status_code == 200
    data_elem = res_elem.json()
    assert data_elem["total_elements"] == 15
    for elem in data_elem["elements"]:
        assert elem["estimated_from_zone"] is True
        assert "E-" in elem["element_id"]


def test_forecast_endpoints():
    for h in [6, 12, 24, 48, 72]:
        res = client.get(f"/api/v1/forecast?hours={h}")
        assert res.status_code == 200
        data = res.json()
        assert data["horizon_hours"] == h
        assert len(data["trajectory"]) == h
        assert data["confidence"]["confidence_level_percent"] == 95.0


def test_maintenance_recommendations():
    rec_res = client.get("/api/v1/maintenance/recommendation")
    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["recommended_action"] in ["CLEAN", "CONTINUE", "MONITOR"]
    assert rec["lockout_period_h"] == 168.0

    hist_res = client.get("/api/v1/maintenance/history")
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert hist["calendar_baseline_cip_count"] == 12
    assert hist["condition_based_cip_count"] == 48
    assert hist["predictive_cip_count"] == 67


def test_authoritative_economics_agreement():
    """Verify API values match authoritative frozen Stage 8C results."""
    res = client.get("/api/v1/economics/summary")
    assert res.status_code == 200
    data = res.json()

    # Water Impact: +44,457.6 m3/yr (+68.10%)
    assert pytest.approx(data["water"]["baseline_permeate_m3"], 0.1) == 65279.7
    assert pytest.approx(data["water"]["watertwin_permeate_m3"], 0.1) == 109737.3
    assert pytest.approx(data["water"]["additional_permeate_m3"], 0.1) == 44457.6 or pytest.approx(data["water"]["additional_permeate_m3"], 0.1) == 44457.5
    assert pytest.approx(data["water"]["water_increase_pct"], 0.1) == 68.10

    # Energy Balance: +57.69% total electricity, -6.19% SEC
    assert pytest.approx(data["energy"]["baseline_total_kwh"], 0.1) == 65054.4
    assert pytest.approx(data["energy"]["watertwin_total_kwh"], 0.1) == 102583.2
    assert pytest.approx(data["energy"]["total_electricity_change_pct"], 0.1) == 57.69
    assert pytest.approx(data["energy"]["baseline_sec_kwh_m3"], 0.001) == 0.9965
    assert pytest.approx(data["energy"]["watertwin_sec_kwh_m3"], 0.001) == 0.9348
    assert pytest.approx(data["energy"]["sec_reduction_pct"], 0.1) == 6.19 or pytest.approx(data["energy"]["sec_reduction_pct"], 0.1) == 6.2

    # Economics: Integrated value ~KES 4,391,948.14
    assert pytest.approx(data["economics"]["integrated_framework_value_kes_year"], 0.1) == 4391948.14
    assert pytest.approx(data["economics"]["condition_based_value_kes_year"], 0.1) == 3902797.57
    assert pytest.approx(data["economics"]["prediction_value_kes_year"], 0.1) == 424164.72
    assert pytest.approx(data["economics"]["mpc_value_kes_year"], 0.1) == 2782.42
    assert pytest.approx(data["economics"]["predictive_decision_intelligence_kes_year"], 0.1) == 426947.14


def test_value_decomposition_waterfall():
    res = client.get("/api/v1/economics/value-decomposition")
    assert res.status_code == 200
    data = res.json()
    assert pytest.approx(data["total_integrated_value_kes_year"], 0.1) == 4391948.14
    assert pytest.approx(data["pure_prediction_share_pct"], 0.01) == 9.66
    assert pytest.approx(data["condition_monitoring_share_pct"], 0.01) == 88.86
    assert pytest.approx(data["mpc_share_pct"], 0.01) == 0.06


def test_policies_benchmarks():
    res = client.get("/api/v1/policies")
    assert res.status_code == 200
    data = res.json()
    assert data["total_policies"] >= 6
    codes = {p["policy_code"] for p in data["policies"]}
    assert "CASE_A" in codes
    assert "CASE_C" in codes
    assert "CASE_D" in codes
    assert "CASE_E" in codes
    assert "ORACLE" in codes

    # Oracle must be non-deployable upper bound
    oracle_p = next(p for p in data["policies"] if p["policy_code"] == "ORACLE")
    assert oracle_p["oracle"] is True
    assert oracle_p["deployable"] is False
    assert oracle_p["theoretical_upper_bound"] is True


def test_simulation_scenario_run():
    payload = {
        "feed_flow_m3_h": 25.0,
        "feed_tds_mg_l": 3000.0,
        "temperature_c": 25.0,
        "p1_bar": 18.0,
        "p2_bar": 25.0,
        "forecast_horizon_h": 24,
    }
    res = client.post("/api/v1/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["feasible"] is True
    assert data["recovery_percent"] > 0
    assert data["sec_kwh_m3"] > 0
    assert data["execution_time_ms"] >= 0
