"""
Training Module for Stage 4 Machine-Learning Surrogates.

Trains and tunes 4 model families across all 7 targets:
1. Linear Regression (Baseline)
2. Random Forest Regressor
3. XGBoost Regressor
4. Feed-forward Artificial Neural Network (MLPRegressor)

Uses validation-set-based tuning and strict anti-leakage isolation.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import xgboost as xgb

from ml.preprocessing import PreprocessingPipeline, FEATURE_COLUMNS, ALL_TARGETS
from ml.metrics import calculate_regression_metrics


def train_linear_regression(
    df_train: pd.DataFrame,
    targets: Optional[List[str]] = None,
) -> Dict[str, LinearRegression]:
    """Train baseline Linear Regression models for each target."""
    targets = targets or ALL_TARGETS
    X_train = df_train[FEATURE_COLUMNS].to_numpy(dtype=float)
    models: Dict[str, LinearRegression] = {}

    for tgt in targets:
        y_train = df_train[tgt].to_numpy(dtype=float)
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        models[tgt] = lr

    return models


def train_random_forest(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    targets: Optional[List[str]] = None,
    seed: int = 42,
) -> Tuple[Dict[str, RandomForestRegressor], Dict[str, Dict[str, Any]]]:
    """
    Train and tune Random Forest models on validation set.
    """
    targets = targets or ALL_TARGETS
    X_train = df_train[FEATURE_COLUMNS].to_numpy(dtype=float)
    X_val = df_val[FEATURE_COLUMNS].to_numpy(dtype=float)

    # Candidate hyperparameter grid for tuning
    param_grid = [
        {"n_estimators": 100, "max_depth": 10, "min_samples_split": 4, "min_samples_leaf": 2, "max_features": "sqrt"},
        {"n_estimators": 200, "max_depth": 15, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": "sqrt"},
        {"n_estimators": 200, "max_depth": 20, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": None},
        {"n_estimators": 300, "max_depth": 25, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": None},
    ]

    models: Dict[str, RandomForestRegressor] = {}
    best_params: Dict[str, Dict[str, Any]] = {}

    for tgt in targets:
        y_train = df_train[tgt].to_numpy(dtype=float)
        y_val = df_val[tgt].to_numpy(dtype=float)

        best_score = -np.inf
        best_model = None
        best_p = param_grid[0]

        for p in param_grid:
            rf = RandomForestRegressor(
                n_estimators=p["n_estimators"],
                max_depth=p["max_depth"],
                min_samples_split=p["min_samples_split"],
                min_samples_leaf=p["min_samples_leaf"],
                max_features=p["max_features"],
                random_state=seed,
                n_jobs=-1,
            )
            rf.fit(X_train, y_train)
            val_preds = rf.predict(X_val)
            val_r2 = calculate_regression_metrics(y_val, val_preds, tgt)["r2"]

            if val_r2 > best_score:
                best_score = val_r2
                best_model = rf
                best_p = p

        models[tgt] = best_model
        best_params[tgt] = best_p

    return models, best_params


def train_xgboost(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    targets: Optional[List[str]] = None,
    seed: int = 42,
) -> Tuple[Dict[str, xgb.XGBRegressor], Dict[str, Dict[str, Any]]]:
    """
    Train and tune XGBoost Regressor models on validation set.
    """
    targets = targets or ALL_TARGETS
    X_train = df_train[FEATURE_COLUMNS].to_numpy(dtype=float)
    X_val = df_val[FEATURE_COLUMNS].to_numpy(dtype=float)

    # Candidate hyperparameter grid for tuning
    param_grid = [
        {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.05, "subsample": 0.8, "colsample_bytree": 0.9, "reg_alpha": 0.01, "reg_lambda": 1.0},
        {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.03, "subsample": 0.85, "colsample_bytree": 1.0, "reg_alpha": 0.05, "reg_lambda": 1.0},
        {"n_estimators": 400, "max_depth": 7, "learning_rate": 0.03, "subsample": 0.9, "colsample_bytree": 1.0, "reg_alpha": 0.01, "reg_lambda": 0.5},
        {"n_estimators": 500, "max_depth": 8, "learning_rate": 0.02, "subsample": 0.9, "colsample_bytree": 1.0, "reg_alpha": 0.01, "reg_lambda": 1.0},
    ]

    models: Dict[str, xgb.XGBRegressor] = {}
    best_params: Dict[str, Dict[str, Any]] = {}

    for tgt in targets:
        y_train = df_train[tgt].to_numpy(dtype=float)
        y_val = df_val[tgt].to_numpy(dtype=float)

        best_score = -np.inf
        best_model = None
        best_p = param_grid[0]

        for p in param_grid:
            model = xgb.XGBRegressor(
                n_estimators=p["n_estimators"],
                max_depth=p["max_depth"],
                learning_rate=p["learning_rate"],
                subsample=p["subsample"],
                colsample_bytree=p["colsample_bytree"],
                reg_alpha=p["reg_alpha"],
                reg_lambda=p["reg_lambda"],
                random_state=seed,
                n_jobs=-1,
                tree_method="hist",
            )
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
            val_preds = model.predict(X_val)
            val_r2 = calculate_regression_metrics(y_val, val_preds, tgt)["r2"]

            if val_r2 > best_score:
                best_score = val_r2
                best_model = model
                best_p = p

        models[tgt] = best_model
        best_params[tgt] = best_p

    return models, best_params


def train_ann_mlp(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    pipeline: PreprocessingPipeline,
    targets: Optional[List[str]] = None,
    seed: int = 42,
) -> Tuple[Dict[str, MLPRegressor], Dict[str, Dict[str, Any]]]:
    """
    Train and tune feed-forward Artificial Neural Network (MLPRegressor) models
    using standardized inputs and outputs with early stopping.
    """
    targets = targets or ALL_TARGETS
    X_train_scaled = pipeline.transform_features(df_train)
    X_val_scaled = pipeline.transform_features(df_val)

    # Candidate hyperparameter grid for ANN
    param_grid = [
        {"hidden_layer_sizes": (64, 64), "activation": "relu", "alpha": 1e-4, "learning_rate_init": 0.005, "batch_size": 32},
        {"hidden_layer_sizes": (128, 64), "activation": "relu", "alpha": 1e-4, "learning_rate_init": 0.003, "batch_size": 32},
        {"hidden_layer_sizes": (128, 128, 64), "activation": "relu", "alpha": 1e-3, "learning_rate_init": 0.002, "batch_size": 32},
        {"hidden_layer_sizes": (256, 128, 64), "activation": "relu", "alpha": 1e-3, "learning_rate_init": 0.001, "batch_size": 64},
    ]

    models: Dict[str, MLPRegressor] = {}
    best_params: Dict[str, Dict[str, Any]] = {}

    for tgt in targets:
        y_train_scaled = pipeline.transform_target(df_train, tgt)
        y_val_raw = df_val[tgt].to_numpy(dtype=float)

        best_score = -np.inf
        best_model = None
        best_p = param_grid[0]

        for p in param_grid:
            mlp = MLPRegressor(
                hidden_layer_sizes=p["hidden_layer_sizes"],
                activation=p["activation"],
                alpha=p["alpha"],
                learning_rate_init=p["learning_rate_init"],
                batch_size=p["batch_size"],
                max_iter=500,
                early_stopping=True,
                n_iter_no_change=20,
                validation_fraction=0.15,
                random_state=seed,
            )
            mlp.fit(X_train_scaled, y_train_scaled)
            val_preds_scaled = mlp.predict(X_val_scaled)
            val_preds_raw = pipeline.inverse_transform_target(val_preds_scaled, tgt)
            val_r2 = calculate_regression_metrics(y_val_raw, val_preds_raw, tgt)["r2"]

            if val_r2 > best_score:
                best_score = val_r2
                best_model = mlp
                best_p = p

        models[tgt] = best_model
        best_params[tgt] = best_p

    return models, best_params
