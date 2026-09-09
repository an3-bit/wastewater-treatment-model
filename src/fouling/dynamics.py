"""
Dynamic Simulation Engine for Coupled Mechanistic RO and Membrane Fouling.

Coordinates:
1. Time-stepping numerical integration across configurable horizons (24h, 72h, 168h).
2. Element-by-element axial permeability updates (15 elements across 2 stages).
3. Operating Mode A (Fixed Pressure) & Mode B (Production-Maintaining Pressure).
4. Strict mass balance verification at every time step (Qf = Qp + Qr, Qf*Cf = Qp*Cp + Qr*Cr).
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from scipy.optimize import minimize_scalar

from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.system import ROSystem, SystemResult
from data_generation.simulator_runner import create_baseline_system
from fouling.model import (
    FoulingParameters,
    ElementFoulingState,
    SystemFoulingState,
    DynamicSimulationResult,
    calculate_clean_membrane_resistance,
    resistance_to_permeability,
)
from fouling.kinetics import update_element_state
from fouling.metrics import compute_dynamic_trajectory_metrics


class DynamicROSimulator:
    """
    Simulates time-dependent reverse osmosis operation subject to literature-grounded fouling.
    """
    def __init__(
        self,
        system: Optional[ROSystem] = None,
        parameters: Optional[FoulingParameters] = None,
        feed_flow_m3h: float = 30.0,
        feed_tds_mgL: float = 2041.0,
        feed_cod_mgL: float = 51.0,
        feed_pH: float = 8.0,
        temperature_C: float = 25.0,
    ) -> None:
        self.system = system or create_baseline_system()
        self.parameters = parameters or FoulingParameters.create_default(temperature_celsius=temperature_C)
        self.feed_flow_m3h = float(feed_flow_m3h)
        self.feed_tds_mgL = float(feed_tds_mgL)
        self.feed_cod_mgL = float(feed_cod_mgL)
        self.feed_pH = float(feed_pH)
        self.temperature_C = float(temperature_C)

    def _initialize_element_states(self) -> List[ElementFoulingState]:
        """Initialize clean element states (Rf = 0, A_eff = A_clean)."""
        states = []
        r_m = self.parameters.r_m_m_inv
        clean_aw = self.parameters.clean_aw_m_pa_s
        
        # Stage 1: 3 vessels x 3 elements (9 elements total, 3 distinct axial positions)
        for elem_idx in range(1, 4):
            for v_idx in range(1, 4):
                states.append(ElementFoulingState(
                    stage_index=1,
                    element_index=elem_idx,
                    global_element_id=f"Stage1_Vessel{v_idx}_Elem{elem_idx}",
                    r_f_m_inv=0.0,
                    r_total_m_inv=r_m,
                    aw_eff_m_pa_s=clean_aw,
                    permeability_ratio=1.0,
                    permeability_decline_pct=0.0,
                    specific_cumulative_volume_m3_m2=0.0,
                    specific_cumulative_volume_l_m2=0.0,
                    local_flux_lmh=0.0,
                    local_polarization_modulus=1.0,
                    local_feed_tds_mg_l=self.feed_tds_mgL,
                    local_concentrate_tds_mg_l=self.feed_tds_mgL,
                    local_surface_tds_mg_l=self.feed_tds_mgL,
                    local_recovery_pct=0.0,
                ))

        # Stage 2: 2 vessels x 3 elements (6 elements total, 3 distinct axial positions)
        for elem_idx in range(1, 4):
            for v_idx in range(1, 3):
                states.append(ElementFoulingState(
                    stage_index=2,
                    element_index=elem_idx,
                    global_element_id=f"Stage2_Vessel{v_idx}_Elem{elem_idx}",
                    r_f_m_inv=0.0,
                    r_total_m_inv=r_m,
                    aw_eff_m_pa_s=clean_aw,
                    permeability_ratio=1.0,
                    permeability_decline_pct=0.0,
                    specific_cumulative_volume_m3_m2=0.0,
                    specific_cumulative_volume_l_m2=0.0,
                    local_flux_lmh=0.0,
                    local_polarization_modulus=1.0,
                    local_feed_tds_mg_l=self.feed_tds_mgL,
                    local_concentrate_tds_mg_l=self.feed_tds_mgL,
                    local_surface_tds_mg_l=self.feed_tds_mgL,
                    local_recovery_pct=0.0,
                ))

        return states

    def _apply_element_permeabilities_to_system(self, elem_states: List[ElementFoulingState]) -> None:
        """Inject element-specific permeability values into the underlying mechanistic simulator."""
        # Stage 1: Get representative axial permeability for element 1, 2, 3
        stg1_states = [s for s in elem_states if s.stage_index == 1]
        for elem_idx in range(1, 4):
            sub = [s for s in stg1_states if s.element_index == elem_idx]
            aw_val = np.mean([s.aw_eff_m_pa_s for s in sub])
            # Set on vessel prototype
            self.system.stages[0].vessel_prototype.elements[elem_idx - 1].properties.Aw_m_pa_s = float(aw_val)

        # Stage 2: Get representative axial permeability for element 1, 2, 3
        stg2_states = [s for s in elem_states if s.stage_index == 2]
        for elem_idx in range(1, 4):
            sub = [s for s in stg2_states if s.element_index == elem_idx]
            aw_val = np.mean([s.aw_eff_m_pa_s for s in sub])
            # Set on vessel prototype
            self.system.stages[1].vessel_prototype.elements[elem_idx - 1].properties.Aw_m_pa_s = float(aw_val)

    def simulate(
        self,
        strategy_name: str,
        initial_p1_bar: float,
        initial_p2_bar: float,
        horizon_hours: float = 168.0,
        time_step_hours: float = 1.0,
        operating_mode: str = "MODE_A_FIXED_PRESSURE",
        target_production_m3h: Optional[float] = None,
    ) -> DynamicSimulationResult:
        """
        Execute dynamic simulation across the specified horizon.
        """
        elem_states = self._initialize_element_states()
        self._apply_element_permeabilities_to_system(elem_states)

        timestamps = list(np.arange(0.0, horizon_hours + 1e-6, time_step_hours))
        system_states: List[SystemFoulingState] = []

        curr_p1 = float(initial_p1_bar)
        curr_p2 = float(initial_p2_bar)
        
        # Initial clean solve (t = 0)
        init_res = self.system.solve(
            feed_flow_m3_hr=self.feed_flow_m3h,
            feed_tds_mg_l=self.feed_tds_mgL,
            stage_pressures_bar=[curr_p1, curr_p2],
            temperature_celsius=self.temperature_C,
        )
        target_qp = target_production_m3h or init_res.permeate_flow_m3_hr

        for step_idx, t_now in enumerate(timestamps):
            # -------------------------------------------------------------
            # Mode B: Production-Maintaining Pressure Adjustment
            # -------------------------------------------------------------
            if operating_mode == "MODE_B_MAINTAIN_PRODUCTION" and step_idx > 0:
                # Solve for pressure multiplier k_p >= 1.0 to match target_qp
                def obj_pressure(k_factor: float) -> float:
                    p1_test = min(curr_p1 * k_factor, 40.0)
                    p2_test = min(curr_p2 * k_factor, 41.0)
                    try:
                        r_test = self.system.solve(
                            feed_flow_m3_hr=self.feed_flow_m3h,
                            feed_tds_mg_l=self.feed_tds_mgL,
                            stage_pressures_bar=[p1_test, p2_test],
                            temperature_celsius=self.temperature_C,
                        )
                        return (r_test.permeate_flow_m3_hr - target_qp) ** 2
                    except Exception:
                        return 1e6

                opt = minimize_scalar(obj_pressure, bounds=(1.0, 2.0), method="bounded")
                k_best = float(opt.x)
                curr_p1 = min(curr_p1 * k_best, 40.0)
                curr_p2 = min(curr_p2 * k_best, 41.0)

            # Solve mechanistic state at current permeability & pressures
            sys_res = self.system.solve(
                feed_flow_m3_hr=self.feed_flow_m3h,
                feed_tds_mg_l=self.feed_tds_mgL,
                stage_pressures_bar=[curr_p1, curr_p2],
                temperature_celsius=self.temperature_C,
            )

            # Extract element results from each stage
            stg1_elem_res = sys_res.stage_results[0].vessel_result.element_results
            stg2_elem_res = sys_res.stage_results[1].vessel_result.element_results

            # Record system-level snapshot
            avg_perm_ratio = np.mean([s.permeability_ratio for s in elem_states])
            avg_decline = (1.0 - avg_perm_ratio) * 100.0
            max_elem_decline = max([s.permeability_decline_pct for s in elem_states])

            snap = SystemFoulingState(
                time_hours=float(t_now),
                element_states=[st for st in elem_states], # Snapshot copy
                average_permeability_ratio=float(avg_perm_ratio),
                average_permeability_decline_pct=float(avg_decline),
                max_element_permeability_decline_pct=float(max_elem_decline),
                total_cumulative_permeate_m3=0.0, # Computed in metrics post-processing
                total_cumulative_electricity_kwh=0.0,
                instantaneous_recovery_pct=float(sys_res.overall_water_recovery_percent),
                instantaneous_sec_kwh_m3=float(sys_res.system_sec_kwh_per_m3),
                instantaneous_permeate_flow_m3_h=float(sys_res.permeate_flow_m3_hr),
                instantaneous_permeate_tds_mg_l=float(sys_res.permeate_tds_mg_l),
                instantaneous_concentrate_flow_m3_h=float(sys_res.concentrate_flow_m3_hr),
                instantaneous_concentrate_tds_mg_l=float(sys_res.concentrate_tds_mg_l),
                stage1_feed_pressure_bar=float(curr_p1),
                stage2_feed_pressure_bar=float(curr_p2),
                water_mass_balance_error_pct=float(sys_res.water_mass_balance_error_percent),
                solute_mass_balance_error_pct=float(sys_res.solute_mass_balance_error_percent),
                converged=bool(sys_res.converged),
            )
            system_states.append(snap)

            # Integrate forward if not at final step
            if step_idx < len(timestamps) - 1:
                dt_h = timestamps[step_idx + 1] - t_now
                new_elem_states = []

                for st in elem_states:
                    if st.stage_index == 1:
                        eres = stg1_elem_res[st.element_index - 1]
                    else:
                        eres = stg2_elem_res[st.element_index - 1]

                    updated_st = update_element_state(
                        current_state=st,
                        flux_lmh=eres.water_flux_lmh,
                        polarization_modulus=eres.polarization_modulus,
                        feed_tds_mg_l=eres.feed_tds_mg_l,
                        concentrate_tds_mg_l=eres.concentrate_tds_mg_l,
                        local_recovery_pct=eres.water_recovery_percent,
                        delta_t_hours=dt_h,
                        parameters=self.parameters,
                    )
                    new_elem_states.append(updated_st)

                elem_states = new_elem_states
                self._apply_element_permeabilities_to_system(elem_states)

        # Post-process metrics
        traj_metrics = compute_dynamic_trajectory_metrics(system_states, total_membrane_area_m2=self.system.total_area_m2)

        return DynamicSimulationResult(
            strategy_name=strategy_name,
            operating_mode=operating_mode,
            time_horizon_hours=float(horizon_hours),
            time_step_hours=float(time_step_hours),
            parameters=self.parameters,
            timestamps_hours=timestamps,
            states=system_states,
            initial_recovery_pct=traj_metrics["initial_recovery_pct"],
            final_recovery_pct=traj_metrics["final_recovery_pct"],
            initial_sec_kwh_m3=traj_metrics["initial_sec_kwh_m3"],
            final_sec_kwh_m3=traj_metrics["final_sec_kwh_m3"],
            initial_avg_flux_lmh=traj_metrics["initial_permeate_flow_m3_h"] * 1000.0 / self.system.total_area_m2,
            final_avg_flux_lmh=traj_metrics["final_permeate_flow_m3_h"] * 1000.0 / self.system.total_area_m2,
            final_permeability_decline_pct=traj_metrics["final_average_permeability_decline_pct"],
            total_cumulative_permeate_m3=traj_metrics["total_cumulative_permeate_m3"],
            total_cumulative_electricity_kwh=traj_metrics["total_cumulative_electricity_kwh"],
            dynamic_average_sec_kwh_m3=traj_metrics["dynamic_average_sec_kwh_m3"],
            specific_cumulative_volume_l_m2=traj_metrics["specific_cumulative_volume_l_m2"],
            time_to_5pct_decline_hours=traj_metrics["time_to_5pct_decline_hours"],
            time_to_10pct_decline_hours=traj_metrics["time_to_10pct_decline_hours"],
            time_to_15pct_decline_hours=traj_metrics["time_to_15pct_decline_hours"],
            max_dynamic_water_error_pct=traj_metrics["max_dynamic_water_error_pct"],
            max_dynamic_solute_error_pct=traj_metrics["max_dynamic_solute_error_pct"],
        )
