"""
Pressure Vessel Module for Reverse Osmosis Membranes in Series.

Models a single pressure vessel containing N spiral-wound RO membrane elements
connected hydraulically in series:
- Feed enters Element 1.
- Element 1 concentrate becomes Element 2 feed (with channel pressure drop).
- Element 2 concentrate becomes Element 3 feed.
- Permeate flows from all elements are combined into a common central collector tube.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import numpy as np

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    m3_per_s_to_m3_per_hr,
    m3_per_hr_to_m3_per_s,
    m_per_s_to_lmh,
    mg_per_l_to_kg_per_m3,
    kg_per_m3_to_mg_per_l
)
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig
)
from ro_model.element import MembraneElement
from ro_model.validation import SimulationResult
from ro_model.water_quality import WaterQualityStream, compute_water_quality_split


@dataclass
class VesselResult:
    """
    Consolidated performance results for a single pressure vessel with N elements in series.
    """
    vessel_id: str
    num_elements: int
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
    
    # Separation & Flux Performance
    water_recovery_percent: float
    salt_rejection_percent: float
    average_water_flux_lmh: float
    total_pressure_drop_bar: float
    
    # Mass Balance Residuals
    water_mass_balance_error_m3_s: float
    water_mass_balance_error_percent: float
    solute_mass_balance_error_kg_s: float
    solute_mass_balance_error_percent: float
    
    # Detailed Element Results
    element_results: List[SimulationResult] = field(default_factory=list)
    converged: bool = True


class PressureVessel:
    """
    Object-oriented model of a multi-element Reverse Osmosis Pressure Vessel.
    """
    def __init__(
        self,
        name: str = "Vessel_1",
        num_elements: int = 3,
        element_properties: Optional[MembraneElementProperties] = None,
        config: Optional[SimulationConfig] = None,
        element_pressure_drop_bar: float = 0.15
    ) -> None:
        self.name = name
        self.num_elements = num_elements
        self.element_properties = element_properties or MembraneElementProperties()
        self.config = config or SimulationConfig()
        self.element_pressure_drop_bar = element_pressure_drop_bar
        
        # Instantiate series elements
        self.elements: List[MembraneElement] = [
            MembraneElement(
                properties=self.element_properties,
                config=self.config,
                element_index=i + 1
            )
            for i in range(num_elements)
        ]
        self.last_result: Optional[VesselResult] = None

    def solve(
        self,
        feed_flow_m3_hr: float,
        feed_tds_mg_l: float,
        feed_pressure_bar: float,
        temperature_celsius: float = 25.0,
        permeate_backpressure_bar: float = 1.01325
    ) -> VesselResult:
        """
        Solve series element transport and hydraulics sequentially through the vessel.
        """
        curr_qf_m3_hr = feed_flow_m3_hr
        curr_cf_mg_l = feed_tds_mg_l
        curr_pf_bar = feed_pressure_bar
        
        elem_results: List[SimulationResult] = []
        total_qp_m3_s = 0.0
        solute_permeate_mass_kg_s = 0.0
        
        for i, elem in enumerate(self.elements):
            if curr_pf_bar <= 1.05:
                raise ValueError(
                    f"Pressure entering element {i+1} ({curr_pf_bar:.2f} bar) is too low for RO operation."
                )
            if curr_qf_m3_hr <= 0:
                raise ValueError(
                    f"Feed flow entering element {i+1} ({curr_qf_m3_hr:.4f} m³/h) is non-positive."
                )
                
            cond = OperatingConditions.from_engineering_units(
                feed_flow_m3_hr=curr_qf_m3_hr,
                feed_tds_mg_l=curr_cf_mg_l,
                feed_pressure_bar=curr_pf_bar,
                temperature_celsius=temperature_celsius,
                permeate_pressure_bar=permeate_backpressure_bar
            )
            
            res = elem.solve(cond)
            elem_results.append(res)
            
            total_qp_m3_s += res.permeate_flow_m3_s
            solute_permeate_mass_kg_s += (res.permeate_flow_m3_s * res.permeate_tds_kg_m3)
            
            # Update feed stream for subsequent element
            curr_qf_m3_hr = res.concentrate_flow_m3_hr
            curr_cf_mg_l = res.concentrate_tds_mg_l
            curr_pf_bar = max(curr_pf_bar - self.element_pressure_drop_bar, 1.01325)

        # Aggregate vessel results
        total_area = self.num_elements * self.element_properties.membrane_area_m2
        total_qp_m3_hr = total_qp_m3_s * 3600.0
        vessel_cp_kg_m3 = (solute_permeate_mass_kg_s / total_qp_m3_s) if total_qp_m3_s > 0 else 0.0
        vessel_cp_mg_l = vessel_cp_kg_m3 * 1000.0
        
        final_qr_m3_hr = elem_results[-1].concentrate_flow_m3_hr
        final_cr_mg_l = elem_results[-1].concentrate_tds_mg_l
        final_pr_bar = elem_results[-1].feed_pressure_bar - self.element_pressure_drop_bar
        
        recovery_frac = (total_qp_m3_hr / feed_flow_m3_hr) if feed_flow_m3_hr > 0 else 0.0
        rejection_frac = 1.0 - (vessel_cp_mg_l / feed_tds_mg_l) if feed_tds_mg_l > 0 else 1.0
        avg_flux_lmh = (total_qp_m3_hr * 1000.0) / total_area
        total_dp_bar = feed_pressure_bar - final_pr_bar
        
        # Mass balance validation across vessel
        q_f_m3_s = feed_flow_m3_hr / 3600.0
        q_r_m3_s = final_qr_m3_hr / 3600.0
        water_res = abs(q_f_m3_s - (total_qp_m3_s + q_r_m3_s))
        water_res_pct = (water_res / q_f_m3_s) * 100.0 if q_f_m3_s > 0 else 0.0
        
        c_f_kg_m3 = feed_tds_mg_l * 1.0e-3
        c_r_kg_m3 = final_cr_mg_l * 1.0e-3
        solute_res = abs((q_f_m3_s * c_f_kg_m3) - (solute_permeate_mass_kg_s + q_r_m3_s * c_r_kg_m3))
        solute_res_pct = (solute_res / (q_f_m3_s * c_f_kg_m3)) * 100.0 if (q_f_m3_s * c_f_kg_m3) > 0 else 0.0
        
        v_res = VesselResult(
            vessel_id=self.name,
            num_elements=self.num_elements,
            total_membrane_area_m2=total_area,
            feed_flow_m3_hr=feed_flow_m3_hr,
            feed_tds_mg_l=feed_tds_mg_l,
            feed_pressure_bar=feed_pressure_bar,
            temperature_celsius=temperature_celsius,
            permeate_flow_m3_hr=total_qp_m3_hr,
            permeate_tds_mg_l=vessel_cp_mg_l,
            concentrate_flow_m3_hr=final_qr_m3_hr,
            concentrate_tds_mg_l=final_cr_mg_l,
            concentrate_pressure_bar=final_pr_bar,
            water_recovery_percent=recovery_frac * 100.0,
            salt_rejection_percent=rejection_frac * 100.0,
            average_water_flux_lmh=avg_flux_lmh,
            total_pressure_drop_bar=total_dp_bar,
            water_mass_balance_error_m3_s=water_res,
            water_mass_balance_error_percent=water_res_pct,
            solute_mass_balance_error_kg_s=solute_res,
            solute_mass_balance_error_percent=solute_res_pct,
            element_results=elem_results,
            converged=all(r.converged for r in elem_results)
        )
        
        self.last_result = v_res
        return v_res

    def __repr__(self) -> str:
        return f"PressureVessel(name='{self.name}', elements={self.num_elements}, area={self.num_elements * self.element_properties.membrane_area_m2} m²)"
