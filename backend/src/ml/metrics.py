"""
Evaluation Metrics Module for Stage 4 ML Surrogates.

Calculates engineering and statistical performance metrics:
- R² (Coefficient of Determination)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- NRMSE (Normalized RMSE = RMSE / (y_max - y_min))
- MAPE (Mean Absolute Percentage Error, guarded against near-zero division)
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_name: str = "target",
    epsilon: float = 1e-6,
) -> Dict[str, float]:
    """
    Calculate comprehensive performance metrics for a single target.
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    # 1. Standard regression metrics
    r2 = float(r2_score(y_t, y_p))
    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    mae = float(mean_absolute_error(y_t, y_p))

    # 2. Normalized RMSE (NRMSE = RMSE / range)
    y_range = float(np.max(y_t) - np.min(y_t))
    nrmse = float(rmse / y_range) if y_range > epsilon else 0.0

    # 3. Guarded MAPE (only calculated where values are sufficiently away from zero)
    # Check if target values approach zero (e.g. min < 0.1)
    if np.min(np.abs(y_t)) < 0.1:
        mape = np.nan
    else:
        mape = float(np.mean(np.abs((y_t - y_p) / y_t)) * 100.0)

    # 4. Max absolute error
    max_error = float(np.max(np.abs(y_t - y_p)))

    return {
        "target": target_name,
        "r2": r2,
        "rmse": rmse,
        "mae": mae,
        "nrmse": nrmse,
        "nrmse_pct": nrmse * 100.0,
        "mape": mape,
        "max_error": max_error,
    }
