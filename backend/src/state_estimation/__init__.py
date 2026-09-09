"""
State Estimation & Virtual Sensor Package for Reverse Osmosis Membranes (Stage 7).

Provides physics-based Extended Kalman Filter (EKF) and Unscented Kalman Filter (UKF)
for hidden membrane fouling resistance estimation and virtual sensor forecasting.

Authoritative Model Version: "2.0-pressure-corrected"
"""

from ro_model.membrane import RO_MODEL_VERSION

# Enforce Version Lock
STAGE7_REQUIRED_VERSION = "2.0-pressure-corrected"
if RO_MODEL_VERSION != STAGE7_REQUIRED_VERSION:
    raise RuntimeError(
        f"Stage 7 requires Model Version '{STAGE7_REQUIRED_VERSION}', but found '{RO_MODEL_VERSION}'."
    )

from state_estimation.state_model import (
    StateRepresentation,
    StateVector,
    StateTransitionModel,
)
from state_estimation.measurement_model import (
    SensorSet,
    SensorClassification,
    MeasurementDefinition,
    ROPlantMeasurementModel,
)
from state_estimation.noise import (
    SensorNoiseModel,
    NoiseLevel,
    get_provenance_noise_table,
)
from state_estimation.observability import (
    ObservabilityAnalyzer,
    ObservabilityReport,
)
from state_estimation.ekf import ExtendedKalmanFilter
from state_estimation.ukf import UnscentedKalmanFilter
from state_estimation.forecasting import VirtualSensorForecaster, ForecastResult
from state_estimation.metrics import (
    StateEstimationMetrics,
    compute_estimation_metrics,
    evaluate_filter_consistency,
)
from state_estimation.sensor_ablation import SensorAblationStudy

__all__ = [
    "RO_MODEL_VERSION",
    "STAGE7_REQUIRED_VERSION",
    "StateRepresentation",
    "StateVector",
    "StateTransitionModel",
    "SensorSet",
    "SensorClassification",
    "MeasurementDefinition",
    "ROPlantMeasurementModel",
    "SensorNoiseModel",
    "NoiseLevel",
    "get_provenance_noise_table",
    "ObservabilityAnalyzer",
    "ObservabilityReport",
    "ExtendedKalmanFilter",
    "UnscentedKalmanFilter",
    "VirtualSensorForecaster",
    "ForecastResult",
    "StateEstimationMetrics",
    "compute_estimation_metrics",
    "evaluate_filter_consistency",
    "SensorAblationStudy",
]
