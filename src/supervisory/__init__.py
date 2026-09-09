"""
Stage 8 Supervisory Operations Package.
"""

from supervisory.annual_simulator import (
    AnnualPlantSimulator,
    PolicySimulationResult,
    AnnualHourlyRecord,
    generate_synthetic_industrial_feed,
    run_full_annual_comparison,
)

__all__ = [
    "AnnualPlantSimulator",
    "PolicySimulationResult",
    "AnnualHourlyRecord",
    "generate_synthetic_industrial_feed",
    "run_full_annual_comparison",
]
