"""
Mechanistic Verification and Audit Interface Module for Stage 4B / Stage 5.

Provides a unified interface to audit surrogate predictions against the full
mechanistic differential-algebraic RO simulator.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from data_generation.simulator_runner import run_single_simulation, create_baseline_system
from ml.inference import Stage4Surrogate
from ml.domain_guard import OptimizationDomainGuard, DomainProximityStatus


def verify_candidate_with_mechanistic_model(
    candidate: Dict[str, float],
    surrogate: Stage4Surrogate,
    domain_guard: Optional[OptimizationDomainGuard] = None,
) -> Dict[str, Any]:
    """
    Execute comprehensive multi-mode audit comparing:
    1. Direct ANN surrogate predictions
    2. Physics-reconstructed surrogate predictions
    3. Mechanistic differential-algebraic simulation ground truth
    
    Calculates absolute and relative errors across all primary and secondary targets.
    """
    qf = float(candidate["feed_flow_m3h"])
    cf = float(candidate["feed_tds_mgL"])
    temp = float(candidate["temperature_C"])
    p1 = float(candidate["stage1_pressure_bar"])
    p2 = float(candidate["stage2_pressure_bar"])
    cod = float(candidate.get("feed_cod_mgL", 51.0))
    ph = float(candidate.get("feed_pH", 8.0))

    # 1. Evaluate Domain Guard
    guard_valid = True
    guard_violations = []
    proximity_status = DomainProximityStatus.IN_DOMAIN.value
    proximity_z = 0.0

    if domain_guard is not None:
        guard_valid, guard_violations = domain_guard.validate_inputs(candidate)
        status_enum, proximity_z = domain_guard.evaluate_proximity_status(candidate)
        proximity_status = status_enum.value

    # 2. ANN Direct Predictions
    df_in = pd.DataFrame([candidate])
    direct_preds = surrogate.predict(df_in).iloc[0].to_dict()

    # 3. ANN Physics-Reconstructed Predictions
    recon_preds = surrogate.predict_physics_reconstructed(df_in).iloc[0].to_dict()

    # 4. Mechanistic Simulator
    system = create_baseline_system()
    mech_res = run_single_simulation(
        feed_flow_m3h=qf,
        feed_tds_mgL=cf,
        feed_cod_mgL=cod,
        feed_pH=ph,
        temperature_C=temp,
        stage1_pressure_bar=p1,
        stage2_pressure_bar=p2,
        system=system,
    )

    # 5. Compute Error Matrix (Reconstructed vs Mechanistic)
    targets_to_compare = [
        "overall_recovery_pct",
        "permeate_tds_mgL",
        "concentrate_tds_mgL",
        "average_flux_LMH",
        "SEC_kWh_m3",
        "maximum_element_recovery_pct",
        "maximum_polarization_modulus",
    ]

    error_matrix = {}
    for tgt in targets_to_compare:
        mech_val = float(mech_res.get(tgt, np.nan))
        recon_val = float(recon_preds.get(tgt, np.nan))
        direct_val = float(direct_preds.get(tgt, np.nan))

        err_recon_abs = abs(mech_val - recon_val) if not np.isnan(mech_val) else np.nan
        err_recon_rel = (err_recon_abs / abs(mech_val)) * 100.0 if (abs(mech_val) > 1e-6 and not np.isnan(mech_val)) else np.nan

        err_direct_abs = abs(mech_val - direct_val) if not np.isnan(mech_val) else np.nan
        err_direct_rel = (err_direct_abs / abs(mech_val)) * 100.0 if (abs(mech_val) > 1e-6 and not np.isnan(mech_val)) else np.nan

        error_matrix[tgt] = {
            "mechanistic": mech_val,
            "ann_direct": direct_val,
            "ann_reconstructed": recon_val,
            "direct_abs_error": err_direct_abs,
            "direct_rel_error_pct": err_direct_rel,
            "recon_abs_error": err_recon_abs,
            "recon_rel_error_pct": err_recon_rel,
        }

    return {
        "candidate_inputs": candidate,
        "domain_guard_valid": guard_valid,
        "domain_violations": guard_violations,
        "proximity_status": proximity_status,
        "proximity_z_distance": proximity_z,
        "mechanistic_feasible": bool(mech_res.get("feasible", False)),
        "direct_predictions": direct_preds,
        "reconstructed_predictions": recon_preds,
        "error_matrix": error_matrix,
        "concentrate_tds_discrepancy_pct": recon_preds.get("concentrate_tds_discrepancy_pct", np.nan),
    }
