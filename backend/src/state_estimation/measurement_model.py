"""
Plant-Observable Measurement Models and Sensor Set Formulations (Stage 7).

Defines:
1. SensorClassification (COMMON_INDUSTRIAL, OPTIONAL, SYNTHETIC_PROHIBITED)
2. SensorSet configurations (CASE_1_MINIMAL, CASE_2_STANDARD, CASE_3_RICH)
3. ROPlantMeasurementModel forward observation operator h(x, u)
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np

from ro_model.membrane import RO_MODEL_VERSION, AW_AUTHORITATIVE_M_PA_S
from ro_model.system import ROSystem, SystemResult
from data_generation.simulator_runner import create_baseline_system
from state_estimation.state_model import StateVector, StateRepresentation


class SensorClassification(str, Enum):
    COMMON_INDUSTRIAL_SENSOR = "COMMON_INDUSTRIAL_SENSOR"
    OPTIONAL_SENSOR = "OPTIONAL_SENSOR"
    SYNTHETIC_NOT_DIRECTLY_MEASURED = "SYNTHETIC_NOT_DIRECTLY_MEASURED"


class SensorSet(str, Enum):
    CASE_1_MINIMAL = "CASE_1_MINIMAL"    # 6 basic skid sensors
    CASE_2_STANDARD = "CASE_2_STANDARD"  # 10 standard sensors with stage pressure & power
    CASE_3_RICH = "CASE_3_RICH"          # 13 rich sensors including stage permeate & concentrate TDS


@dataclass
class MeasurementDefinition:
    name: str
    symbol: str
    unit: str
    classification: SensorClassification
    description: str


ALL_MEASUREMENT_DEFINITIONS: Dict[str, MeasurementDefinition] = {
    "feed_flow_m3h": MeasurementDefinition(
        name="feed_flow_m3h",
        symbol="Q_f",
        unit="m3/h",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Total plant raw wastewater feed volumetric flow rate",
    ),
    "feed_tds_mgL": MeasurementDefinition(
        name="feed_tds_mgL",
        symbol="C_f",
        unit="mg/L",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Feed water Total Dissolved Solids / electrical conductivity equivalent",
    ),
    "temperature_C": MeasurementDefinition(
        name="temperature_C",
        symbol="T",
        unit="degC",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Feed water stream operating temperature",
    ),
    "stage1_pressure_bar": MeasurementDefinition(
        name="stage1_pressure_bar",
        symbol="P_1",
        unit="bar",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="High-pressure feed pump discharge pressure to Stage 1",
    ),
    "total_permeate_flow_m3h": MeasurementDefinition(
        name="total_permeate_flow_m3h",
        symbol="Q_p,tot",
        unit="m3/h",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Combined permeate flow rate from all stages",
    ),
    "permeate_tds_mgL": MeasurementDefinition(
        name="permeate_tds_mgL",
        symbol="C_p,tot",
        unit="mg/L",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Combined permeate stream TDS / electrical conductivity equivalent",
    ),
    "stage2_pressure_bar": MeasurementDefinition(
        name="stage2_pressure_bar",
        symbol="P_2",
        unit="bar",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Inter-stage booster pump discharge pressure to Stage 2",
    ),
    "interstage_pressure_bar": MeasurementDefinition(
        name="interstage_pressure_bar",
        symbol="P_int",
        unit="bar",
        classification=SensorClassification.OPTIONAL_SENSOR,
        description="Stage 1 concentrate exit pressure / Stage 2 booster suction pressure",
    ),
    "concentrate_tds_mgL": MeasurementDefinition(
        name="concentrate_tds_mgL",
        symbol="C_c,tot",
        unit="mg/L",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Final Stage 2 concentrate brine stream TDS / conductivity",
    ),
    "total_electrical_power_kw": MeasurementDefinition(
        name="total_electrical_power_kw",
        symbol="W_elec",
        unit="kW",
        classification=SensorClassification.COMMON_INDUSTRIAL_SENSOR,
        description="Total electrical power consumption of high-pressure and booster pumps",
    ),
    "stage1_permeate_flow_m3h": MeasurementDefinition(
        name="stage1_permeate_flow_m3h",
        symbol="Q_p,1",
        unit="m3/h",
        classification=SensorClassification.OPTIONAL_SENSOR,
        description="Individual Stage 1 permeate collection header flow rate",
    ),
    "stage2_permeate_flow_m3h": MeasurementDefinition(
        name="stage2_permeate_flow_m3h",
        symbol="Q_p,2",
        unit="m3/h",
        classification=SensorClassification.OPTIONAL_SENSOR,
        description="Individual Stage 2 permeate collection header flow rate",
    ),
    "stage1_concentrate_tds_mgL": MeasurementDefinition(
        name="stage1_concentrate_tds_mgL",
        symbol="C_c,1",
        unit="mg/L",
        classification=SensorClassification.OPTIONAL_SENSOR,
        description="Inter-stage concentrate stream TDS entering Stage 2",
    ),
}

# Strictly prohibited variables from measurement inputs (Anti-Leakage)
PROHIBITED_MEASUREMENTS = [
    "r_f",
    "r_f_15",
    "aw_eff",
    "permeability_ratio",
    "permeability_decline_pct",
    "polarization_modulus",
    "surface_tds_mg_l",
    "membrane_wall_concentration",
]

# Sensor lists for each case
SENSOR_SET_MEMBERS: Dict[SensorSet, List[str]] = {
    SensorSet.CASE_1_MINIMAL: [
        "feed_flow_m3h",
        "feed_tds_mgL",
        "temperature_C",
        "stage1_pressure_bar",
        "total_permeate_flow_m3h",
        "permeate_tds_mgL",
    ],
    SensorSet.CASE_2_STANDARD: [
        "feed_flow_m3h",
        "feed_tds_mgL",
        "temperature_C",
        "stage1_pressure_bar",
        "total_permeate_flow_m3h",
        "permeate_tds_mgL",
        "stage2_pressure_bar",
        "interstage_pressure_bar",
        "concentrate_tds_mgL",
        "total_electrical_power_kw",
    ],
    SensorSet.CASE_3_RICH: [
        "feed_flow_m3h",
        "feed_tds_mgL",
        "temperature_C",
        "stage1_pressure_bar",
        "total_permeate_flow_m3h",
        "permeate_tds_mgL",
        "stage2_pressure_bar",
        "interstage_pressure_bar",
        "concentrate_tds_mgL",
        "total_electrical_power_kw",
        "stage1_permeate_flow_m3h",
        "stage2_permeate_flow_m3h",
        "stage1_concentrate_tds_mgL",
    ],
}


import copy


class ROPlantMeasurementModel:
    """
    Forward observation operator h(x, u).
    Solves the mechanistic RO model to map estimated state x and plant inputs u to observable sensor values.
    """
    def __init__(self, sensor_set: SensorSet = SensorSet.CASE_2_STANDARD) -> None:
        self.sensor_set = sensor_set
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
        self.measurement_keys = SENSOR_SET_MEMBERS[sensor_set]

    def set_sensor_set(self, sensor_set: SensorSet) -> None:
        self.sensor_set = sensor_set
        self.measurement_keys = SENSOR_SET_MEMBERS[sensor_set]

    @property
    def observation_dimension(self) -> int:
        return len(self.measurement_keys)

    def _apply_state_to_system(self, state: StateVector, temperature_celsius: float) -> None:
        aw_15 = state.to_effective_permeabilities_15(temperature_celsius)
        stg1_e1 = np.mean([aw_15[0], aw_15[3], aw_15[6]])
        stg1_e2 = np.mean([aw_15[1], aw_15[4], aw_15[7]])
        stg1_e3 = np.mean([aw_15[2], aw_15[5], aw_15[8]])
        self.system.stages[0].vessel_prototype.elements[0].properties.Aw_m_pa_s = float(stg1_e1)
        self.system.stages[0].vessel_prototype.elements[1].properties.Aw_m_pa_s = float(stg1_e2)
        self.system.stages[0].vessel_prototype.elements[2].properties.Aw_m_pa_s = float(stg1_e3)

        stg2_e1 = np.mean([aw_15[9], aw_15[12]])
        stg2_e2 = np.mean([aw_15[10], aw_15[13]])
        stg2_e3 = np.mean([aw_15[11], aw_15[14]])
        self.system.stages[1].vessel_prototype.elements[0].properties.Aw_m_pa_s = float(stg2_e1)
        self.system.stages[1].vessel_prototype.elements[1].properties.Aw_m_pa_s = float(stg2_e2)
        self.system.stages[1].vessel_prototype.elements[2].properties.Aw_m_pa_s = float(stg2_e3)

    def compute_all_observables(
        self,
        state: StateVector,
        u_inputs: Dict[str, float],
    ) -> Dict[str, float]:
        """Compute the full master dictionary of all 13 observable measurements."""
        q_feed = float(u_inputs.get("feed_flow_m3h", 30.0))
        c_feed = float(u_inputs.get("feed_tds_mgL", 2041.0))
        temp_c = float(u_inputs.get("temperature_C", 25.0))
        p1 = float(u_inputs.get("stage1_pressure_bar", 13.0))
        p2 = float(u_inputs.get("stage2_pressure_bar", 18.0))

        self._apply_state_to_system(state, temp_c)

        sys_res = self.system.solve(
            feed_flow_m3_hr=q_feed,
            feed_tds_mg_l=c_feed,
            stage_pressures_bar=[p1, p2],
            temperature_celsius=temp_c,
        )

        stg1_res = sys_res.stage_results[0]
        stg2_res = sys_res.stage_results[1]

        all_obs = {
            "feed_flow_m3h": q_feed,
            "feed_tds_mgL": c_feed,
            "temperature_C": temp_c,
            "stage1_pressure_bar": p1,
            "total_permeate_flow_m3h": float(sys_res.permeate_flow_m3_hr),
            "permeate_tds_mgL": float(sys_res.permeate_tds_mg_l),
            "stage2_pressure_bar": p2,
            "interstage_pressure_bar": float(stg1_res.concentrate_pressure_bar),
            "concentrate_tds_mgL": float(sys_res.concentrate_tds_mg_l),
            "total_electrical_power_kw": float(sys_res.total_electrical_power_kw),
            "stage1_permeate_flow_m3h": float(stg1_res.permeate_flow_m3_hr),
            "stage2_permeate_flow_m3h": float(stg2_res.permeate_flow_m3_hr),
            "stage1_concentrate_tds_mgL": float(stg1_res.concentrate_tds_mg_l),
        }
        return all_obs

    def observe(
        self,
        state: StateVector,
        u_inputs: Dict[str, float],
        custom_sensor_list: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Evaluate observation vector h(x, u) matching the configured sensor set.
        """
        obs_dict = self.compute_all_observables(state, u_inputs)
        keys = custom_sensor_list or self.measurement_keys
        return np.array([obs_dict[k] for k in keys], dtype=float)
