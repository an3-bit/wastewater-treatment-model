"""
Uncertainty and Sensitivity Analysis for Dynamic Membrane Fouling.

Evaluates:
1. Parametric uncertainty in fouling rate constant (+/- 25% r_spec).
2. Upstream feed salinity disturbances (TDS = 1500, 2041, 3000 mg/L).
3. Strategy ranking robustness across operating horizons.
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

from fouling.model import FoulingParameters
from fouling.dynamics import DynamicROSimulator


def run_fouling_rate_uncertainty_study(
    strategies: Dict[str, Tuple[float, float]],
    base_r_spec: float = 2.45e13,
    variations: List[float] = [-0.25, 0.0, 0.25],
    horizon_hours: float = 168.0,
    time_step_hours: float = 1.0,
    feed_tds_mgL: float = 2041.0,
) -> pd.DataFrame:
    """
    Evaluate strategy metrics under -25%, baseline, and +25% fouling rate constants.
    """
    rows = []

    for var_frac in variations:
        var_pct = var_frac * 100.0
        current_r_spec = base_r_spec * (1.0 + var_frac)
        params = FoulingParameters.create_default(r_spec=current_r_spec)
        
        sim = DynamicROSimulator(
            parameters=params,
            feed_tds_mgL=feed_tds_mgL,
        )

        for strat_name, (p1, p2) in strategies.items():
            res = sim.simulate(
                strategy_name=strat_name,
                initial_p1_bar=p1,
                initial_p2_bar=p2,
                horizon_hours=horizon_hours,
                time_step_hours=time_step_hours,
                operating_mode="MODE_A_FIXED_PRESSURE",
            )

            rows.append({
                "variation_pct": var_pct,
                "r_spec_value": current_r_spec,
                "strategy_name": strat_name,
                "p1_bar": p1,
                "p2_bar": p2,
                "initial_recovery_pct": res.initial_recovery_pct,
                "final_recovery_pct": res.final_recovery_pct,
                "recovery_decline_pct": res.initial_recovery_pct - res.final_recovery_pct,
                "permeability_decline_pct": res.final_permeability_decline_pct,
                "total_cumulative_permeate_m3": res.total_cumulative_permeate_m3,
                "total_cumulative_electricity_kwh": res.total_cumulative_electricity_kwh,
                "dynamic_average_sec_kwh_m3": res.dynamic_average_sec_kwh_m3,
                "specific_cumulative_volume_l_m2": res.specific_cumulative_volume_l_m2,
                "time_to_15pct_decline_hours": res.time_to_15pct_decline_hours,
            })

    return pd.DataFrame(rows)


def run_feed_tds_disturbance_study(
    strategies: Dict[str, Tuple[float, float]],
    tds_levels: List[float] = [1500.0, 2041.0, 3000.0],
    r_spec: float = 2.45e13,
    horizon_hours: float = 168.0,
    time_step_hours: float = 1.0,
) -> pd.DataFrame:
    """
    Evaluate strategy dynamics under varying upstream feed salinity levels.
    """
    rows = []
    params = FoulingParameters.create_default(r_spec=r_spec)

    for tds_val in tds_levels:
        sim = DynamicROSimulator(
            parameters=params,
            feed_tds_mgL=tds_val,
        )

        for strat_name, (p1, p2) in strategies.items():
            res = sim.simulate(
                strategy_name=strat_name,
                initial_p1_bar=p1,
                initial_p2_bar=p2,
                horizon_hours=horizon_hours,
                time_step_hours=time_step_hours,
                operating_mode="MODE_A_FIXED_PRESSURE",
            )

            rows.append({
                "feed_tds_mgL": tds_val,
                "strategy_name": strat_name,
                "p1_bar": p1,
                "p2_bar": p2,
                "initial_recovery_pct": res.initial_recovery_pct,
                "final_recovery_pct": res.final_recovery_pct,
                "permeability_decline_pct": res.final_permeability_decline_pct,
                "total_cumulative_permeate_m3": res.total_cumulative_permeate_m3,
                "total_cumulative_electricity_kwh": res.total_cumulative_electricity_kwh,
                "dynamic_average_sec_kwh_m3": res.dynamic_average_sec_kwh_m3,
                "time_to_15pct_decline_hours": res.time_to_15pct_decline_hours,
            })

    return pd.DataFrame(rows)
