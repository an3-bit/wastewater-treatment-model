"""
SHAP Interpretability and Feature Importance Module for Stage 4 Surrogates.

Uses shap.TreeExplainer on the selected tree-based surrogate model to explain
model prediction mechanisms and compare against first-principles process physics.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from ml.preprocessing import FEATURE_COLUMNS, ALL_TARGETS


def compute_tree_shap_explanations(
    tree_model_dict: Dict[str, Any],
    df_eval: pd.DataFrame,
    targets: Optional[List[str]] = None,
) -> Dict[str, np.ndarray]:
    """
    Compute SHAP values for each target using TreeExplainer.
    """
    targets = targets or ALL_TARGETS
    X = df_eval[FEATURE_COLUMNS].to_numpy(dtype=float)
    shap_values_dict: Dict[str, np.ndarray] = {}

    for tgt in targets:
        model = tree_model_dict[tgt]
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X)
        shap_values_dict[tgt] = sv

    return shap_values_dict


def generate_shap_plots(
    shap_values_dict: Dict[str, np.ndarray],
    df_eval: pd.DataFrame,
    output_dir: Path,
    targets: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Generate SHAP summary bar plots and compute mean absolute SHAP feature rankings.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = targets or list(shap_values_dict.keys())
    X = df_eval[FEATURE_COLUMNS]

    importance_records = []

    for tgt in targets:
        sv = shap_values_dict[tgt]
        mean_abs_shap = np.mean(np.abs(sv), axis=0)

        for feat_name, imp in zip(FEATURE_COLUMNS, mean_abs_shap):
            importance_records.append({
                "Target": tgt,
                "Feature": feat_name,
                "Mean_Absolute_SHAP": float(imp),
            })

        # Generate summary bar chart
        fig, ax = plt.subplots(figsize=(8, 5))
        indices = np.argsort(mean_abs_shap)
        y_pos = np.arange(len(FEATURE_COLUMNS))
        ax.barh(y_pos, mean_abs_shap[indices], color="#2980b9", edgecolor="black", alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([FEATURE_COLUMNS[i] for i in indices])
        ax.set_xlabel("Mean |SHAP Value| (Impact on Model Output)")
        ax.set_title(f"SHAP Feature Importance: {tgt}")
        fig.tight_layout()
        fig.savefig(output_dir / f"shap_importance_{tgt}.png")
        plt.close(fig)

    df_imp = pd.DataFrame(importance_records)
    return df_imp
