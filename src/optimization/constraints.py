"""
Constraint Checking and Evaluation Module for Stage 5 Optimization.

Provides standalone constraint checkers, constraint margin calculations,
and feasibility reporting for candidate solutions.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

from ml.domain_guard import OptimizationDomainGuard, DomainProximityStatus


@dataclass
class CandidateConstraintReport:
    """Detailed feasibility and constraint margin breakdown for an operating point."""
    is_feasible: bool
    violations: List[str]
    p1_bar: float
    p2_bar: float
    p2_ge_p1_margin_bar: float  # P2 - P1 (must be >= 0)
    max_element_rec_margin_pct: float  # 30.0 - max_elem_rec (must be >= 0)
    permeate_tds_margin_mgL: float  # 18.0 - permeate_tds (must be >= 0)
    polarization_margin: float  # 1.40 - beta_max (must be >= 0)
    domain_proximity_status: str
    domain_z_distance: float


def check_candidate_constraints(
    p1: float,
    p2: float,
    predicted_state: Dict[str, float],
    domain_guard: OptimizationDomainGuard,
    permeate_tds_limit: float = 18.0,
    max_element_rec_limit: float = 30.0,
    polarization_limit: float = 1.40,
    enforce_polarization_limit: bool = False,
) -> CandidateConstraintReport:
    """
    Evaluate all engineering and domain constraints for a candidate operating point.
    """
    violations = []

    # 1. Inter-stage booster pressure ordering
    p2_ge_p1_margin = float(p2 - p1)
    if p2 < p1 - 1e-4:
        violations.append(f"Stage 2 pressure ({p2:.2f} bar) < Stage 1 pressure ({p1:.2f} bar)")

    # 2. Maximum element recovery safeguard (<= 30%)
    elem_rec = float(predicted_state.get("maximum_element_recovery_pct", 0.0))
    elem_rec_margin = float(max_element_rec_limit - elem_rec)
    if elem_rec > max_element_rec_limit:
        violations.append(f"Maximum element recovery ({elem_rec:.2f}%) exceeds {max_element_rec_limit:.1f}% limit")

    # 3. Permeate quality constraint (Cp <= 18 mg/L)
    cp = float(predicted_state.get("permeate_tds_mgL", 0.0))
    cp_margin = float(permeate_tds_limit - cp)
    if cp > permeate_tds_limit:
        violations.append(f"Permeate TDS ({cp:.2f} mg/L) exceeds {permeate_tds_limit:.1f} mg/L reference limit")

    # 4. Optional polarization safeguard (beta <= 1.40)
    beta = float(predicted_state.get("maximum_polarization_modulus", 1.0))
    beta_margin = float(polarization_limit - beta)
    if enforce_polarization_limit and beta > polarization_limit:
        violations.append(f"Maximum polarization modulus ({beta:.3f}) exceeds {polarization_limit:.2f} safeguard")

    # 5. Domain Guard inputs & proximity
    candidate_inputs = {
        "feed_flow_m3h": float(predicted_state.get("feed_flow_m3h", 30.0)),
        "feed_tds_mgL": float(predicted_state.get("feed_tds_mgL", 2041.0)),
        "temperature_C": float(predicted_state.get("temperature_C", 25.0)),
        "stage1_pressure_bar": float(p1),
        "stage2_pressure_bar": float(p2),
    }
    input_valid, input_viols = domain_guard.validate_inputs(candidate_inputs)
    if not input_valid:
        violations.extend(input_viols)

    status_enum, d_z = domain_guard.evaluate_proximity_status(candidate_inputs)
    if status_enum == DomainProximityStatus.OUT_OF_DOMAIN:
        violations.append(f"Operating point is OUT_OF_DOMAIN (z-dist={d_z:.2f})")

    is_feasible = len(violations) == 0

    return CandidateConstraintReport(
        is_feasible=is_feasible,
        violations=violations,
        p1_bar=p1,
        p2_bar=p2,
        p2_ge_p1_margin_bar=p2_ge_p1_margin,
        max_element_rec_margin_pct=elem_rec_margin,
        permeate_tds_margin_mgL=cp_margin,
        polarization_margin=beta_margin,
        domain_proximity_status=status_enum.value,
        domain_z_distance=d_z,
    )
