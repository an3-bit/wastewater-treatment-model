"""
Dataset Curation and Engineering Envelope Classification Module.

Distinguishes MATHEMATICAL FEASIBILITY from ENGINEERING ACCEPTABILITY:
- PHYSICAL_VALID: Mathematically converged, closed mass/solute balances, no osmotic stall, P <= 41 bar.
- ENGINEERING_ACCEPTABLE: PHYSICAL_VALID and maximum_element_recovery_pct <= 30% (project engineering safeguard).
- BOUNDARY_STRESS: PHYSICAL_VALID but maximum_element_recovery_pct > 30% (retained for constraint modeling).
- INFEASIBLE: Fails physical/numerical constraints.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from data_generation.dataset import assign_dataset_splits


class OperatingClassification(str, Enum):
    """Classification taxonomy for simulation operating scenarios."""
    PHYSICAL_VALID = "PHYSICAL_VALID"
    ENGINEERING_ACCEPTABLE = "ENGINEERING_ACCEPTABLE"
    BOUNDARY_STRESS = "BOUNDARY_STRESS"
    INFEASIBLE = "INFEASIBLE"


class OODClassification(str, Enum):
    """Classification taxonomy for Out-Of-Distribution (OOD) stress testing scenarios."""
    OOD_ENGINEERING_ACCEPTABLE = "OOD_ENGINEERING_ACCEPTABLE"
    OOD_BOUNDARY_STRESS = "OOD_BOUNDARY_STRESS"
    OOD_INFEASIBLE = "OOD_INFEASIBLE"


def classify_scenario(
    row: Dict[str, Any],
    max_element_recovery_threshold: float = 30.0,
) -> OperatingClassification:
    """
    Classify an operating scenario row into the 4-tier taxonomy.
    """
    is_feasible = row.get("feasible", 0) == 1
    if not is_feasible:
        return OperatingClassification.INFEASIBLE

    max_elem_rec = row.get("maximum_element_recovery_pct", np.nan)
    if np.isnan(max_elem_rec):
        return OperatingClassification.INFEASIBLE

    if max_elem_rec <= max_element_recovery_threshold:
        return OperatingClassification.ENGINEERING_ACCEPTABLE
    else:
        return OperatingClassification.BOUNDARY_STRESS


def compute_safeguard_sensitivities(
    df_feasible: pd.DataFrame,
    thresholds: Optional[List[float]] = None,
) -> pd.DataFrame:
    """
    Evaluate dataset size sensitivity across multiple element recovery safeguard thresholds.
    """
    thresholds = thresholds or [20.0, 25.0, 30.0, 35.0]
    total_feasible = len(df_feasible)
    records = []

    for thresh in thresholds:
        count = (df_feasible["maximum_element_recovery_pct"] <= thresh).sum()
        pct_of_feasible = (count / total_feasible) * 100.0 if total_feasible > 0 else 0.0
        pct_of_all_5000 = (count / 5000.0) * 100.0
        records.append({
            "Safeguard Threshold (%)": f"<= {thresh:.0f}%",
            "Threshold Value (%)": thresh,
            "Accepted Scenarios": count,
            "% of Feasible Data": round(pct_of_feasible, 2),
            "% of 5,000 Candidates": round(pct_of_all_5000, 2),
            "Boundary Stress Scenarios": total_feasible - count,
        })

    return pd.DataFrame(records)


def compute_recovery_bands(df_feasible: pd.DataFrame) -> pd.DataFrame:
    """
    Profile key engineering stress metrics across 4 overall recovery domain bands:
    - LOW: < 50%
    - NORMAL: 50–80%
    - HIGH: 80–90%
    - EXTREME: > 90%
    """
    df = df_feasible.copy()
    bands = [
        ("LOW (< 50%)", df["overall_recovery_pct"] < 50.0),
        ("NORMAL (50–80%)", (df["overall_recovery_pct"] >= 50.0) & (df["overall_recovery_pct"] <= 80.0)),
        ("HIGH (80–90%)", (df["overall_recovery_pct"] > 80.0) & (df["overall_recovery_pct"] <= 90.0)),
        ("EXTREME (> 90%)", df["overall_recovery_pct"] > 90.0),
    ]

    records = []
    for name, mask in bands:
        sub = df[mask]
        cnt = len(sub)
        if cnt == 0:
            continue
        records.append({
            "Recovery Band": name,
            "Count": cnt,
            "% of Feasible": round((cnt / len(df)) * 100.0, 2),
            "Mean Overall Recovery (%)": round(sub["overall_recovery_pct"].mean(), 2),
            "Mean SEC (kWh/m³)": round(sub["SEC_kWh_m3"].mean(), 4),
            "Mean Concentrate TDS (mg/L)": round(sub["concentrate_tds_mgL"].mean(), 2),
            "Mean Max Elem Recovery (%)": round(sub["maximum_element_recovery_pct"].mean(), 2),
            "Mean Max Pol Modulus": round(sub["maximum_polarization_modulus"].mean(), 4),
            "Mean Permeate TDS (mg/L)": round(sub["permeate_tds_mgL"].mean(), 2),
        })

    return pd.DataFrame(records)


def curate_stage3_datasets(
    raw_data_dir: str = "data/generated",
    max_element_recovery_threshold: float = 30.0,
    seed: int = 42,
) -> Dict[str, pd.DataFrame]:
    """
    Load raw simulation data and create curated datasets:
    - stage3_engineering_acceptable.csv
    - stage3_boundary_stress.csv
    - stage3_ood_curated.csv
    
    Preserves all raw files without modification.
    """
    p_dir = Path(raw_data_dir)
    p_all = p_dir / "stage3_all_scenarios.csv"
    p_feas = p_dir / "stage3_feasible_scenarios.csv"
    p_ood = p_dir / "stage3_ood_scenarios.csv"

    if not p_all.exists() or not p_feas.exists():
        raise FileNotFoundError(f"Raw simulation files not found in {raw_data_dir}")

    df_all = pd.read_csv(p_all)
    df_feasible = pd.read_csv(p_feas)

    # 1. Apply classification taxonomy to all feasible data
    is_acceptable = df_feasible["maximum_element_recovery_pct"] <= max_element_recovery_threshold
    df_acceptable = df_feasible[is_acceptable].copy()
    df_boundary = df_feasible[~is_acceptable].copy()

    df_acceptable["operating_classification"] = OperatingClassification.ENGINEERING_ACCEPTABLE.value
    df_boundary["operating_classification"] = OperatingClassification.BOUNDARY_STRESS.value

    # 2. Recreate deterministic 70/15/15 splits on the curated engineering-acceptable set
    df_acceptable = assign_dataset_splits(
        df_acceptable,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=seed,
    )
    df_boundary["dataset_split"] = "boundary_stress"

    # 3. Export curated datasets
    p_acc_csv = p_dir / "stage3_engineering_acceptable.csv"
    p_bnd_csv = p_dir / "stage3_boundary_stress.csv"

    df_acceptable.to_csv(p_acc_csv, index=False)
    df_boundary.to_csv(p_bnd_csv, index=False)

    # 4. Process OOD dataset if available
    df_ood_curated = pd.DataFrame()
    if p_ood.exists():
        df_ood = pd.read_csv(p_ood)
        ood_classes = []
        for _, row in df_ood.iterrows():
            if row.get("feasible", 0) != 1:
                ood_classes.append(OODClassification.OOD_INFEASIBLE.value)
            elif row.get("maximum_element_recovery_pct", 100.0) <= max_element_recovery_threshold:
                ood_classes.append(OODClassification.OOD_ENGINEERING_ACCEPTABLE.value)
            else:
                ood_classes.append(OODClassification.OOD_BOUNDARY_STRESS.value)
        df_ood["ood_classification"] = ood_classes
        p_ood_curated = p_dir / "stage3_ood_curated.csv"
        df_ood.to_csv(p_ood_curated, index=False)
        df_ood_curated = df_ood

    return {
        "engineering_acceptable": df_acceptable,
        "boundary_stress": df_boundary,
        "ood_curated": df_ood_curated,
    }
