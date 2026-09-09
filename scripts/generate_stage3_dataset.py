"""
Script: generate_stage3_dataset.py
Project: AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse
Stage: 3 - Simulation-Based Dataset Development for AI

Generates 5,000 Latin Hypercube Sampled operating scenarios and a separate
Out-Of-Distribution (OOD) test set, simulates each scenario through the Stage 2
mechanistic RO plant model (Topology A, 3:2 vessel staging, 15 Toray TML20D-400 elements),
assigns deterministic train/val/test splits (70/15/15), and exports CSV & Parquet files.
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data_generation.sampling import LatinHypercubeSampler, generate_ood_samples
from data_generation.dataset import (
    generate_batch_dataset,
    assign_dataset_splits,
    save_stage3_datasets,
)


def main():
    print("=" * 80)
    print("STAGE 3: SIMULATION-BASED DATASET GENERATION")
    print("Target: 5,000 LHS Scenarios + 200 OOD Scenarios")
    print("Model: Two-Stage Mechanistic RO (Topology A, 3:2 Array, 15 Elements)")
    print("=" * 80)

    start_time = time.time()

    # 1. Generate 5,000 LHS candidate scenarios
    print("\n[1/4] Generating 5,000 candidate operating scenarios via Latin Hypercube Sampling...")
    sampler = LatinHypercubeSampler(seed=42)
    candidate_df = sampler.generate_samples(n_samples=5000)
    print(f"Generated {len(candidate_df)} candidate scenarios.")
    print("Sample parameter ranges:")
    for col in candidate_df.columns:
        print(f"  - {col:22s}: [{candidate_df[col].min():8.2f}, {candidate_df[col].max():8.2f}]")

    # 2. Simulate all 5,000 scenarios
    print("\n[2/4] Simulating candidate scenarios through mechanistic process engine...")
    sim_start = time.time()
    df_all = generate_batch_dataset(
        candidate_df,
        sampling_method="latin_hypercube",
        random_seed=42,
        model_version="2.0.0",
        parameter_set="manufacturer_reconciled",
        topology="concentrate_staging_3x2",
        show_progress=True,
    )
    sim_time = time.time() - sim_start
    print(f"Completed 5,000 simulations in {sim_time:.2f} seconds ({len(df_all)/sim_time:.1f} sims/sec).")

    # 3. Assign train / validation / test splits to feasible rows
    print("\n[3/4] Assigning deterministic train / val / test splits (70% / 15% / 15%)...")
    df_all = assign_dataset_splits(df_all, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42)
    split_counts = df_all["dataset_split"].value_counts()
    print("Dataset split allocation:")
    for split_name, count in split_counts.items():
        print(f"  - {split_name:10s}: {count:5d} ({count/len(df_all)*100:5.1f}%)")

    # 4. Generate & simulate Out-Of-Distribution (OOD) scenarios
    print("\n[4/4] Generating and simulating Out-Of-Distribution (OOD) dataset (200 scenarios)...")
    candidate_ood = generate_ood_samples(n_samples=200, seed=101)
    df_ood = generate_batch_dataset(
        candidate_ood,
        sampling_method="latin_hypercube_ood",
        random_seed=101,
        model_version="2.0.0",
        parameter_set="manufacturer_reconciled",
        topology="concentrate_staging_3x2",
        show_progress=False,
    )
    df_ood["dataset_split"] = "ood"

    # Save all datasets
    output_dir = Path("data/generated")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = save_stage3_datasets(df_all, output_dir=str(output_dir))

    # Save OOD
    ood_csv = output_dir / "stage3_ood_scenarios.csv"
    df_ood.to_csv(ood_csv, index=False)
    paths["ood_csv"] = str(ood_csv)
    try:
        ood_pq = output_dir / "stage3_ood_scenarios.parquet"
        df_ood.to_parquet(ood_pq, index=False)
        paths["ood_parquet"] = str(ood_pq)
    except Exception:
        pass

    total_time = time.time() - start_time
    feasible_count = (df_all["feasible"] == 1).sum()
    infeasible_count = (df_all["feasible"] == 0).sum()

    print("\n" + "=" * 80)
    print("DATASET GENERATION COMPLETE")
    print(f"Total Scenarios Generated : {len(df_all):d}")
    print(f"Feasible Scenarios        : {feasible_count:d} ({feasible_count/len(df_all)*100:.2f}%)")
    print(f"Infeasible Scenarios      : {infeasible_count:d} ({infeasible_count/len(df_all)*100:.2f}%)")
    print(f"OOD Scenarios             : {len(df_ood):d} (Feasible: {(df_ood['feasible']==1).sum():d})")
    print(f"Total Wall Time           : {total_time:.2f} seconds")
    print("Saved Files:")
    for k, v in paths.items():
        print(f"  - {k:18s}: {v}")
    print("=" * 80)


if __name__ == "__main__":
    main()
