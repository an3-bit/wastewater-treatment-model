"""
Reverse Osmosis Stage Module (Parallel Pressure Vessels).

Models an RO Stage consisting of M parallel pressure vessels, each housing N
spiral-wound membrane elements in series.
"""

from typing import Optional, List, Dict, Any
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
from ro_model.vessel import PressureVessel, VesselResult
from ro_model.energy import calculate_pump_energy, PumpEnergyResult


@dataclass
class StageResult:
    """
    Consolidated performance metrics for an entire RO stage (parallel pressure vessels).
    """
    stage_name: str
    parallel_vessels: int
    elements_per_vessel: int
    total_elements: int
    total_membrane_area_m2: float
    
    # Inlet Conditions
    feed_flow_m3_hr: float
    feed_tds_mg_l: float
    feed_pressure_bar: float
    temperature_celsius: float
    
    # Outlet Streams
    permeate_flow_m3_hr: float
    permeate_tds_mg_l: float
    concentrate_flow_m3_hr: float
    concentrate_tds_mg_l: float
    concentrate_pressure_bar: float
    
    # Performance Metrics
    stage_water_recovery_percent: float
    stage_salt_rejection_percent: float
    stage_average_flux_lmh: float
    stage_pressure_drop_bar: float
    
    # Energy
    hydraulic_power_kw: float
    electrical_power_kw: float
    sec_kwh_per_m3: float
    
    # Mass Balance Residuals
    water_mass_balance_error_m3_s: float
    water_mass_balance_error_percent: float
    solute_mass_balance_error_kg_s: float
    solute_mass_balance_error_percent: float
    
    # Vessel Details
    vessel_result: Optional[VesselResult] = None
    converged: bool = True


class ROStage:
    """
    Model of an RO stage with M parallel pressure vessels.
    """
    def __init__(
        self,
        name: str = "Stage_1",
        parallel_vessels: int = 4,
        elements_per_vessel: int = 3,
        element_properties: Optional[MembraneElementProperties] = None,
        config: Optional[SimulationConfig] = None,
        element_pressure_drop_bar: float = 0.15
    ) -> None:
        self.name = name
        self.parallel_vessels = parallel_vessels
        self.elements_per_vessel = elements_per_vessel
        self.element_properties = element_properties or MembraneElementProperties()
        self.config = config or SimulationConfig()
        self.element_pressure_drop_bar = element_pressure_drop_bar
        
        # Reference vessel prototype
        self.vessel_prototype = PressureVessel(
            name=f"{name}_VesselPrototype",
            num_elements=elements_per_vessel,
            element_properties=self.element_properties,
            config=self.config,
            element_pressure_drop_bar=element_pressure_drop_bar
        )
        self.last_result: Optional[StageResult] = None

    @property
    def total_elements(self) -> int:
        """Total number of elements in stage."""
        return self.parallel_vessels * self.elements_per_vessel

    @property
    def total_area_m2(self) -> float:
        """Total active membrane area in stage."""
        return self.total_elements * self.element_properties.membrane_area_m2

    def solve(
        self,
        feed_flow_m3_hr: float,
        feed_tds_mg_l: float,
        feed_pressure_bar: float,
        temperature_celsius: float = 25.0,
        inlet_suction_pressure_bar: float = 1.01325,
        permeate_backpressure_bar: float = 1.01325
    ) -> StageResult:
        """
        Solve stage hydraulics and separation across all parallel vessels.
        """
        if self.parallel_vessels <= 0:
            raise ValueError(f"parallel_vessels must be >= 1, got {self.parallel_vessels}")
            
        # Feed flow distributed evenly to all parallel vessels
        vessel_qf_m3_hr = feed_flow_m3_hr / self.parallel_vessels
        
        v_res = self.vessel_prototype.solve(
            feed_flow_m3_hr=vessel_qf_m3_hr,
            feed_tds_mg_l=feed_tds_mg_l,
            feed_pressure_bar=feed_pressure_bar,
            temperature_celsius=temperature_celsius,
            permeate_backpressure_bar=permeate_backpressure_bar
        )
        
        # Aggregate stage totals
        stage_qp_m3_hr = v_res.permeate_flow_m3_hr * self.parallel_vessels
        stage_qr_m3_hr = v_res.concentrate_flow_m3_hr * self.parallel_vessels
        stage_cp_mg_l = v_res.permeate_tds_mg_l
        stage_cr_mg_l = v_res.concentrate_tds_mg_l
        stage_pr_bar = v_res.concentrate_pressure_bar
        
        stage_wr_pct = (stage_qp_m3_hr / feed_flow_m3_hr) * 100.0 if feed_flow_m3_hr > 0 else 0.0
        stage_sr_pct = (1.0 - stage_cp_mg_l / feed_tds_mg_l) * 100.0 if feed_tds_mg_l > 0 else 100.0
        stage_avg_flux_lmh = (stage_qp_m3_hr * 1000.0) / self.total_area_m2
        
        # Energy computation for stage pump
        q_f_s = m3_per_hr_to_m3_per_s(feed_flow_m3_hr)
        q_p_s = m3_per_hr_to_m3_per_s(stage_qp_m3_hr)
        p_feed_pa = bar_to_pa(feed_pressure_bar)
        p_inlet_pa = bar_to_pa(inlet_suction_pressure_bar)
        
        pump_res = calculate_pump_energy(
            feed_flow_m3_s=q_f_s,
            permeate_flow_m3_s=q_p_s,
            feed_pressure_pa=p_feed_pa,
            inlet_feed_pressure_pa=p_inlet_pa,
            pump_efficiency=self.config.pump_efficiency
        )
        
        # Mass balance verification
        q_r_s = m3_per_hr_to_m3_per_s(stage_qr_m3_hr)
        water_res = abs(q_f_s - (q_p_s + q_r_s))
        water_res_pct = (water_res / q_f_s) * 100.0 if q_f_s > 0 else 0.0
        
        c_f_kg_m3 = feed_tds_mg_l * 1.0e-3
        c_p_kg_m3 = stage_cp_mg_l * 1.0e-3
        c_r_kg_m3 = stage_cr_mg_l * 1.0e-3
        solute_res = abs((q_f_s * c_f_kg_m3) - (q_p_s * c_p_kg_m3 + q_r_s * c_r_kg_m3))
        solute_res_pct = (solute_res / (q_f_s * c_f_kg_m3)) * 100.0 if (q_f_s * c_f_kg_m3) > 0 else 0.0
        
        s_res = StageResult(
            stage_name=self.name,
            parallel_vessels=self.parallel_vessels,
            elements_per_vessel=self.elements_per_vessel,
            total_elements=self.total_elements,
            total_membrane_area_m2=self.total_area_m2,
            feed_flow_m3_hr=feed_flow_m3_hr,
            feed_tds_mg_l=feed_tds_mg_l,
            feed_pressure_bar=feed_pressure_bar,
            temperature_celsius=temperature_celsius,
            permeate_flow_m3_hr=stage_qp_m3_hr,
            permeate_tds_mg_l=stage_cp_mg_l,
            concentrate_flow_m3_hr=stage_qr_m3_hr,
            concentrate_tds_mg_l=stage_cr_mg_l,
            concentrate_pressure_bar=stage_pr_bar,
            stage_water_recovery_percent=stage_wr_pct,
            stage_salt_rejection_percent=stage_sr_pct,
            stage_average_flux_lmh=stage_avg_flux_lmh,
            stage_pressure_drop_bar=feed_pressure_bar - stage_pr_bar,
            hydraulic_power_kw=pump_res.hydraulic_power_kw,
            electrical_power_kw=pump_res.electrical_power_kw,
            sec_kwh_per_m3=pump_res.sec_kwh_per_m3,
            water_mass_balance_error_m3_s=water_res,
            water_mass_balance_error_percent=water_res_pct,
            solute_mass_balance_error_kg_s=solute_res,
            solute_mass_balance_error_percent=solute_res_pct,
            vessel_result=v_res,
            converged=v_res.converged
        )
        
        self.last_result = s_res
        return s_res

    def __repr__(self) -> str:
        return f"ROStage(name='{self.name}', vessels={self.parallel_vessels}, elements_per_vessel={self.elements_per_vessel}, total_elements={self.total_elements})"
