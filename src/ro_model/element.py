"""
Membrane Element Class and Single-Element Solver Wrapper.

Encapsulates individual spiral-wound reverse osmosis membrane element properties,
operating conditions, and solution-diffusion transport calculations.
"""

from typing import Optional, Dict, Any
import numpy as np

from ro_model.units import (
    bar_to_pa,
    pa_to_bar,
    m3_per_s_to_m3_per_hr,
    m_per_s_to_lmh,
    kg_per_m3_to_mg_per_l,
    mg_per_l_to_kg_per_m3
)
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig
)
from ro_model.validation import SimulationResult
from ro_model.water_quality import WaterQualityStream


class MembraneElement:
    """
    Object-oriented model of an individual spiral-wound RO membrane element.
    """
    def __init__(
        self,
        properties: Optional[MembraneElementProperties] = None,
        config: Optional[SimulationConfig] = None,
        element_index: int = 1
    ) -> None:
        self.properties = properties or MembraneElementProperties()
        self.config = config or SimulationConfig()
        self.element_index = element_index
        self.last_result: Optional[SimulationResult] = None

    def solve(
        self,
        conditions: OperatingConditions,
        config_override: Optional[SimulationConfig] = None
    ) -> SimulationResult:
        """
        Solve the nonlinear coupled transport equations for this single element.
        """
        from ro_model.solver import solve_membrane_element
        cfg = config_override or self.config
        res = solve_membrane_element(self, conditions, cfg)
        self.last_result = res
        return res

    def solve_stream(
        self,
        feed_stream: WaterQualityStream,
        pressure_bar: float,
        config_override: Optional[SimulationConfig] = None
    ) -> SimulationResult:
        """
        Solve element performance using a WaterQualityStream input.
        """
        from ro_model.solver import simulate_ro
        cfg = config_override or self.config
        res = simulate_ro(
            feed_flow=feed_stream.flow_m3_hr,
            feed_tds=feed_stream.tds_mg_l,
            pressure=pressure_bar,
            pressure_unit="bar",
            temperature=feed_stream.temperature_celsius,
            membrane_properties=self.properties,
            config=cfg
        )
        self.last_result = res
        return res

    def __repr__(self) -> str:
        return (
            f"MembraneElement(index={self.element_index}, name='{self.properties.name}', "
            f"area={self.properties.membrane_area_m2} m², "
            f"Aw={self.properties.Aw_m_pa_s:.2e} m/(Pa·s), "
            f"As={self.properties.As_m_s:.2e} m/s)"
        )
