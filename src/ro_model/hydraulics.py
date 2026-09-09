"""
Hydraulics, Concentration Polarization Mass Transfer, and Pressure Drop Module.

Provides:
1. Mass transfer coefficient calculation:
   - MODE A: User-specified mass-transfer coefficient k [m/s].
   - MODE B: Correlation-based Sherwood calculation for spiral-wound spacer channels:
       Sh = a * Re^b * Sc^c
       k = Sh * D_AB / d_h
2. Feed-channel hydraulic pressure drop across the membrane element:
   - Baseline: ΔP_element = 0 (documented assumption).
   - Pluggable friction correlation: Darcy-Weisbach spacer-filled channel model.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class ChannelHydraulicProperties:
    """
    Feed-channel geometry and fluid physical properties for Mode B calculations.
    
    All values are documented assumptions when literature geometry is unavailable.
    """
    spacer_thickness_m: float = 0.76e-3    # Feed spacer thickness [m] (~30 mil)
    void_fraction: float = 0.85            # Channel porosity / void fraction [-]
    element_length_m: float = 1.016        # Standard 40-inch spiral wound element length [m]
    solute_diffusivity_m2_s: float = 1.5e-9 # Aqueous solute diffusivity [m²/s] (NaCl at 25°C)
    fluid_density_kg_m3: float = 997.0     # Fluid density [kg/m³]
    dynamic_viscosity_pa_s: float = 8.9e-4 # Dynamic viscosity [Pa·s] (water at 25°C)
    
    # Sherwood correlation coefficients: Sh = a * Re^b * Sc^c (e.g. Geraldes et al., Schock & Miquel)
    sh_a: float = 0.065
    sh_b: float = 0.875
    sh_c: float = 0.25
    
    # Friction factor correlation: f = f_a * Re^(-f_b)
    friction_a: float = 0.42
    friction_b: float = 0.15


def calculate_mass_transfer_coefficient(
    mode: str,
    k_specified: float = 5.0e-5,
    feed_flow_m3_s: float = 30.0 / 3600.0,
    membrane_area_m2: float = 37.0,
    membrane_diameter_m: float = 0.201,
    hydraulics: Optional[ChannelHydraulicProperties] = None,
) -> float:
    """
    Compute mass-transfer coefficient k [m/s] for concentration polarization.

    Args:
        mode: "mode_a" (user-specified) or "mode_b" (correlation-based).
        k_specified: Explicit mass transfer coefficient [m/s] for Mode A.
        feed_flow_m3_s: Feed flow rate [m³/s].
        membrane_area_m2: Membrane surface area [m²].
        membrane_diameter_m: Module outer diameter [m].
        hydraulics: Hydraulic properties for Mode B.

    Returns:
        Mass transfer coefficient k in m/s.
    """
    mode_clean = mode.lower().strip()
    
    if mode_clean in ("mode_a", "specified", "user_specified", "a"):
        if k_specified <= 0:
            raise ValueError(f"Specified mass transfer coefficient must be > 0, got {k_specified}")
        return float(k_specified)
    
    elif mode_clean in ("mode_b", "correlation", "sherwood", "b"):
        if hydraulics is None:
            hydraulics = ChannelHydraulicProperties()
            
        h_sp = hydraulics.spacer_thickness_m
        eps = hydraulics.void_fraction
        L_el = hydraulics.element_length_m
        D_AB = hydraulics.solute_diffusivity_m2_s
        rho = hydraulics.fluid_density_kg_m3
        mu = hydraulics.dynamic_viscosity_pa_s
        
        # Characteristic hydraulic diameter for spacer channel: d_h ≈ 4 * eps / (2/h_sp + (1-eps)*S_v) ≈ 2 * h_sp
        d_h = 2.0 * h_sp * eps
        
        # Effective channel cross-sectional flow area: A_flow = W_channel * h_sp * eps
        # For spiral wound envelope: W_channel ≈ Total membrane area / (2 * Element length)
        w_channel = membrane_area_m2 / (2.0 * L_el)
        a_flow = w_channel * h_sp * eps
        
        # Cross-flow superficial / interstitial velocity [m/s]
        u_crossflow = max(feed_flow_m3_s / a_flow, 1.0e-5)
        
        # Dimensionless numbers
        reynolds = (rho * u_crossflow * d_h) / mu
        schmidt = mu / (rho * D_AB)
        
        # Sherwood number
        sherwood = hydraulics.sh_a * (reynolds ** hydraulics.sh_b) * (schmidt ** hydraulics.sh_c)
        sherwood = max(sherwood, 1.0)
        
        # Mass transfer coefficient k [m/s]
        k_calc = (sherwood * D_AB) / d_h
        return float(k_calc)
    
    else:
        raise ValueError(
            f"Invalid CP mode '{mode}'. Choose 'mode_a' (user-specified) or 'mode_b' (correlation-based)."
        )


def calculate_feed_channel_pressure_drop_pa(
    feed_flow_m3_s: float,
    membrane_area_m2: float = 37.0,
    specified_dp_pa: float = 0.0,
    use_correlation: bool = False,
    hydraulics: Optional[ChannelHydraulicProperties] = None,
) -> float:
    """
    Calculate feed channel pressure drop ΔP_element [Pa] across the membrane element.

    Args:
        feed_flow_m3_s: Volumetric feed flow rate [m³/s].
        membrane_area_m2: Membrane surface area [m²].
        specified_dp_pa: Baseline specified pressure drop [Pa] (Default: 0.0 Pa).
        use_correlation: If True, uses Darcy-Weisbach spacer channel friction model.
        hydraulics: Geometric & fluid properties.

    Returns:
        Pressure drop across element in Pascals [Pa].
    """
    if not use_correlation:
        # Default baseline assumption: ΔP_element = specified_dp_pa (0.0 Pa)
        return max(float(specified_dp_pa), 0.0)
    
    if hydraulics is None:
        hydraulics = ChannelHydraulicProperties()
        
    h_sp = hydraulics.spacer_thickness_m
    eps = hydraulics.void_fraction
    L_el = hydraulics.element_length_m
    rho = hydraulics.fluid_density_kg_m3
    mu = hydraulics.dynamic_viscosity_pa_s
    
    d_h = 2.0 * h_sp * eps
    w_channel = membrane_area_m2 / (2.0 * L_el)
    a_flow = w_channel * h_sp * eps
    u = feed_flow_m3_s / a_flow
    
    reynolds = (rho * u * d_h) / mu
    friction_factor = hydraulics.friction_a * (reynolds ** (-hydraulics.friction_b))
    
    # Darcy-Weisbach pressure drop: ΔP = f * (L / d_h) * (rho * u^2 / 2)
    dp_pa = friction_factor * (L_el / d_h) * (0.5 * rho * (u ** 2))
    return float(dp_pa)
