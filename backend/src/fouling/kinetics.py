"""
Dynamic Fouling Kinetics and Element Rate Equations.

Implements the rate equation:
d R_f,i / dt = r_spec * J_v,i * (beta_i / beta_ref)^alpha * (C_m,i / C_f,0)^gamma
"""

from typing import Dict, List, Optional, Any, Union
import numpy as np

from fouling.model import FoulingParameters, ElementFoulingState


def compute_element_fouling_rate_per_second(
    flux_lmh: float,
    polarization_modulus: float,
    surface_tds_mg_l: float,
    parameters: FoulingParameters,
) -> float:
    """
    Compute instantaneous fouling resistance growth rate dR_f / dt [m^-1 / s].
    
    Parameters:
    - flux_lmh: Local element volumetric permeate flux [LMH]
    - polarization_modulus: Local concentration polarization modulus beta
    - surface_tds_mg_l: Local membrane wall solute concentration Cm [mg/L]
    - parameters: FoulingParameters holding r_spec, alpha, gamma, etc.
    
    Returns:
    - dRf_dt: [m^-1 / s]
    """
    # Convert flux from LMH (L/(m^2.h)) to SI (m/s)
    # 1 LMH = 1e-3 m^3 / (m^2 * 3600 s) = 1.0 / 3.6e6 m/s
    flux_m_s = flux_lmh / 3.6e6
    if flux_m_s <= 0:
        return 0.0

    # Dimensionless polarization factor
    beta_factor = (polarization_modulus / parameters.reference_polarization) ** parameters.polarization_exponent
    
    # Dimensionless concentration factor
    cf0 = max(parameters.reference_feed_tds_mg_l, 1.0)
    cm_factor = (surface_tds_mg_l / cf0) ** parameters.concentration_exponent

    # Rate in m^-1 / s
    drf_dt = parameters.specific_fouling_resistance * flux_m_s * beta_factor * cm_factor
    return float(drf_dt)


def compute_element_fouling_rate_per_hour(
    flux_lmh: float,
    polarization_modulus: float,
    surface_tds_mg_l: float,
    parameters: FoulingParameters,
) -> float:
    """
    Compute instantaneous fouling resistance growth rate dR_f / dt [m^-1 / hr].
    """
    rate_sec = compute_element_fouling_rate_per_second(
        flux_lmh=flux_lmh,
        polarization_modulus=polarization_modulus,
        surface_tds_mg_l=surface_tds_mg_l,
        parameters=parameters,
    )
    return float(rate_sec * 3600.0)


def update_element_state(
    current_state: ElementFoulingState,
    flux_lmh: float,
    polarization_modulus: float,
    feed_tds_mg_l: float,
    concentrate_tds_mg_l: float,
    local_recovery_pct: float,
    delta_t_hours: float,
    parameters: FoulingParameters,
) -> ElementFoulingState:
    """
    Integrate element fouling forward by delta_t_hours and update all internal states.
    """
    # Local wall salinity: Cm = C_bulk_avg * beta
    c_bulk_avg = (feed_tds_mg_l + concentrate_tds_mg_l) / 2.0
    c_wall = c_bulk_avg * polarization_modulus

    # Compute dRf/dt
    drf_dt_hr = compute_element_fouling_rate_per_hour(
        flux_lmh=flux_lmh,
        polarization_modulus=polarization_modulus,
        surface_tds_mg_l=c_wall,
        parameters=parameters,
    )

    # Forward Euler step for Rf
    new_rf = current_state.r_f_m_inv + drf_dt_hr * delta_t_hours
    new_r_total = parameters.r_m_m_inv + new_rf

    # Permeability updates
    new_aw = 1.0 / (parameters.r_m_m_inv * (new_r_total / parameters.r_m_m_inv)) # A_eff = A_clean * (R_m / R_total)
    perm_ratio = parameters.r_m_m_inv / new_r_total
    decline_pct = (1.0 - perm_ratio) * 100.0
    
    # Clean Aw is converted using calculate_clean_membrane_resistance logic
    from fouling.model import resistance_to_permeability
    aw_eff_actual = resistance_to_permeability(new_r_total, parameters.temperature_celsius)

    # Specific cumulative volume integration: delta_v = Jv * delta_t [L/m^2]
    delta_v_l_m2 = flux_lmh * delta_t_hours
    new_v_l_m2 = current_state.specific_cumulative_volume_l_m2 + delta_v_l_m2
    new_v_m3_m2 = new_v_l_m2 * 1.0e-3

    return ElementFoulingState(
        stage_index=current_state.stage_index,
        element_index=current_state.element_index,
        global_element_id=current_state.global_element_id,
        r_f_m_inv=new_rf,
        r_total_m_inv=new_r_total,
        aw_eff_m_pa_s=aw_eff_actual,
        permeability_ratio=perm_ratio,
        permeability_decline_pct=decline_pct,
        specific_cumulative_volume_m3_m2=new_v_m3_m2,
        specific_cumulative_volume_l_m2=new_v_l_m2,
        local_flux_lmh=flux_lmh,
        local_polarization_modulus=polarization_modulus,
        local_feed_tds_mg_l=feed_tds_mg_l,
        local_concentrate_tds_mg_l=concentrate_tds_mg_l,
        local_surface_tds_mg_l=c_wall,
        local_recovery_pct=local_recovery_pct,
    )
