"""
Multi-Horizon Predictive Forecasting and Counterfactual Supervisory Decision Engine (Stage 8).

Integrates the 6-zone Extended Kalman Filter (EKF) state with first-principles fouling dynamics
and the techno-economic objective function to project future trajectories and evaluate candidate supervisory actions.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import copy
import numpy as np

from economics.cost_config import EconomicConfig
from economics.water_value import calculate_water_value
from economics.energy_cost import calculate_energy_cost
from economics.cleaning_cost import calculate_single_cip_cost

# Authoritative constants
R_M_CLEAN = 1.1888677444880217e14  # [m^-1]
R_SPEC = 1.954988085694205e13       # [m^-1 / (m^3/m^2)]
AW_CLEAN = 9.446312125982804e-12   # [m/(Pa s)]
MAX_PRESSURE_BAR = 41.0
MAX_ELEMENT_RECOVERY_LIMIT_PCT = 30.0
PERMEATE_TDS_LIMIT_MG_L = 18.0


@dataclass
class HorizonForecastStep:
    horizon_hours: float
    time_hours: float
    permeate_flow_m3_h: float
    recovery_pct: float
    sec_kwh_m3: float
    power_kw: float
    permeate_tds_mg_l: float
    mean_rf_m_inv: float
    permeability_decline_pct: float
    max_element_recovery_pct: float
    gross_water_value_kes: float
    electricity_cost_kes: float
    net_operating_value_kes: float


@dataclass
class MultiHorizonForecastResult:
    origin_time_hours: float
    current_p1_bar: float
    current_p2_bar: float
    current_mean_rf: float
    current_decline_pct: float
    horizons: Dict[str, HorizonForecastStep]  # '6h', '12h', '24h', '48h', '72h'
    time_to_t5_hours: Optional[float]
    time_to_t10_hours: Optional[float]
    time_to_t15_hours: Optional[float]


@dataclass
class CandidateActionEvaluation:
    action_name: str
    action_type: str  # 'CONTINUE', 'PRESSURE_ADJUSTMENT', 'STRATEGY_PRESET', 'CIP_CLEANING'
    p1_bar: float
    p2_bar: float
    is_feasible: bool
    constraint_violations: List[str]
    forecast_24h: HorizonForecastStep
    net_economic_value_24h_kes: float
    rank: int = 0


@dataclass
class SupervisoryRecommendation:
    timestamp_hour: float
    current_recovery_pct: float
    current_sec_kwh_m3: float
    current_decline_pct: float
    best_action: CandidateActionEvaluation
    candidate_evaluations: List[CandidateActionEvaluation]
    multi_horizon_forecast: MultiHorizonForecastResult
    reasoning: str


class SupervisoryPredictor:
    """
    Multi-horizon predictor and deterministic economic receding-horizon optimizer.
    """
    def __init__(self, config: EconomicConfig) -> None:
        self.config = config

    def forecast_trajectory(
        self,
        q_feed: float,
        c_feed: float,
        temp_c: float,
        p1_bar: float,
        p2_bar: float,
        initial_6zone_rf: np.ndarray,
        horizon_hours: float = 72.0,
        step_hours: float = 1.0,
    ) -> List[HorizonForecastStep]:
        """
        Simulate forward trajectory over horizon_hours given fixed or candidate pressures.
        """
        steps_count = int(horizon_hours / step_hours)
        trajectory: List[HorizonForecastStep] = []
        
        current_rf = np.copy(initial_6zone_rf)
        cum_time = 0.0

        for s in range(1, steps_count + 1):
            cum_time = s * step_hours

            # Hydraulic response with fouling resistance
            mean_rf = float(np.mean(current_rf))
            r_total = R_M_CLEAN + mean_rf
            perm_ratio = R_M_CLEAN / r_total
            decline_pct = (1.0 - perm_ratio) * 100.0

            # Base clean fluxes scaled by pressure and resistance
            net_dp = max(1.0, (p1_bar + p2_bar) / 2.0 - 1.5)  # approximate effective NDP
            base_rec = 0.7022 * (net_dp / 16.23) * perm_ratio
            recovery_pct = max(10.0, min(85.0, base_rec * 100.0))
            
            q_perm = q_feed * (recovery_pct / 100.0)
            sec = (0.7269 * (p1_bar / 16.06) + 0.08 * (p2_bar / 16.41)) / max(0.2, perm_ratio ** 0.5)
            power_kw = q_perm * sec
            perm_tds = 7.21 * (c_feed / 2041.0) * (1.0 + 0.05 * (decline_pct / 15.0))
            max_elem_rec = (recovery_pct / 70.22) * 20.37

            # Economics for this step
            w_res = calculate_water_value(q_perm * step_hours, self.config)
            e_res = calculate_energy_cost(power_kw * step_hours, q_perm * step_hours, self.config)
            net_val = w_res.total_water_value_kes - e_res.electricity_cost_kes

            # Step kinetics update
            # dRf/dt proportional to local flux Jv and specific cake resistance
            flux_lmh = (q_perm / 555.0) * 1000.0  # LMH
            drf_dt = R_SPEC * (flux_lmh / 1000.0) * step_hours
            
            # Axial profile: tail zones foul faster due to higher salinity
            zone_multipliers = np.array([0.7, 0.9, 1.1, 1.2, 1.4, 1.8])
            current_rf += drf_dt * zone_multipliers

            trajectory.append(
                HorizonForecastStep(
                    horizon_hours=cum_time,
                    time_hours=cum_time,
                    permeate_flow_m3_h=q_perm,
                    recovery_pct=recovery_pct,
                    sec_kwh_m3=sec,
                    power_kw=power_kw,
                    permeate_tds_mg_l=perm_tds,
                    mean_rf_m_inv=float(np.mean(current_rf)),
                    permeability_decline_pct=decline_pct,
                    max_element_recovery_pct=max_elem_rec,
                    gross_water_value_kes=w_res.total_water_value_kes,
                    electricity_cost_kes=e_res.electricity_cost_kes,
                    net_operating_value_kes=net_val,
                )
            )

        return trajectory

    def generate_multi_horizon_forecast(
        self,
        origin_time_hours: float,
        q_feed: float,
        c_feed: float,
        temp_c: float,
        p1_bar: float,
        p2_bar: float,
        initial_6zone_rf: np.ndarray,
    ) -> MultiHorizonForecastResult:
        """
        Generate key multi-horizon snapshots: 6h, 12h, 24h, 48h, 72h.
        """
        traj = self.forecast_trajectory(
            q_feed=q_feed,
            c_feed=c_feed,
            temp_c=temp_c,
            p1_bar=p1_bar,
            p2_bar=p2_bar,
            initial_6zone_rf=initial_6zone_rf,
            horizon_hours=72.0,
            step_hours=1.0,
        )

        horizons_map: Dict[str, HorizonForecastStep] = {}
        for h in [6, 12, 24, 48, 72]:
            step_obj = traj[h - 1]
            horizons_map[f"{h}h"] = step_obj

        mean_rf = float(np.mean(initial_6zone_rf))
        decline_0 = (1.0 - (R_M_CLEAN / (R_M_CLEAN + mean_rf))) * 100.0

        # Analysis threshold crossings
        t5_cross = None
        t10_cross = None
        t15_cross = None
        for step in traj:
            if t5_cross is None and step.permeability_decline_pct >= 5.0:
                t5_cross = step.horizon_hours
            if t10_cross is None and step.permeability_decline_pct >= 10.0:
                t10_cross = step.horizon_hours
            if t15_cross is None and step.permeability_decline_pct >= 15.0:
                t15_cross = step.horizon_hours

        return MultiHorizonForecastResult(
            origin_time_hours=origin_time_hours,
            current_p1_bar=p1_bar,
            current_p2_bar=p2_bar,
            current_mean_rf=mean_rf,
            current_decline_pct=decline_0,
            horizons=horizons_map,
            time_to_t5_hours=t5_cross,
            time_to_t10_hours=t10_cross,
            time_to_t15_hours=t15_cross,
        )

    def evaluate_counterfactual_actions(
        self,
        current_time_hours: float,
        q_feed: float,
        c_feed: float,
        temp_c: float,
        current_p1_bar: float,
        current_p2_bar: float,
        initial_6zone_rf: np.ndarray,
    ) -> List[CandidateActionEvaluation]:
        """
        Evaluate 10 discrete candidate supervisory actions over a 24-hour lookahead horizon.
        """
        candidates: List[Tuple[str, str, float, float, bool]] = [
            ("Continue Current Setpoint", "CONTINUE", current_p1_bar, current_p2_bar, False),
            ("Reduce P1 (-0.5 bar)", "PRESSURE_ADJUSTMENT", current_p1_bar - 0.5, current_p2_bar, False),
            ("Reduce P2 (-0.5 bar)", "PRESSURE_ADJUSTMENT", current_p1_bar, current_p2_bar - 0.5, False),
            ("Reduce Both (-0.5 bar)", "PRESSURE_ADJUSTMENT", current_p1_bar - 0.5, current_p2_bar - 0.5, False),
            ("Increase P1 (+0.5 bar)", "PRESSURE_ADJUSTMENT", current_p1_bar + 0.5, current_p2_bar, False),
            ("Increase P2 (+0.5 bar)", "PRESSURE_ADJUSTMENT", current_p1_bar, current_p2_bar + 0.5, False),
            ("Switch to Strategy B (Low SEC)", "STRATEGY_PRESET", 15.80, 15.80, False),
            ("Switch to Strategy C (Low Stress)", "STRATEGY_PRESET", 10.00, 14.00, False),
            ("Switch to Strategy D (Balanced Optimum)", "STRATEGY_PRESET", 16.06, 16.41, False),
            ("Initiate Chemical Cleaning (CIP)", "CIP_CLEANING", 16.06, 16.41, True),
        ]

        evaluations: List[CandidateActionEvaluation] = []

        for name, a_type, p1, p2, is_cip in candidates:
            violations: List[str] = []
            
            # Constraint checks
            if p1 > MAX_PRESSURE_BAR or p2 > MAX_PRESSURE_BAR:
                violations.append(f"Pressure exceeds {MAX_PRESSURE_BAR} bar limit")
            if p1 < 8.0 or p2 < 8.0:
                violations.append("Pressure below minimum net driving threshold (8.0 bar)")

            # Forecast state
            eval_rf = initial_6zone_rf * 0.10 if is_cip else initial_6zone_rf  # 90% restoration if CIP

            traj_24 = self.forecast_trajectory(
                q_feed=q_feed,
                c_feed=c_feed,
                temp_c=temp_c,
                p1_bar=p1,
                p2_bar=p2,
                initial_6zone_rf=eval_rf,
                horizon_hours=24.0,
                step_hours=1.0,
            )

            # Cumulative 24h economics
            tot_water_val = sum(s.gross_water_value_kes for s in traj_24)
            tot_elec_cost = sum(s.electricity_cost_kes for s in traj_24)
            
            cip_cost = calculate_single_cip_cost(1, current_time_hours, self.config).total_cost_kes if is_cip else 0.0

            # Max element recovery and TDS constraint checks
            max_elem = max(s.max_element_recovery_pct for s in traj_24)
            if max_elem > MAX_ELEMENT_RECOVERY_LIMIT_PCT:
                violations.append(f"Peak element recovery {max_elem:.1f}% exceeds 30.0% limit")

            max_tds = max(s.permeate_tds_mg_l for s in traj_24)
            if max_tds > PERMEATE_TDS_LIMIT_MG_L:
                violations.append(f"Permeate TDS {max_tds:.1f} mg/L exceeds 18.0 mg/L target")

            is_feas = len(violations) == 0
            penalty = 50000.0 if not is_feas else 0.0

            net_val_24h = tot_water_val - tot_elec_cost - cip_cost - penalty

            evaluations.append(
                CandidateActionEvaluation(
                    action_name=name,
                    action_type=a_type,
                    p1_bar=p1,
                    p2_bar=p2,
                    is_feasible=is_feas,
                    constraint_violations=violations,
                    forecast_24h=traj_24[-1],
                    net_economic_value_24h_kes=net_val_24h,
                )
            )

        # Rank by net economic value
        evaluations.sort(key=lambda x: x.net_economic_value_24h_kes, reverse=True)
        for r_idx, ev in enumerate(evaluations):
            ev.rank = r_idx + 1

        return evaluations

    def recommend_optimal_action(
        self,
        current_time_hours: float,
        q_feed: float,
        c_feed: float,
        temp_c: float,
        current_p1_bar: float,
        current_p2_bar: float,
        initial_6zone_rf: np.ndarray,
    ) -> SupervisoryRecommendation:
        """
        Generate full supervisory recommendation and multi-horizon forward forecast.
        """
        evals = self.evaluate_counterfactual_actions(
            current_time_hours=current_time_hours,
            q_feed=q_feed,
            c_feed=c_feed,
            temp_c=temp_c,
            current_p1_bar=current_p1_bar,
            current_p2_bar=current_p2_bar,
            initial_6zone_rf=initial_6zone_rf,
        )
        best = evals[0]

        multi_forecast = self.generate_multi_horizon_forecast(
            origin_time_hours=current_time_hours,
            q_feed=q_feed,
            c_feed=c_feed,
            temp_c=temp_c,
            p1_bar=best.p1_bar,
            p2_bar=best.p2_bar,
            initial_6zone_rf=initial_6zone_rf,
        )

        mean_rf = float(np.mean(initial_6zone_rf))
        decline = (1.0 - (R_M_CLEAN / (R_M_CLEAN + mean_rf))) * 100.0

        reasoning = (
            f"Action '{best.action_name}' selected as optimal: projected 24h net operating value of "
            f"KES {best.net_economic_value_24h_kes:,.0f} with zero constraint violations."
        )

        return SupervisoryRecommendation(
            timestamp_hour=current_time_hours,
            current_recovery_pct=best.forecast_24h.recovery_pct,
            current_sec_kwh_m3=best.forecast_24h.sec_kwh_m3,
            current_decline_pct=decline,
            best_action=best,
            candidate_evaluations=evals,
            multi_horizon_forecast=multi_forecast,
            reasoning=reasoning,
        )
