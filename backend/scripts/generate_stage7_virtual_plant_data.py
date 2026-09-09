"""
Synthetic Plant Data Generation Script (Stage 7).

Generates rich virtual plant dynamic operating trajectories:
1. Multi-Strategy Baseline & Representative Operating Strategies (Baseline, A, B, C, D)
2. Variable Initial Conditions (Clean Starts, Partially Fouled Starts)
3. Kinetic Variants (Nominal, Slow, Fast Fouling)
4. Transient Process Disturbances (Feed TDS Pulse, Flow Step, Temperature Step)
5. Dynamic Pressure Operations (Mode B Production Maintaining)
6. Controlled Plant/Model Mismatch Scenarios (r_spec +/- 10%, Mass Transfer +/- 10%, Sensor Bias)
7. Multi-Level Sensor Noise Realizations (Low, Nominal, High)

Authoritative Model Version: "2.0-pressure-corrected"
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import copy
import json
import pickle
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from ro_model.membrane import RO_MODEL_VERSION, AW_AUTHORITATIVE_M_PA_S
from ro_model.system import ROSystem
from fouling.model import FoulingParameters, RM_AUTHORITATIVE_M_INV, calculate_clean_membrane_resistance
from fouling.calibration import calibrate_fouling_rate_constant
from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import (
    SensorSet,
    SENSOR_SET_MEMBERS,
    ROPlantMeasurementModel,
)
from state_estimation.noise import SensorNoiseModel, NoiseLevel, get_provenance_noise_table


def generate_single_trajectory(
    strategy_name: str,
    p1_bar: float,
    p2_bar: float,
    horizon_hours: float = 168.0,
    dt_hours: float = 1.0,
    parameters: Optional[FoulingParameters] = None,
    initial_rf_15: Optional[np.ndarray] = None,
    operating_mode: str = "MODE_A_FIXED_PRESSURE",
    feed_flow_profile: Optional[List[float]] = None,
    feed_tds_profile: Optional[List[float]] = None,
    temperature_profile: Optional[List[float]] = None,
    pressure1_profile: Optional[List[float]] = None,
    pressure2_profile: Optional[List[float]] = None,
    sensor_bias_dict: Optional[Dict[str, float]] = None,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Generate a full synthetic virtual plant trajectory with true hidden states and noisy observable outputs.
    """
    params = parameters or FoulingParameters.create_default()
    meas_model = ROPlantMeasurementModel(sensor_set=SensorSet.CASE_3_RICH)
    all_sensor_keys = SENSOR_SET_MEMBERS[SensorSet.CASE_3_RICH]

    noise_low = SensorNoiseModel(noise_level=NoiseLevel.LOW, random_seed=random_seed + 1)
    noise_nom = SensorNoiseModel(noise_level=NoiseLevel.NOMINAL, random_seed=random_seed + 2)
    noise_high = SensorNoiseModel(noise_level=NoiseLevel.HIGH, random_seed=random_seed + 3)

    timestamps = list(np.arange(0.0, horizon_hours + 1e-6, dt_hours))
    n_steps = len(timestamps)

    # Initial state
    if initial_rf_15 is None:
        curr_rf_15 = np.zeros(15, dtype=float)
    else:
        curr_rf_15 = np.asarray(initial_rf_15, dtype=float).copy()

    history_records = []

    curr_p1 = float(p1_bar)
    curr_p2 = float(p2_bar)

    for step_idx, t_now in enumerate(timestamps):
        # Determine current inputs
        q_feed = feed_flow_profile[step_idx] if feed_flow_profile else 30.0
        c_feed = feed_tds_profile[step_idx] if feed_tds_profile else 2041.0
        t_celsius = temperature_profile[step_idx] if temperature_profile else 25.0
        if pressure1_profile:
            curr_p1 = pressure1_profile[step_idx]
        if pressure2_profile:
            curr_p2 = pressure2_profile[step_idx]

        u_inputs = {
            "feed_flow_m3h": float(q_feed),
            "feed_tds_mgL": float(c_feed),
            "temperature_C": float(t_celsius),
            "stage1_pressure_bar": float(curr_p1),
            "stage2_pressure_bar": float(curr_p2),
        }

        # Current state vector
        st_curr = StateVector(values=curr_rf_15.copy(), representation=StateRepresentation.FULL_15_ELEMENT)

        # 1. Compute true process observables
        all_obs_dict = meas_model.compute_all_observables(st_curr, u_inputs)

        # Apply sensor bias if any
        if sensor_bias_dict:
            for k, bias in sensor_bias_dict.items():
                if k in all_obs_dict:
                    all_obs_dict[k] += bias

        y_true_vec = np.array([all_obs_dict[k] for k in all_sensor_keys], dtype=float)

        # 2. Generate noisy realizations
        y_low = noise_low.add_noise(y_true_vec, all_sensor_keys)
        y_nom = noise_nom.add_noise(y_true_vec, all_sensor_keys)
        y_high = noise_high.add_noise(y_true_vec, all_sensor_keys)

        # Decline metrics
        r_m = calculate_clean_membrane_resistance(AW_AUTHORITATIVE_M_PA_S, t_celsius)
        r_tot_15 = r_m + curr_rf_15
        decl_15 = (1.0 - (r_m / r_tot_15)) * 100.0
        avg_decline = float(np.mean(decl_15))

        step_record = {
            "step_index": step_idx,
            "time_hours": float(t_now),
            "u_inputs": u_inputs,
            "true_rf_15": curr_rf_15.copy(),
            "true_permeability_decline_15": decl_15.copy(),
            "true_average_permeability_decline_pct": avg_decline,
            "true_observables_dict": all_obs_dict,
            "y_measured_all_true": {k: y_true_vec[i] for i, k in enumerate(all_sensor_keys)},
            "y_measured_all": {k: y_nom[i] for i, k in enumerate(all_sensor_keys)},
            "y_measured_all_low_noise": {k: y_low[i] for i, k in enumerate(all_sensor_keys)},
            "y_measured_all_high_noise": {k: y_high[i] for i, k in enumerate(all_sensor_keys)},
        }
        history_records.append(step_record)

        # 3. Dynamic integration to next step
        if step_idx < n_steps - 1:
            dt = timestamps[step_idx + 1] - t_now
            # Solve local hydraulics to update each element
            meas_model._apply_state_to_system(st_curr, t_celsius)
            sys_res = meas_model.system.solve(
                feed_flow_m3_hr=q_feed,
                feed_tds_mg_l=c_feed,
                stage_pressures_bar=[curr_p1, curr_p2],
                temperature_celsius=t_celsius,
            )

            stg1_eres = sys_res.stage_results[0].vessel_result.element_results
            stg2_eres = sys_res.stage_results[1].vessel_result.element_results

            from fouling.kinetics import compute_element_fouling_rate_per_hour

            new_rf_15 = np.zeros(15, dtype=float)
            for e_i in range(15):
                if e_i < 9:
                    axial_pos = e_i % 3
                    eres = stg1_eres[axial_pos]
                else:
                    axial_pos = (e_i - 9) % 3
                    eres = stg2_eres[axial_pos]

                c_bulk = (eres.feed_tds_mg_l + eres.concentrate_tds_mg_l) / 2.0
                c_wall = c_bulk * eres.polarization_modulus
                drf_dt = compute_element_fouling_rate_per_hour(
                    flux_lmh=eres.water_flux_lmh,
                    polarization_modulus=eres.polarization_modulus,
                    surface_tds_mg_l=c_wall,
                    parameters=params,
                )
                new_rf_15[e_i] = max(0.0, curr_rf_15[e_i] + drf_dt * dt)

            curr_rf_15 = new_rf_15

    return {
        "strategy_name": strategy_name,
        "operating_mode": operating_mode,
        "horizon_hours": horizon_hours,
        "time_step_hours": dt_hours,
        "parameters": params,
        "records": history_records,
    }


def generate_all_stage7_datasets() -> None:
    print("=" * 80)
    print("STAGE 7: SYNTHETIC VIRTUAL PLANT DATASET GENERATION")
    print(f"Model Version: {RO_MODEL_VERSION}")
    print("=" * 80)

    out_dir = Path("results/stage7/trajectories")
    out_dir.mkdir(parents=True, exist_ok=True)
    tables_dir = Path("results/stage7/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Save noise provenance table
    noise_df = get_provenance_noise_table()
    noise_df.to_csv(tables_dir / "sensor_noise_provenance.csv", index=False)
    print(f"[OK] Saved sensor noise provenance table to {tables_dir / 'sensor_noise_provenance.csv'}")

    calib = calibrate_fouling_rate_constant()
    default_params = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec)

    strategies = {
        "Baseline": (13.00, 18.00),
        "Strategy_A": (20.00, 20.25),
        "Strategy_B": (15.80, 15.80),
        "Strategy_C": (10.00, 14.00),
        "Strategy_D": (16.06, 16.41),
    }

    # 1. Clean Start Trajectories (168h) for all strategies
    for name, (p1, p2) in strategies.items():
        print(f"  Generating 168h Clean Start Trajectory: {name} (P1={p1}, P2={p2})...")
        traj = generate_single_trajectory(
            strategy_name=name,
            p1_bar=p1,
            p2_bar=p2,
            horizon_hours=168.0,
            parameters=default_params,
        )
        with open(out_dir / f"traj_clean_{name}.pkl", "wb") as f:
            pickle.dump(traj, f)

    # 2. Partially Fouled Start (Strategy D, 168h, Rf(0) = 5.0e12)
    print("  Generating Partially Fouled Start Trajectory...")
    rf_part = np.linspace(3e12, 7e12, 15)
    traj_part = generate_single_trajectory(
        strategy_name="Strategy_D_Partially_Fouled",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        initial_rf_15=rf_part,
        parameters=default_params,
    )
    with open(out_dir / "traj_partially_fouled_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_part, f)

    # 3. Slow & Fast Fouling (Strategy D)
    print("  Generating Slow & Fast Fouling Trajectories...")
    params_slow = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec * 0.5)
    traj_slow = generate_single_trajectory(
        strategy_name="Strategy_D_Slow_Fouling",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=params_slow,
    )
    with open(out_dir / "traj_slow_fouling_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_slow, f)

    params_fast = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec * 2.0)
    traj_fast = generate_single_trajectory(
        strategy_name="Strategy_D_Fast_Fouling",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=params_fast,
    )
    with open(out_dir / "traj_fast_fouling_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_fast, f)

    # 4. Process Disturbance Trajectories (Feed TDS Pulse, Flow Variations, Temp Shift)
    print("  Generating Transient Disturbance Trajectories...")
    timestamps = list(np.arange(0.0, 168.0 + 1e-6, 1.0))
    n_steps = len(timestamps)

    # TDS pulse: +20% (2450 mg/L) from hour 30 to 48, then -15% (1735 mg/L) from hour 80 to 96
    tds_profile = [2041.0] * n_steps
    for idx, t in enumerate(timestamps):
        if 30.0 <= t <= 48.0:
            tds_profile[idx] = 2041.0 * 1.20
        elif 80.0 <= t <= 96.0:
            tds_profile[idx] = 2041.0 * 0.85

    traj_tds_dist = generate_single_trajectory(
        strategy_name="Strategy_D_TDS_Disturbance",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=default_params,
        feed_tds_profile=tds_profile,
    )
    with open(out_dir / "traj_tds_disturbance_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_tds_dist, f)

    # Flow & Temp disturbances
    flow_profile = [30.0] * n_steps
    temp_profile = [25.0] * n_steps
    for idx, t in enumerate(timestamps):
        if 40.0 <= t <= 60.0:
            flow_profile[idx] = 30.0 * 1.15
        if 70.0 <= t <= 100.0:
            temp_profile[idx] = 30.0  # +5 C shift

    traj_multi_dist = generate_single_trajectory(
        strategy_name="Strategy_D_Multi_Disturbance",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=default_params,
        feed_flow_profile=flow_profile,
        temperature_profile=temp_profile,
    )
    with open(out_dir / "traj_multi_disturbance_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_multi_dist, f)

    # 5. Model Mismatch Trajectories (r_spec +10%, r_spec -10%, sensor bias)
    print("  Generating Model Mismatch Trajectories...")
    params_mismatch_plus = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec * 1.10)
    traj_mis_plus = generate_single_trajectory(
        strategy_name="Strategy_D_Mismatch_Plus10pct",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=params_mismatch_plus,
    )
    with open(out_dir / "traj_mismatch_plus10_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_mis_plus, f)

    params_mismatch_minus = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec * 0.90)
    traj_mis_minus = generate_single_trajectory(
        strategy_name="Strategy_D_Mismatch_Minus10pct",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=params_mismatch_minus,
    )
    with open(out_dir / "traj_mismatch_minus10_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_mis_minus, f)

    # Sensor bias (+0.30 bar on P1, -0.40 m3/h on Qp)
    sensor_bias = {
        "stage1_pressure_bar": 0.30,
        "total_permeate_flow_m3h": -0.40,
    }
    traj_bias = generate_single_trajectory(
        strategy_name="Strategy_D_Sensor_Bias",
        p1_bar=16.06,
        p2_bar=16.41,
        horizon_hours=168.0,
        parameters=default_params,
        sensor_bias_dict=sensor_bias,
    )
    with open(out_dir / "traj_sensor_bias_Strategy_D.pkl", "wb") as f:
        pickle.dump(traj_bias, f)

    print("\n[COMPLETE] Successfully generated all Stage 7 virtual plant benchmark datasets.")


if __name__ == "__main__":
    generate_all_stage7_datasets()
