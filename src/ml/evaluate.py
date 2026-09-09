"""
Evaluation Module for Stage 4 ML Surrogates.

Evaluates all trained models across:
1. Primary Test Set (336 engineering-acceptable scenarios)
2. Boundary Stress Set (2,712 scenarios)
3. Out-of-Distribution Set (200 scenarios)
4. Stage 2 Baseline Operating Point
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS
from ml.metrics import calculate_regression_metrics


def predict_model_targets(
    model_dict: Dict[str, Any],
    df: pd.DataFrame,
    pipeline: Optional[PreprocessingPipeline] = None,
    is_neural_net: bool = False,
    targets: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Generate physical-scale predictions for all targets from a model dictionary.
    """
    targets = targets or ALL_TARGETS
    predictions = {}

    if is_neural_net:
        if pipeline is None:
            raise ValueError("PreprocessingPipeline required for neural network predictions.")
        X_scaled = pipeline.transform_features(df)
        for tgt in targets:
            preds_scaled = model_dict[tgt].predict(X_scaled)
            preds_raw = pipeline.inverse_transform_target(preds_scaled, tgt)
            predictions[tgt] = preds_raw
    else:
        X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
        for tgt in targets:
            predictions[tgt] = model_dict[tgt].predict(X)

    return pd.DataFrame(predictions, index=df.index)


def evaluate_model_on_dataset(
    model_name: str,
    model_dict: Dict[str, Any],
    df: pd.DataFrame,
    dataset_label: str = "Test Set",
    pipeline: Optional[PreprocessingPipeline] = None,
    is_neural_net: bool = False,
    targets: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Evaluate a model family against all targets on a specific dataset.
    """
    targets = targets or ALL_TARGETS
    pred_df = predict_model_targets(
        model_dict=model_dict,
        df=df,
        pipeline=pipeline,
        is_neural_net=is_neural_net,
        targets=targets,
    )

    records = []
    for tgt in targets:
        y_true = df[tgt].to_numpy(dtype=float)
        y_pred = pred_df[tgt].to_numpy(dtype=float)
        m = calculate_regression_metrics(y_true, y_pred, tgt)
        records.append({
            "Model": model_name,
            "Dataset": dataset_label,
            "Target": tgt,
            "R2": m["r2"],
            "RMSE": m["rmse"],
            "MAE": m["mae"],
            "NRMSE_pct": m["nrmse_pct"],
            "MAPE": m["mape"],
            "Max_Error": m["max_error"],
        })

    return pd.DataFrame(records)


def evaluate_baseline_point(
    models: Dict[str, Dict[str, Any]],
    baseline_record: Dict[str, Any],
    pipeline: PreprocessingPipeline,
    targets: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Evaluate all models at the single Stage 2 baseline operating point.
    """
    targets = targets or ALL_TARGETS
    df_base = pd.DataFrame([baseline_record])

    records = []
    for model_name, model_dict in models.items():
        is_nn = "ANN" in model_name or "MLP" in model_name
        pred_df = predict_model_targets(
            model_dict=model_dict,
            df=df_base,
            pipeline=pipeline,
            is_neural_net=is_nn,
            targets=targets,
        )

        for tgt in targets:
            y_true = float(baseline_record[tgt])
            y_pred = float(pred_df[tgt].iloc[0])
            abs_err = abs(y_true - y_pred)
            rel_err_pct = (abs_err / abs(y_true)) * 100.0 if abs(y_true) > 1e-6 else np.nan

            records.append({
                "Model": model_name,
                "Target": tgt,
                "Mechanistic_Value": y_true,
                "ML_Prediction": y_pred,
                "Absolute_Error": abs_err,
                "Relative_Error_pct": rel_err_pct,
            })

    return pd.DataFrame(records)
