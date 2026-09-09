"""
Multi-Objective Optimization Problem Definition for Stage 5.

Implements the reverse osmosis operating optimization problem using pymoo:
Decision variables:
- x1 = stage1_pressure_bar (P1)
- x2 = stage2_pressure_bar (P2)

Objectives (minimization framework):
- f1 = -overall_recovery_pct (Maximize water recovery)
- f2 = SEC_kWh_m3 (Minimize specific energy consumption)
- f3 = maximum_element_recovery_pct (Minimize membrane operating stress proxy)

Constraints:
- g1: P1 - P2 <= 0 (Inter-stage booster pressure ordering: P2 >= P1)
- g2: maximum_element_recovery_pct - 30.0 <= 0 (30% single-element recovery safeguard)
- g3: permeate_tds_mgL - 18.0 <= 0 (Published reference-case permeate quality constraint)
- g4: (Optional Case B) maximum_polarization_modulus - 1.40 <= 0 (Project engineering polarization safeguard)
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
import pandas as pd
from pymoo.core.problem import Problem

from ml.inference import Stage4Surrogate
from ml.domain_guard import OptimizationDomainGuard, DomainProximityStatus


class ROOperatingOptimizationProblem(Problem):
    """
    Pymoo Problem wrapper for two-stage RO operating pressure optimization.
    """

    def __init__(
        self,
        surrogate: Optional[Stage4Surrogate] = None,
        domain_guard: Optional[OptimizationDomainGuard] = None,
        feed_flow_m3h: float = 30.0,
        feed_tds_mgL: float = 2041.0,
        temperature_C: float = 25.0,
        feed_cod_mgL: float = 51.0,
        feed_pH: float = 8.0,
        permeate_tds_limit: float = 18.0,
        max_element_recovery_limit: float = 30.0,
        enforce_polarization_limit: bool = False,
        polarization_limit: float = 1.40,
        models_dir: Union[str, Path] = "models/stage4",
    ):
        # 1. Load domain guard to obtain exact authoritative empirical bounds
        if domain_guard is None:
            self.domain_guard = OptimizationDomainGuard.from_training_dataset()
        else:
            self.domain_guard = domain_guard

        # 2. Load surrogate model (Primary ANN surrogate)
        if surrogate is None:
            self.surrogate = Stage4Surrogate.load(
                model_dir=models_dir,
                model_name="ann___mlp",
                is_neural_net=True,
            )
        else:
            self.surrogate = surrogate

        # Fixed disturbance conditions
        self.feed_flow_m3h = float(feed_flow_m3h)
        self.feed_tds_mgL = float(feed_tds_mgL)
        self.temperature_C = float(temperature_C)
        self.feed_cod_mgL = float(feed_cod_mgL)
        self.feed_pH = float(feed_pH)

        # Constraint settings
        self.permeate_tds_limit = float(permeate_tds_limit)
        self.max_element_recovery_limit = float(max_element_recovery_limit)
        self.enforce_polarization_limit = bool(enforce_polarization_limit)
        self.polarization_limit = float(polarization_limit)

        # Bounds from domain guard
        xl = np.array([self.domain_guard.bounds.p1_min, self.domain_guard.bounds.p2_min], dtype=float)
        xu = np.array([self.domain_guard.bounds.p1_max, self.domain_guard.bounds.p2_max], dtype=float)

        # Number of constraints: 3 for Case A (P2>=P1, MaxElemRec<=30, Cp<=18), 4 for Case B (+ Beta<=1.40)
        n_constr = 4 if self.enforce_polarization_limit else 3

        super().__init__(
            n_var=2,
            n_obj=3,
            n_ieq_constr=n_constr,
            xl=xl,
            xu=xu,
            vtype=float,
        )

    def _evaluate(self, x: np.ndarray, out: Dict[str, Any], *args, **kwargs) -> None:
        """
        Vectorized evaluation of candidate population x (shape: N x 2).
        """
        n_samples = x.shape[0]
        p1 = x[:, 0]
        p2 = x[:, 1]

        # Construct input DataFrame for vectorized surrogate inference
        df_in = pd.DataFrame({
            "feed_flow_m3h": np.full(n_samples, self.feed_flow_m3h),
            "feed_tds_mgL": np.full(n_samples, self.feed_tds_mgL),
            "temperature_C": np.full(n_samples, self.temperature_C),
            "stage1_pressure_bar": p1,
            "stage2_pressure_bar": p2,
        })

        # Physics-reconstructed prediction guarantees global solute conservation
        preds = self.surrogate.predict_physics_reconstructed(df_in)

        rec = preds["overall_recovery_pct"].to_numpy(dtype=float)
        sec = preds["SEC_kWh_m3"].to_numpy(dtype=float)
        elem_rec = preds["maximum_element_recovery_pct"].to_numpy(dtype=float)
        cp = preds["permeate_tds_mgL"].to_numpy(dtype=float)
        beta = preds["maximum_polarization_modulus"].to_numpy(dtype=float)

        # Objectives (minimization):
        # f1 = -recovery (%)
        # f2 = SEC (kWh/m3)
        # f3 = max element recovery (%)
        f1 = -rec
        f2 = sec
        f3 = elem_rec
        out["F"] = np.column_stack([f1, f2, f3])

        # Constraints (g_i <= 0 is feasible):
        # g1: P1 - P2 <= 0  (i.e. P2 >= P1)
        # g2: elem_rec - max_elem_rec_limit <= 0
        # g3: cp - permeate_tds_limit <= 0
        g1 = p1 - p2
        g2 = elem_rec - self.max_element_recovery_limit
        g3 = cp - self.permeate_tds_limit

        if self.enforce_polarization_limit:
            g4 = beta - self.polarization_limit
            out["G"] = np.column_stack([g1, g2, g3, g4])
        else:
            out["G"] = np.column_stack([g1, g2, g3])

    def evaluate_full_state(self, p1: np.ndarray, p2: np.ndarray) -> pd.DataFrame:
        """
        Evaluate full state including all 7 outputs and conserved flow rates for given P1 and P2 vectors.
        """
        n_samples = len(p1)
        df_in = pd.DataFrame({
            "feed_flow_m3h": np.full(n_samples, self.feed_flow_m3h),
            "feed_tds_mgL": np.full(n_samples, self.feed_tds_mgL),
            "temperature_C": np.full(n_samples, self.temperature_C),
            "stage1_pressure_bar": p1,
            "stage2_pressure_bar": p2,
        })
        preds = self.surrogate.predict_physics_reconstructed(df_in)
        preds["stage1_pressure_bar"] = p1
        preds["stage2_pressure_bar"] = p2
        preds["feed_flow_m3h"] = self.feed_flow_m3h
        preds["feed_tds_mgL"] = self.feed_tds_mgL
        preds["temperature_C"] = self.temperature_C
        return preds
