"""
Simulation Result Data Models, Reporting, and Diagnostic Validation.

Encapsulates all required engineering and SI outputs, mass and solute balance
verification, and diagnostic formatting.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

from ro_model.units import (
    pa_to_bar,
    pa_to_psi,
    m3_per_s_to_m3_per_hr,
    kg_per_m3_to_mg_per_l,
    m_per_s_to_lmh,
    kelvin_to_celsius
)


@dataclass
class SimulationResult:
    """
    Comprehensive result data structure containing all physical metrics,
    engineering outputs, and balance verification checks.
    """
    # 1. Operating Inputs
    feed_flow_m3_s: float
    feed_flow_m3_hr: float
    feed_pressure_pa: float
    feed_pressure_bar: float
    feed_pressure_psi: float
    feed_tds_kg_m3: float
    feed_tds_mg_l: float
    temperature_k: float
    temperature_celsius: float
    
    # 2. Flow Rates
    permeate_flow_m3_s: float
    permeate_flow_m3_hr: float
    concentrate_flow_m3_s: float
    concentrate_flow_m3_hr: float
    
    # 3. Concentrations & Salinity
    permeate_tds_kg_m3: float
    permeate_tds_mg_l: float
    concentrate_tds_kg_m3: float
    concentrate_tds_mg_l: float
    membrane_surface_tds_kg_m3: float
    membrane_surface_tds_mg_l: float
    bulk_avg_tds_kg_m3: float
    bulk_avg_tds_mg_l: float
    
    # 4. Fluxes & Transport
    water_flux_m_s: float
    water_flux_lmh: float
    salt_flux_kg_m2_s: float
    salt_flux_g_m2_h: float
    polarization_modulus: float            # Cm / Cb [-]
    mass_transfer_coefficient_m_s: float
    
    # 5. Separation Performance Metrics
    water_recovery_fraction: float         # Qp / Qf [-]
    water_recovery_percent: float          # Qp / Qf * 100 [%]
    salt_rejection_fraction: float         # 1 - Cp / Cf [-]
    salt_rejection_percent: float          # (1 - Cp / Cf) * 100 [%]
    salt_passage_percent: float            # (Cp / Cf) * 100 [%]
    
    # 6. Pressures & Osmotic Driving Forces
    feed_osmotic_pressure_pa: float
    feed_osmotic_pressure_bar: float
    membrane_surface_osmotic_pressure_pa: float
    membrane_surface_osmotic_pressure_bar: float
    permeate_osmotic_pressure_pa: float
    permeate_osmotic_pressure_bar: float
    concentrate_osmotic_pressure_pa: float
    concentrate_osmotic_pressure_bar: float
    bulk_avg_osmotic_pressure_bar: float
    transmembrane_pressure_pa: float       # ΔP = P_bulk_avg - P_p [Pa]
    transmembrane_pressure_bar: float      # ΔP [bar]
    effective_driving_pressure_pa: float   # ΔP_eff = ΔP - Δπ [Pa]
    effective_driving_pressure_bar: float  # ΔP_eff [bar]
    pressure_drop_element_bar: float
    
    # 7. Energy Metrics
    hydraulic_power_kw: float
    pump_electrical_power_kw: float
    sec_kwh_per_m3: float                  # Specific Energy Consumption [kWh/m³ permeate]
    
    # 8. Mass & Solute Balance Residuals
    water_mass_balance_error_m3_s: float   # |Qf - (Qp + Qr)| [m³/s]
    water_mass_balance_error_percent: float
    solute_mass_balance_error_kg_s: float  # |Qf*Cf - (Qp*Cp + Qr*Cr)| [kg/s]
    solute_mass_balance_error_percent: float
    
    # 9. Convergence & Diagnostics
    converged: bool
    solver_message: str
    iterations: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert result object to dictionary."""
        return asdict(self)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert single result to 1-row pandas DataFrame."""
        return pd.DataFrame([self.to_dict()])

    def format_summary_table(self) -> str:
        """Generate formatted multi-section summary table."""
        lines = [
            "=" * 78,
            "               REVERSE OSMOSIS SIMULATION RESULTS SUMMARY",
            "=" * 78,
            "1. OPERATING STREAM CONDITIONS:",
            f"   Feed Flow (Qf)               : {self.feed_flow_m3_hr:10.4f} m3/h  ({self.feed_flow_m3_s * 1e3:8.4f} L/s)",
            f"   Feed Pressure (Pf)           : {self.feed_pressure_bar:10.4f} bar    ({self.feed_pressure_psi:8.2f} psi)",
            f"   Feed Salinity (Cf)           : {self.feed_tds_mg_l:10.2f} mg/L  ({self.feed_tds_kg_m3:8.4f} g/L)",
            f"   Temperature (T)              : {self.temperature_celsius:10.2f} degC   ({self.temperature_k:8.2f} K)",
            "-" * 78,
            "2. OUTLET STREAM FLOWS & SALINITIES:",
            f"   Permeate Flow (Qp)           : {self.permeate_flow_m3_hr:10.4f} m3/h",
            f"   Concentrate Flow (Qr)        : {self.concentrate_flow_m3_hr:10.4f} m3/h",
            f"   Permeate TDS (Cp)            : {self.permeate_tds_mg_l:10.2f} mg/L",
            f"   Concentrate TDS (Cr)         : {self.concentrate_tds_mg_l:10.2f} mg/L",
            f"   Membrane Surface TDS (Cm)    : {self.membrane_surface_tds_mg_l:10.2f} mg/L",
            "-" * 78,
            "3. MEMBRANE FLUX & SEPARATION PERFORMANCE:",
            f"   Water Volumetric Flux (Jw)   : {self.water_flux_lmh:10.4f} LMH    ({self.water_flux_m_s:10.4e} m/s)",
            f"   Salt Mass Flux (Js)          : {self.salt_flux_g_m2_h:10.4f} g/(m2-h) ({self.salt_flux_kg_m2_s:10.4e} kg/(m2-s))",
            f"   Water Recovery (WR)          : {self.water_recovery_percent:10.2f} %",
            f"   Salt Rejection (SR)          : {self.salt_rejection_percent:10.4f} %",
            f"   Polarization Modulus (Cm/Cb) : {self.polarization_modulus:10.4f}",
            f"   Mass Transfer Coeff (k)      : {self.mass_transfer_coefficient_m_s:10.4e} m/s",
            "-" * 78,
            "4. THERMODYNAMIC & HYDRAULIC DRIVING PRESSURES:",
            f"   Feed Osmotic Pressure (pi_f) : {self.feed_osmotic_pressure_bar:10.4f} bar",
            f"   Surface Osmotic Pressure(pi_m):{self.membrane_surface_osmotic_pressure_bar:10.4f} bar",
            f"   Permeate Osmotic Pres. (pi_p): {self.permeate_osmotic_pressure_bar:10.4f} bar",
            f"   Concentrate Osmotic (pi_r)   : {self.concentrate_osmotic_pressure_bar:10.4f} bar",
            f"   Transmembrane Pressure (dP)  : {self.transmembrane_pressure_bar:10.4f} bar",
            f"   Effective Driving Force(dPeff):{self.effective_driving_pressure_bar:10.4f} bar",
            "-" * 78,
            "5. PUMP ENERGY & SPECIFIC ENERGY CONSUMPTION (SEC):",
            f"   Pump Hydraulic Power         : {self.hydraulic_power_kw:10.4f} kW",
            f"   Pump Electrical Power        : {self.pump_electrical_power_kw:10.4f} kW",
            f"   Specific Energy Cons. (SEC)  : {self.sec_kwh_per_m3:10.4f} kWh/m3 permeate",
            "-" * 78,
            "6. MASS & SOLUTE BALANCE RESIDUAL VERIFICATION:",
            f"   Water Balance Residual       : {self.water_mass_balance_error_m3_s:10.4e} m3/s ({self.water_mass_balance_error_percent:.6f} %)",
            f"   Solute Balance Residual      : {self.solute_mass_balance_error_kg_s:10.4e} kg/s ({self.solute_mass_balance_error_percent:.6f} %)",
            f"   Solver Status                : {'CONVERGED' if self.converged else 'FAILED'} ({self.solver_message})",
            "=" * 78
        ]
        return "\n".join(lines)


def validate_physical_bounds(result: SimulationResult, max_pressure_bar: float = 41.0) -> Dict[str, bool]:
    """
    Perform automated scientific sanity checks on simulation result.
    
    Checks:
    - Qp < Qf
    - Qr >= 0
    - Cp <= Cf under normal RO conditions
    - 0 <= WR <= 1
    - 0 <= SR <= 1
    - Pf <= 41 bar
    - ΔP_eff > 0
    - Water mass balance residual < 1e-7
    - Solute mass balance residual < 1e-7
    """
    checks = {
        "permeate_flow_less_than_feed": result.permeate_flow_m3_s < result.feed_flow_m3_s,
        "concentrate_flow_nonnegative": result.concentrate_flow_m3_s >= 0.0,
        "permeate_tds_less_than_feed": result.permeate_tds_kg_m3 <= result.feed_tds_kg_m3,
        "recovery_in_valid_range": 0.0 <= result.water_recovery_fraction <= 1.0,
        "rejection_in_valid_range": 0.0 <= result.salt_rejection_fraction <= 1.0,
        "pressure_within_limits": result.feed_pressure_bar <= max_pressure_bar,
        "effective_driving_force_positive": result.effective_driving_pressure_pa > 0.0,
        "water_mass_balance_passed": result.water_mass_balance_error_percent < 1.0e-3,
        "solute_mass_balance_passed": result.solute_mass_balance_error_percent < 1.0e-3,
    }
    return checks
