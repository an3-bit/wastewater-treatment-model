"""
Membrane Element, Operating Conditions, and Configuration Data Models.

Defines:
1. MembraneElementProperties: Intrinsic specifications (Aw, As, Area, Limits).
2. OperatingConditions: Feed flow, TDS, pressure, temperature, permeate backpressure.
3. SimulationConfig: Solver settings, assumptions, CP modes.
4. MembraneElement: Model representation of a single spiral-wound RO element.
5. ROStage & ROTrain: Base classes prepared for future multi-stage industrial plant models.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import yaml

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    m3_per_hr_to_m3_per_s,
    mg_per_l_to_kg_per_m3,
    celsius_to_kelvin,
    aw_bar_to_pa
)


RO_MODEL_VERSION: str = "2.0-pressure-corrected"
AW_AUTHORITATIVE_M_PA_S: float = 9.446312125982804e-12
AW_AUTHORITATIVE_M_BAR_S: float = 9.446312125982804e-07
AW_AUTHORITATIVE_LMH_BAR: float = 3.400672365353809


@dataclass
class MembraneElementProperties:
    """
    Physical and transport properties of an RO membrane element.
    
    Default parameters represent the Toray TML20D-400 low-fouling element
    reconciled against manufacturer standard test performance under the
    authoritative transmembrane differential pressure convention (225 psi = 15.5132 bar).
    """
    name: str = "Toray TML20D-400"
    membrane_area_m2: float = 37.0                # Effective membrane surface area [m²]
    membrane_diameter_m: float = 0.201           # Module outer diameter [m] (8-inch)
    
    # Intrinsic transport parameters from Model Version 2.0 reconciliation
    Aw_m_pa_s: float = AW_AUTHORITATIVE_M_PA_S    # Water permeability [m/(Pa·s)] (9.4463e-7 m/(bar·s))
    As_m_s: float = 1.7827e-8                    # Apparent salt permeability [m/s] (textile baseline)
    
    # Mechanical & operational limits
    max_operating_pressure_pa: float = 4.1e6     # Maximum design pressure [Pa] (41.0 bar)
    nominal_product_flow_m3_day: float = 39.7    # Nominal product/permeate flow [m³/day] (10,500 GPD)
    min_product_flow_m3_day: float = 31.8        # Minimum product/permeate flow [m³/day] (8,400 GPD)
    nominal_water_recovery: float = 0.15         # Nominal single-element test recovery [15%]
    nominal_salt_rejection: float = 0.998        # Nominal salt rejection [99.8%]

    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> "MembraneElementProperties":
        """Instantiate from a configuration dictionary (e.g. loaded from YAML)."""
        src = config.get("source_reported", {})
        
        aw_val = src.get("Aw", 9.08e-5)
        # Convert Aw if supplied in m/(bar·s)
        aw_pa = aw_bar_to_pa(aw_val) if aw_val > 1.0e-7 else aw_val
        
        max_p_bar = src.get("max_operating_pressure_bar", 41.0)
        nom_qp_day = src.get("nominal_product_flow_m3_day", 39.7)
        min_qp_day = src.get("min_product_flow_m3_day", 31.8)
        
        return cls(
            name=config.get("metadata", {}).get("membrane_model", "Toray TML20D-400"),
            membrane_area_m2=float(src.get("membrane_area", 37.0)),
            membrane_diameter_m=float(src.get("membrane_diameter", 0.201)),
            Aw_m_pa_s=float(aw_pa),
            As_m_s=float(src.get("As", 1.1834e-9)),
            max_operating_pressure_pa=bar_to_pa(max_p_bar),
            nominal_product_flow_m3_day=float(nom_qp_day),
            min_product_flow_m3_day=float(min_qp_day),
            nominal_water_recovery=float(src.get("nominal_water_recovery", 0.15)),
            nominal_salt_rejection=float(src.get("nominal_salt_rejection_nom", 0.998))
        )


@dataclass
class OperatingConditions:
    """
    Operating stream conditions entering a membrane unit.
    
    Internal units are strictly SI:
    - feed_flow_m3_s: [m³/s]
    - feed_concentration_kg_m3: [kg/m³] (g/L)
    - feed_pressure_pa: [Pa]
    - temperature_k: [K]
    - permeate_pressure_pa: [Pa]
    """
    feed_flow_m3_s: float
    feed_concentration_kg_m3: float
    feed_pressure_pa: float
    temperature_k: float = 298.15
    permeate_pressure_pa: float = 101325.0
    feed_cod_mg_l: Optional[float] = None
    feed_ph: Optional[float] = None

    @classmethod
    def from_engineering_units(
        cls,
        feed_flow_m3_hr: float,
        feed_tds_mg_l: float,
        feed_pressure_bar: Optional[float] = None,
        feed_pressure_psi: Optional[float] = None,
        temperature_celsius: float = 25.0,
        permeate_pressure_bar: float = 1.01325,
        feed_cod_mg_l: Optional[float] = None,
        feed_ph: Optional[float] = None
    ) -> "OperatingConditions":
        """Construct OperatingConditions from standard engineering units."""
        if feed_pressure_bar is not None:
            p_pa = bar_to_pa(feed_pressure_bar)
        elif feed_pressure_psi is not None:
            from ro_model.units import psi_to_pa
            p_pa = psi_to_pa(feed_pressure_psi)
        else:
            raise ValueError("Must provide either feed_pressure_bar or feed_pressure_psi")
            
        return cls(
            feed_flow_m3_s=m3_per_hr_to_m3_per_s(feed_flow_m3_hr),
            feed_concentration_kg_m3=mg_per_l_to_kg_per_m3(feed_tds_mg_l),
            feed_pressure_pa=p_pa,
            temperature_k=celsius_to_kelvin(temperature_celsius),
            permeate_pressure_pa=bar_to_pa(permeate_pressure_bar),
            feed_cod_mg_l=feed_cod_mg_l,
            feed_ph=feed_ph
        )


@dataclass
class SimulationConfig:
    """
    Configuration parameters and assumptions for the simulation run.
    """
    pump_efficiency: float = 0.80
    vanthoff_factor: float = 2.0
    solute_molar_mass_kg_mol: float = 0.058443
    cp_mode: str = "mode_a"
    mass_transfer_coefficient: float = 5.0e-5
    pressure_drop_pa: float = 0.0
    inlet_pressure_pa: float = 101325.0
    solver_tolerance: float = 1.0e-8
    max_solver_iterations: int = 200
    max_element_recovery: float = 0.30
    warn_on_high_element_recovery: bool = True

    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> "SimulationConfig":
        """Instantiate from config dictionary."""
        asm = config.get("assumptions", {})
        
        p_drop_bar = asm.get("pressure_drop_bar", 0.0)
        p_inlet_bar = asm.get("inlet_feed_pressure_bar", 1.01325)
        
        return cls(
            pump_efficiency=float(asm.get("pump_efficiency", 0.80)),
            vanthoff_factor=float(asm.get("vanthoff_factor", 2.0)),
            solute_molar_mass_kg_mol=float(asm.get("solute_molar_mass_g_mol", 58.44)) * 1.0e-3,
            cp_mode=str(asm.get("cp_mode", "mode_a")),
            mass_transfer_coefficient=float(asm.get("mass_transfer_coefficient", 5.0e-5)),
            pressure_drop_pa=bar_to_pa(p_drop_bar),
            inlet_pressure_pa=bar_to_pa(p_inlet_bar),
            solver_tolerance=float(asm.get("solver_tolerance", 1.0e-8)),
            max_solver_iterations=int(asm.get("max_solver_iterations", 200)),
            max_element_recovery=float(asm.get("max_element_recovery", 0.30)),
            warn_on_high_element_recovery=bool(asm.get("warn_on_high_element_recovery", True))
        )


class MembraneElement:
    """
    Object-oriented representation of an individual spiral-wound RO membrane element.
    """
    def __init__(
        self,
        properties: Optional[MembraneElementProperties] = None,
        config: Optional[SimulationConfig] = None
    ) -> None:
        self.properties = properties or MembraneElementProperties()
        self.config = config or SimulationConfig()

    def __repr__(self) -> str:
        return (
            f"MembraneElement(name='{self.properties.name}', "
            f"area={self.properties.membrane_area_m2} m², "
            f"Aw={self.properties.Aw_m_pa_s:.2e} m/(Pa·s), "
            f"As={self.properties.As_m_s:.2e} m/s)"
        )


class ROStage:
    """
    Abstract architecture placeholder for a multi-element RO stage (Stage 2 extension).
    Encapsulates pressure vessels arranged in parallel with series elements.
    """
    def __init__(self, name: str, elements_in_series: int = 3, parallel_vessels: int = 1) -> None:
        self.name = name
        self.elements_in_series = elements_in_series
        self.parallel_vessels = parallel_vessels
        self.elements: List[MembraneElement] = [
            MembraneElement() for _ in range(elements_in_series)
        ]

    def __repr__(self) -> str:
        return f"ROStage(name='{self.name}', vessels={self.parallel_vessels}, elements_per_vessel={self.elements_in_series})"


class ROTrain:
    """
    Abstract architecture placeholder for multi-stage RO trains (e.g. 2-stage textile plant).
    """
    def __init__(self, name: str, stages: Optional[List[ROStage]] = None) -> None:
        self.name = name
        self.stages = stages or []

    def add_stage(self, stage: ROStage) -> None:
        self.stages.append(stage)
