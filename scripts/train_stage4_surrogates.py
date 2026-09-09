"""
Stage 4 Training and Surrogates Experiment Execution Script.

Workflow:
1. Load curated dataset: data/generated/stage3_engineering_acceptable.csv
2. Partition deterministically using existing split column: train (1569), val (336), test (336)
3. Fit PreprocessingPipeline strictly on train partition.
4. Train & tune:
   - Baseline Linear Regression
   - Random Forest Regressor
   - XGBoost Regressor
   - Feed-Forward Artificial Neural Network (MLPRegressor)
5. Evaluate all models on:
   - Primary Test Set (336 rows)
   - Boundary Stress Set (2,712 rows)
   - Synthetic OOD Set (200 rows)
   - Stage 2 Baseline Operating Point
6. Save models, scalers, and metadata to models/stage4/
7. Save summary tables to results/stage4/tables/
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib

from ml.preprocessing import (
    PreprocessingPipeline,
    FEATURE_COLUMNS,
    ALL_TARGETS,
    PRIMARY_TARGETS,
    SECONDARY_TARGETS,
)
from ml.train import (
    train_linear_regression,
    train_random_forest,
    train_xgboost,
    train_ann_mlp,
)
from ml.evaluate import (
    evaluate_model_on_dataset,
    evaluate_baseline_point,
    predict_model_targets,
)
from ml.physics_checks import BASELINE_POINT
from data_generation.curation import classify_scenario


def main():
    print("=" * 70)
    print("STAGE 4: MACHINE-LEARNING SURROGATE MODEL DEVELOPMENT")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "generated"
    models_dir = base_dir / "models" / "stage4"
    results_tab_dir = base_dir / "results" / "stage4" / "tables"

    models_dir.mkdir(parents=True, exist_ok=True)
    results_tab_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load datasets
    curated_path = data_dir / "stage3_engineering_acceptable.csv"
    boundary_path = data_dir / "stage3_boundary_stress.csv"
    ood_path = data_dir / "stage3_ood_scenarios.csv"

    print(f"Loading curated primary dataset: {curated_path}")
    df_curated = pd.read_csv(curated_path)
    df_boundary = pd.read_csv(boundary_path)
    df_ood = pd.read_csv(ood_path)

    df_train = df_curated[df_curated["dataset_split"] == "train"].copy().reset_index(drop=True)
    df_val = df_curated[df_curated["dataset_split"].isin(["val", "validation"])].copy().reset_index(drop=True)
    df_test = df_curated[df_curated["dataset_split"] == "test"].copy().reset_index(drop=True)

    print(f"Partitions: Train={len(df_train)}, Validation={len(df_val)}, Test={len(df_test)}")
    assert len(df_train) > 0, f"Expected non-empty train split, got {len(df_train)}"
    assert len(df_val) > 0, f"Expected non-empty val split, got {len(df_val)}"
    assert len(df_test) > 0, f"Expected non-empty test split, got {len(df_test)}"

    # 2. Fit Preprocessing Pipeline strictly on train
    print("\nFitting Preprocessing Pipeline (anti-leakage isolation on train set)...")
    pipeline = PreprocessingPipeline().fit(df_train)
    joblib.dump(pipeline, models_dir / "preprocessing_pipeline.joblib")

    # 3. Train all 4 model families
    print("\n--- Training Model 1: Baseline Linear Regression ---")
    lr_models = train_linear_regression(df_train)

    print("--- Training & Tuning Model 2: Random Forest Regressor ---")
    rf_models, rf_params = train_random_forest(df_train, df_val, seed=42)

    print("--- Training & Tuning Model 3: XGBoost Regressor ---")
    xgb_models, xgb_params = train_xgboost(df_train, df_val, seed=42)

    print("--- Training & Tuning Model 4: Artificial Neural Network (MLP) ---")
    ann_models, ann_params = train_ann_mlp(df_train, df_val, pipeline=pipeline, seed=42)

    all_model_families = {
        "Linear Regression": {"models": lr_models, "is_nn": False, "params": {}},
        "Random Forest": {"models": rf_models, "is_nn": False, "params": rf_params},
        "XGBoost": {"models": xgb_models, "is_nn": False, "params": xgb_params},
        "ANN / MLP": {"models": ann_models, "is_nn": True, "params": ann_params},
    }

    # Save hyperparameters
    hyperparams_summary = {
        "Random Forest": rf_params,
        "XGBoost": xgb_params,
        "ANN / MLP": {k: {pk: str(pv) if not isinstance(pv, (int, float, bool)) else pv for pk, pv in v.items()} for k, v in ann_params.items()},
    }
    with open(results_tab_dir / "hyperparameters.json", "w", encoding="utf-8") as f:
        json.dump(hyperparams_summary, f, indent=2)

    # 4. Save Model Binaries
    print("\nSaving model artifacts to models/stage4/...")
    with open(models_dir / "feature_order.json", "w", encoding="utf-8") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)

    with open(models_dir / "target_order.json", "w", encoding="utf-8") as f:
        json.dump(ALL_TARGETS, f, indent=2)

    for fam_name, fam_data in all_model_families.items():
        sub_dir = models_dir / fam_name.lower().replace(" ", "_").replace("/", "_")
        sub_dir.mkdir(parents=True, exist_ok=True)
        for tgt, m in fam_data["models"].items():
            joblib.dump(m, sub_dir / f"{tgt}.joblib")

    # 5. Evaluate on Primary Test Set (336 scenarios)
    print("\nEvaluating on Primary Test Set...")
    test_eval_dfs = []
    for fam_name, fam_data in all_model_families.items():
        res = evaluate_model_on_dataset(
            model_name=fam_name,
            model_dict=fam_data["models"],
            df=df_test,
            dataset_label="Primary Test Set",
            pipeline=pipeline,
            is_neural_net=fam_data["is_nn"],
        )
        test_eval_dfs.append(res)
    df_test_metrics = pd.concat(test_eval_dfs, ignore_index=True)
    df_test_metrics.to_csv(results_tab_dir / "test_metrics.csv", index=False)
    print(df_test_metrics.to_string())

    # 6. Evaluate on Boundary Stress Set (2,712 scenarios)
    print("\nEvaluating on Boundary Stress Set...")
    boundary_eval_dfs = []
    for fam_name, fam_data in all_model_families.items():
        res = evaluate_model_on_dataset(
            model_name=fam_name,
            model_dict=fam_data["models"],
            df=df_boundary,
            dataset_label="Boundary Stress Set",
            pipeline=pipeline,
            is_neural_net=fam_data["is_nn"],
        )
        boundary_eval_dfs.append(res)
    df_boundary_metrics = pd.concat(boundary_eval_dfs, ignore_index=True)
    df_boundary_metrics.to_csv(results_tab_dir / "boundary_metrics.csv", index=False)

    # 7. Evaluate on Synthetic OOD Set (200 scenarios)
    print("\nEvaluating on Synthetic OOD Set...")
    # Check OOD classification
    ood_classes = [classify_scenario(r) for _, r in df_ood.iterrows()]
    df_ood["engineering_classification"] = ood_classes
    print(f"OOD Classification breakdown: {df_ood['engineering_classification'].value_counts().to_dict()}")

    ood_eval_dfs = []
    for fam_name, fam_data in all_model_families.items():
        res = evaluate_model_on_dataset(
            model_name=fam_name,
            model_dict=fam_data["models"],
            df=df_ood,
            dataset_label="Synthetic OOD Set",
            pipeline=pipeline,
            is_neural_net=fam_data["is_nn"],
        )
        ood_eval_dfs.append(res)
    df_ood_metrics = pd.concat(ood_eval_dfs, ignore_index=True)
    df_ood_metrics.to_csv(results_tab_dir / "ood_metrics.csv", index=False)

    # 8. Evaluate Stage 2 Baseline Operating Point
    print("\nEvaluating Baseline Operating Point...")
    base_eval_dict = {
        fam_name: fam_data["models"]
        for fam_name, fam_data in all_model_families.items()
    }
    # Mechanistic values for baseline operating point (from Stage 2 / Stage 3)
    baseline_record_full = dict(BASELINE_POINT)
    # Get ground truth from baseline simulation
    from data_generation.simulator_runner import run_single_simulation, create_baseline_system
    sys_base = create_baseline_system()
    mech_base = run_single_simulation(
        feed_flow_m3h=BASELINE_POINT["feed_flow_m3h"],
        feed_tds_mgL=BASELINE_POINT["feed_tds_mgL"],
        feed_cod_mgL=BASELINE_POINT.get("feed_cod_mgL", 51.0),
        feed_pH=BASELINE_POINT.get("feed_pH", 8.0),
        temperature_C=BASELINE_POINT["temperature_C"],
        stage1_pressure_bar=BASELINE_POINT["stage1_pressure_bar"],
        stage2_pressure_bar=BASELINE_POINT["stage2_pressure_bar"],
        system=sys_base,
    )
    for tgt in ALL_TARGETS:
        baseline_record_full[tgt] = mech_base[tgt]

    df_base_eval = evaluate_baseline_point(
        models=base_eval_dict,
        baseline_record=baseline_record_full,
        pipeline=pipeline,
    )
    df_base_eval.to_csv(results_tab_dir / "baseline_point_metrics.csv", index=False)
    print(df_base_eval.to_string())

    # Save model metadata
    model_metadata = {
        "project": "AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse",
        "stage": "Stage 4: Machine-Learning Surrogate Model Development",
        "training_dataset": "data/generated/stage3_engineering_acceptable.csv (train split)",
        "train_rows": len(df_train),
        "val_rows": len(df_val),
        "test_rows": len(df_test),
        "boundary_stress_rows": len(df_boundary),
        "ood_rows": len(df_ood),
        "features": FEATURE_COLUMNS,
        "targets": ALL_TARGETS,
        "random_seed": 42,
        "models_evaluated": list(all_model_families.keys()),
        "curated_envelope_ranges": {
            "feed_flow_m3h": [float(df_train["feed_flow_m3h"].min()), float(df_train["feed_flow_m3h"].max())],
            "feed_tds_mgL": [float(df_train["feed_tds_mgL"].min()), float(df_train["feed_tds_mgL"].max())],
            "temperature_C": [float(df_train["temperature_C"].min()), float(df_train["temperature_C"].max())],
            "stage1_pressure_bar": [float(df_train["stage1_pressure_bar"].min()), float(df_train["stage1_pressure_bar"].max())],
            "stage2_pressure_bar": [float(df_train["stage2_pressure_bar"].min()), float(df_train["stage2_pressure_bar"].max())],
        }
    }
    with open(models_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2)

    print("\nStage 4 model training and initial evaluation complete.")
    print(f"Models saved to: {models_dir}")
    print(f"Tables saved to: {results_tab_dir}")


if __name__ == "__main__":
    main()
