"""
Unscented Kalman Filter (UKF) for RO Membrane Fouling State Estimation (Stage 7).

Implements derivative-free UKF using the Merwe scaled unscented transform with:
1. Deterministic sigma point propagation through nonlinear coupled RO dynamics
2. Nonlinear measurement expectation and cross-covariance mapping
3. Robust Cholesky decomposition with jitter fallback
4. Physical state non-negativity bounding
5. Statistical consistency tracking (NIS and NEES)
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


@dataclass
class UKFStepResult:
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


class UnscentedKalmanFilter:
    """
    Unscented Kalman Filter for nonlinear RO fouling resistance estimation.
    """
    def __init__(
        self,
        representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE,
        sensor_set: SensorSet = SensorSet.CASE_2_STANDARD,
        noise_level: NoiseLevel = NoiseLevel.NOMINAL,
        alpha: float = 1e-3,                      # Spread of sigma points
        beta: float = 2.0,                        # Optimal for Gaussian distributions
        kappa: float = 0.0,                       # Secondary scaling
        process_noise_diag_scale: float = 1.0e20, # Q scale [m^-2]
        initial_covariance_diag: float = 1.0e24,  # P_0 scale [(m^-1)^2]
    ) -> None:
        self.representation = representation
        self.sensor_set = sensor_set
        self.noise_level = noise_level
        self.dim_x = StateVector.get_dimension(representation)

        # UKF Tuning parameters
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.kappa = float(kappa)
        self.n = self.dim_x
        self.num_sigma = 2 * self.n + 1

        self.lambda_param = (self.alpha ** 2) * (self.n + self.kappa) - self.n
        self.gamma = np.sqrt(self.n + self.lambda_param)

        # Compute Weights
        self.wm = np.zeros(self.num_sigma, dtype=float)
        self.wc = np.zeros(self.num_sigma, dtype=float)

        self.wm[0] = self.lambda_param / (self.n + self.lambda_param)
        self.wc[0] = self.wm[0] + (1.0 - self.alpha ** 2 + self.beta)

        for i in range(1, self.num_sigma):
            self.wm[i] = 1.0 / (2.0 * (self.n + self.lambda_param))
            self.wc[i] = self.wm[i]

        # Physics models
        self.transition_model = StateTransitionModel(representation=representation)
        self.measurement_model = ROPlantMeasurementModel(sensor_set=sensor_set)
        self.noise_model = SensorNoiseModel(noise_level=noise_level)

        self.sensor_keys = SENSOR_SET_MEMBERS[sensor_set]
        self.dim_y = len(self.sensor_keys)
        self.R = self.noise_model.build_covariance_matrix(self.sensor_keys)

        # Covariance Matrices
        self.Q = np.eye(self.dim_x) * process_noise_diag_scale
        self.x_hat = StateVector.create_clean(representation=representation)
        self.P = np.eye(self.dim_x) * initial_covariance_diag
        self.history: List[UKFStepResult] = []

    def initialize(
        self,
        initial_state: StateVector,
        initial_covariance: Optional[np.ndarray] = None,
    ) -> None:
        if initial_state.representation != self.representation:
            raise ValueError(
                f"State representation mismatch: {initial_state.representation} vs {self.representation}"
            )
        self.x_hat = StateVector(values=initial_state.values.copy(), representation=self.representation)
        if initial_covariance is not None:
            self.P = np.asarray(initial_covariance, dtype=float).copy()
        self.history = []

    def _generate_sigma_points(self, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
        """
        Generate 2n + 1 sigma points around mean vector.
        Shape: (num_sigma, dim_x)
        """
        sigma_pts = np.zeros((self.num_sigma, self.dim_x), dtype=float)
        sigma_pts[0, :] = mean

        # Symmetrize covariance
        cov_sym = 0.5 * (cov + cov.T)
        
        # Robust matrix square root via Cholesky with jitter fallback
        try:
            sqrt_cov = np.linalg.cholesky(cov_sym)
        except np.linalg.LinAlgError:
            jitter = 1e-8 * np.trace(cov_sym) / self.dim_x
            try:
                sqrt_cov = np.linalg.cholesky(cov_sym + np.eye(self.dim_x) * jitter)
            except np.linalg.LinAlgError:
                # Fallback to SVD
                u, s, _ = np.linalg.svd(cov_sym)
                s_clamped = np.maximum(s, 1e-12)
                sqrt_cov = u @ np.diag(np.sqrt(s_clamped))

        scaled_sqrt = self.gamma * sqrt_cov

        for i in range(self.n):
            sigma_pts[1 + i, :] = np.maximum(0.0, mean + scaled_sqrt[:, i])
            sigma_pts[1 + self.n + i, :] = np.maximum(0.0, mean - scaled_sqrt[:, i])

        return sigma_pts

    def step(
        self,
        y_measured: np.ndarray,
        u_inputs: Dict[str, float],
        time_hours: float,
        delta_t_hours: float = 1.0,
        true_state_for_benchmark: Optional[StateVector] = None,
    ) -> UKFStepResult:
        """
        Execute one complete UKF Predict-Correct cycle.
        """
        t_start = time.perf_counter()
        step_idx = len(self.history)

        # -------------------------------------------------------------
        # 1. TIME UPDATE (PREDICT)
        # -------------------------------------------------------------
        # Generate prior sigma points from current posterior
        sigma_x_prev = self._generate_sigma_points(self.x_hat.values, self.P)

        # Propagate each sigma point through nonlinear process model f(chi, u, dt)
        sigma_x_prop = np.zeros_like(sigma_x_prev)
        for i in range(self.num_sigma):
            st_pt = StateVector(values=sigma_x_prev[i, :], representation=self.representation)
            st_next = self.transition_model.predict_next_state(st_pt, u_inputs, delta_t_hours)
            sigma_x_prop[i, :] = st_next.values

        # Reconstruct predicted state mean
        x_prior_vals = np.sum(self.wm[:, None] * sigma_x_prop, axis=0)
        x_prior = StateVector(values=x_prior_vals, representation=self.representation)

        # Reconstruct predicted covariance
        diff_x = sigma_x_prop - x_prior_vals[None, :]
        P_prior = np.zeros((self.dim_x, self.dim_x), dtype=float)
        for i in range(self.num_sigma):
            P_prior += self.wc[i] * np.outer(diff_x[i, :], diff_x[i, :])
        P_prior += self.Q * delta_t_hours
        P_prior = 0.5 * (P_prior + P_prior.T)

        # -------------------------------------------------------------
        # 2. MEASUREMENT UPDATE (CORRECT)
        # -------------------------------------------------------------
        # Generate new sigma points from predicted state and covariance
        sigma_x_prior = self._generate_sigma_points(x_prior_vals, P_prior)

        # Propagate through nonlinear measurement model h(chi, u)
        sigma_y = np.zeros((self.num_sigma, self.dim_y), dtype=float)
        for i in range(self.num_sigma):
            st_pt = StateVector(values=sigma_x_prior[i, :], representation=self.representation)
            sigma_y[i, :] = self.measurement_model.observe(st_pt, u_inputs)

        # Predicted measurement mean
        y_hat = np.sum(self.wm[:, None] * sigma_y, axis=0)

        # Innovation covariance S and cross-covariance Pxy
        diff_y = sigma_y - y_hat[None, :]
        diff_x_prior = sigma_x_prior - x_prior_vals[None, :]

        S = np.zeros((self.dim_y, self.dim_y), dtype=float)
        P_xy = np.zeros((self.dim_x, self.dim_y), dtype=float)

        for i in range(self.num_sigma):
            S += self.wc[i] * np.outer(diff_y[i, :], diff_y[i, :])
            P_xy += self.wc[i] * np.outer(diff_x_prior[i, :], diff_y[i, :])

        S += self.R
        S = 0.5 * (S + S.T)

        # Kalman Gain
        K = P_xy @ np.linalg.inv(S)

        # Innovation
        nu = y_measured - y_hat

        # Posterior State
        x_post_vals = x_prior_vals + K @ nu
        x_post_vals = np.maximum(0.0, x_post_vals)
        x_post = StateVector(values=x_post_vals, representation=self.representation)

        # Posterior Covariance
        P_post = P_prior - K @ S @ K.T
        P_post = 0.5 * (P_post + P_post.T)

        # -------------------------------------------------------------
        # 3. STATISTICAL METRICS (NIS & NEES)
        # -------------------------------------------------------------
        nis = float(nu.T @ np.linalg.inv(S) @ nu)

        nees = None
        if true_state_for_benchmark is not None:
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

        self.x_hat = x_post
        self.P = P_post

        result = UKFStepResult(
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
