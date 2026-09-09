"""
Performance Metrics, Error Statistics, and Filter Consistency Evaluation (Stage 7).

Provides functions to compute:
1. RMSE, NRMSE, and MAE for Rf resistance and permeability decline
2. Convergence time from perturbed initial conditions
3. Statistical filter consistency tests (NIS and NEES vs chi-square bounds)
4. Computation benchmark statistics
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats

from state_estimation.state_model import StateVector, StateRepresentation
from state_estimation.ekf import EKFStepResult
from state_estimation.ukf import UKFStepResult
from fouling.model import RM_AUTHORITATIVE_M_INV


@dataclass
class StateEstimationMetrics:
    rmse_rf_m_inv: float
    nrmse_rf: float
    mae_rf_m_inv: float
    mae_permeability_decline_pct: float
    rmse_permeability_decline_pct: float
    max_permeability_decline_error_pct: float
    p95_permeability_decline_error_pct: float
    convergence_time_hours: Optional[float]
    mean_step_duration_ms: float
    max_step_duration_ms: float
    mean_nis: float
    nis_95pct_ci_pass_rate: float
    mean_nees: Optional[float] = None
    nees_95pct_ci_pass_rate: Optional[float] = None


def compute_estimation_metrics(
    step_history: Union[List[EKFStepResult], List[UKFStepResult]],
    true_states_15: List[np.ndarray],  # List of (15,) arrays at each time step
    temperature_celsius: float = 25.0,
    convergence_threshold_pct: float = 5.0,
) -> StateEstimationMetrics:
    """
    Compute comprehensive estimation accuracy and consistency statistics across trajectory.
    """
    n_steps = len(step_history)
    if n_steps == 0:
        raise ValueError("Cannot compute metrics on empty step history.")

    rf_errors = []
    rf_true_norms = []
    decline_errors = []
    durations = []
    nis_values = []
    nees_values = []

    meas_dim = len(step_history[0].innovation_residual)
    state_dim = step_history[0].posterior_state.values.shape[0]

    converged_idx: Optional[int] = None

    for idx, (res, st_true_15) in enumerate(zip(step_history, true_states_15)):
        # True state projected to 15 elements
        rf_true = np.asarray(st_true_15, dtype=float).flatten()
        rf_est = res.posterior_state.to_15_element_array()

        # Rf errors
        diff_rf = rf_est - rf_true
        rf_errors.append(diff_rf)
        rf_true_norms.append(np.linalg.norm(rf_true))

        # Permeability decline error
        decl_true = (1.0 - (RM_AUTHORITATIVE_M_INV / (RM_AUTHORITATIVE_M_INV + rf_true))) * 100.0
        decl_est = res.posterior_state.to_permeability_decline_pct_15(temperature_celsius)
        diff_decl = np.mean(np.abs(decl_est - decl_true))
        decline_errors.append(diff_decl)

        durations.append(res.step_duration_ms)
        nis_values.append(res.nis)
        if res.nees is not None and not np.isnan(res.nees):
            nees_values.append(res.nees)

        # Check convergence: element-wise relative error <= threshold_pct
        rel_err_max = np.max(np.abs(diff_rf) / np.maximum(rf_true, RM_AUTHORITATIVE_M_INV * 0.05)) * 100.0
        if rel_err_max <= convergence_threshold_pct and converged_idx is None:
            # Verify if it stays converged for subsequent steps
            converged_idx = idx

    all_rf_diffs = np.concatenate(rf_errors)
    rmse_rf = float(np.sqrt(np.mean(all_rf_diffs ** 2)))
    mae_rf = float(np.mean(np.abs(all_rf_diffs)))
    mean_true_rf = float(np.mean(np.concatenate(true_states_15)))
    nrmse_rf = float(rmse_rf / max(mean_true_rf, RM_AUTHORITATIVE_M_INV * 0.1))

    mae_decl = float(np.mean(decline_errors))
    rmse_decl = float(np.sqrt(np.mean(np.array(decline_errors) ** 2)))
    max_decl = float(np.max(decline_errors))
    p95_decl = float(np.percentile(decline_errors, 95))

    conv_time = float(step_history[converged_idx].time_hours) if converged_idx is not None else None

    # Filter consistency tests
    mean_nis = float(np.mean(nis_values))
    # Chi-squared 95% acceptance interval for NIS: [chi2(0.025, m), chi2(0.975, m)]
    nis_low = stats.chi2.ppf(0.025, df=meas_dim)
    nis_high = stats.chi2.ppf(0.975, df=meas_dim)
    nis_pass = float(np.mean([(nis_low <= v <= nis_high) for v in nis_values]) * 100.0)

    mean_nees = float(np.mean(nees_values)) if nees_values else None
    nees_pass = None
    if nees_values:
        nees_low = stats.chi2.ppf(0.025, df=state_dim)
        nees_high = stats.chi2.ppf(0.975, df=state_dim)
        nees_pass = float(np.mean([(nees_low <= v <= nees_high) for v in nees_values]) * 100.0)

    return StateEstimationMetrics(
        rmse_rf_m_inv=rmse_rf,
        nrmse_rf=nrmse_rf,
        mae_rf_m_inv=mae_rf,
        mae_permeability_decline_pct=mae_decl,
        rmse_permeability_decline_pct=rmse_decl,
        max_permeability_decline_error_pct=max_decl,
        p95_permeability_decline_error_pct=p95_decl,
        convergence_time_hours=conv_time,
        mean_step_duration_ms=float(np.mean(durations)),
        max_step_duration_ms=float(np.max(durations)),
        mean_nis=mean_nis,
        nis_95pct_ci_pass_rate=nis_pass,
        mean_nees=mean_nees,
        nees_95pct_ci_pass_rate=nees_pass,
    )


def evaluate_filter_consistency(
    nis_list: List[float],
    meas_dimension: int,
    nees_list: Optional[List[float]] = None,
    state_dimension: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Perform formal two-sided chi-square hypothesis testing on NIS and NEES sequences.
    """
    n = len(nis_list)
    nis_low = stats.chi2.ppf(0.025, df=meas_dimension)
    nis_high = stats.chi2.ppf(0.975, df=meas_dimension)
    nis_mean = float(np.mean(nis_list))

    # Average NIS bound: chi2(m*N) / N
    avg_nis_low = stats.chi2.ppf(0.025, df=meas_dimension * n) / n
    avg_nis_high = stats.chi2.ppf(0.975, df=meas_dimension * n) / n
    nis_consistent = bool(avg_nis_low <= nis_mean <= avg_nis_high)

    report = {
        "meas_dimension": meas_dimension,
        "sample_count": n,
        "mean_nis": nis_mean,
        "expected_nis": float(meas_dimension),
        "nis_95_bounds": (float(avg_nis_low), float(avg_nis_high)),
        "nis_consistent": nis_consistent,
    }

    if nees_list and state_dimension:
        nees_mean = float(np.mean(nees_list))
        avg_nees_low = stats.chi2.ppf(0.025, df=state_dimension * n) / n
        avg_nees_high = stats.chi2.ppf(0.975, df=state_dimension * n) / n
        nees_consistent = bool(avg_nees_low <= nees_mean <= avg_nees_high)
        report.update({
            "state_dimension": state_dimension,
            "mean_nees": nees_mean,
            "expected_nees": float(state_dimension),
            "nees_95_bounds": (float(avg_nees_low), float(avg_nees_high)),
            "nees_consistent": nees_consistent,
        })

    return report
