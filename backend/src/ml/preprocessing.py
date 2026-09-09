"""
Preprocessing and Anti-Leakage Module for Stage 4 ML Surrogates.

Guarantees:
1. Feature scalers (StandardScaler / MinMaxScaler) fit ONLY on training data.
2. Target scalers for neural networks fit ONLY on training data.
3. Clean separation of 5 mechanistic causal inputs from metadata and targets.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler


FEATURE_COLUMNS: List[str] = [
    "feed_flow_m3h",
    "feed_tds_mgL",
    "temperature_C",
    "stage1_pressure_bar",
    "stage2_pressure_bar",
]

PRIMARY_TARGETS: List[str] = [
    "overall_recovery_pct",
    "permeate_tds_mgL",
    "concentrate_tds_mgL",
    "average_flux_LMH",
    "SEC_kWh_m3",
]

SECONDARY_TARGETS: List[str] = [
    "maximum_element_recovery_pct",
    "maximum_polarization_modulus",
]

ALL_TARGETS: List[str] = PRIMARY_TARGETS + SECONDARY_TARGETS


@dataclass
class PreprocessingPipeline:
    """
    Manages input and target scaling with strict anti-leakage isolation.
    """
    feature_names: List[str] = field(default_factory=lambda: list(FEATURE_COLUMNS))
    target_names: List[str] = field(default_factory=lambda: list(ALL_TARGETS))
    input_scaler: StandardScaler = field(default_factory=StandardScaler)
    target_scalers: Dict[str, StandardScaler] = field(default_factory=dict)
    fitted: bool = False

    def fit(self, df_train: pd.DataFrame) -> "PreprocessingPipeline":
        """
        Fit all input and target scalers strictly on the training partition.
        """
        X_train = df_train[self.feature_names].to_numpy(dtype=float)
        self.input_scaler.fit(X_train)

        self.target_scalers = {}
        for tgt in self.target_names:
            scaler = StandardScaler()
            y_train = df_train[[tgt]].to_numpy(dtype=float)
            scaler.fit(y_train)
            self.target_scalers[tgt] = scaler

        self.fitted = True
        return self

    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        """Transform input features using fitted training statistics."""
        if not self.fitted:
            raise RuntimeError("PreprocessingPipeline must be fitted before transform.")
        X = df[self.feature_names].to_numpy(dtype=float)
        return self.input_scaler.transform(X)

    def transform_target(self, df: pd.DataFrame, target_name: str) -> np.ndarray:
        """Transform a specific target using fitted training statistics."""
        if not self.fitted:
            raise RuntimeError("PreprocessingPipeline must be fitted before transform.")
        y = df[[target_name]].to_numpy(dtype=float)
        return self.target_scalers[target_name].transform(y).ravel()

    def inverse_transform_target(self, y_scaled: np.ndarray, target_name: str) -> np.ndarray:
        """Inverse transform scaled target predictions back to physical engineering units."""
        if not self.fitted:
            raise RuntimeError("PreprocessingPipeline must be fitted before inverse_transform.")
        y_2d = np.asarray(y_scaled).reshape(-1, 1)
        return self.target_scalers[target_name].inverse_transform(y_2d).ravel()
