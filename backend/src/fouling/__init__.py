"""
Fouling package for dynamic reverse osmosis membrane performance modeling.
"""

from fouling.model import (
    FoulingParameters,
    ElementFoulingState,
    SystemFoulingState,
    DynamicSimulationResult,
    calculate_water_viscosity,
    calculate_clean_membrane_resistance,
    resistance_to_permeability,
)
from fouling.kinetics import (
    compute_element_fouling_rate_per_second,
    compute_element_fouling_rate_per_hour,
    update_element_state,
)
from fouling.calibration import (
    CalibrationReport,
    calibrate_fouling_rate_constant,
)
from fouling.cleaning import (
    apply_cleaning_event,
)
from fouling.metrics import (
    compute_dynamic_trajectory_metrics,
)
from fouling.dynamics import (
    DynamicROSimulator,
)
from fouling.sensitivity import (
    run_fouling_rate_uncertainty_study,
    run_feed_tds_disturbance_study,
)

__all__ = [
    "FoulingParameters",
    "ElementFoulingState",
    "SystemFoulingState",
    "DynamicSimulationResult",
    "calculate_water_viscosity",
    "calculate_clean_membrane_resistance",
    "resistance_to_permeability",
    "compute_element_fouling_rate_per_second",
    "compute_element_fouling_rate_per_hour",
    "update_element_state",
    "CalibrationReport",
    "calibrate_fouling_rate_constant",
    "apply_cleaning_event",
    "compute_dynamic_trajectory_metrics",
    "DynamicROSimulator",
    "run_fouling_rate_uncertainty_study",
    "run_feed_tds_disturbance_study",
]
