"""
Unit Conversion and Physical Constants Module for Reverse Osmosis Modeling.

Internal SI Unit Standard:
- Pressure: Pascal [Pa]
- Volumetric Flow Rate: Cubic meters per second [m³/s]
- Concentration: Kilograms per cubic meter [kg/m³] (equivalent to g/L)
- Molar Concentration: Moles per cubic meter [mol/m³]
- Mass Flux: Kilograms per square meter per second [kg/(m²·s)]
- Volumetric Flux: Meters per second [m/s]
- Permeability (Water): Meters per Pascal second [m/(Pa·s)]
- Permeability (Salt): Meters per second [m/s]
- Temperature: Kelvin [K]
- Power: Watts [W]
- Energy Consumption: Joules per cubic meter [J/m³]

Engineering / Display Units:
- Pressure: bar, psi, kPa
- Volumetric Flow Rate: m³/h, m³/day, L/h, L/min
- Concentration: mg/L, g/L, ppm (approx wt/vol)
- Volumetric Flux: LMH (L/(m²·h)), GFD (gal/(ft²·day))
- Permeability (Water): m/(bar·s), LMH/bar
- Temperature: °C
- Power: kW
- Specific Energy Consumption: kWh/m³
"""

from typing import Union

# Universal Physical Constants
GAS_CONSTANT_R: float = 8.31446261815324  # Ideal gas constant [J/(mol·K)]
STANDARD_ATM_PA: float = 101325.0         # Standard atmospheric pressure [Pa]
BAR_TO_PA: float = 1.0e5                  # 1 bar in Pascals
PSI_TO_PA: float = 6894.757293168361      # 1 psi in Pascals
M3_PER_SEC_TO_M3_PER_HR: float = 3600.0   # 1 m³/s to m³/h
M3_PER_SEC_TO_M3_PER_DAY: float = 86400.0 # 1 m³/s to m³/day
LMH_TO_M_PER_S: float = 1.0 / (3.6e6)     # 1 LMH = 10^-3 m³ / (3600 s · m²) = 1/(3.6e6) m/s
J_PER_M3_TO_KWH_PER_M3: float = 1.0 / 3.6e6 # 1 J/m³ = 1 W·s/m³ = (1/3600 h) * (1/1000 kW) = 1/(3.6e6) kWh/m³


# ==============================================================================
# PRESSURE CONVERSIONS
# ==============================================================================

def bar_to_pa(pressure_bar: float) -> float:
    """Convert pressure from bar to Pascals [Pa]."""
    return pressure_bar * BAR_TO_PA


def pa_to_bar(pressure_pa: float) -> float:
    """Convert pressure from Pascals [Pa] to bar."""
    return pressure_pa / BAR_TO_PA


def psi_to_pa(pressure_psi: float) -> float:
    """Convert pressure from pounds per square inch [psi] to Pascals [Pa]."""
    return pressure_psi * PSI_TO_PA


def pa_to_psi(pressure_pa: float) -> float:
    """Convert pressure from Pascals [Pa] to pounds per square inch [psi]."""
    return pressure_pa / PSI_TO_PA


def psi_to_bar(pressure_psi: float) -> float:
    """Convert pressure from psi to bar."""
    return pa_to_bar(psi_to_pa(pressure_psi))


def bar_to_psi(pressure_bar: float) -> float:
    """Convert pressure from bar to psi."""
    return pa_to_psi(bar_to_pa(pressure_bar))


# ==============================================================================
# FLOW RATE CONVERSIONS
# ==============================================================================

def m3_per_hr_to_m3_per_s(flow_m3_hr: float) -> float:
    """Convert volumetric flow rate from m³/h to m³/s."""
    return flow_m3_hr / M3_PER_SEC_TO_M3_PER_HR


def m3_per_s_to_m3_per_hr(flow_m3_s: float) -> float:
    """Convert volumetric flow rate from m³/s to m³/h."""
    return flow_m3_s * M3_PER_SEC_TO_M3_PER_HR


def m3_per_day_to_m3_per_s(flow_m3_day: float) -> float:
    """Convert volumetric flow rate from m³/day to m³/s."""
    return flow_m3_day / M3_PER_SEC_TO_M3_PER_DAY


def m3_per_s_to_m3_per_day(flow_m3_s: float) -> float:
    """Convert volumetric flow rate from m³/s to m³/day."""
    return flow_m3_s * M3_PER_SEC_TO_M3_PER_DAY


def l_per_hr_to_m3_per_s(flow_l_hr: float) -> float:
    """Convert volumetric flow rate from L/h to m³/s."""
    return (flow_l_hr * 1.0e-3) / 3600.0


def m3_per_s_to_l_per_hr(flow_m3_s: float) -> float:
    """Convert volumetric flow rate from m³/s to L/h."""
    return flow_m3_s * 3.6e6


# ==============================================================================
# CONCENTRATION & MOLARITY CONVERSIONS
# ==============================================================================

def mg_per_l_to_kg_per_m3(conc_mg_l: float) -> float:
    """
    Convert mass concentration from mg/L to internal SI kg/m³.
    Note: 1 mg/L = 10^-3 g / 10^-3 m³ = 1 g/m³ = 10^-3 kg/m³ = 1e-3 kg/m³.
    1 kg/m³ = 1000 mg/L = 1 g/L.
    """
    return conc_mg_l * 1.0e-3


def kg_per_m3_to_mg_per_l(conc_kg_m3: float) -> float:
    """Convert mass concentration from kg/m³ to mg/L."""
    return conc_kg_m3 * 1.0e3


def conc_to_molarity(conc_kg_m3: float, molar_mass_kg_mol: float) -> float:
    """
    Convert mass concentration [kg/m³] to molar concentration [mol/m³].
    
    Args:
        conc_kg_m3: Concentration in kg/m³ (equivalent to g/L).
        molar_mass_kg_mol: Solute molar mass in kg/mol (e.g. 0.05844 kg/mol for NaCl).
        
    Returns:
        Molar concentration in mol/m³.
    """
    if molar_mass_kg_mol <= 0:
        raise ValueError(f"Molar mass must be positive, got {molar_mass_kg_mol}")
    return conc_kg_m3 / molar_mass_kg_mol


def molarity_to_conc(molar_conc_mol_m3: float, molar_mass_kg_mol: float) -> float:
    """Convert molar concentration [mol/m³] to mass concentration [kg/m³]."""
    return molar_conc_mol_m3 * molar_mass_kg_mol


# ==============================================================================
# FLUX CONVERSIONS
# ==============================================================================

def m_per_s_to_lmh(flux_m_s: float) -> float:
    """
    Convert volumetric water flux from m/s to LMH (L/(m²·h)).
    1 m/s = 1000 L / (1 m² · (1/3600 h)) = 3.6e6 LMH.
    """
    return flux_m_s * 3.6e6


def lmh_to_m_per_s(flux_lmh: float) -> float:
    """Convert volumetric water flux from LMH (L/(m²·h)) to m/s."""
    return flux_lmh * LMH_TO_M_PER_S


# ==============================================================================
# WATER PERMEABILITY (Aw) CONVERSIONS
# ==============================================================================

def aw_bar_to_pa(aw_m_bar_s: float) -> float:
    """
    Convert water permeability coefficient Aw from m/(bar·s) to m/(Pa·s).
    1 bar = 10^5 Pa -> Aw [m/(Pa·s)] = Aw [m/(bar·s)] / 10^5.
    """
    return aw_m_bar_s / BAR_TO_PA


def aw_pa_to_bar(aw_m_pa_s: float) -> float:
    """Convert water permeability coefficient Aw from m/(Pa·s) to m/(bar·s)."""
    return aw_m_pa_s * BAR_TO_PA


def aw_to_lmh_bar(aw_m_bar_s: float) -> float:
    """Convert water permeability coefficient Aw from m/(bar·s) to LMH/bar."""
    return aw_m_bar_s * 3.6e6


# ==============================================================================
# TEMPERATURE CONVERSIONS
# ==============================================================================

def celsius_to_kelvin(temp_celsius: float) -> float:
    """Convert temperature from Celsius [°C] to Kelvin [K]."""
    return temp_celsius + 273.15


def kelvin_to_celsius(temp_kelvin: float) -> float:
    """Convert temperature from Kelvin [K] to Celsius [°C]."""
    return temp_kelvin - 273.15


# ==============================================================================
# POWER & ENERGY CONVERSIONS
# ==============================================================================

def watts_to_kw(power_w: float) -> float:
    """Convert power from Watts [W] to kilowatts [kW]."""
    return power_w * 1.0e-3


def kw_to_watts(power_kw: float) -> float:
    """Convert power from kilowatts [kW] to Watts [W]."""
    return power_kw * 1.0e3


def specific_energy_j_to_kwh_per_m3(sec_j_m3: float) -> float:
    """
    Convert Specific Energy Consumption from J/m³ to kWh/m³.
    1 J/m³ = 1 W·s/m³ = (1/3600 h) * (1/1000 kW) = 1/(3.6e6) kWh/m³.
    """
    return sec_j_m3 * J_PER_M3_TO_KWH_PER_M3
