"""
Solution-Diffusion Transport and Film-Theory Concentration Polarization Module.

Implements the fundamental phenomenological equations for reverse osmosis:
1. Water Volumetric Flux:
       Jw = Aw * (ΔP - Δπ)
   where:
       ΔP = P_bulk_avg - P_permeate
       Δπ = π(C_m) - π(C_p)
2. Solute Mass Flux:
       Js = As * (C_m - C_p)
3. Concentration Polarization (Film Theory):
       C_m = C_p + (C_b - C_p) * exp(Jw / k)
4. Local Permeate Concentration:
       C_p = Js / Jw = (As * C_m) / (Jw + As)   [for Jw > 0]
"""

from typing import Tuple
import numpy as np


def calculate_water_flux(
    aw_m_pa_s: float,
    delta_p_pa: float,
    delta_pi_pa: float
) -> float:
    """
    Calculate volumetric water flux Jw [m/s] using solution-diffusion theory.

    Args:
        aw_m_pa_s: Water permeability coefficient [m/(Pa·s)].
        delta_p_pa: Transmembrane hydraulic pressure difference [Pa].
        delta_pi_pa: Transmembrane osmotic pressure difference [Pa] (π_m - π_p).

    Returns:
        Water flux Jw in m/s.
    """
    effective_driving_force = delta_p_pa - delta_pi_pa
    if effective_driving_force <= 0:
        return 0.0
    return aw_m_pa_s * effective_driving_force


def calculate_solute_flux(
    as_m_s: float,
    c_membrane_kg_m3: float,
    c_permeate_kg_m3: float
) -> float:
    """
    Calculate solute mass flux Js [kg/(m²·s)] using solution-diffusion theory.

    Args:
        as_m_s: Salt permeability coefficient [m/s].
        c_membrane_kg_m3: Solute concentration at the membrane surface [kg/m³].
        c_permeate_kg_m3: Solute concentration in permeate [kg/m³].

    Returns:
        Solute flux Js in kg/(m²·s).
    """
    delta_c = max(c_membrane_kg_m3 - c_permeate_kg_m3, 0.0)
    return as_m_s * delta_c


def calculate_membrane_surface_concentration(
    c_bulk_kg_m3: float,
    c_permeate_kg_m3: float,
    water_flux_m_s: float,
    mass_transfer_coeff_m_s: float
) -> float:
    """
    Calculate membrane surface concentration Cm [kg/m³] using film theory.

    Equation:
        Cm = Cp + (Cb - Cp) * exp(Jw / k)

    Args:
        c_bulk_kg_m3: Bulk solution concentration [kg/m³].
        c_permeate_kg_m3: Permeate concentration [kg/m³].
        water_flux_m_s: Water flux Jw [m/s].
        mass_transfer_coeff_m_s: Mass transfer coefficient k [m/s].

    Returns:
        Membrane surface concentration Cm in kg/m³.
    """
    if mass_transfer_coeff_m_s <= 0:
        raise ValueError(f"Mass transfer coefficient must be > 0, got {mass_transfer_coeff_m_s}")
    
    # Bound exponent to prevent numerical overflow in extreme scenarios
    exponent = min(water_flux_m_s / mass_transfer_coeff_m_s, 20.0)
    polarization_factor = np.exp(exponent)
    
    c_m = c_permeate_kg_m3 + (c_bulk_kg_m3 - c_permeate_kg_m3) * polarization_factor
    return max(float(c_m), float(c_bulk_kg_m3))


def calculate_permeate_concentration(
    c_membrane_kg_m3: float,
    water_flux_m_s: float,
    as_m_s: float
) -> float:
    """
    Calculate permeate concentration Cp [kg/m³] from solute mass balance across the active layer.

    From:
        Js = Jw * Cp = As * (Cm - Cp)
        => Cp * (Jw + As) = As * Cm
        => Cp = (As * Cm) / (Jw + As)

    Args:
        c_membrane_kg_m3: Membrane surface concentration [kg/m³].
        water_flux_m_s: Water flux Jw [m/s].
        as_m_s: Salt permeability coefficient [m/s].

    Returns:
        Permeate concentration Cp in kg/m³.
    """
    if water_flux_m_s <= 0:
        return float(c_membrane_kg_m3)
    
    cp = (as_m_s * c_membrane_kg_m3) / (water_flux_m_s + as_m_s)
    return float(cp)
