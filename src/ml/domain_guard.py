"""
Optimization Domain Guard and Proximity Trust Indicator Module for Stage 4B / Stage 5.

Guarantees:
1. Optimization candidate inputs remain strictly within the engineering-acceptable training domain.
2. Inter-stage booster pressure satisfies P2 >= P1.
3. Maximum operating pressure does not exceed membrane specification (41 bar).
4. Predicted single-element recovery satisfies the 30% project engineering safeguard.
5. Quantifies domain proximity status: IN_DOMAIN, NEAR_BOUNDARY, OUT_OF_DOMAIN.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd

from ml.preprocessing import FEATURE_COLUMNS


class DomainProximityStatus(str, Enum):
    """Classification of operating scenarios relative to the training distribution."""
    IN_DOMAIN = "IN_DOMAIN"
    NEAR_BOUNDARY = "NEAR_BOUNDARY"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"


@dataclass
class DomainBounds:
    """Exact training-set bounds derived from curated engineering-acceptable data."""
    feed_flow_min: float
    feed_flow_max: float
    feed_tds_min: float
    feed_tds_max: float
    temp_min: float
    temp_max: float
    p1_min: float
    p1_max: float
    p2_min: float
    p2_max: float
    max_element_recovery_threshold: float = 30.0
    max_operating_pressure_bar: float = 41.0

    @classmethod
    def from_dataframe(
        cls,
        df_train: pd.DataFrame,
        max_element_recovery_threshold: float = 30.0,
        max_operating_pressure_bar: float = 41.0,
    ) -> "DomainBounds":
        """Compute exact empirical training bounds from dataframe."""
        return cls(
            feed_flow_min=float(df_train["feed_flow_m3h"].min()),
            feed_flow_max=float(df_train["feed_flow_m3h"].max()),
            feed_tds_min=float(df_train["feed_tds_mgL"].min()),
            feed_tds_max=float(df_train["feed_tds_mgL"].max()),
            temp_min=float(df_train["temperature_C"].min()),
            temp_max=float(df_train["temperature_C"].max()),
            p1_min=float(df_train["stage1_pressure_bar"].min()),
            p1_max=float(df_train["stage1_pressure_bar"].max()),
            p2_min=float(df_train["stage2_pressure_bar"].min()),
            p2_max=float(df_train["stage2_pressure_bar"].max()),
            max_element_recovery_threshold=max_element_recovery_threshold,
            max_operating_pressure_bar=max_operating_pressure_bar,
        )


@dataclass
class OptimizationDomainGuard:
    """
    Validates operating points against physical constraints and the curated engineering domain.
    """
    bounds: DomainBounds
    feature_means: np.ndarray
    feature_stds: np.ndarray

    @classmethod
    def from_training_dataset(
        cls,
        csv_path: Union[str, Path] = "data/generated/stage3_engineering_acceptable.csv",
    ) -> "OptimizationDomainGuard":
        """Initialize guard using authoritative training partition."""
        p = Path(csv_path)
        df = pd.read_csv(p)
        df_train = df[df["dataset_split"] == "train"].copy().reset_index(drop=True)
        bounds = DomainBounds.from_dataframe(df_train)

        X_train = df_train[FEATURE_COLUMNS].to_numpy(dtype=float)
        means = np.mean(X_train, axis=0)
        stds = np.std(X_train, axis=0)
        stds = np.where(stds < 1e-6, 1.0, stds)

        return cls(
            bounds=bounds,
            feature_means=means,
            feature_stds=stds,
        )

    def validate_inputs(self, candidate: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Check if candidate inputs strictly satisfy operating and envelope constraints.
        """
        violations = []
        qf = candidate.get("feed_flow_m3h", np.nan)
        cf = candidate.get("feed_tds_mgL", np.nan)
        temp = candidate.get("temperature_C", np.nan)
        p1 = candidate.get("stage1_pressure_bar", np.nan)
        p2 = candidate.get("stage2_pressure_bar", np.nan)

        # 1. Bounds checks
        if not (self.bounds.feed_flow_min <= qf <= self.bounds.feed_flow_max):
            violations.append(f"feed_flow_m3h={qf:.2f} out of bounds [{self.bounds.feed_flow_min:.1f}, {self.bounds.feed_flow_max:.1f}]")
        if not (self.bounds.feed_tds_min <= cf <= self.bounds.feed_tds_max):
            violations.append(f"feed_tds_mgL={cf:.1f} out of bounds [{self.bounds.feed_tds_min:.1f}, {self.bounds.feed_tds_max:.1f}]")
        if not (self.bounds.temp_min <= temp <= self.bounds.temp_max):
            violations.append(f"temperature_C={temp:.1f} out of bounds [{self.bounds.temp_min:.1f}, {self.bounds.temp_max:.1f}]")
        if not (self.bounds.p1_min <= p1 <= self.bounds.p1_max):
            violations.append(f"stage1_pressure_bar={p1:.2f} out of bounds [{self.bounds.p1_min:.1f}, {self.bounds.p1_max:.1f}]")
        if not (self.bounds.p2_min <= p2 <= self.bounds.p2_max):
            violations.append(f"stage2_pressure_bar={p2:.2f} out of bounds [{self.bounds.p2_min:.1f}, {self.bounds.p2_max:.1f}]")

        # 2. Stage pressure ordering: P2 >= P1
        if p2 < p1 - 1e-4:
            violations.append(f"Stage 2 pressure ({p2:.2f} bar) is less than Stage 1 pressure ({p1:.2f} bar)")

        # 3. Maximum membrane pressure limit (41 bar)
        if p1 > self.bounds.max_operating_pressure_bar:
            violations.append(f"P1 ({p1:.2f} bar) exceeds maximum allowable 41 bar")
        if p2 > self.bounds.max_operating_pressure_bar:
            violations.append(f"P2 ({p2:.2f} bar) exceeds maximum allowable 41 bar")

        is_valid = len(violations) == 0
        return is_valid, violations

    def validate_predicted_state(
        self,
        predicted_max_element_recovery_pct: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify that surrogate-predicted single-element recovery does not violate the 30% safeguard.
        """
        if predicted_max_element_recovery_pct > self.bounds.max_element_recovery_threshold:
            msg = (
                f"Predicted maximum element recovery ({predicted_max_element_recovery_pct:.2f}%) "
                f"exceeds 30.0% safeguard limit."
            )
            return False, msg
        return True, None

    def evaluate_proximity_status(
        self,
        candidate: Dict[str, float],
    ) -> Tuple[DomainProximityStatus, float]:
        """
        Evaluate domain proximity using normalized z-distance from training distribution mean:
        d_z = sqrt(sum(((x_i - mu_i) / sigma_i)^2))
        """
        x_vec = np.array([
            candidate.get("feed_flow_m3h", self.feature_means[0]),
            candidate.get("feed_tds_mgL", self.feature_means[1]),
            candidate.get("temperature_C", self.feature_means[2]),
            candidate.get("stage1_pressure_bar", self.feature_means[3]),
            candidate.get("stage2_pressure_bar", self.feature_means[4]),
        ], dtype=float)

        z_scores = (x_vec - self.feature_means) / self.feature_stds
        d_z = float(np.sqrt(np.sum(z_scores**2)))

        is_valid_box, _ = self.validate_inputs(candidate)

        if is_valid_box and d_z <= 2.5:
            status = DomainProximityStatus.IN_DOMAIN
        elif is_valid_box or (d_z <= 3.5):
            status = DomainProximityStatus.NEAR_BOUNDARY
        else:
            status = DomainProximityStatus.OUT_OF_DOMAIN

        return status, d_z
