"""
Pareto Front Post-Processing, Representative Solution Selection, and Dominance Analysis.

Functions for:
1. Extracting and sorting non-dominated solutions.
2. Selecting 4 representative operating strategies (Max Recovery, Min Energy, Min Stress, Knee).
3. Mathematical knee-point identification using normalized Euclidean distance to the ideal point.
4. Baseline dominance testing against the authoritative Stage 4B baseline.
5. Sampling evenly distributed candidates across the Pareto front for verification.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
import pandas as pd

# Authoritative Stage 4B / V2.0 Mechanistic Baseline values
AUTHORITATIVE_BASELINE = {
    "stage1_pressure_bar": 13.0,
    "stage2_pressure_bar": 18.0,
    "feed_flow_m3h": 30.0,
    "feed_tds_mgL": 2041.0,
    "temperature_C": 25.0,
    "overall_recovery_pct": 65.454298,
    "SEC_kWh_m3": 0.824396,
    "maximum_element_recovery_pct": 21.244116,
    "permeate_tds_mgL": 7.179466,
    "concentrate_tds_mgL": 5894.512507,
    "average_flux_LMH": 35.380702,
    "maximum_polarization_modulus": 1.281999,
}


def find_non_dominated_front(df_candidates: pd.DataFrame) -> pd.DataFrame:
    """
    Filter dataframe of candidates to retain only the non-dominated Pareto front
    for the 3 objectives: Maximize Recovery (f1 = -recovery), Minimize SEC (f2 = SEC),
    Minimize Max Element Recovery (f3 = max_elem_rec).
    """
    if df_candidates.empty:
        return df_candidates.copy()

    # Form cost matrix (all minimized)
    f1 = -df_candidates["overall_recovery_pct"].to_numpy(dtype=float)
    f2 = df_candidates["SEC_kWh_m3"].to_numpy(dtype=float)
    f3 = df_candidates["maximum_element_recovery_pct"].to_numpy(dtype=float)
    F = np.column_stack([f1, f2, f3])
    n = len(F)

    is_dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i != j and not is_dominated[j]:
                # Check if j dominates i
                if np.all(F[j] <= F[i] + 1e-8) and np.any(F[j] < F[i] - 1e-8):
                    is_dominated[i] = True
                    break

    df_front = df_candidates.iloc[~is_dominated].copy().reset_index(drop=True)
    # Sort by overall recovery ascending
    df_front = df_front.sort_values(by="overall_recovery_pct", ascending=True).reset_index(drop=True)
    return df_front


def select_knee_solution(df_pareto: pd.DataFrame) -> Tuple[pd.Series, float]:
    """
    Select the balanced/knee solution using the normalized Euclidean distance to the ideal point:
    z_k(i) = (f_k(i) - min(f_k)) / (max(f_k) - min(f_k) + 1e-12)
    d(i) = sqrt(sum(z_k(i)^2))
    Knee = argmin_i d(i)
    """
    if df_pareto.empty:
        raise ValueError("Pareto front is empty; cannot select knee point.")

    f1 = -df_pareto["overall_recovery_pct"].to_numpy(dtype=float)
    f2 = df_pareto["SEC_kWh_m3"].to_numpy(dtype=float)
    f3 = df_pareto["maximum_element_recovery_pct"].to_numpy(dtype=float)
    F = np.column_stack([f1, f2, f3])

    f_min = np.min(F, axis=0)
    f_max = np.max(F, axis=0)
    denom = np.where((f_max - f_min) < 1e-8, 1.0, f_max - f_min)

    Z = (F - f_min) / denom
    distances = np.sqrt(np.sum(Z**2, axis=1))

    best_idx = int(np.argmin(distances))
    knee_solution = df_pareto.iloc[best_idx].copy()
    knee_solution["knee_ideal_distance"] = distances[best_idx]

    return knee_solution, float(distances[best_idx])


def select_representative_solutions(df_pareto: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Extract the 4 key representative operating strategies from the Pareto front:
    A. Maximum Recovery
    B. Minimum Energy (SEC)
    C. Minimum Membrane Stress (Max Element Recovery)
    D. Balanced / Knee Solution
    """
    if df_pareto.empty:
        raise ValueError("Cannot select representative solutions from an empty Pareto front.")

    # A. Max Recovery
    idx_max_rec = int(df_pareto["overall_recovery_pct"].idxmax())
    sol_max_rec = df_pareto.loc[idx_max_rec].to_dict()
    sol_max_rec["strategy_name"] = "A_MAX_RECOVERY"

    # B. Min Energy (SEC)
    idx_min_sec = int(df_pareto["SEC_kWh_m3"].idxmin())
    sol_min_sec = df_pareto.loc[idx_min_sec].to_dict()
    sol_min_sec["strategy_name"] = "B_MIN_ENERGY"

    # C. Min Stress (Max Element Recovery)
    idx_min_stress = int(df_pareto["maximum_element_recovery_pct"].idxmin())
    sol_min_stress = df_pareto.loc[idx_min_stress].to_dict()
    sol_min_stress["strategy_name"] = "C_MIN_STRESS"

    # D. Knee point
    sol_knee_series, dist = select_knee_solution(df_pareto)
    sol_knee = sol_knee_series.to_dict()
    sol_knee["strategy_name"] = "D_BALANCED_KNEE"

    return {
        "max_recovery": sol_max_rec,
        "min_energy": sol_min_sec,
        "min_stress": sol_min_stress,
        "balanced_knee": sol_knee,
    }


def evaluate_baseline_dominance(
    df_pareto: pd.DataFrame,
    baseline: Optional[Dict[str, float]] = None,
    tolerance: float = 1e-4,
) -> Dict[str, Any]:
    """
    Perform rigorous dominance test between the Pareto front and the authoritative baseline:
    Baseline: Recovery=69.3597%, SEC=0.771027 kWh/m3, MaxElemRec=23.6858%.

    A solution i dominates baseline iff:
    R_i >= R_base - tol AND SEC_i <= SEC_base + tol AND ElemRec_i <= ElemRec_base + tol
    AND at least one strict inequality.
    """
    if baseline is None:
        baseline = AUTHORITATIVE_BASELINE

    r_base = float(baseline["overall_recovery_pct"])
    sec_base = float(baseline["SEC_kWh_m3"])
    elem_rec_base = float(baseline["maximum_element_recovery_pct"])

    r_vec = df_pareto["overall_recovery_pct"].to_numpy(dtype=float)
    sec_vec = df_pareto["SEC_kWh_m3"].to_numpy(dtype=float)
    elem_rec_vec = df_pareto["maximum_element_recovery_pct"].to_numpy(dtype=float)

    # 1. Candidates that dominate baseline
    cond_rec_better_eq = r_vec >= r_base - tolerance
    cond_sec_better_eq = sec_vec <= sec_base + tolerance
    cond_elem_better_eq = elem_rec_vec <= elem_rec_base + tolerance

    cond_strict = (
        (r_vec > r_base + tolerance) |
        (sec_vec < sec_base - tolerance) |
        (elem_rec_vec < elem_rec_base - tolerance)
    )

    dominates_baseline = cond_rec_better_eq & cond_sec_better_eq & cond_elem_better_eq & cond_strict
    dominating_indices = np.where(dominates_baseline)[0]
    n_dominating = len(dominating_indices)

    # 2. Does baseline dominate any candidates in the set?
    cond_base_rec_better_eq = r_base >= r_vec - tolerance
    cond_base_sec_better_eq = sec_base <= sec_vec + tolerance
    cond_base_elem_better_eq = elem_rec_base <= elem_rec_vec + tolerance
    cond_base_strict = (
        (r_base > r_vec + tolerance) |
        (sec_base < sec_vec - tolerance) |
        (elem_rec_base < elem_rec_vec - tolerance)
    )
    baseline_dominates_cand = cond_base_rec_better_eq & cond_base_sec_better_eq & cond_base_elem_better_eq & cond_base_strict
    n_dominated_by_baseline = int(np.sum(baseline_dominates_cand))

    if n_dominating > 0:
        baseline_status = "DOMINATED"
    elif n_dominated_by_baseline > 0:
        baseline_status = "DOMINATING"
    else:
        baseline_status = "NON_DOMINATED"

    # Find closest Pareto candidate to baseline in objective space
    f_base = np.array([-r_base, sec_base, elem_rec_base])
    F_pareto = np.column_stack([-r_vec, sec_vec, elem_rec_vec])
    # Normalize by baseline scale
    scale = np.array([abs(r_base), sec_base, elem_rec_base])
    diff_norm = np.linalg.norm((F_pareto - f_base) / scale, axis=1)
    closest_idx = int(np.argmin(diff_norm))
    closest_solution = df_pareto.iloc[closest_idx].to_dict()

    return {
        "baseline_status": baseline_status,
        "n_candidates_dominating_baseline": n_dominating,
        "n_candidates_dominated_by_baseline": n_dominated_by_baseline,
        "closest_pareto_candidate": closest_solution,
        "closest_relative_distance": float(diff_norm[closest_idx]),
        "dominating_candidates": df_pareto.iloc[dominating_indices].to_dict(orient="records") if n_dominating > 0 else [],
    }


def select_distributed_pareto_candidates(
    df_pareto: pd.DataFrame,
    representative_solutions: Dict[str, Dict[str, Any]],
    n_additional: int = 10,
) -> List[Dict[str, Any]]:
    """
    Select representative solutions plus n_additional evenly spaced Pareto points across recovery.
    """
    df_sorted = df_pareto.sort_values(by="overall_recovery_pct").reset_index(drop=True)
    n = len(df_sorted)

    candidates_to_verify = []

    # Add the 4 representative solutions first
    rep_keys = ["max_recovery", "min_energy", "min_stress", "balanced_knee"]
    added_pressures = set()

    for rk in rep_keys:
        sol = representative_solutions[rk]
        p_key = (round(sol["stage1_pressure_bar"], 3), round(sol["stage2_pressure_bar"], 3))
        if p_key not in added_pressures:
            candidates_to_verify.append(sol)
            added_pressures.add(p_key)

    # Uniform quantiles across the sorted front
    if n > n_additional:
        indices = np.linspace(0, n - 1, n_additional + 2, dtype=int)[1:-1]
        for idx in indices:
            sol = df_sorted.iloc[idx].to_dict()
            p_key = (round(sol["stage1_pressure_bar"], 3), round(sol["stage2_pressure_bar"], 3))
            if p_key not in added_pressures:
                sol["strategy_name"] = f"PARETO_SAMPLE_{idx+1}"
                candidates_to_verify.append(sol)
                added_pressures.add(p_key)
    else:
        for idx, row in df_sorted.iterrows():
            sol = row.to_dict()
            p_key = (round(sol["stage1_pressure_bar"], 3), round(sol["stage2_pressure_bar"], 3))
            if p_key not in added_pressures:
                sol["strategy_name"] = f"PARETO_SAMPLE_{idx+1}"
                candidates_to_verify.append(sol)
                added_pressures.add(p_key)

    return candidates_to_verify
