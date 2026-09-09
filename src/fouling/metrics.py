"""
Dynamic Metrics and Performance Evaluation for Fouled RO Systems.

Computes:
1. Cumulative permeate production [m^3].
2. Cumulative electricity consumption [kWh].
3. Dynamic weighted average SEC [kWh/m^3].
4. Permeability decline percentages [%].
5. Time to 5%, 10%, and 15% analysis decline thresholds [hours].
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd

from fouling.model import SystemFoulingState, DynamicSimulationResult


def compute_dynamic_trajectory_metrics(
    states: List[SystemFoulingState],
    total_membrane_area_m2: float = 555.0,
) -> Dict[str, Any]:
    """
    Aggregate dynamic trajectory metrics over time steps.
    """
    if len(states) == 0:
        return {}

    times = np.array([s.time_hours for s in states], dtype=float)
    qp_vals = np.array([s.instantaneous_permeate_flow_m3_h for s in states], dtype=float)
    power_vals = np.array([s.instantaneous_sec_kwh_m3 * s.instantaneous_permeate_flow_m3_h for s in states], dtype=float)
    sec_vals = np.array([s.instantaneous_sec_kwh_m3 for s in states], dtype=float)
    rec_vals = np.array([s.instantaneous_recovery_pct for s in states], dtype=float)
    decline_vals = np.array([s.average_permeability_decline_pct for s in states], dtype=float)
    max_elem_decline_vals = np.array([s.max_element_permeability_decline_pct for s in states], dtype=float)

    # Trapezoidal integration for cumulative volumes & energy
    total_cum_qp_m3 = 0.0
    total_cum_elec_kwh = 0.0

    for i in range(1, len(states)):
        dt = times[i] - times[i - 1]
        # Average flow in interval
        qp_avg = (qp_vals[i] + qp_vals[i - 1]) / 2.0
        power_avg = (power_vals[i] + power_vals[i - 1]) / 2.0
        
        total_cum_qp_m3 += qp_avg * dt
        total_cum_elec_kwh += power_avg * dt

    # Dynamic average SEC
    dyn_avg_sec = (total_cum_elec_kwh / total_cum_qp_m3) if total_cum_qp_m3 > 0 else sec_vals[0]
    specific_cum_vol_l_m2 = (total_cum_qp_m3 * 1000.0) / total_membrane_area_m2

    # Calculate time to threshold crossings via linear interpolation
    def find_time_to_threshold(threshold_pct: float) -> Optional[float]:
        for i in range(len(decline_vals)):
            if decline_vals[i] >= threshold_pct:
                if i == 0:
                    return float(times[0])
                # Linear interpolation
                t0, t1 = times[i - 1], times[i]
                d0, d1 = decline_vals[i - 1], decline_vals[i]
                if abs(d1 - d0) < 1e-6:
                    return float(t0)
                t_interp = t0 + (threshold_pct - d0) * (t1 - t0) / (d1 - d0)
                return float(t_interp)
        return None

    t_5 = find_time_to_threshold(5.0)
    t_10 = find_time_to_threshold(10.0)
    t_15 = find_time_to_threshold(15.0)

    # Maximum mass balance residuals
    max_water_err = max(s.water_mass_balance_error_pct for s in states)
    max_solute_err = max(s.solute_mass_balance_error_pct for s in states)

    return {
        "initial_recovery_pct": float(rec_vals[0]),
        "final_recovery_pct": float(rec_vals[-1]),
        "initial_sec_kwh_m3": float(sec_vals[0]),
        "final_sec_kwh_m3": float(sec_vals[-1]),
        "initial_permeate_flow_m3_h": float(qp_vals[0]),
        "final_permeate_flow_m3_h": float(qp_vals[-1]),
        "final_average_permeability_decline_pct": float(decline_vals[-1]),
        "final_max_element_decline_pct": float(max_elem_decline_vals[-1]),
        "total_cumulative_permeate_m3": float(total_cum_qp_m3),
        "total_cumulative_electricity_kwh": float(total_cum_elec_kwh),
        "dynamic_average_sec_kwh_m3": float(dyn_avg_sec),
        "specific_cumulative_volume_l_m2": float(specific_cum_vol_l_m2),
        "time_to_5pct_decline_hours": t_5,
        "time_to_10pct_decline_hours": t_10,
        "time_to_15pct_decline_hours": t_15,
        "max_dynamic_water_error_pct": float(max_water_err),
        "max_dynamic_solute_error_pct": float(max_solute_err),
    }
