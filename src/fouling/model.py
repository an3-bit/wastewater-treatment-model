"""
Core Data Models and Physical State Representations for Dynamic Membrane Fouling.

Defines:
1. FoulingParameters: Physical, transport, and kinetic rate constants.
2. ElementFoulingState: Time-dependent state of an individual membrane element.
3. SystemFoulingState: Train-level aggregation of all 15 membrane element states.
4. DynamicSimulationResult: Complete time-series history of a dynamic RO simulation.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import numpy as np


def calculate_water_viscosity(temperature_celsius: float = 25.0) -> float:
    """
    Calculate dynamic viscosity of pure water as a function of temperature.
    Uses the standard empirical correlation: mu(T) [Pa.s].
    At 25 C: mu = 8.904e-4 Pa.s.
    """
    T = temperature_celsius
    # Vogel-Fulcher-Tammann or standard empirical correlation for water viscosity
    # mu = A * 10^(B / (T - C)) with T in Kelvin
    # Simplified standard correlation:
    mu = 2.414e-5 * (10.0 ** (247.8 / (temperature_celsius + 273.15 - 140.0)))
    return float(mu)


AW_AUTHORITATIVE_M_PA_S: float = 9.446312125982804e-12
RM_AUTHORITATIVE_M_INV: float = 1.1888677444880217e+14
R_SPEC_AUTHORITATIVE: float = 1.954988085694205e+13


def calculate_clean_membrane_resistance(
    aw_m_pa_s: float = AW_AUTHORITATIVE_M_PA_S,
    temperature_celsius: float = 25.0,
) -> float:
    """
    Calculate intrinsic clean membrane resistance R_m [m^-1] from Aw and viscosity:
    R_m = 1 / (mu * Aw).
    """
    mu = calculate_water_viscosity(temperature_celsius)
    if aw_m_pa_s <= 0:
        raise ValueError("Aw must be strictly positive to calculate resistance.")
    return float(1.0 / (mu * aw_m_pa_s))


def resistance_to_permeability(
    r_total_m_inv: float,
    temperature_celsius: float = 25.0,
) -> float:
    """
    Convert total hydraulic resistance R_total [m^-1] to effective permeability Aw [m/(Pa.s)].
    Aw = 1 / (mu * R_total).
    """
    mu = calculate_water_viscosity(temperature_celsius)
    if r_total_m_inv <= 0:
        raise ValueError("Resistance must be strictly positive.")
    return float(1.0 / (mu * r_total_m_inv))


@dataclass
class FoulingParameters:
    """
    Physical parameters governing the dynamic fouling kinetics under Model Version 2.0.
    """
    clean_aw_m_pa_s: float = AW_AUTHORITATIVE_M_PA_S          # Clean water permeability [m/(Pa.s)] (9.4463e-7 m/(bar.s))
    clean_as_m_s: float = 1.7827e-8                           # Clean salt permeability [m/s]
    r_m_m_inv: float = RM_AUTHORITATIVE_M_INV                 # Clean membrane intrinsic resistance [m^-1]
    specific_fouling_resistance: float = R_SPEC_AUTHORITATIVE # r_spec [m^-1 / (m^3/m^2)]
    polarization_exponent: float = 1.0                        # alpha: exponent for concentration polarization beta
    concentration_exponent: float = 1.0                       # gamma: exponent for local wall TDS ratio (Cm / Cf0)
    reference_polarization: float = 1.30                      # beta_ref: normalizing baseline polarization
    reference_feed_tds_mg_l: float = 2041.0                   # Cf0: reference feed salinity [mg/L]
    cleaning_efficiency: float = 0.90                         # eta_clean: fraction of Rf removed during cleaning
    temperature_celsius: float = 25.0                         # Operating temperature [C]

    @classmethod
    def create_default(
        cls,
        r_spec: float = R_SPEC_AUTHORITATIVE,
        temperature_celsius: float = 25.0,
        cleaning_efficiency: float = 0.90,
    ) -> "FoulingParameters":
        """Instantiate default parameters calibrated at 25 C."""
        r_m = calculate_clean_membrane_resistance(AW_AUTHORITATIVE_M_PA_S, temperature_celsius)
        return cls(
            clean_aw_m_pa_s=AW_AUTHORITATIVE_M_PA_S,
            clean_as_m_s=1.7827e-8,
            r_m_m_inv=r_m,
            specific_fouling_resistance=r_spec,
            polarization_exponent=1.0,
            concentration_exponent=1.0,
            reference_polarization=1.30,
            reference_feed_tds_mg_l=2041.0,
            cleaning_efficiency=cleaning_efficiency,
            temperature_celsius=temperature_celsius,
        )


@dataclass
class ElementFoulingState:
    """
    Dynamic physical state of an individual membrane element.
    """
    stage_index: int                                          # 1 or 2
    element_index: int                                        # 1 to 3 within vessel
    global_element_id: str                                    # e.g. "Stage1_Elem1", "Stage2_Elem3"
    r_f_m_inv: float = 0.0                                    # Dynamic fouling resistance [m^-1]
    r_total_m_inv: float = RM_AUTHORITATIVE_M_INV             # Total resistance [m^-1] = R_m + R_f
    aw_eff_m_pa_s: float = AW_AUTHORITATIVE_M_PA_S           # Effective permeability [m/(Pa.s)]
    permeability_ratio: float = 1.0               # A_eff / A_clean = R_m / (R_m + R_f)
    permeability_decline_pct: float = 0.0         # (1 - A_eff / A_clean) * 100%
    specific_cumulative_volume_m3_m2: float = 0.0 # Cumulative permeate per unit area [m^3/m^2]
    specific_cumulative_volume_l_m2: float = 0.0  # Cumulative permeate per unit area [L/m^2]
    local_flux_lmh: float = 0.0                   # Instantaneous trans-membrane flux [LMH]
    local_polarization_modulus: float = 1.0       # Instantaneous polarization beta
    local_feed_tds_mg_l: float = 2041.0           # Local inlet salinity [mg/L]
    local_concentrate_tds_mg_l: float = 2041.0    # Local outlet salinity [mg/L]
    local_surface_tds_mg_l: float = 2041.0        # Local membrane wall salinity Cm [mg/L]
    local_recovery_pct: float = 0.0               # Single-element water recovery [%]


@dataclass
class SystemFoulingState:
    """
    Consolidated state of all 15 membrane elements across the 2-stage train at time t.
    """
    time_hours: float
    element_states: List[ElementFoulingState] = field(default_factory=list)
    average_permeability_ratio: float = 1.0
    average_permeability_decline_pct: float = 0.0
    max_element_permeability_decline_pct: float = 0.0
    total_cumulative_permeate_m3: float = 0.0
    total_cumulative_electricity_kwh: float = 0.0
    instantaneous_recovery_pct: float = 0.0
    instantaneous_sec_kwh_m3: float = 0.0
    instantaneous_permeate_flow_m3_h: float = 0.0
    instantaneous_permeate_tds_mg_l: float = 0.0
    instantaneous_concentrate_flow_m3_h: float = 0.0
    instantaneous_concentrate_tds_mg_l: float = 0.0
    stage1_feed_pressure_bar: float = 13.0
    stage2_feed_pressure_bar: float = 18.0
    water_mass_balance_error_pct: float = 0.0
    solute_mass_balance_error_pct: float = 0.0
    converged: bool = True


@dataclass
class DynamicSimulationResult:
    """
    Complete trajectory ledger for a dynamic simulation run over a time horizon.
    """
    strategy_name: str
    operating_mode: str                           # "MODE_A_FIXED_PRESSURE" or "MODE_B_MAINTAIN_PRODUCTION"
    time_horizon_hours: float
    time_step_hours: float
    parameters: FoulingParameters
    timestamps_hours: List[float] = field(default_factory=list)
    states: List[SystemFoulingState] = field(default_factory=list)
    
    # Summary Metrics over Full Horizon
    initial_recovery_pct: float = 0.0
    final_recovery_pct: float = 0.0
    initial_sec_kwh_m3: float = 0.0
    final_sec_kwh_m3: float = 0.0
    initial_avg_flux_lmh: float = 0.0
    final_avg_flux_lmh: float = 0.0
    final_permeability_decline_pct: float = 0.0
    total_cumulative_permeate_m3: float = 0.0
    total_cumulative_electricity_kwh: float = 0.0
    dynamic_average_sec_kwh_m3: float = 0.0
    specific_cumulative_volume_l_m2: float = 0.0
    time_to_5pct_decline_hours: Optional[float] = None
    time_to_10pct_decline_hours: Optional[float] = None
    time_to_15pct_decline_hours: Optional[float] = None
    max_dynamic_water_error_pct: float = 0.0
    max_dynamic_solute_error_pct: float = 0.0
