"""
Extended Kalman Filter (EKF) for RO Membrane Fouling State Estimation (Stage 7).

Implements physics-based EKF with:
1. Mechanistic process kinetics time update
2. Numerical measurement Jacobian evaluation
3. Numerically stabilized Joseph-form covariance update
4. Physical non-negativity state bounding
5. Statistical innovation monitoring (NIS and NEES)
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np

from state_estimation.state_model import (
    StateRepresentation,
    StateVector,
    StateTransitionModel,
)
from state_estimation.measurement_model import (
    ROPlantMeasurementModel,
    SensorSet,
    SENSOR_SET_MEMBERS,
)
from state_estimation.noise import SensorNoiseModel, NoiseLevel
from state_estimation.observability import ObservabilityAnalyzer


@dataclass
class EKFStepResult:
    step_index: int
    time_hours: float
    prior_state: StateVector
    posterior_state: StateVector
    prior_covariance: np.ndarray
    posterior_covariance: np.ndarray
    innovation_residual: np.ndarray
    innovation_covariance: np.ndarray
    kalman_gain: np.ndarray
    nis: float
    nees: Optional[float] = None
    step_duration_ms: float = 0.0


class ExtendedKalmanFilter:
    """
    Extended Kalman Filter for dynamic membrane fouling resistance estimation.
    """
    def __init__(
        self,
        representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE,
        sensor_set: SensorSet = SensorSet.CASE_2_STANDARD,
        noise_level: NoiseLevel = NoiseLevel.NOMINAL,
        process_noise_diag_scale: float = 1.0e20,  # Q scale for dRf/dt uncertainty [m^-2]
        initial_covariance_diag: float = 1.0e24,   # P_0 initial state uncertainty [(m^-1)^2]
    ) -> None:
        self.representation = representation
        self.sensor_set = sensor_set
        self.noise_level = noise_level
        self.dim_x = StateVector.get_dimension(representation)

        # Core physics models
        self.transition_model = StateTransitionModel(representation=representation)
        self.measurement_model = ROPlantMeasurementModel(sensor_set=sensor_set)
        self.noise_model = SensorNoiseModel(noise_level=noise_level)
        self.observability_analyzer = ObservabilityAnalyzer(noise_level=noise_level)

        # Covariance Matrices
        self.sensor_keys = SENSOR_SET_MEMBERS[sensor_set]
        self.dim_y = len(self.sensor_keys)
        self.R = self.noise_model.build_covariance_matrix(self.sensor_keys)

        # Process Noise Covariance Q (diagonal)
        self.Q = np.eye(self.dim_x) * process_noise_diag_scale

        # Filter state
        self.x_hat = StateVector.create_clean(representation=representation)
        self.P = np.eye(self.dim_x) * initial_covariance_diag
        self.history: List[EKFStepResult] = []

    def initialize(
        self,
        initial_state: StateVector,
        initial_covariance: Optional[np.ndarray] = None,
    ) -> None:
        """Set filter starting point."""
        if initial_state.representation != self.representation:
            raise ValueError(
                f"State representation mismatch: {initial_state.representation} vs {self.representation}"
            )
        self.x_hat = StateVector(values=initial_state.values.copy(), representation=self.representation)
        if initial_covariance is not None:
            self.P = np.asarray(initial_covariance, dtype=float).copy()
        self.history = []

    def step(
        self,
        y_measured: np.ndarray,
        u_inputs: Dict[str, float],
        time_hours: float,
        delta_t_hours: float = 1.0,
        true_state_for_benchmark: Optional[StateVector] = None,
    ) -> EKFStepResult:
        """
        Execute one complete Predict-Correct EKF cycle.
        """
        t_start = time.perf_counter()
        step_idx = len(self.history)

        # -------------------------------------------------------------
        # 1. TIME UPDATE (PREDICT)
        # -------------------------------------------------------------
        # Predict state through nonlinear dynamic model f(x, u, dt)
        x_prior = self.transition_model.predict_next_state(
            current_state=self.x_hat,
            u_inputs=u_inputs,
            delta_t_hours=delta_t_hours,
        )

        # Process Jacobian F = df/dx (approximate as Identity for small dt or evaluate)
        # Given small dt=1.0h, F approx Identity + dt * d(f_dot)/dx.
        F = np.eye(self.dim_x)

        # Predict covariance
        P_prior = F @ self.P @ F.T + self.Q * delta_t_hours

        # -------------------------------------------------------------
        # 2. MEASUREMENT UPDATE (CORRECT)
        # -------------------------------------------------------------
        # Predict measurement y_hat = h(x_prior, u)
        y_hat = self.measurement_model.observe(x_prior, u_inputs)

        # Numerical Jacobian H = dh/dx
        H = self.observability_analyzer.compute_jacobian(x_prior, u_inputs, self.measurement_model)

        # Innovation
        nu = y_measured - y_hat
        S = H @ P_prior @ H.T + self.R

        # Kalman Gain
        # S is symmetric positive definite; use solve instead of direct inv for stability
        K = P_prior @ H.T @ np.linalg.inv(S)

        # Posterior state
        x_post_vals = x_prior.values + K @ nu
        # Physical boundary: Rf >= 0
        x_post_vals = np.maximum(0.0, x_post_vals)
        x_post = StateVector(values=x_post_vals, representation=self.representation)

        # Joseph-form Covariance Update: P = (I - KH) P_prior (I - KH)^T + K R K^T
        I_KH = np.eye(self.dim_x) - K @ H
        P_post = I_KH @ P_prior @ I_KH.T + K @ self.R @ K.T
        # Symmetrize
        P_post = 0.5 * (P_post + P_post.T)

        # -------------------------------------------------------------
        # 3. STATISTICAL METRICS (NIS & NEES)
        # -------------------------------------------------------------
        nis = float(nu.T @ np.linalg.inv(S) @ nu)

        nees = None
        if true_state_for_benchmark is not None:
            # Project true state to matching representation
            x_true_arr = StateVector.from_15_element_array(
                true_state_for_benchmark.to_15_element_array(),
                representation=self.representation,
            ).values
            e_x = x_post.values - x_true_arr
            try:
                nees = float(e_x.T @ np.linalg.inv(P_post) @ e_x)
            except np.linalg.LinAlgError:
                nees = float("nan")

        t_end = time.perf_counter()
        dur_ms = (t_end - t_start) * 1000.0

        # Update internal state
        self.x_hat = x_post
        self.P = P_post

        result = EKFStepResult(
            step_index=step_idx,
            time_hours=float(time_hours),
            prior_state=x_prior,
            posterior_state=x_post,
            prior_covariance=P_prior,
            posterior_covariance=P_post,
            innovation_residual=nu,
            innovation_covariance=S,
            kalman_gain=K,
            nis=nis,
            nees=nees,
            step_duration_ms=dur_ms,
        )
        self.history.append(result)
        return result
