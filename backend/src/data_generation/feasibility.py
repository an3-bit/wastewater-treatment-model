"""
Feasibility and Failure Classification Module.

Standardizes simulation feasibility states and classifies failure mechanisms
for Stage 3 dataset tracking.
"""

from enum import Enum
from typing import Optional, Tuple


class FailureCategory(str, Enum):
    """Enumeration of possible simulation failure mechanisms."""
    NONE = "NONE"
    OSMOTIC_STALL = "OSMOTIC_STALL"
    PRESSURE_LIMIT = "PRESSURE_LIMIT"
    ELEMENT_RECOVERY_LIMIT = "ELEMENT_RECOVERY_LIMIT"
    NEGATIVE_FLOW = "NEGATIVE_FLOW"
    SOLVER_FAILURE = "SOLVER_FAILURE"
    EXCESSIVE_POLARIZATION = "EXCESSIVE_POLARIZATION"
    FEED_STARVATION = "FEED_STARVATION"
    OTHER = "OTHER"


def classify_simulation_failure(
    exception: Optional[Exception] = None,
    error_message: str = "",
    context: Optional[dict] = None,
) -> Tuple[FailureCategory, str]:
    """
    Classify a simulation failure into a standard FailureCategory and descriptive message.
    """
    msg = (str(exception) if exception else error_message).lower()
    ctx = context or {}

    # Check context-driven physical boundaries first
    if ctx.get("pressure_limit_exceeded", False) or "pressure" in msg and "exceed" in msg:
        return FailureCategory.PRESSURE_LIMIT, "Operating pressure exceeds mechanical limit of 41.0 bar"

    if "element recovery" in msg or "element recovery exceeds limit" in msg or ctx.get("recovery_limit_exceeded", False):
        return FailureCategory.ELEMENT_RECOVERY_LIMIT, "Single element recovery exceeds safeguard limit (30%)"

    if "osmotic stall" in msg or "driving pressure" in msg or "negative net driving" in msg:
        return FailureCategory.OSMOTIC_STALL, "Transmembrane driving pressure below local osmotic pressure"

    if "negative" in msg and ("flow" in msg or "flux" in msg):
        return FailureCategory.NEGATIVE_FLOW, "Non-physical negative volumetric flow or flux encountered"

    if "starvation" in msg or "feed flow insufficient" in msg:
        return FailureCategory.FEED_STARVATION, "Downstream stage/element feed flow below minimum operating threshold"

    if "polarization" in msg or "polarization modulus" in msg:
        return FailureCategory.EXCESSIVE_POLARIZATION, "Concentration polarization modulus exceeded physical bounds"

    if "solver" in msg or "convergence" in msg or "did not converge" in msg or "maxiter" in msg:
        return FailureCategory.SOLVER_FAILURE, f"Nonlinear algebraic solver failed to converge: {str(exception)}"

    if exception is not None:
        return FailureCategory.OTHER, f"Unexpected simulation failure: {str(exception)}"

    return FailureCategory.NONE, ""
