"""
State Representations and Process Transition Models for Membrane Fouling State Estimation.

Defines:
1. StateRepresentation (Full 15-Element, Axial 6-Zone, Lumped 2-Stage)
2. StateVector with algebraic conversions (Rf <-> Rtotal <-> Aeff <-> Decline %)
3. StateTransitionModel using authoritative Stage 6 fouling kinetics
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np

from ro_model.membrane import RO_MODEL_VERSION, AW_AUTHORITATIVE_M_PA_S
from ro_model.system import ROSystem
from data_generation.simulator_runner import create_baseline_system
from fouling.model import (
    FoulingParameters,
    calculate_water_viscosity,
    calculate_clean_membrane_resistance,
    resistance_to_permeability,
    RM_AUTHORITATIVE_M_INV,
)
from fouling.kinetics import compute_element_fouling_rate_per_hour


class StateRepresentation(str, Enum):
    """Fouling state representation dimensionality."""
    FULL_15_ELEMENT = "FULL_15_ELEMENT"  # Dim = 15: Rf for each physical element
    AXIAL_6_ZONE = "AXIAL_6_ZONE"        # Dim = 6: S1_Lead, S1_Mid, S1_Tail, S2_Lead, S2_Mid, S2_Tail
    LUMPED_2_STAGE = "LUMPED_2_STAGE"    # Dim = 2: S1_Lumped, S2_Lumped


# Mapping from 15 elements to 6 axial zones
# Stage 1: 3 vessels x 3 elements (idx 0..8)
# Stage 2: 2 vessels x 3 elements (idx 9..14)
# Element indexing within vessel is (idx % 3) for Stage 1 and ((idx - 9) % 3) for Stage 2.
ELEMENT_TO_ZONE_MAP_15_TO_6 = [
    0, 1, 2,  # Vessel 1: E1, E2, E3 -> Zone 0, 1, 2
    0, 1, 2,  # Vessel 2: E1, E2, E3 -> Zone 0, 1, 2
    0, 1, 2,  # Vessel 3: E1, E2, E3 -> Zone 0, 1, 2
    3, 4, 5,  # Vessel 1: E1, E2, E3 -> Zone 3, 4, 5
    3, 4, 5,  # Vessel 2: E1, E2, E3 -> Zone 3, 4, 5
]

ELEMENT_TO_STAGE_MAP_15_TO_2 = [
    0, 0, 0, 0, 0, 0, 0, 0, 0,  # Stage 1 (9 elements) -> Stage 0
    1, 1, 1, 1, 1, 1            # Stage 2 (6 elements) -> Stage 1
]


@dataclass
class StateVector:
    """
    Encapsulates the state vector and provides lossless mapping to 15-element physical distributions.
    """
    values: np.ndarray  # Shape: (dim,)
    representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE

    def __post_init__(self):
        self.values = np.asarray(self.values, dtype=float).flatten()
        expected_dim = self.get_dimension(self.representation)
        if len(self.values) != expected_dim:
            raise ValueError(
                f"StateVector dimension mismatch for {self.representation.value}: "
                f"expected {expected_dim}, got {len(self.values)}"
            )

    @staticmethod
    def get_dimension(rep: StateRepresentation) -> int:
        if rep == StateRepresentation.FULL_15_ELEMENT:
            return 15
        elif rep == StateRepresentation.AXIAL_6_ZONE:
            return 6
        elif rep == StateRepresentation.LUMPED_2_STAGE:
            return 2
        raise ValueError(f"Unknown state representation: {rep}")

    @classmethod
    def create_clean(cls, representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE) -> "StateVector":
        dim = cls.get_dimension(representation)
        return cls(values=np.zeros(dim, dtype=float), representation=representation)

    def to_15_element_array(self) -> np.ndarray:
        """Expand state vector to 15 physical elements."""
        if self.representation == StateRepresentation.FULL_15_ELEMENT:
            return self.values.copy()
        elif self.representation == StateRepresentation.AXIAL_6_ZONE:
            arr15 = np.zeros(15, dtype=float)
            for elem_idx, zone_idx in enumerate(ELEMENT_TO_ZONE_MAP_15_TO_6):
                arr15[elem_idx] = self.values[zone_idx]
            return arr15
        elif self.representation == StateRepresentation.LUMPED_2_STAGE:
            arr15 = np.zeros(15, dtype=float)
            for elem_idx, stage_idx in enumerate(ELEMENT_TO_STAGE_MAP_15_TO_2):
                arr15[elem_idx] = self.values[stage_idx]
            return arr15
        raise ValueError(f"Unsupported representation: {self.representation}")

    @classmethod
    def from_15_element_array(
        cls,
        rf_15: np.ndarray,
        representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE
    ) -> "StateVector":
        """Aggregate 15-element array into chosen state representation."""
        rf_15 = np.asarray(rf_15, dtype=float).flatten()
        if len(rf_15) != 15:
            raise ValueError(f"Expected 15 elements, got {len(rf_15)}")

        if representation == StateRepresentation.FULL_15_ELEMENT:
            return cls(values=rf_15.copy(), representation=representation)
        elif representation == StateRepresentation.AXIAL_6_ZONE:
            # Average across parallel vessels for each axial position
            vals = np.zeros(6, dtype=float)
            counts = np.zeros(6, dtype=float)
            for elem_idx, zone_idx in enumerate(ELEMENT_TO_ZONE_MAP_15_TO_6):
                vals[zone_idx] += rf_15[elem_idx]
                counts[zone_idx] += 1.0
            return cls(values=vals / counts, representation=representation)
        elif representation == StateRepresentation.LUMPED_2_STAGE:
            vals = np.zeros(2, dtype=float)
            counts = np.zeros(2, dtype=float)
            for elem_idx, stg_idx in enumerate(ELEMENT_TO_STAGE_MAP_15_TO_2):
                vals[stg_idx] += rf_15[elem_idx]
                counts[stg_idx] += 1.0
            return cls(values=vals / counts, representation=representation)
        raise ValueError(f"Unsupported representation: {representation}")

    def to_effective_permeabilities_15(self, temperature_celsius: float = 25.0) -> np.ndarray:
        """Convert states to effective Aw for all 15 elements."""
        rf_15 = self.to_15_element_array()
        r_m = calculate_clean_membrane_resistance(AW_AUTHORITATIVE_M_PA_S, temperature_celsius)
        r_tot = r_m + rf_15
        mu = calculate_water_viscosity(temperature_celsius)
        return 1.0 / (mu * r_tot)

    def to_permeability_decline_pct_15(self, temperature_celsius: float = 25.0) -> np.ndarray:
        """Convert states to permeability decline percentage for all 15 elements."""
        rf_15 = self.to_15_element_array()
        r_m = calculate_clean_membrane_resistance(AW_AUTHORITATIVE_M_PA_S, temperature_celsius)
        r_tot = r_m + rf_15
        return (1.0 - (r_m / r_tot)) * 100.0

    def get_average_permeability_decline_pct(self, temperature_celsius: float = 25.0) -> float:
        """Train-average permeability decline percentage."""
        decl_15 = self.to_permeability_decline_pct_15(temperature_celsius)
        return float(np.mean(decl_15))


import copy


class StateTransitionModel:
    """
    Mechanistic state transition model f(x, u, dt).
    Simulates coupled RO hydraulics + Stage 6 dynamic fouling kinetics.
    """
    def __init__(
        self,
        parameters: Optional[FoulingParameters] = None,
        representation: StateRepresentation = StateRepresentation.AXIAL_6_ZONE,
    ) -> None:
        self.parameters = parameters or FoulingParameters.create_default()
        self.representation = representation
        self.system = create_baseline_system()
        # Ensure each element has an independent properties instance
        for stage in self.system.stages:
            stage.vessel_prototype.elements = [
                stage.vessel_prototype.elements[i].__class__(
                    properties=copy.deepcopy(stage.element_properties),
                    config=stage.config,
                    element_index=i + 1
                )
                for i in range(stage.elements_per_vessel)
            ]

    def _apply_state_to_system(self, state: StateVector, temperature_celsius: float) -> None:
        """Set element permeabilities on the internal ROSystem solver prototype."""
        aw_15 = state.to_effective_permeabilities_15(temperature_celsius)
        # Stage 1: vessels share prototype with 3 elements
        # aw_15[0..2] is vessel 1, [3..5] vessel 2, [6..8] vessel 3
        # In symmetric conditions they are equal; take mean for element 1, 2, 3
        stg1_e1 = np.mean([aw_15[0], aw_15[3], aw_15[6]])
        stg1_e2 = np.mean([aw_15[1], aw_15[4], aw_15[7]])
        stg1_e3 = np.mean([aw_15[2], aw_15[5], aw_15[8]])
        self.system.stages[0].vessel_prototype.elements[0].properties.Aw_m_pa_s = float(stg1_e1)
        self.system.stages[0].vessel_prototype.elements[1].properties.Aw_m_pa_s = float(stg1_e2)
        self.system.stages[0].vessel_prototype.elements[2].properties.Aw_m_pa_s = float(stg1_e3)

        # Stage 2: vessels share prototype with 3 elements
        # aw_15[9..11] is vessel 1, [12..14] is vessel 2
        stg2_e1 = np.mean([aw_15[9], aw_15[12]])
        stg2_e2 = np.mean([aw_15[10], aw_15[13]])
        stg2_e3 = np.mean([aw_15[11], aw_15[14]])
        self.system.stages[1].vessel_prototype.elements[0].properties.Aw_m_pa_s = float(stg2_e1)
        self.system.stages[1].vessel_prototype.elements[1].properties.Aw_m_pa_s = float(stg2_e2)
        self.system.stages[1].vessel_prototype.elements[2].properties.Aw_m_pa_s = float(stg2_e3)

    def predict_next_state(
        self,
        current_state: StateVector,
        u_inputs: Dict[str, float],
        delta_t_hours: float = 1.0,
    ) -> StateVector:
        """
        Integrate dynamic fouling equations forward by delta_t_hours.
        
        u_inputs keys:
        - feed_flow_m3h: float
        - feed_tds_mgL: float
        - temperature_C: float
        - stage1_pressure_bar: float
        - stage2_pressure_bar: float
        """
        q_feed = float(u_inputs.get("feed_flow_m3h", 30.0))
        c_feed = float(u_inputs.get("feed_tds_mgL", 2041.0))
        temp_c = float(u_inputs.get("temperature_C", 25.0))
        p1 = float(u_inputs.get("stage1_pressure_bar", 13.0))
        p2 = float(u_inputs.get("stage2_pressure_bar", 18.0))

        # Update system permeabilities
        self._apply_state_to_system(current_state, temp_c)

        # Solve hydraulics
        sys_res = self.system.solve(
            feed_flow_m3_hr=q_feed,
            feed_tds_mg_l=c_feed,
            stage_pressures_bar=[p1, p2],
            temperature_celsius=temp_c,
        )

        stg1_elem_res = sys_res.stage_results[0].vessel_result.element_results
        stg2_elem_res = sys_res.stage_results[1].vessel_result.element_results

        # Current 15-element Rf array
        rf_15 = current_state.to_15_element_array()
        new_rf_15 = np.zeros(15, dtype=float)

        # Compute growth rate for each element
        for elem_idx in range(15):
            if elem_idx < 9:
                # Stage 1
                axial_pos = elem_idx % 3
                eres = stg1_elem_res[axial_pos]
            else:
                # Stage 2
                axial_pos = (elem_idx - 9) % 3
                eres = stg2_elem_res[axial_pos]

            c_bulk_avg = (eres.feed_tds_mg_l + eres.concentrate_tds_mg_l) / 2.0
            c_wall = c_bulk_avg * eres.polarization_modulus

            drf_dt_hr = compute_element_fouling_rate_per_hour(
                flux_lmh=eres.water_flux_lmh,
                polarization_modulus=eres.polarization_modulus,
                surface_tds_mg_l=c_wall,
                parameters=self.parameters,
            )

            new_rf_15[elem_idx] = max(0.0, rf_15[elem_idx] + drf_dt_hr * delta_t_hours)

        return StateVector.from_15_element_array(new_rf_15, representation=self.representation)
