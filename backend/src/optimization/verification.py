"""
Mechanistic Verification and Surrogate Exploitation Audit for Stage 5.

Performs batch ground-truth verification of surrogate Pareto candidates using the
full mechanistic differential-algebraic RO simulator.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
import pandas as pd

from ml.inference import Stage4Surrogate
from ml.domain_guard import OptimizationDomainGuard
from ml.verification import verify_candidate_with_mechanistic_model


def verify_pareto_candidates_batch(
    candidates: List[Dict[str, Any]],
    surrogate: Stage4Surrogate,
    domain_guard: OptimizationDomainGuard,
    permeate_tds_limit: float = 18.0,
    max_element_recovery_limit: float = 30.0,
    polarization_limit: float = 1.40,
) -> pd.DataFrame:
    """
    Rerun candidate operating points through the full mechanistic RO simulator.
    Evaluates:
    1. Ground-truth feasibility and objective values.
    2. Prediction errors for ANN Direct and Physics-Reconstructed modes.
    3. Ground-truth constraint satisfaction (safeguards, quality limits).
    """
    rows = []

    for cand in candidates:
        audit = verify_candidate_with_mechanistic_model(
            candidate=cand,
            surrogate=surrogate,
            domain_guard=domain_guard,
        )

        p1 = float(cand["stage1_pressure_bar"])
        p2 = float(cand["stage2_pressure_bar"])
        strategy = cand.get("strategy_name", "PARETO_CANDIDATE")

        err_mat = audit["error_matrix"]
        mech_feas = audit["mechanistic_feasible"]
        recon_preds = audit["reconstructed_predictions"]

        # Ground truth mechanistic values
        mech_rec = err_mat["overall_recovery_pct"]["mechanistic"]
        mech_sec = err_mat["SEC_kWh_m3"]["mechanistic"]
        mech_elem_rec = err_mat["maximum_element_recovery_pct"]["mechanistic"]
        mech_cp = err_mat["permeate_tds_mgL"]["mechanistic"]
        mech_cr = err_mat["concentrate_tds_mgL"]["mechanistic"]
        mech_flux = err_mat["average_flux_LMH"]["mechanistic"]
        mech_beta = err_mat["maximum_polarization_modulus"]["mechanistic"]

        # Reconstructed surrogate predictions
        surr_rec = err_mat["overall_recovery_pct"]["ann_reconstructed"]
        surr_sec = err_mat["SEC_kWh_m3"]["ann_reconstructed"]
        surr_elem_rec = err_mat["maximum_element_recovery_pct"]["ann_reconstructed"]
        surr_cp = err_mat["permeate_tds_mgL"]["ann_reconstructed"]
        surr_cr = err_mat["concentrate_tds_mgL"]["ann_reconstructed"]
        surr_flux = err_mat["average_flux_LMH"]["ann_reconstructed"]
        surr_beta = err_mat["maximum_polarization_modulus"]["ann_reconstructed"]

        # Ground-truth constraint checks
        mech_p2_ge_p1 = (p2 >= p1 - 1e-4)
        mech_elem_rec_safe = (mech_elem_rec <= max_element_recovery_limit + 1e-4)
        mech_cp_safe = (mech_cp <= permeate_tds_limit + 1e-4)
        mech_beta_safe = (mech_beta <= polarization_limit + 1e-4)
        mech_all_safe = bool(mech_feas and mech_p2_ge_p1 and mech_elem_rec_safe and mech_cp_safe)

        row = {
            "strategy_name": strategy,
            "stage1_pressure_bar": p1,
            "stage2_pressure_bar": p2,
            "feed_flow_m3h": float(cand["feed_flow_m3h"]),
            "feed_tds_mgL": float(cand["feed_tds_mgL"]),
            "temperature_C": float(cand["temperature_C"]),
            "domain_proximity_status": audit["proximity_status"],
            "domain_z_distance": audit["proximity_z_distance"],
            # Mechanistic ground truth
            "mech_overall_recovery_pct": mech_rec,
            "mech_SEC_kWh_m3": mech_sec,
            "mech_max_element_rec_pct": mech_elem_rec,
            "mech_permeate_tds_mgL": mech_cp,
            "mech_concentrate_tds_mgL": mech_cr,
            "mech_average_flux_LMH": mech_flux,
            "mech_max_polarization_modulus": mech_beta,
            # Surrogate reconstructed predictions
            "surr_overall_recovery_pct": surr_rec,
            "surr_SEC_kWh_m3": surr_sec,
            "surr_max_element_rec_pct": surr_elem_rec,
            "surr_permeate_tds_mgL": surr_cp,
            "surr_concentrate_tds_mgL": surr_cr,
            "surr_average_flux_LMH": surr_flux,
            "surr_max_polarization_modulus": surr_beta,
            # Errors (Reconstructed vs Mechanistic)
            "err_recovery_abs_pct": err_mat["overall_recovery_pct"]["recon_abs_error"],
            "err_recovery_rel_pct": err_mat["overall_recovery_pct"]["recon_rel_error_pct"],
            "err_sec_abs_kWh_m3": err_mat["SEC_kWh_m3"]["recon_abs_error"],
            "err_sec_rel_pct": err_mat["SEC_kWh_m3"]["recon_rel_error_pct"],
            "err_max_elem_rec_abs_pct": err_mat["maximum_element_recovery_pct"]["recon_abs_error"],
            "err_max_elem_rec_rel_pct": err_mat["maximum_element_recovery_pct"]["recon_rel_error_pct"],
            "err_permeate_tds_abs_mgL": err_mat["permeate_tds_mgL"]["recon_abs_error"],
            "err_permeate_tds_rel_pct": err_mat["permeate_tds_mgL"]["recon_rel_error_pct"],
            "err_concentrate_tds_abs_mgL": err_mat["concentrate_tds_mgL"]["recon_abs_error"],
            "err_concentrate_tds_rel_pct": err_mat["concentrate_tds_mgL"]["recon_rel_error_pct"],
            "err_polarization_abs": err_mat["maximum_polarization_modulus"]["recon_abs_error"],
            # Direct ANN vs Conserved discrepancy
            "concentrate_tds_discrepancy_pct": audit["concentrate_tds_discrepancy_pct"],
            # Ground truth safety verification
            "mech_feasible": mech_feas,
            "mech_elem_rec_safe": mech_elem_rec_safe,
            "mech_cp_safe": mech_cp_safe,
            "mech_beta_safe": mech_beta_safe,
            "mech_verified_fully_feasible": mech_all_safe,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def analyze_surrogate_exploitation(df_verified: pd.DataFrame) -> Dict[str, Any]:
    """
    Examine whether NSGA-II exploited ANN surrogate approximation errors.
    Tests for error trends as a function of recovery, pressure, and proximity to bounds.
    """
    rec = df_verified["mech_overall_recovery_pct"].to_numpy(dtype=float)
    elem_rec = df_verified["mech_max_element_rec_pct"].to_numpy(dtype=float)
    err_rec = df_verified["err_recovery_abs_pct"].to_numpy(dtype=float)
    err_sec = df_verified["err_sec_abs_kWh_m3"].to_numpy(dtype=float)
    err_elem_rec = df_verified["err_max_elem_rec_abs_pct"].to_numpy(dtype=float)

    # Correlation checks
    corr_rec_err = float(np.corrcoef(rec, err_rec)[0, 1]) if len(rec) > 2 else 0.0
    corr_elem_rec_err = float(np.corrcoef(elem_rec, err_elem_rec)[0, 1]) if len(elem_rec) > 2 else 0.0

    max_rec_err = float(np.max(err_rec))
    mean_rec_err = float(np.mean(err_rec))
    max_sec_err = float(np.max(err_sec))
    mean_sec_err = float(np.mean(err_sec))
    max_elem_rec_err = float(np.max(err_elem_rec))
    mean_elem_rec_err = float(np.mean(err_elem_rec))

    # Check if any candidate falsely appeared feasible but violated mechanistic limits
    false_feasible_candidates = df_verified[
        (df_verified["surr_max_element_rec_pct"] <= 30.0) &
        (df_verified["mech_max_element_rec_pct"] > 30.0)
    ]
    n_false_feasible = len(false_feasible_candidates)

    is_exploited = (n_false_feasible > 0) or (max_rec_err > 2.0) or (max_sec_err > 0.05)

    return {
        "mean_recovery_abs_error_pct": mean_rec_err,
        "max_recovery_abs_error_pct": max_rec_err,
        "mean_sec_abs_error_kWh_m3": mean_sec_err,
        "max_sec_abs_error_kWh_m3": max_sec_err,
        "mean_elem_rec_abs_error_pct": mean_elem_rec_err,
        "max_elem_rec_abs_error_pct": max_elem_rec_err,
        "correlation_recovery_vs_error": corr_rec_err,
        "correlation_elem_rec_vs_error": corr_elem_rec_err,
        "n_false_feasible_candidates": n_false_feasible,
        "evidence_of_exploitation": is_exploited,
    }
