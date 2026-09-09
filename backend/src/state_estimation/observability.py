"""
Observability, Identifiability, and Numerical Conditioning Analysis (Stage 7).

Provides mathematical tools to:
1. Compute the numerical measurement sensitivity Jacobian H = dh/dx
2. Evaluate Fisher Information Matrix (FIM = H^T R^-1 H) and SVD conditioning
3. Quantify state collinearity and determine the maximally observable state dimension
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd

from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import ROPlantMeasurementModel, SensorSet, SENSOR_SET_MEMBERS
from state_estimation.noise import SensorNoiseModel, NoiseLevel


@dataclass
class ObservabilityReport:
    state_representation: StateRepresentation
    sensor_set: SensorSet
    state_dimension: int
    measurement_dimension: int
    jacobian_matrix: np.ndarray
    singular_values: np.ndarray
    effective_rank: int
    condition_number: float
    collinearity_matrix: np.ndarray
    fim_eigenvalues: np.ndarray
    observable_modes_summary: str


class ObservabilityAnalyzer:
    """
    Computes local sensitivity, observability Gramian / Fisher Information,
    and conditioning for RO fouling state estimation.
    """
    def __init__(
        self,
        noise_level: NoiseLevel = NoiseLevel.NOMINAL,
        perturbation_rf_m_inv: float = 1.0e11,
    ) -> None:
        self.noise_model = SensorNoiseModel(noise_level=noise_level)
        self.delta_rf = perturbation_rf_m_inv

    def compute_jacobian(
        self,
        nominal_state: StateVector,
        u_inputs: Dict[str, float],
        measurement_model: ROPlantMeasurementModel,
    ) -> np.ndarray:
        """
        Compute numerical measurement Jacobian H = dh(x, u)/dx via forward differences.
        H shape: (num_measurements, state_dimension)
        """
        m_dim = measurement_model.observation_dimension
        n_dim = StateVector.get_dimension(nominal_state.representation)
        H = np.zeros((m_dim, n_dim), dtype=float)

        x_nominal = nominal_state.values.copy()
        y_nominal = measurement_model.observe(nominal_state, u_inputs)

        for j in range(n_dim):
            x_plus = x_nominal.copy()
            x_plus[j] += self.delta_rf
            state_plus = StateVector(values=x_plus, representation=nominal_state.representation)
            y_plus = measurement_model.observe(state_plus, u_inputs)
            H[:, j] = (y_plus - y_nominal) / self.delta_rf

        return H

    def analyze(
        self,
        nominal_state: StateVector,
        u_inputs: Dict[str, float],
        sensor_set: SensorSet = SensorSet.CASE_2_STANDARD,
    ) -> ObservabilityReport:
        """
        Execute comprehensive observability, FIM, and conditioning analysis.
        """
        meas_model = ROPlantMeasurementModel(sensor_set=sensor_set)
        sensor_keys = SENSOR_SET_MEMBERS[sensor_set]
        R = self.noise_model.build_covariance_matrix(sensor_keys)
        R_inv = np.linalg.inv(R)

        # 1. Jacobian
        H = self.compute_jacobian(nominal_state, u_inputs, meas_model)

        # 2. SVD of Jacobian
        U, s, Vt = np.linalg.svd(H, full_matrices=False)
        rank_tol = s[0] * max(H.shape) * np.finfo(float).eps * 1e4
        eff_rank = int(np.sum(s > rank_tol))
        cond_num = float(s[0] / s[-1]) if s[-1] > 1e-15 else float("inf")

        # 3. Fisher Information Matrix (FIM = H^T R^-1 H)
        FIM = H.T @ R_inv @ H
        fim_eig = np.linalg.eigvalsh(FIM)[::-1]  # Descending order

        # 4. Collinearity / Correlation Matrix between sensitivity columns
        n_dim = H.shape[1]
        collin = np.zeros((n_dim, n_dim), dtype=float)
        norms = np.linalg.norm(H, axis=0)

        for i in range(n_dim):
            for j in range(n_dim):
                if norms[i] > 1e-12 and norms[j] > 1e-12:
                    collin[i, j] = np.dot(H[:, i], H[:, j]) / (norms[i] * norms[j])
                else:
                    collin[i, j] = 1.0 if i == j else 0.0

        # Summary text
        if eff_rank < n_dim:
            summary = (
                f"STRUCTURALLY UNCERTAIN / RANK DEFICIENT: State dimension {n_dim} exceeds "
                f"observable rank {eff_rank}. Null space dimension = {n_dim - eff_rank}."
            )
        else:
            if cond_num > 1e4:
                summary = (
                    f"ILL-CONDITIONED (Full Rank {eff_rank}/{n_dim}, Condition Number = {cond_num:.1e}): "
                    f"Weakly observable modes present; high sensitivity to noise."
                )
            else:
                summary = (
                    f"WELL-CONDITIONED & FULLY OBSERVABLE (Rank {eff_rank}/{n_dim}, "
                    f"Condition Number = {cond_num:.2f})."
                )

        return ObservabilityReport(
            state_representation=nominal_state.representation,
            sensor_set=sensor_set,
            state_dimension=n_dim,
            measurement_dimension=len(sensor_keys),
            jacobian_matrix=H,
            singular_values=s,
            effective_rank=eff_rank,
            condition_number=cond_num,
            collinearity_matrix=collin,
            fim_eigenvalues=fim_eig,
            observable_modes_summary=summary,
        )
