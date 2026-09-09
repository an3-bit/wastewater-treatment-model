"""
Measurement Noise Models, Provenance Metadata, and Covariance Formulations (Stage 7).

Provides:
1. NoiseLevel enumeration (LOW, NOMINAL, HIGH)
2. Provenance ledger documenting assumed industrial sensor noise levels
3. SensorNoiseModel for synthetic noisy measurement generation and covariance R calculation
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd

from state_estimation.measurement_model import SensorSet, SENSOR_SET_MEMBERS, ALL_MEASUREMENT_DEFINITIONS


class NoiseLevel(str, Enum):
    LOW = "LOW"          # High-precision / laboratory-grade calibrated sensors
    NOMINAL = "NOMINAL"  # Standard modern industrial RO skid instrumentation
    HIGH = "HIGH"        # Harsh industrial environment / drift-prone sensors


@dataclass
class SensorNoiseProvenance:
    sensor_name: str
    symbol: str
    unit: str
    instrument_technology: str
    nominal_std_dev: float
    low_std_dev: float
    high_std_dev: float
    relative_error_pct_nominal: float
    provenance_classification: str
    notes: str


NOISE_PROVENANCE_LEDGER: Dict[str, SensorNoiseProvenance] = {
    "feed_flow_m3h": SensorNoiseProvenance(
        sensor_name="feed_flow_m3h",
        symbol="Q_f",
        unit="m3/h",
        instrument_technology="Electromagnetic flowmeter (inline)",
        nominal_std_dev=0.45,
        low_std_dev=0.15,
        high_std_dev=1.00,
        relative_error_pct_nominal=1.5,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Typical textile wastewater inlet flowmeter (accuracy +/- 0.5-2.0% FS)",
    ),
    "feed_tds_mgL": SensorNoiseProvenance(
        sensor_name="feed_tds_mgL",
        symbol="C_f",
        unit="mg/L",
        instrument_technology="Toroidal inductive conductivity cell (temperature-compensated)",
        nominal_std_dev=20.0,
        low_std_dev=5.0,
        high_std_dev=50.0,
        relative_error_pct_nominal=1.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Linear conversion factor 0.65 mg/L per uS/cm from calibrated baseline",
    ),
    "temperature_C": SensorNoiseProvenance(
        sensor_name="temperature_C",
        symbol="T",
        unit="degC",
        instrument_technology="Pt100 4-wire RTD Class A transmitter",
        nominal_std_dev=0.30,
        low_std_dev=0.10,
        high_std_dev=0.80,
        relative_error_pct_nominal=1.2,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Standard immersion RTD with 4-20mA transmitter",
    ),
    "stage1_pressure_bar": SensorNoiseProvenance(
        sensor_name="stage1_pressure_bar",
        symbol="P_1",
        unit="bar",
        instrument_technology="Piezoresistive ceramic diaphragm pressure transmitter",
        nominal_std_dev=0.15,
        low_std_dev=0.05,
        high_std_dev=0.40,
        relative_error_pct_nominal=1.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="High-pressure feed pump discharge pressure gauge (+/- 0.5-1.0% FS)",
    ),
    "total_permeate_flow_m3h": SensorNoiseProvenance(
        sensor_name="total_permeate_flow_m3h",
        symbol="Q_p,tot",
        unit="m3/h",
        instrument_technology="Electromagnetic flowmeter / Coriolis meter",
        nominal_std_dev=0.25,
        low_std_dev=0.08,
        high_std_dev=0.60,
        relative_error_pct_nominal=1.5,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Combined permeate manifold meter",
    ),
    "permeate_tds_mgL": SensorNoiseProvenance(
        sensor_name="permeate_tds_mgL",
        symbol="C_p,tot",
        unit="mg/L",
        instrument_technology="Low-conductivity 2-electrode contacting cell",
        nominal_std_dev=0.50,
        low_std_dev=0.15,
        high_std_dev=1.50,
        relative_error_pct_nominal=5.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Permeate purity monitor (nominal ~10 mg/L TDS)",
    ),
    "stage2_pressure_bar": SensorNoiseProvenance(
        sensor_name="stage2_pressure_bar",
        symbol="P_2",
        unit="bar",
        instrument_technology="Piezoresistive pressure transmitter",
        nominal_std_dev=0.18,
        low_std_dev=0.06,
        high_std_dev=0.45,
        relative_error_pct_nominal=1.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Stage 2 booster discharge pressure",
    ),
    "interstage_pressure_bar": SensorNoiseProvenance(
        sensor_name="interstage_pressure_bar",
        symbol="P_int",
        unit="bar",
        instrument_technology="Piezoresistive pressure transmitter",
        nominal_std_dev=0.15,
        low_std_dev=0.05,
        high_std_dev=0.40,
        relative_error_pct_nominal=1.2,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Inter-stage suction manifold pressure",
    ),
    "concentrate_tds_mgL": SensorNoiseProvenance(
        sensor_name="concentrate_tds_mgL",
        symbol="C_c,tot",
        unit="mg/L",
        instrument_technology="Toroidal inductive conductivity cell (high salinity)",
        nominal_std_dev=50.0,
        low_std_dev=15.0,
        high_std_dev=120.0,
        relative_error_pct_nominal=1.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Brine discharge concentration monitor (~5000 mg/L)",
    ),
    "total_electrical_power_kw": SensorNoiseProvenance(
        sensor_name="total_electrical_power_kw",
        symbol="W_elec",
        unit="kW",
        instrument_technology="True-RMS 3-phase digital power analyzer",
        nominal_std_dev=0.30,
        low_std_dev=0.10,
        high_std_dev=0.80,
        relative_error_pct_nominal=1.5,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="VFD / motor power telemetry (+/- 1.0% reading)",
    ),
    "stage1_permeate_flow_m3h": SensorNoiseProvenance(
        sensor_name="stage1_permeate_flow_m3h",
        symbol="Q_p,1",
        unit="m3/h",
        instrument_technology="Electromagnetic flowmeter (Stage 1 header)",
        nominal_std_dev=0.18,
        low_std_dev=0.06,
        high_std_dev=0.45,
        relative_error_pct_nominal=1.5,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Optional individual stage 1 permeate flowmeter",
    ),
    "stage2_permeate_flow_m3h": SensorNoiseProvenance(
        sensor_name="stage2_permeate_flow_m3h",
        symbol="Q_p,2",
        unit="m3/h",
        instrument_technology="Electromagnetic flowmeter (Stage 2 header)",
        nominal_std_dev=0.10,
        low_std_dev=0.03,
        high_std_dev=0.25,
        relative_error_pct_nominal=1.5,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Optional individual stage 2 permeate flowmeter",
    ),
    "stage1_concentrate_tds_mgL": SensorNoiseProvenance(
        sensor_name="stage1_concentrate_tds_mgL",
        symbol="C_c,1",
        unit="mg/L",
        instrument_technology="Toroidal inductive conductivity cell (interstage)",
        nominal_std_dev=35.0,
        low_std_dev=10.0,
        high_std_dev=90.0,
        relative_error_pct_nominal=1.0,
        provenance_classification="ASSUMED / STUDY VALUE",
        notes="Optional interstage concentrate salinity monitor",
    ),
}


def get_provenance_noise_table() -> pd.DataFrame:
    """Export provenance ledger as a pandas DataFrame."""
    rows = []
    for prov in NOISE_PROVENANCE_LEDGER.values():
        rows.append({
            "Sensor Name": prov.sensor_name,
            "Symbol": prov.symbol,
            "Unit": prov.unit,
            "Technology": prov.instrument_technology,
            "Nominal Std Dev": prov.nominal_std_dev,
            "Low Std Dev": prov.low_std_dev,
            "High Std Dev": prov.high_std_dev,
            "Nominal Rel Error (%)": prov.relative_error_pct_nominal,
            "Provenance Classification": prov.provenance_classification,
            "Notes": prov.notes,
        })
    return pd.DataFrame(rows)


class SensorNoiseModel:
    """
    Applies configurable Gaussian measurement noise and builds measurement covariance R.
    """
    def __init__(
        self,
        noise_level: NoiseLevel = NoiseLevel.NOMINAL,
        random_seed: Optional[int] = 42,
    ) -> None:
        self.noise_level = noise_level
        self.rng = np.random.RandomState(random_seed)

    def get_standard_deviation(self, sensor_name: str) -> float:
        if sensor_name not in NOISE_PROVENANCE_LEDGER:
            raise KeyError(f"Unknown sensor name: '{sensor_name}'")
        prov = NOISE_PROVENANCE_LEDGER[sensor_name]
        if self.noise_level == NoiseLevel.LOW:
            return prov.low_std_dev
        elif self.noise_level == NoiseLevel.NOMINAL:
            return prov.nominal_std_dev
        elif self.noise_level == NoiseLevel.HIGH:
            return prov.high_std_dev
        raise ValueError(f"Unknown noise level: {self.noise_level}")

    def build_covariance_matrix(self, sensor_keys: List[str]) -> np.ndarray:
        """
        Construct diagonal measurement noise covariance matrix R.
        R_jj = sigma_j^2
        """
        variances = [self.get_standard_deviation(k) ** 2 for k in sensor_keys]
        return np.diag(variances)

    def add_noise(self, observation_vector: np.ndarray, sensor_keys: List[str]) -> np.ndarray:
        """
        Add zero-mean Gaussian noise to a true observation vector: y_noisy = y_true + v, v ~ N(0, R).
        """
        stds = np.array([self.get_standard_deviation(k) for k in sensor_keys], dtype=float)
        noise = self.rng.normal(loc=0.0, scale=stds)
        y_noisy = observation_vector + noise
        # Physical lower bounds clipping (e.g. flow and TDS cannot be negative)
        return np.maximum(0.0, y_noisy)
