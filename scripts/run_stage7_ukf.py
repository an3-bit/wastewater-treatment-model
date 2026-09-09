"""
Unscented Kalman Filter (UKF) Benchmark Execution Script (Stage 7).

Executes:
1. Multi-strategy 168h evaluation (Baseline, Strategy A, B, C, D)
2. Initialization robustness tests (0%, 10%, 25%, 50% error, unknown fouled)
3. Noise sensitivity tests (Low, Nominal, High noise)
4. State dimension evaluation (Model A, Model B, Model C)
5. Generates results/stage7/tables/ukf_benchmark.csv

Authoritative Model Version: "2.0-pressure-corrected"
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pickle
from typing import Dict, List, Any
import numpy as np
import pandas as pd

from ro_model.membrane import RO_MODEL_VERSION
from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import SensorSet, SENSOR_SET_MEMBERS
from state_estimation.noise import NoiseLevel
from state_estimation.ukf import UnscentedKalmanFilter
from state_estimation.metrics import compute_estimation_metrics


def run_ukf_on_trajectory(
    traj_data: Dict[str, Any],
    representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE,
    sensor_set: SensorSet = SensorSet.CASE_2_STANDARD,
    noise_level: NoiseLevel = NoiseLevel.NOMINAL,
    initial_error_fraction: float = 0.0,
    forced_clean_init_on_fouled: bool = False,
) -> Dict[str, Any]:
    """Execute UKF on a synthetic trajectory and return metrics and history."""
    records = traj_data["records"]
    all_sensor_keys = SENSOR_SET_MEMBERS[SensorSet.CASE_3_RICH]
    active_keys = SENSOR_SET_MEMBERS[sensor_set]

    ukf = UnscentedKalmanFilter(
        representation=representation,
        sensor_set=sensor_set,
        noise_level=noise_level,
    )

    true_rf_0 = records[0]["true_rf_15"]
    if forced_clean_init_on_fouled:
        init_st = StateVector.create_clean(representation=representation)
    else:
        init_st_true = StateVector.from_15_element_array(true_rf_0, representation=representation)
        perturbed_vals = init_st_true.values * (1.0 + initial_error_fraction)
        if np.all(perturbed_vals == 0.0) and initial_error_fraction > 0:
            perturbed_vals = np.ones_like(perturbed_vals) * 2.0e12 * initial_error_fraction
        init_st = StateVector(values=perturbed_vals, representation=representation)

    ukf.initialize(init_st)

    true_states_15 = []
    for step_data in records:
        t_now = step_data["time_hours"]
        u_in = step_data["u_inputs"]
        
        if noise_level == NoiseLevel.LOW:
            meas_dict = step_data["y_measured_all_low_noise"]
        elif noise_level == NoiseLevel.NOMINAL:
            meas_dict = step_data["y_measured_all"]
        elif noise_level == NoiseLevel.HIGH:
            meas_dict = step_data["y_measured_all_high_noise"]

        y_meas_vec = np.array([meas_dict[k] for k in active_keys], dtype=float)
        rf_true = step_data["true_rf_15"]
        true_states_15.append(rf_true)
        st_true_vec = StateVector(values=rf_true, representation=StateRepresentation.FULL_15_ELEMENT)

        ukf.step(
            y_measured=y_meas_vec,
            u_inputs=u_in,
            time_hours=t_now,
            delta_t_hours=1.0,
            true_state_for_benchmark=st_true_vec,
        )

    metrics = compute_estimation_metrics(
        step_history=ukf.history,
        true_states_15=true_states_15,
    )

    return {
        "metrics": metrics,
        "history": ukf.history,
    }


def run_stage7_ukf_benchmark():
    print("=" * 80)
    print("STAGE 7: UNSCENTED KALMAN FILTER (UKF) BENCHMARK SUITE")
    print(f"Model Version: {RO_MODEL_VERSION}")
    print("=" * 80)

    traj_dir = Path("results/stage7/trajectories")
    tables_dir = Path("results/stage7/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    # 1. Multi-Strategy Runs on Clean Trajectories (Model B, Standard Sensors, Nominal Noise)
    strategies = ["Baseline", "Strategy_A", "Strategy_B", "Strategy_C", "Strategy_D"]
    for strat in strategies:
        pkl_path = traj_dir / f"traj_clean_{strat}.pkl"
        if not pkl_path.exists():
            continue
        with open(pkl_path, "rb") as f:
            traj = pickle.load(f)

        print(f"  Running UKF on {strat} (Model B, Standard Sensors)...")
        res = run_ukf_on_trajectory(traj, representation=StateRepresentation.AXIAL_6_ZONE)
        m = res["metrics"]

        rows.append({
            "test_category": "Strategy Evaluation",
            "scenario_name": strat,
            "state_model": "Model B (Axial 6-Zone)",
            "sensor_set": "Case 2 (Standard)",
            "noise_level": "NOMINAL",
            "initial_error": "0%",
            "rmse_rf_m_inv": m.rmse_rf_m_inv,
            "nrmse_rf": m.nrmse_rf,
            "mae_decline_pct": m.mae_permeability_decline_pct,
            "rmse_decline_pct": m.rmse_permeability_decline_pct,
            "max_decline_error_pct": m.max_permeability_decline_error_pct,
            "p95_decline_error_pct": m.p95_permeability_decline_error_pct,
            "convergence_time_h": m.convergence_time_hours if m.convergence_time_hours is not None else 0.0,
            "mean_step_time_ms": m.mean_step_duration_ms,
            "mean_nis": m.mean_nis,
            "nis_95_pass_pct": m.nis_95pct_ci_pass_rate,
        })

    # 2. Initialization Robustness Tests (Strategy D)
    with open(traj_dir / "traj_clean_Strategy_D.pkl", "rb") as f:
        traj_d = pickle.load(f)

    init_errors = [0.0, 0.10, 0.25, 0.50]
    for err in init_errors:
        print(f"  Running UKF Initialization Robustness: +{int(err*100)}% Error...")
        res = run_ukf_on_trajectory(traj_d, initial_error_fraction=err)
        m = res["metrics"]
        rows.append({
            "test_category": "Initialization Robustness",
            "scenario_name": f"Strategy_D_InitError_{int(err*100)}pct",
            "state_model": "Model B (Axial 6-Zone)",
            "sensor_set": "Case 2 (Standard)",
            "noise_level": "NOMINAL",
            "initial_error": f"+{int(err*100)}%",
            "rmse_rf_m_inv": m.rmse_rf_m_inv,
            "nrmse_rf": m.nrmse_rf,
            "mae_decline_pct": m.mae_permeability_decline_pct,
            "rmse_decline_pct": m.rmse_permeability_decline_pct,
            "max_decline_error_pct": m.max_permeability_decline_error_pct,
            "p95_decline_error_pct": m.p95_permeability_decline_error_pct,
            "convergence_time_h": m.convergence_time_hours if m.convergence_time_hours is not None else 0.0,
            "mean_step_time_ms": m.mean_step_duration_ms,
            "mean_nis": m.mean_nis,
            "nis_95_pass_pct": m.nis_95pct_ci_pass_rate,
        })

    # Partially Fouled Start (Unknown fouled: assume clean)
    with open(traj_dir / "traj_partially_fouled_Strategy_D.pkl", "rb") as f:
        traj_part = pickle.load(f)
    print("  Running UKF on Unknown Partially Fouled Start (Assumed Clean Initial Condition)...")
    res_part = run_ukf_on_trajectory(traj_part, forced_clean_init_on_fouled=True)
    m = res_part["metrics"]
    rows.append({
        "test_category": "Initialization Robustness",
        "scenario_name": "Strategy_D_Unknown_Partially_Fouled",
        "state_model": "Model B (Axial 6-Zone)",
        "sensor_set": "Case 2 (Standard)",
        "noise_level": "NOMINAL",
        "initial_error": "Unknown Fouled (Assumed Clean)",
        "rmse_rf_m_inv": m.rmse_rf_m_inv,
        "nrmse_rf": m.nrmse_rf,
        "mae_decline_pct": m.mae_permeability_decline_pct,
        "rmse_decline_pct": m.rmse_permeability_decline_pct,
        "max_decline_error_pct": m.max_permeability_decline_error_pct,
        "p95_decline_error_pct": m.p95_permeability_decline_error_pct,
        "convergence_time_h": m.convergence_time_hours if m.convergence_time_hours is not None else 0.0,
        "mean_step_time_ms": m.mean_step_duration_ms,
        "mean_nis": m.mean_nis,
        "nis_95_pass_pct": m.nis_95pct_ci_pass_rate,
    })

    # 3. Noise Sensitivity Tests (Low, Nominal, High)
    for n_level in [NoiseLevel.LOW, NoiseLevel.NOMINAL, NoiseLevel.HIGH]:
        print(f"  Running UKF Noise Sensitivity: {n_level.value} Noise...")
        res = run_ukf_on_trajectory(traj_d, noise_level=n_level)
        m = res["metrics"]
        rows.append({
            "test_category": "Noise Sensitivity",
            "scenario_name": f"Strategy_D_{n_level.value}_Noise",
            "state_model": "Model B (Axial 6-Zone)",
            "sensor_set": "Case 2 (Standard)",
            "noise_level": n_level.value,
            "initial_error": "0%",
            "rmse_rf_m_inv": m.rmse_rf_m_inv,
            "nrmse_rf": m.nrmse_rf,
            "mae_decline_pct": m.mae_permeability_decline_pct,
            "rmse_decline_pct": m.rmse_permeability_decline_pct,
            "max_decline_error_pct": m.max_permeability_decline_error_pct,
            "p95_decline_error_pct": m.p95_permeability_decline_error_pct,
            "convergence_time_h": m.convergence_time_hours if m.convergence_time_hours is not None else 0.0,
            "mean_step_time_ms": m.mean_step_duration_ms,
            "mean_nis": m.mean_nis,
            "nis_95_pass_pct": m.nis_95pct_ci_pass_rate,
        })

    # 4. State Representation Comparison (Model A vs Model B vs Model C)
    for s_rep, name_str in [
        (StateRepresentation.FULL_15_ELEMENT, "Model A (Full 15-Element)"),
        (StateRepresentation.AXIAL_6_ZONE, "Model B (Axial 6-Zone)"),
        (StateRepresentation.LUMPED_2_STAGE, "Model C (Lumped 2-Stage)"),
    ]:
        print(f"  Running UKF State Representation: {name_str}...")
        res = run_ukf_on_trajectory(traj_d, representation=s_rep)
        m = res["metrics"]
        rows.append({
            "test_category": "State Representation Comparison",
            "scenario_name": f"Strategy_D_{s_rep.value}",
            "state_model": name_str,
            "sensor_set": "Case 2 (Standard)",
            "noise_level": "NOMINAL",
            "initial_error": "0%",
            "rmse_rf_m_inv": m.rmse_rf_m_inv,
            "nrmse_rf": m.nrmse_rf,
            "mae_decline_pct": m.mae_permeability_decline_pct,
            "rmse_decline_pct": m.rmse_permeability_decline_pct,
            "max_decline_error_pct": m.max_permeability_decline_error_pct,
            "p95_decline_error_pct": m.p95_permeability_decline_error_pct,
            "convergence_time_h": m.convergence_time_hours if m.convergence_time_hours is not None else 0.0,
            "mean_step_time_ms": m.mean_step_duration_ms,
            "mean_nis": m.mean_nis,
            "nis_95_pass_pct": m.nis_95pct_ci_pass_rate,
        })

    df = pd.DataFrame(rows)
    df.to_csv(tables_dir / "ukf_benchmark.csv", index=False)
    print(f"\n[OK] Saved UKF benchmark summary table to {tables_dir / 'ukf_benchmark.csv'}")


if __name__ == "__main__":
    run_stage7_ukf_benchmark()
