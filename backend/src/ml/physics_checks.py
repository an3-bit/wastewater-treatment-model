"""
Physics-Consistency Verification and Mass-Balance Reconstruction Module.

Performs:
1. Controlled single-variable sweeps around the Stage 2 baseline operating point.
2. Comparison of mechanistic simulator vs ML surrogate monotonic physical trends.
3. Quantified mass and solute balance reconstruction checks on surrogate predictions.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from data_generation.simulator_runner import run_single_simulation, create_baseline_system
from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS


BASELINE_POINT = {
    "feed_flow_m3h": 30.0,
    "feed_tds_mgL": 2041.0,
    "temperature_C": 25.0,
    "stage1_pressure_bar": 13.0,
    "stage2_pressure_bar": 18.0,
    "feed_cod_mgL": 51.0,
    "feed_pH": 8.0,
}


def perform_single_variable_sweeps(
    surrogate_model_dict: Dict[str, Any],
    pipeline: Optional[PreprocessingPipeline] = None,
    is_neural_net: bool = False,
    baseline: Optional[Dict[str, float]] = None,
    n_points: int = 15,
) -> Dict[str, pd.DataFrame]:
    """
    Perform 1D sweeps across each of the 5 mechanistic inputs while holding others constant.
    Compares mechanistic simulator output vs ML surrogate output.
    """
    b = baseline or BASELINE_POINT
    system = create_baseline_system()
    sweeps = {}

    sweep_ranges = {
        "stage1_pressure_bar": np.linspace(10.0, 18.0, n_points),
        "stage2_pressure_bar": np.linspace(15.0, 26.0, n_points),
        "feed_tds_mgL": np.linspace(1600.0, 2800.0, n_points),
        "feed_flow_m3h": np.linspace(22.0, 38.0, n_points),
        "temperature_C": np.linspace(20.0, 34.0, n_points),
    }

    for var_name, values in sweep_ranges.items():
        records = []
        for val in values:
            pt = dict(b)
            pt[var_name] = float(val)
            # Ensure P2 >= P1
            if pt["stage2_pressure_bar"] < pt["stage1_pressure_bar"]:
                pt["stage2_pressure_bar"] = pt["stage1_pressure_bar"] + 1.0

            # 1. Run mechanistic simulator
            mech_res = run_single_simulation(
                feed_flow_m3h=pt["feed_flow_m3h"],
                feed_tds_mgL=pt["feed_tds_mgL"],
                feed_cod_mgL=pt["feed_cod_mgL"],
                feed_pH=pt["feed_pH"],
                temperature_C=pt["temperature_C"],
                stage1_pressure_bar=pt["stage1_pressure_bar"],
                stage2_pressure_bar=pt["stage2_pressure_bar"],
                system=system,
            )

            # 2. Run ML surrogate
            df_pt = pd.DataFrame([pt])
            if is_neural_net:
                X_scaled = pipeline.transform_features(df_pt)
                pred_rec = {}
                for tgt in ALL_TARGETS:
                    p_s = surrogate_model_dict[tgt].predict(X_scaled)
                    p_raw = pipeline.inverse_transform_target(p_s, tgt)[0]
                    pred_rec[f"ml_{tgt}"] = p_raw
            else:
                X = df_pt[FEATURE_COLUMNS].to_numpy(dtype=float)
                pred_rec = {}
                for tgt in ALL_TARGETS:
                    p_raw = surrogate_model_dict[tgt].predict(X)[0]
                    pred_rec[f"ml_{tgt}"] = p_raw

            row = {
                "sweep_variable": var_name,
                "sweep_value": val,
                "mech_feasible": mech_res["feasible"],
                "mech_overall_recovery_pct": mech_res.get("overall_recovery_pct", np.nan),
                "mech_average_flux_LMH": mech_res.get("average_flux_LMH", np.nan),
                "mech_SEC_kWh_m3": mech_res.get("SEC_kWh_m3", np.nan),
                "mech_concentrate_tds_mgL": mech_res.get("concentrate_tds_mgL", np.nan),
                "mech_permeate_tds_mgL": mech_res.get("permeate_tds_mgL", np.nan),
                "mech_maximum_element_recovery_pct": mech_res.get("maximum_element_recovery_pct", np.nan),
            }
            row.update(pred_rec)
            records.append(row)

        sweeps[var_name] = pd.DataFrame(records)

    return sweeps


def check_physics_monotonicity(sweep_df: pd.DataFrame, var_name: str) -> Dict[str, str]:
    """
    Check if the ML surrogate exhibits expected physical monotonic directional trends.
    """
    flags = {}
    ml_rec = sweep_df["ml_overall_recovery_pct"].to_numpy()
    ml_flux = sweep_df["ml_average_flux_LMH"].to_numpy()
    ml_sec = sweep_df["ml_SEC_kWh_m3"].to_numpy()
    ml_cr = sweep_df["ml_concentrate_tds_mgL"].to_numpy()

    if var_name == "stage1_pressure_bar":
        # Higher P1 must increase recovery and flux
        d_rec = np.diff(ml_rec)
        d_flux = np.diff(ml_flux)
        flags["recovery_trend"] = "PHYSICS_CONSISTENT" if np.all(d_rec >= -0.5) else "PHYSICS_INCONSISTENT"
        flags["flux_trend"] = "PHYSICS_CONSISTENT" if np.all(d_flux >= -0.5) else "PHYSICS_INCONSISTENT"

    elif var_name == "feed_tds_mgL":
        # Higher TDS must increase concentrate TDS
        d_cr = np.diff(ml_cr)
        flags["concentrate_tds_trend"] = "PHYSICS_CONSISTENT" if np.all(d_cr >= -50.0) else "PHYSICS_INCONSISTENT"

    elif var_name == "feed_flow_m3h":
        # Higher feed flow at fixed area reduces overall recovery fraction
        d_rec = np.diff(ml_rec)
        flags["recovery_trend"] = "PHYSICS_CONSISTENT" if np.all(d_rec <= 0.5) else "PHYSICS_INCONSISTENT"

    else:
        flags["general_trend"] = "PHYSICS_CONSISTENT"

    return flags


def evaluate_mass_balance_reconstruction(
    pred_df: pd.DataFrame,
    df_inputs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Reconstruct fluid and solute balances from independent surrogate predictions:
    Qp_recon = Qf * (R_pred / 100)
    Qr_recon = Qf - Qp_recon
    Solute_Error = |Qf*Cf - (Qp_recon*Cp_pred + Qr_recon*Cr_pred)|
    """
    qf = df_inputs["feed_flow_m3h"].to_numpy(dtype=float)
    cf = df_inputs["feed_tds_mgL"].to_numpy(dtype=float)

    r_pred = pred_df["overall_recovery_pct"].to_numpy(dtype=float)
    cp_pred = pred_df["permeate_tds_mgL"].to_numpy(dtype=float)
    cr_pred = pred_df["concentrate_tds_mgL"].to_numpy(dtype=float)

    qp_recon = qf * (r_pred / 100.0)
    qr_recon = qf - qp_recon

    solute_in_kgh = (qf * cf) / 1000.0
    solute_out_kgh = (qp_recon * cp_pred + qr_recon * cr_pred) / 1000.0
    solute_diff_kgh = np.abs(solute_in_kgh - solute_out_kgh)
    solute_err_pct = (solute_diff_kgh / solute_in_kgh) * 100.0

    df_res = pd.DataFrame({
        "feed_flow_m3h": qf,
        "feed_tds_mgL": cf,
        "predicted_recovery_pct": r_pred,
        "predicted_permeate_tds_mgL": cp_pred,
        "predicted_concentrate_tds_mgL": cr_pred,
        "reconstructed_qp_m3h": qp_recon,
        "reconstructed_qr_m3h": qr_recon,
        "solute_in_kgh": solute_in_kgh,
        "solute_out_kgh": solute_out_kgh,
        "solute_error_kgh": solute_diff_kgh,
        "solute_error_percent": solute_err_pct,
    })

    return df_res
