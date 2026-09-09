"""
Dataset Orchestration and Export Module for Stage 3.

Manages batch simulation runs, attaches provenance metadata, assigns
deterministic train/val/test splits (70/15/15), and exports CSV and Parquet files.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from data_generation.sampling import (
    LatinHypercubeSampler,
    generate_ood_samples,
    OperatingDomainBounds,
    OODDomainBounds,
)
from data_generation.simulator_runner import (
    create_baseline_system,
    run_single_simulation,
)


def generate_batch_dataset(
    candidate_df: pd.DataFrame,
    sampling_method: str = "latin_hypercube",
    random_seed: int = 42,
    model_version: str = "2.0-pressure-corrected",
    parameter_set: str = "manufacturer_reconciled",
    topology: str = "concentrate_staging_3x2",
    show_progress: bool = True,
) -> pd.DataFrame:
    """
    Simulate a batch of candidate scenarios, collect outputs, and attach provenance metadata.
    """
    system = create_baseline_system()
    now_iso = datetime.now(timezone.utc).isoformat()

    results: List[Dict] = []
    total = len(candidate_df)

    for idx, row in candidate_df.iterrows():
        sim_id = f"SIM_{idx+1:05d}"
        res_dict = run_single_simulation(
            feed_flow_m3h=row["feed_flow_m3h"],
            feed_tds_mgL=row["feed_tds_mgL"],
            feed_cod_mgL=row["feed_cod_mgL"],
            feed_pH=row["feed_pH"],
            temperature_C=row["temperature_C"],
            stage1_pressure_bar=row["stage1_pressure_bar"],
            stage2_pressure_bar=row["stage2_pressure_bar"],
            system=system,
        )

        # Attach metadata
        res_dict["simulation_id"] = sim_id
        res_dict["sampling_method"] = sampling_method
        res_dict["random_seed"] = random_seed
        res_dict["model_version"] = model_version
        res_dict["parameter_set"] = parameter_set
        res_dict["topology"] = topology
        res_dict["timestamp"] = now_iso

        results.append(res_dict)

        if show_progress and ((idx + 1) % 500 == 0 or (idx + 1) == total):
            feasible_count = sum(r["feasible"] for r in results)
            print(f"Processed {idx+1}/{total} scenarios (Feasible: {feasible_count}/{idx+1} = {feasible_count/(idx+1)*100:.1f}%)")

    df_out = pd.DataFrame(results)

    # Reorder columns: ID and metadata first, inputs, status, outputs, balance errors
    metadata_cols = [
        "simulation_id",
        "sampling_method",
        "random_seed",
        "model_version",
        "parameter_set",
        "topology",
        "timestamp",
    ]
    input_cols = [
        "feed_flow_m3h",
        "feed_tds_mgL",
        "feed_cod_mgL",
        "feed_pH",
        "temperature_C",
        "stage1_pressure_bar",
        "stage2_pressure_bar",
    ]
    status_cols = [
        "feasible",
        "failure_reason",
        "failure_message",
        "quality_flag",
    ]
    output_cols = [
        "overall_recovery_pct",
        "permeate_flow_m3h",
        "concentrate_flow_m3h",
        "permeate_tds_mgL",
        "concentrate_tds_mgL",
        "overall_tds_rejection_pct",
        "stage1_recovery_pct",
        "stage2_recovery_pct",
        "average_flux_LMH",
        "minimum_flux_LMH",
        "maximum_flux_LMH",
        "maximum_element_recovery_pct",
        "maximum_polarization_modulus",
        "feed_osmotic_pressure_bar",
        "final_concentrate_osmotic_pressure_bar",
        "stage1_pump_power_kW",
        "stage2_booster_power_kW",
        "total_power_kW",
        "SEC_kWh_m3",
        "water_balance_error",
        "solute_balance_error",
        "flux_decline_stage1_pct",
        "flux_decline_stage2_pct",
        "max_element_concentrate_tds_mgL",
        "max_element_osmotic_pressure_bar",
    ]

    all_cols = metadata_cols + input_cols + status_cols + output_cols
    # Retain any extra columns
    extra_cols = [c for c in df_out.columns if c not in all_cols]
    df_out = df_out[all_cols + extra_cols]

    return df_out


def assign_dataset_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Deterministically assign train / val / test split labels to feasible scenarios.
    Infeasible scenarios are labeled 'none'.
    """
    df = df.copy()
    df["dataset_split"] = "none"

    feasible_indices = df[df["feasible"] == 1].index.to_numpy()
    n_feasible = len(feasible_indices)

    if n_feasible == 0:
        return df

    rng = np.random.default_rng(seed)
    shuffled_idx = rng.permutation(feasible_indices)

    n_train = int(np.round(n_feasible * train_ratio))
    n_val = int(np.round(n_feasible * val_ratio))
    # Test gets remaining to ensure exact sum
    train_idx = shuffled_idx[:n_train]
    val_idx = shuffled_idx[n_train : n_train + n_val]
    test_idx = shuffled_idx[n_train + n_val :]

    df.loc[train_idx, "dataset_split"] = "train"
    df.loc[val_idx, "dataset_split"] = "val"
    df.loc[test_idx, "dataset_split"] = "test"

    return df


def save_stage3_datasets(
    df_all: pd.DataFrame,
    output_dir: str = "data/generated",
) -> Dict[str, str]:
    """
    Save all, feasible, and infeasible subsets to CSV and Parquet.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df_feasible = df_all[df_all["feasible"] == 1].copy()
    df_infeasible = df_all[df_all["feasible"] == 0].copy()

    paths = {}

    # CSV exports
    p_all_csv = out_path / "stage3_all_scenarios.csv"
    p_feas_csv = out_path / "stage3_feasible_scenarios.csv"
    p_inf_csv = out_path / "stage3_infeasible_scenarios.csv"

    df_all.to_csv(p_all_csv, index=False)
    df_feasible.to_csv(p_feas_csv, index=False)
    df_infeasible.to_csv(p_inf_csv, index=False)

    paths["all_csv"] = str(p_all_csv)
    paths["feasible_csv"] = str(p_feas_csv)
    paths["infeasible_csv"] = str(p_inf_csv)

    # Parquet exports if pyarrow or fastparquet installed
    try:
        p_all_pq = out_path / "stage3_all_scenarios.parquet"
        p_feas_pq = out_path / "stage3_feasible_scenarios.parquet"
        p_inf_pq = out_path / "stage3_infeasible_scenarios.parquet"

        df_all.to_parquet(p_all_pq, index=False)
        df_feasible.to_parquet(p_feas_pq, index=False)
        df_infeasible.to_parquet(p_inf_pq, index=False)

        paths["all_parquet"] = str(p_all_pq)
        paths["feasible_parquet"] = str(p_feas_pq)
        paths["infeasible_parquet"] = str(p_inf_pq)
    except Exception as e:
        print(f"Parquet export skipped or failed: {e}")

    return paths
