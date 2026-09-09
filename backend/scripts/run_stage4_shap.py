"""
Stage 4 SHAP Interpretability and Explainability Script.

Uses shap.TreeExplainer on the best-performing tree surrogate (XGBoost)
to explain model prediction mechanisms and verify consistency with first-principles process physics.
"""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import joblib

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS, PRIMARY_TARGETS, SECONDARY_TARGETS
from ml.interpretability import compute_tree_shap_explanations, generate_shap_plots


def main():
    print("=" * 70)
    print("STAGE 4: SHAP TREE INTERPRETABILITY ANALYSIS")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "generated"
    models_dir = base_dir / "models" / "stage4"
    fig_dir = base_dir / "results" / "stage4" / "figures"
    tab_dir = base_dir / "results" / "stage4" / "tables"

    fig_dir.mkdir(parents=True, exist_ok=True)
    tab_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load curated test dataset
    curated_path = data_dir / "stage3_engineering_acceptable.csv"
    df_curated = pd.read_csv(curated_path)
    df_test = df_curated[df_curated["dataset_split"] == "test"].copy().reset_index(drop=True)
    print(f"Loaded test dataset for SHAP evaluation: {len(df_test)} rows")

    # 2. Load trained XGBoost models
    xgb_dir = models_dir / "xgboost"
    if not xgb_dir.exists():
        print(f"Directory {xgb_dir} does not exist yet. Please ensure train_stage4_surrogates.py has finished.")
        return

    xgb_models = {}
    for tgt in ALL_TARGETS:
        m_file = xgb_dir / f"{tgt}.joblib"
        xgb_models[tgt] = joblib.load(m_file)
    print("Successfully loaded XGBoost model artifacts.")

    # 3. Compute SHAP values for all targets
    print("\nComputing TreeExplainer SHAP values across test scenarios...")
    X_test = df_test[FEATURE_COLUMNS]
    shap_values_dict = {}
    shap_explainers = {}

    for tgt in ALL_TARGETS:
        model = xgb_models[tgt]
        explainer = shap.TreeExplainer(model)
        shap_values_dict[tgt] = explainer(X_test)
        shap_explainers[tgt] = explainer

    # 4. Generate SHAP Summary Beeswarm Plots and Feature Importance
    print("\nGenerating SHAP summary and importance plots...")
    importance_records = []

    for tgt in ALL_TARGETS:
        shap_exp = shap_values_dict[tgt]
        sv_values = shap_exp.values  # (N, n_features)
        mean_abs_shap = np.mean(np.abs(sv_values), axis=0)

        for feat_name, imp in zip(FEATURE_COLUMNS, mean_abs_shap):
            importance_records.append({
                "Target": tgt,
                "Feature": feat_name,
                "Mean_Absolute_SHAP": float(imp),
            })

        # Summary Beeswarm Plot
        fig, ax = plt.subplots(figsize=(9, 6))
        shap.summary_plot(
            sv_values,
            X_test,
            feature_names=FEATURE_COLUMNS,
            show=False,
            plot_size=(9, 6),
        )
        plt.title(f"SHAP Summary (Beeswarm): {tgt}", fontsize=13, pad=15)
        plt.tight_layout()
        plt.savefig(fig_dir / f"shap_beeswarm_{tgt}.png", dpi=300, bbox_inches="tight")
        plt.close()

        # Feature Importance Bar Plot
        fig, ax = plt.subplots(figsize=(8, 5))
        indices = np.argsort(mean_abs_shap)
        y_pos = np.arange(len(FEATURE_COLUMNS))
        ax.barh(y_pos, mean_abs_shap[indices], color="#2980b9", edgecolor="black", alpha=0.85)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([FEATURE_COLUMNS[i] for i in indices])
        ax.set_xlabel("Mean |SHAP Value| (Impact on Model Output)")
        ax.set_title(f"SHAP Feature Importance: {tgt}")
        ax.grid(True, linestyle=":", alpha=0.6)
        fig.tight_layout()
        fig.savefig(fig_dir / f"shap_importance_{tgt}.png", dpi=300)
        plt.close(fig)

    # Save feature importance table
    df_imp = pd.DataFrame(importance_records)
    df_imp.to_csv(tab_dir / "shap_feature_importance.csv", index=False)
    print(f"Saved SHAP importance table to: {tab_dir / 'shap_feature_importance.csv'}")
    print(f"Saved SHAP figures to: {fig_dir}")
    print("\nSHAP interpretability analysis completed successfully.")


if __name__ == "__main__":
    main()
