"""
Quality Control Module for Stage 3 Simulation Dataset.

Performs rigorous automated verification on each candidate simulation row
to ensure physical plausibility, thermodynamic consistency, and mass conservation.
"""

from enum import Enum
from typing import Any, Dict, List, Tuple
import numpy as np


class QualityFlag(str, Enum):
    """Quality assessment classification flags."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


def verify_scenario_quality(
    row: Dict[str, Any],
    flow_tol_m3h: float = 1e-4,
    solute_tol_kgh: float = 1e-3,
) -> Tuple[QualityFlag, List[str]]:
    """
    Verify physical and mathematical consistency of a simulated scenario row.
    
    Checks:
    1. Recovery in (0, 100)
    2. Mass conservation: Qf == Qp + Qr
    3. Solute conservation: Qf*Cf == Qp*Cp + Qr*Cr
    4. Permeate TDS <= Feed TDS
    5. Concentrate TDS >= Feed TDS
    6. Specific Energy Consumption > 0
    7. Average Flux > 0
    8. Maximum Pressure <= 41.0 bar
    9. No NaN or Inf in numeric outputs
    """
    reasons: List[str] = []
    is_feasible = row.get("feasible", 1) == 1

    if not is_feasible:
        # Infeasible rows are expected to have failure reason, flagged as PASS for provenance
        return QualityFlag.PASS, []

    # 1. NaN / Inf checks
    for k, v in row.items():
        if isinstance(v, (int, float, np.floating, np.integer)):
            if np.isnan(v) or np.isinf(v):
                reasons.append(f"NaN or Inf encountered in field '{k}'")

    if reasons:
        return QualityFlag.FAIL, reasons

    # 2. Recovery check
    recovery = float(row.get("overall_recovery_pct", 0.0))
    if recovery <= 0.0 or recovery >= 100.0:
        reasons.append(f"Overall recovery ({recovery:.2f}%) out of physical bounds (0, 100)")

    # 3. Volumetric flow balance: Qf = Qp + Qr
    qf = float(row.get("feed_flow_m3h", 0.0))
    qp = float(row.get("permeate_flow_m3h", 0.0))
    qr = float(row.get("concentrate_flow_m3h", 0.0))
    flow_diff = abs(qf - (qp + qr))
    if flow_diff > flow_tol_m3h:
        reasons.append(f"Water mass balance error ({flow_diff:.6f} m3/h) exceeds tolerance ({flow_tol_m3h})")

    # 4. Solute mass balance: Qf*Cf = Qp*Cp + Qr*Cr
    # Convert mg/L * m3/h -> kg/h (/1000)
    cf = float(row.get("feed_tds_mgL", 0.0))
    cp = float(row.get("permeate_tds_mgL", 0.0))
    cr = float(row.get("concentrate_tds_mgL", 0.0))
    solute_in = (qf * cf) / 1000.0
    solute_out = (qp * cp + qr * cr) / 1000.0
    solute_diff = abs(solute_in - solute_out)
    if solute_diff > solute_tol_kgh:
        reasons.append(f"Solute mass balance error ({solute_diff:.6f} kg/h) exceeds tolerance ({solute_tol_kgh})")

    # 5. Salinity separation bounds
    if cp > cf:
        reasons.append(f"Permeate TDS ({cp:.2f} mg/L) exceeds Feed TDS ({cf:.2f} mg/L)")
    if cr < cf:
        reasons.append(f"Concentrate TDS ({cr:.2f} mg/L) is lower than Feed TDS ({cf:.2f} mg/L)")

    # 6. Energetics and flux
    sec = float(row.get("SEC_kWh_m3", 0.0))
    if sec <= 0.0:
        reasons.append(f"SEC ({sec:.4f} kWh/m3) is non-positive")

    flux = float(row.get("average_flux_LMH", 0.0))
    if flux <= 0.0:
        reasons.append(f"Average flux ({flux:.2f} LMH) is non-positive")

    # 7. Mechanical pressure constraint
    p1 = float(row.get("stage1_pressure_bar", 0.0))
    p2 = float(row.get("stage2_pressure_bar", 0.0))
    if p1 > 41.0 or p2 > 41.0:
        reasons.append(f"Operating pressure (P1={p1:.1f}, P2={p2:.1f} bar) exceeds mechanical limit (41.0 bar)")

    # 8. Polarization modulus
    cp_mod = float(row.get("maximum_polarization_modulus", 1.0))
    if cp_mod < 1.0 or cp_mod > 10.0:
        reasons.append(f"Maximum polarization modulus ({cp_mod:.4f}) outside physical bounds [1.0, 10.0]")

    if len(reasons) == 0:
        return QualityFlag.PASS, []
    elif len(reasons) == 1 and "polarization" in reasons[0]:
        return QualityFlag.WARNING, reasons
    else:
        return QualityFlag.FAIL, reasons
