"""
Numerical Solver and Simulation API for Reverse Osmosis Mechanistic Modeling.

Solves the coupled nonlinear algebraic system of equations describing:
1. Solution-diffusion water transport: Jw = Aw * (ΔP - Δπ)
2. Solution-diffusion solute transport: Js = As * (Cm - Cp)
3. Film-theory concentration polarization: Cm = Cp + (Cb - Cp) * exp(Jw / k)
4. Overall fluid and solute mass conservation balances.

Uses scipy.optimize.least_squares / scipy.optimize.root with physical box bounds
and strict residual verification.
"""

from typing import Optional, Dict, Any, Tuple, Union
import numpy as np
from scipy.optimize import least_squares, root

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    psi_to_pa,
    pa_to_psi,
    m3_per_hr_to_m3_per_s,
    m3_per_s_to_m3_per_hr,
    mg_per_l_to_kg_per_m3,
    kg_per_m3_to_mg_per_l,
    m_per_s_to_lmh,
    celsius_to_kelvin,
    kelvin_to_celsius
)
from ro_model.osmotic import calculate_osmotic_pressure_pa
from ro_model.hydraulics import (
    calculate_mass_transfer_coefficient,
    calculate_feed_channel_pressure_drop_pa,
    ChannelHydraulicProperties
)
from ro_model.transport import (
    calculate_water_flux,
    calculate_solute_flux,
    calculate_membrane_surface_concentration,
    calculate_permeate_concentration
)
from ro_model.energy import calculate_pump_energy
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig,
    MembraneElement
)
from ro_model.validation import SimulationResult, validate_physical_bounds


def _residual_system_2var(
    vars_vec: np.ndarray,
    element_props: MembraneElementProperties,
    conditions: OperatingConditions,
    config: SimulationConfig,
    k_mass_transfer: float,
    delta_p_element: float
) -> np.ndarray:
    """
    Compute normalized residuals F(y) = 0 for the 2-variable state vector y = [Jw/1e-5, Cm/scale_c].
    
    Variables:
        vars_vec[0]: y_jw = Jw / 1.0e-5  (dimensionless ~ 1.0)
        vars_vec[1]: y_cm = Cm / scale_c (dimensionless ~ 1.0)
    """
    jw = max(vars_vec[0] * 1.0e-5, 0.0)
    
    q_f = conditions.feed_flow_m3_s
    c_f = conditions.feed_concentration_kg_m3
    p_f = conditions.feed_pressure_pa
    p_p = conditions.permeate_pressure_pa
    temp_k = conditions.temperature_k
    
    a_m = element_props.membrane_area_m2
    a_w = element_props.Aw_m_pa_s
    a_s = element_props.As_m_s
    
    i_factor = config.vanthoff_factor
    mw_solute = config.solute_molar_mass_kg_mol
    scale_c = max(c_f, 1.0e-4)
    
    cm = max(vars_vec[1] * scale_c, 0.0)
    
    # Active layer solute balance: Cp = As * Cm / (Jw + As)
    cp = (a_s * cm) / (jw + a_s)
    
    # Fluid and solute mass balances
    q_p = jw * a_m
    q_r = max(q_f - q_p, 1.0e-12)
    cr = max((q_f * c_f - q_p * cp) / q_r, 0.0)
    c_b = 0.5 * (c_f + cr)
    
    # 1. Hydraulic & Osmotic Pressures
    p_bulk_avg = p_f - 0.5 * delta_p_element
    delta_p = max(p_bulk_avg - p_p, 0.0)
    
    pi_m = calculate_osmotic_pressure_pa(cm, temp_k, i_factor, mw_solute)
    pi_p = calculate_osmotic_pressure_pa(cp, temp_k, i_factor, mw_solute)
    delta_pi = pi_m - pi_p
    
    # Target values from physical transport equations
    jw_target = a_w * max(delta_p - delta_pi, 0.0)
    
    polarization_exp = np.exp(min(jw / k_mass_transfer, 20.0))
    cm_target = cp + (c_b - cp) * polarization_exp
    
    # Normalized residuals
    res_jw = (jw - jw_target) / 1.0e-5
    res_cm = (cm - cm_target) / scale_c
    
    return np.array([res_jw, res_cm])


def solve_membrane_element(
    element: MembraneElement,
    conditions: OperatingConditions,
    config: Optional[SimulationConfig] = None
) -> SimulationResult:
    """
    Numerically solve the coupled transport, thermodynamics, and mass balance
    equations for a single RO membrane element.

    Args:
        element: MembraneElement instance containing geometric & transport properties.
        conditions: Operating conditions (Qf, Cf, Pf, T, Pp).
        config: Optional simulation configuration and assumptions.

    Returns:
        SimulationResult instance populated with full engineering and SI results.

    Raises:
        ValueError: If input bounds are violated (e.g. pressure exceeds 41 bar).
        RuntimeError: If nonlinear solver fails to converge.
    """
    props = element.properties
    cfg = config or element.config
    
    # Physical sanity checks on inputs
    if conditions.feed_pressure_pa > props.max_operating_pressure_pa:
        raise ValueError(
            f"Feed pressure {pa_to_bar(conditions.feed_pressure_pa):.2f} bar exceeds "
            f"maximum allowable limit {pa_to_bar(props.max_operating_pressure_pa):.2f} bar."
        )
    if conditions.feed_flow_m3_s <= 0:
        raise ValueError(f"Feed flow must be strictly positive, got {conditions.feed_flow_m3_s} m³/s")
    if conditions.feed_concentration_kg_m3 < 0:
        raise ValueError(f"Feed concentration cannot be negative, got {conditions.feed_concentration_kg_m3} kg/m³")

    # 1. Compute hydraulics: mass transfer coefficient k and pressure drop ΔP
    k_mt = calculate_mass_transfer_coefficient(
        mode=cfg.cp_mode,
        k_specified=cfg.mass_transfer_coefficient,
        feed_flow_m3_s=conditions.feed_flow_m3_s,
        membrane_area_m2=props.membrane_area_m2,
        membrane_diameter_m=props.membrane_diameter_m
    )
    
    delta_p_elem = calculate_feed_channel_pressure_drop_pa(
        feed_flow_m3_s=conditions.feed_flow_m3_s,
        membrane_area_m2=props.membrane_area_m2,
        specified_dp_pa=cfg.pressure_drop_pa,
        use_correlation=False
    )
    
    # 2. Estimate initial guess
    temp_k = conditions.temperature_k
    q_f = conditions.feed_flow_m3_s
    c_f = conditions.feed_concentration_kg_m3
    p_f = conditions.feed_pressure_pa
    p_p = conditions.permeate_pressure_pa
    a_m = props.membrane_area_m2
    a_w = props.Aw_m_pa_s
    a_s = props.As_m_s
    
    pi_f = calculate_osmotic_pressure_pa(c_f, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    delta_p_approx = max((p_f - 0.5 * delta_p_elem) - p_p, 0.0)
    
    if delta_p_approx <= pi_f:
        raise ValueError(
            f"Applied pressure ({pa_to_bar(delta_p_approx):.2f} bar) is less than feed osmotic pressure "
            f"({pa_to_bar(pi_f):.2f} bar). Reverse osmosis cannot proceed (effective driving force <= 0)."
        )
        
    scale_c = max(c_f, 1.0e-4)
    jw_max = (q_f / a_m) * 0.999
    jw_guess = np.clip(a_w * (delta_p_approx - pi_f), 1.0e-7, jw_max * 0.5)
    cm_guess = max(c_f * 1.05, 1.0e-4)
    
    y0 = np.array([jw_guess / 1.0e-5, cm_guess / scale_c])
    lb = np.array([0.0, 0.0])
    ub = np.array([(jw_max / 1.0e-5), 200.0])
    
    # 4. Numerical solution via Scipy least_squares
    res = least_squares(
        _residual_system_2var,
        x0=np.clip(y0, lb + 1e-5, ub - 1e-5),
        bounds=(lb, ub),
        args=(props, conditions, cfg, k_mt, delta_p_elem),
        ftol=cfg.solver_tolerance,
        xtol=cfg.solver_tolerance,
        gtol=cfg.solver_tolerance,
        max_nfev=cfg.max_solver_iterations
    )
    
    if not res.success:
        raise RuntimeError(f"RO Model numerical solver failed to converge: {res.message}")
        
    jw_sol = res.x[0] * 1.0e-5
    cm_sol = res.x[1] * scale_c
    cp_sol = (a_s * cm_sol) / (jw_sol + a_s)
    q_p_sol = jw_sol * a_m
    q_r_sol = max(q_f - q_p_sol, 0.0)
    cr_sol = max((q_f * c_f - q_p_sol * cp_sol) / max(q_r_sol, 1e-12), 0.0)
    
    # 5. Compute derived stream quantities
    q_p_sol = jw_sol * a_m
    q_r_sol = max(q_f - q_p_sol, 0.0)
    c_b_sol = 0.5 * (c_f + cr_sol)
    
    pi_feed = calculate_osmotic_pressure_pa(c_f, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    pi_m_sol = calculate_osmotic_pressure_pa(cm_sol, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    pi_p_sol = calculate_osmotic_pressure_pa(cp_sol, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    pi_r_sol = calculate_osmotic_pressure_pa(cr_sol, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    pi_b_sol = calculate_osmotic_pressure_pa(c_b_sol, temp_k, cfg.vanthoff_factor, cfg.solute_molar_mass_kg_mol)
    
    p_bulk_avg = p_f - 0.5 * delta_p_elem
    delta_p_trans = p_bulk_avg - p_p
    delta_pi_eff = pi_m_sol - pi_p_sol
    delta_p_eff = delta_p_trans - delta_pi_eff
    
    js_sol = calculate_solute_flux(a_s, cm_sol, cp_sol)
    
    # Separation metrics
    wr_fraction = q_p_sol / q_f
    sr_fraction = 1.0 - (cp_sol / c_f) if c_f > 0 else 1.0
    polarization_mod = cm_sol / c_b_sol if c_b_sol > 0 else 1.0
    
    # Mass balance checks
    water_mb_error_m3_s = abs(q_f - (q_p_sol + q_r_sol))
    water_mb_error_pct = (water_mb_error_m3_s / q_f) * 100.0 if q_f > 0 else 0.0
    
    solute_mb_error_kg_s = abs((q_f * c_f) - (q_p_sol * cp_sol + q_r_sol * cr_sol))
    solute_mb_error_pct = (solute_mb_error_kg_s / (q_f * c_f)) * 100.0 if (q_f * c_f) > 0 else 0.0
    
    # Energy metrics
    pump_energy = calculate_pump_energy(
        feed_flow_m3_s=q_f,
        permeate_flow_m3_s=q_p_sol,
        feed_pressure_pa=p_f,
        inlet_feed_pressure_pa=cfg.inlet_pressure_pa,
        pump_efficiency=cfg.pump_efficiency
    )
    
    return SimulationResult(
        feed_flow_m3_s=q_f,
        feed_flow_m3_hr=m3_per_s_to_m3_per_hr(q_f),
        feed_pressure_pa=p_f,
        feed_pressure_bar=pa_to_bar(p_f),
        feed_pressure_psi=pa_to_psi(p_f),
        feed_tds_kg_m3=c_f,
        feed_tds_mg_l=kg_per_m3_to_mg_per_l(c_f),
        temperature_k=temp_k,
        temperature_celsius=kelvin_to_celsius(temp_k),
        
        permeate_flow_m3_s=q_p_sol,
        permeate_flow_m3_hr=m3_per_s_to_m3_per_hr(q_p_sol),
        concentrate_flow_m3_s=q_r_sol,
        concentrate_flow_m3_hr=m3_per_s_to_m3_per_hr(q_r_sol),
        
        permeate_tds_kg_m3=cp_sol,
        permeate_tds_mg_l=kg_per_m3_to_mg_per_l(cp_sol),
        concentrate_tds_kg_m3=cr_sol,
        concentrate_tds_mg_l=kg_per_m3_to_mg_per_l(cr_sol),
        membrane_surface_tds_kg_m3=cm_sol,
        membrane_surface_tds_mg_l=kg_per_m3_to_mg_per_l(cm_sol),
        bulk_avg_tds_kg_m3=c_b_sol,
        bulk_avg_tds_mg_l=kg_per_m3_to_mg_per_l(c_b_sol),
        
        water_flux_m_s=jw_sol,
        water_flux_lmh=m_per_s_to_lmh(jw_sol),
        salt_flux_kg_m2_s=js_sol,
        salt_flux_g_m2_h=js_sol * 1.0e3 * 3600.0,
        polarization_modulus=polarization_mod,
        mass_transfer_coefficient_m_s=k_mt,
        
        water_recovery_fraction=wr_fraction,
        water_recovery_percent=wr_fraction * 100.0,
        salt_rejection_fraction=sr_fraction,
        salt_rejection_percent=sr_fraction * 100.0,
        salt_passage_percent=(1.0 - sr_fraction) * 100.0,
        
        feed_osmotic_pressure_pa=pi_feed,
        feed_osmotic_pressure_bar=pa_to_bar(pi_feed),
        membrane_surface_osmotic_pressure_pa=pi_m_sol,
        membrane_surface_osmotic_pressure_bar=pa_to_bar(pi_m_sol),
        permeate_osmotic_pressure_pa=pi_p_sol,
        permeate_osmotic_pressure_bar=pa_to_bar(pi_p_sol),
        concentrate_osmotic_pressure_pa=pi_r_sol,
        concentrate_osmotic_pressure_bar=pa_to_bar(pi_r_sol),
        bulk_avg_osmotic_pressure_bar=pa_to_bar(pi_b_sol),
        transmembrane_pressure_pa=delta_p_trans,
        transmembrane_pressure_bar=pa_to_bar(delta_p_trans),
        effective_driving_pressure_pa=delta_p_eff,
        effective_driving_pressure_bar=pa_to_bar(delta_p_eff),
        pressure_drop_element_bar=pa_to_bar(delta_p_elem),
        
        hydraulic_power_kw=pump_energy.hydraulic_power_kw,
        pump_electrical_power_kw=pump_energy.electrical_power_kw,
        sec_kwh_per_m3=pump_energy.sec_kwh_per_m3,
        
        water_mass_balance_error_m3_s=water_mb_error_m3_s,
        water_mass_balance_error_percent=water_mb_error_pct,
        solute_mass_balance_error_kg_s=solute_mb_error_kg_s,
        solute_mass_balance_error_percent=solute_mb_error_pct,
        
        converged=res.success,
        solver_message=res.message,
        iterations=res.nfev
    )


def simulate_ro(
    feed_flow: float,
    feed_tds: float,
    pressure: float,
    temperature: float = 25.0,
    pressure_unit: str = "bar",
    flow_unit: str = "m3_hr",
    tds_unit: str = "mg_l",
    feed_cod: Optional[float] = None,
    feed_ph: Optional[float] = None,
    recovery_target: Optional[float] = None,
    membrane_properties: Optional[MembraneElementProperties] = None,
    config: Optional[SimulationConfig] = None,
) -> SimulationResult:
    """
    High-level API for simulating reverse osmosis performance.
    
    Designed to be easily callable for dataset generation, surrogate model training,
    and optimization loops.

    Args:
        feed_flow: Feed volumetric flow rate (default unit: m³/h).
        feed_tds: Feed total dissolved solids concentration (default unit: mg/L).
        pressure: Feed operating pressure (unit specified by pressure_unit).
        temperature: Operating temperature [°C] (default: 25.0 °C).
        pressure_unit: "bar" or "psi" (default: "bar").
        flow_unit: "m3_hr", "m3_day", or "m3_s".
        tds_unit: "mg_l" or "g_l".
        feed_cod: Optional feed COD [mg/L] for textile wastewater characterization.
        feed_ph: Optional feed pH.
        recovery_target: Optional target recovery (for future multi-stage optimization).
        membrane_properties: Membrane properties instance (defaults to Toray TML20D-400).
        config: SimulationConfig instance (defaults to baseline assumptions).

    Returns:
        SimulationResult instance containing all flow, concentration, flux, and energy outputs.
    """
    # Unit conversions for feed flow
    if flow_unit == "m3_hr":
        q_f_m3_s = m3_per_hr_to_m3_per_s(feed_flow)
    elif flow_unit == "m3_day":
        from ro_model.units import m3_per_day_to_m3_per_s
        q_f_m3_s = m3_per_day_to_m3_per_s(feed_flow)
    elif flow_unit == "m3_s":
        q_f_m3_s = feed_flow
    else:
        raise ValueError(f"Unsupported flow_unit '{flow_unit}'")

    # Unit conversions for TDS
    if tds_unit == "mg_l":
        c_f_kg_m3 = mg_per_l_to_kg_per_m3(feed_tds)
    elif tds_unit == "g_l":
        c_f_kg_m3 = feed_tds
    else:
        raise ValueError(f"Unsupported tds_unit '{tds_unit}'")

    # Unit conversions for pressure
    if pressure_unit.lower() == "bar":
        p_f_pa = bar_to_pa(pressure)
    elif pressure_unit.lower() == "psi":
        p_f_pa = psi_to_pa(pressure)
    elif pressure_unit.lower() == "pa":
        p_f_pa = pressure
    else:
        raise ValueError(f"Unsupported pressure_unit '{pressure_unit}'")

    cond = OperatingConditions(
        feed_flow_m3_s=q_f_m3_s,
        feed_concentration_kg_m3=c_f_kg_m3,
        feed_pressure_pa=p_f_pa,
        temperature_k=celsius_to_kelvin(temperature),
        permeate_pressure_pa=bar_to_pa(1.01325),
        feed_cod_mg_l=feed_cod,
        feed_ph=feed_ph
    )
    
    elem = MembraneElement(
        properties=membrane_properties or MembraneElementProperties(),
        config=config or SimulationConfig()
    )
    
    return solve_membrane_element(elem, cond, config)
