"""
Osmotic Pressure Thermodynamics Module for Reverse Osmosis Modeling.

Calculates solution osmotic pressure based on van 't Hoff relation and
electrolyte solution thermodynamics.

Formulation:
    π = i * C_molar * R * T
where:
    π = Osmotic pressure [Pa]
    i = van 't Hoff dissociation factor [-] (default: 2.0 for 1:1 electrolyte like NaCl)
    C_molar = Molar concentration [mol/m³] = C_mass [kg/m³] / M_w [kg/mol]
    R = Universal gas constant [8.31446 J/(mol·K)]
    T = Absolute temperature [K]

Assumptions:
    - Default solute representation: NaCl-equivalent electrolyte (M_w = 58.44 g/mol).
    - Ideal dilute-to-moderate electrolyte behavior governed by van 't Hoff factor i = 2.0.
    - Zero concentration yields zero osmotic pressure.
"""

from typing import Union
import numpy as np

from ro_model.units import GAS_CONSTANT_R, conc_to_molarity, pa_to_bar, bar_to_pa


# Default Solute Properties (NaCl Equivalent)
DEFAULT_NACL_MW_KG_MOL: float = 0.058443  # Molar mass of NaCl [kg/mol] (58.443 g/mol)
DEFAULT_VANTHOFF_I: float = 2.0           # Complete dissociation into Na+ and Cl-


def calculate_osmotic_pressure_pa(
    concentration_kg_m3: Union[float, np.ndarray],
    temperature_k: float,
    vanthoff_i: float = DEFAULT_VANTHOFF_I,
    molar_mass_kg_mol: float = DEFAULT_NACL_MW_KG_MOL,
) -> Union[float, np.ndarray]:
    """
    Calculate osmotic pressure in Pascals [Pa] from mass concentration [kg/m³].

    Args:
        concentration_kg_m3: Solute mass concentration in kg/m³ (1 kg/m³ = 1000 mg/L = 1 g/L).
        temperature_k: Absolute temperature in Kelvin [K].
        vanthoff_i: van 't Hoff dissociation factor [-] (assumed 2.0 for NaCl).
        molar_mass_kg_mol: Solute molar mass in kg/mol (default: 0.05844 kg/mol for NaCl).

    Returns:
        Osmotic pressure in Pascals [Pa].

    Raises:
        ValueError: If concentration, temperature, or molar mass are negative.
    """
    if np.any(concentration_kg_m3 < 0):
        raise ValueError(f"Concentration must be non-negative, got {concentration_kg_m3}")
    if temperature_k <= 0:
        raise ValueError(f"Temperature must be strictly positive (Kelvin), got {temperature_k}")
    if vanthoff_i <= 0:
        raise ValueError(f"van 't Hoff factor must be positive, got {vanthoff_i}")
    if molar_mass_kg_mol <= 0:
        raise ValueError(f"Molar mass must be positive, got {molar_mass_kg_mol}")

    # Convert mass concentration [kg/m³] to molarity [mol/m³]
    c_molar = conc_to_molarity(concentration_kg_m3, molar_mass_kg_mol)
    
    # Thermodynamic van 't Hoff osmotic pressure [Pa]
    osmotic_pressure_pa = vanthoff_i * c_molar * GAS_CONSTANT_R * temperature_k
    return osmotic_pressure_pa


def calculate_osmotic_pressure_bar(
    concentration_mg_l: Union[float, np.ndarray],
    temperature_celsius: float,
    vanthoff_i: float = DEFAULT_VANTHOFF_I,
    molar_mass_g_mol: float = 58.443,
) -> Union[float, np.ndarray]:
    """
    Calculate osmotic pressure in bar from engineering units (mg/L, °C).

    Args:
        concentration_mg_l: Solute concentration in mg/L.
        temperature_celsius: Temperature in °C.
        vanthoff_i: van 't Hoff factor [-].
        molar_mass_g_mol: Molar mass in g/mol.

    Returns:
        Osmotic pressure in bar.
    """
    conc_kg_m3 = concentration_mg_l * 1.0e-3
    temp_k = temperature_celsius + 273.15
    molar_mass_kg_mol = molar_mass_g_mol * 1.0e-3
    
    pi_pa = calculate_osmotic_pressure_pa(
        concentration_kg_m3=conc_kg_m3,
        temperature_k=temp_k,
        vanthoff_i=vanthoff_i,
        molar_mass_kg_mol=molar_mass_kg_mol
    )
    return pa_to_bar(pi_pa)


def calculate_osmotic_pressure_derivative(
    temperature_k: float,
    vanthoff_i: float = DEFAULT_VANTHOFF_I,
    molar_mass_kg_mol: float = DEFAULT_NACL_MW_KG_MOL,
) -> float:
    """
    Calculate linear derivative d(π)/d(C) in Pa/(kg/m³).
    
    Returns:
        d(π)/d(C) = (i * R * T) / M_w in Pa/(kg/m³).
    """
    return (vanthoff_i * GAS_CONSTANT_R * temperature_k) / molar_mass_kg_mol
