"""
Multi-Stage Reverse Osmosis System Architecture and Plant Solver.

Models industrial multi-stage RO networks with:
1. Configurable inter-stage topologies ("concentrate_to_stage2" or "permeate_to_stage2")
2. Interstage booster pumps and pressure staging
3. Global fluid and solute conservation verification
4. Level A (thermodynamic TDS) + Level B (water quality descriptors) integration
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
import numpy as np

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    m3_per_s_to_m3_per_hr,
    m3_per_hr_to_m3_per_s,
    m_per_s_to_lmh
)
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig
)
from ro_model.stage import ROStage, StageResult
from ro_model.energy import calculate_pump_energy
from ro_model.water_quality import (
    WaterQualityStream,
    ApparentRejectionProfile,
    compute_water_quality_split
)


@dataclass
class SystemResult:
    """
    Consolidated performance metrics for a multi-stage industrial RO plant.
    """
    system_name: str
    topology: str
    num_stages: int
    total_elements: int
    total_membrane_area_m2: float
    
    # Inlet Conditions
    feed_flow_m3_hr: float
    feed_tds_mg_l: float
    feed_pressure_bar: float
    temperature_celsius: float
    
    # Overall System Outlet Streams
    permeate_flow_m3_hr: float
    permeate_tds_mg_l: float
    concentrate_flow_m3_hr: float
    concentrate_tds_mg_l: float
    
    # Global Separation & Energy Metrics
    overall_water_recovery_percent: float
    overall_salt_rejection_percent: float
    average_system_flux_lmh: float
    total_electrical_power_kw: float
    system_sec_kwh_per_m3: float
    
    # Stage-by-Stage Results
    stage_results: List[StageResult] = field(default_factory=list)
    
    # Water Quality Descriptor Streams (Level B)
    feed_quality: Optional[WaterQualityStream] = None
    permeate_quality: Optional[WaterQualityStream] = None
    concentrate_quality: Optional[WaterQualityStream] = None
    
    # Mass Balance Residuals
    water_mass_balance_error_m3_s: float = 0.0
    water_mass_balance_error_percent: float = 0.0
    solute_mass_balance_error_kg_s: float = 0.0
    solute_mass_balance_error_percent: float = 0.0
    converged: bool = True


class ROSystem:
    """
    Model of a multi-stage industrial reverse osmosis train.
    """
    def __init__(
        self,
        name: str = "Nice_Cotton_2Stage_RO",
        stages: Optional[List[ROStage]] = None,
        topology: str = "concentrate_to_stage2",
        config: Optional[SimulationConfig] = None
    ) -> None:
        self.name = name
        self.stages = stages or []
        self.topology = topology
        self.config = config or SimulationConfig()
        self.last_result: Optional[SystemResult] = None

    def add_stage(self, stage: ROStage) -> None:
        """Append an ROStage to the train."""
        self.stages.append(stage)

    @property
    def total_elements(self) -> int:
        """Total number of elements across all stages."""
        return sum(s.total_elements for s in self.stages)

    @property
    def total_area_m2(self) -> float:
        """Total active membrane area across all stages."""
        return sum(s.total_area_m2 for s in self.stages)

    def solve(
        self,
        feed_flow_m3_hr: float,
        feed_tds_mg_l: float,
        stage_pressures_bar: List[float],
        temperature_celsius: float = 25.0,
        feed_quality_stream: Optional[WaterQualityStream] = None,
        rejection_profile: Optional[ApparentRejectionProfile] = None
    ) -> SystemResult:
        """
        Solve the multi-stage RO network sequentially according to the specified topology.
        """
        if len(self.stages) == 0:
            raise ValueError("ROSystem has no stages configured.")
        if len(stage_pressures_bar) < len(self.stages):
            raise ValueError(
                f"Must provide at least {len(self.stages)} stage pressures, got {len(stage_pressures_bar)}"
            )
        for idx, p_val in enumerate(stage_pressures_bar[:len(self.stages)]):
            max_p_bar = self.stages[idx].element_properties.max_operating_pressure_pa / 1.0e5
            if p_val > max_p_bar:
                raise ValueError(
                    f"Stage {idx+1} pressure {p_val:.2f} bar exceeds maximum allowed limit {max_p_bar:.2f} bar."
                )

        stage_results: List[StageResult] = []
        total_elec_power_kw = 0.0
        
        # ---------------------------------------------------------------------
        # TOPOLOGY 1: Concentrate Staging (concentrate_to_stage2)
        # ---------------------------------------------------------------------
        if self.topology == "concentrate_to_stage2":
            curr_qf_m3_hr = feed_flow_m3_hr
            curr_cf_mg_l = feed_tds_mg_l
            prev_pr_bar = 1.01325  # Suction pressure for Stage 1 pump
            
            combined_qp_m3_s = 0.0
            solute_permeate_mass_kg_s = 0.0
            
            for idx, stage in enumerate(self.stages):
                p_stage_bar = stage_pressures_bar[idx]
                
                # Determine suction pressure: for Stage 1 = 1.01325 bar; for Stage 2+ = previous stage concentrate pressure
                inlet_suction_p_bar = 1.01325 if idx == 0 else prev_pr_bar
                
                s_res = stage.solve(
                    feed_flow_m3_hr=curr_qf_m3_hr,
                    feed_tds_mg_l=curr_cf_mg_l,
                    feed_pressure_bar=p_stage_bar,
                    temperature_celsius=temperature_celsius,
                    inlet_suction_pressure_bar=inlet_suction_p_bar
                )
                stage_results.append(s_res)
                
                # Permeate summation
                qp_s = m3_per_hr_to_m3_per_s(s_res.permeate_flow_m3_hr)
                combined_qp_m3_s += qp_s
                solute_permeate_mass_kg_s += (qp_s * s_res.permeate_tds_mg_l * 1.0e-3)
                
                # Energy summation
                total_elec_power_kw += s_res.electrical_power_kw
                
                # Feed for next stage
                curr_qf_m3_hr = s_res.concentrate_flow_m3_hr
                curr_cf_mg_l = s_res.concentrate_tds_mg_l
                prev_pr_bar = s_res.concentrate_pressure_bar

            # Final overall stream outputs
            overall_qp_m3_hr = combined_qp_m3_s * 3600.0
            overall_cp_kg_m3 = (solute_permeate_mass_kg_s / combined_qp_m3_s) if combined_qp_m3_s > 0 else 0.0
            overall_cp_mg_l = overall_cp_kg_m3 * 1000.0
            
            final_qr_m3_hr = stage_results[-1].concentrate_flow_m3_hr
            final_cr_mg_l = stage_results[-1].concentrate_tds_mg_l

        # ---------------------------------------------------------------------
        # TOPOLOGY 2: Permeate Staging / 2-Pass (permeate_to_stage2)
        # ---------------------------------------------------------------------
        elif self.topology == "permeate_to_stage2":
            # Stage 1
            s1_res = self.stages[0].solve(
                feed_flow_m3_hr=feed_flow_m3_hr,
                feed_tds_mg_l=feed_tds_mg_l,
                feed_pressure_bar=stage_pressures_bar[0],
                temperature_celsius=temperature_celsius
            )
            stage_results.append(s1_res)
            total_elec_power_kw += s1_res.electrical_power_kw
            
            # Stage 2 receives Stage 1 Permeate
            s2_res = self.stages[1].solve(
                feed_flow_m3_hr=s1_res.permeate_flow_m3_hr,
                feed_tds_mg_l=s1_res.permeate_tds_mg_l,
                feed_pressure_bar=stage_pressures_bar[1],
                temperature_celsius=temperature_celsius
            )
            stage_results.append(s2_res)
            total_elec_power_kw += s2_res.electrical_power_kw
            
            overall_qp_m3_hr = s2_res.permeate_flow_m3_hr
            overall_cp_mg_l = s2_res.permeate_tds_mg_l
            
            # Combined rejects from Pass 1 and Pass 2
            final_qr_m3_hr = s1_res.concentrate_flow_m3_hr + s2_res.concentrate_flow_m3_hr
            final_cr_mg_l = (
                (s1_res.concentrate_flow_m3_hr * s1_res.concentrate_tds_mg_l +
                 s2_res.concentrate_flow_m3_hr * s2_res.concentrate_tds_mg_l) / final_qr_m3_hr
            )
        else:
            raise ValueError(f"Unsupported topology: '{self.topology}'")

        # Global metrics
        overall_wr_pct = (overall_qp_m3_hr / feed_flow_m3_hr) * 100.0 if feed_flow_m3_hr > 0 else 0.0
        overall_sr_pct = (1.0 - overall_cp_mg_l / feed_tds_mg_l) * 100.0 if feed_tds_mg_l > 0 else 100.0
        avg_flux_lmh = (overall_qp_m3_hr * 1000.0) / self.total_area_m2
        system_sec = (total_elec_power_kw / overall_qp_m3_hr) if overall_qp_m3_hr > 0 else 0.0

        # Mass Balance Residuals across System
        q_f_s = feed_flow_m3_hr / 3600.0
        q_p_s = overall_qp_m3_hr / 3600.0
        q_r_s = final_qr_m3_hr / 3600.0
        water_res = abs(q_f_s - (q_p_s + q_r_s))
        water_res_pct = (water_res / q_f_s) * 100.0 if q_f_s > 0 else 0.0

        c_f_kg = feed_tds_mg_l * 1.0e-3
        c_p_kg = overall_cp_mg_l * 1.0e-3
        c_r_kg = final_cr_mg_l * 1.0e-3
        solute_res = abs((q_f_s * c_f_kg) - (q_p_s * c_p_kg + q_r_s * c_r_kg))
        solute_res_pct = (solute_res / (q_f_s * c_f_kg)) * 100.0 if (q_f_s * c_f_kg) > 0 else 0.0

        # Level B Water Quality Tracking
        if feed_quality_stream is not None:
            perm_qual, conc_qual = compute_water_quality_split(
                feed_stream=feed_quality_stream,
                permeate_flow_m3_s=q_p_s,
                permeate_tds_mg_l=overall_cp_mg_l,
                rejection_profile=rejection_profile
            )
        else:
            feed_qual_stream = WaterQualityStream(
                flow_m3_s=q_f_s,
                tds_mg_l=feed_tds_mg_l,
                temperature_celsius=temperature_celsius,
                pressure_bar=stage_pressures_bar[0]
            )
            perm_qual, conc_qual = compute_water_quality_split(
                feed_stream=feed_qual_stream,
                permeate_flow_m3_s=q_p_s,
                permeate_tds_mg_l=overall_cp_mg_l,
                rejection_profile=rejection_profile
            )
            feed_quality_stream = feed_qual_stream

        sys_res = SystemResult(
            system_name=self.name,
            topology=self.topology,
            num_stages=len(self.stages),
            total_elements=self.total_elements,
            total_membrane_area_m2=self.total_area_m2,
            feed_flow_m3_hr=feed_flow_m3_hr,
            feed_tds_mg_l=feed_tds_mg_l,
            feed_pressure_bar=stage_pressures_bar[0],
            temperature_celsius=temperature_celsius,
            permeate_flow_m3_hr=overall_qp_m3_hr,
            permeate_tds_mg_l=overall_cp_mg_l,
            concentrate_flow_m3_hr=final_qr_m3_hr,
            concentrate_tds_mg_l=final_cr_mg_l,
            overall_water_recovery_percent=overall_wr_pct,
            overall_salt_rejection_percent=overall_sr_pct,
            average_system_flux_lmh=avg_flux_lmh,
            total_electrical_power_kw=total_elec_power_kw,
            system_sec_kwh_per_m3=system_sec,
            stage_results=stage_results,
            feed_quality=feed_quality_stream,
            permeate_quality=perm_qual,
            concentrate_quality=conc_qual,
            water_mass_balance_error_m3_s=water_res,
            water_mass_balance_error_percent=water_res_pct,
            solute_mass_balance_error_kg_s=solute_res,
            solute_mass_balance_error_percent=solute_res_pct,
            converged=all(s.converged for s in stage_results)
        )
        
        self.last_result = sys_res
        return sys_res

    def __repr__(self) -> str:
        return f"ROSystem(name='{self.name}', topology='{self.topology}', stages={len(self.stages)}, total_elements={self.total_elements})"
