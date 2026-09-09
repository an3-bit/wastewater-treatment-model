"""
Reverse Osmosis (RO) Mechanistic Process Modeling Package.

Physics-based simulation foundation for AI-enabled textile wastewater reuse optimization.
Based on Sowgath, Sarker & Mujtaba (2025).
"""

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
    lmh_to_m_per_s,
    celsius_to_kelvin,
    kelvin_to_celsius
)
from ro_model.osmotic import (
    calculate_osmotic_pressure_pa,
    calculate_osmotic_pressure_bar,
    calculate_osmotic_pressure_derivative
)
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
from ro_model.energy import (
    calculate_pump_energy,
    PumpEnergyResult
)
from ro_model.water_quality import (
    WaterQualityStream,
    ApparentRejectionProfile,
    compute_water_quality_split,
    calculate_apparent_rejection
)
from ro_model.membrane import (
    MembraneElementProperties,
    OperatingConditions,
    SimulationConfig
)
from ro_model.element import MembraneElement
from ro_model.vessel import PressureVessel, VesselResult
from ro_model.stage import ROStage, StageResult
from ro_model.system import ROSystem, SystemResult
from ro_model.solver import (
    solve_membrane_element,
    simulate_ro
)
from ro_model.validation import (
    SimulationResult,
    validate_physical_bounds
)

__all__ = [
    # Units
    "bar_to_pa",
    "pa_to_bar",
    "psi_to_pa",
    "pa_to_psi",
    "m3_per_hr_to_m3_per_s",
    "m3_per_s_to_m3_per_hr",
    "mg_per_l_to_kg_per_m3",
    "kg_per_m3_to_mg_per_l",
    "m_per_s_to_lmh",
    "lmh_to_m_per_s",
    "celsius_to_kelvin",
    "kelvin_to_celsius",
    # Osmotic
    "calculate_osmotic_pressure_pa",
    "calculate_osmotic_pressure_bar",
    "calculate_osmotic_pressure_derivative",
    # Hydraulics
    "calculate_mass_transfer_coefficient",
    "calculate_feed_channel_pressure_drop_pa",
    "ChannelHydraulicProperties",
    # Transport
    "calculate_water_flux",
    "calculate_solute_flux",
    "calculate_membrane_surface_concentration",
    "calculate_permeate_concentration",
    # Energy
    "calculate_pump_energy",
    "PumpEnergyResult",
    # Water Quality
    "WaterQualityStream",
    "ApparentRejectionProfile",
    "compute_water_quality_split",
    "calculate_apparent_rejection",
    # Architecture
    "MembraneElementProperties",
    "OperatingConditions",
    "SimulationConfig",
    "MembraneElement",
    "PressureVessel",
    "VesselResult",
    "ROStage",
    "StageResult",
    "ROSystem",
    "SystemResult",
    # Solver & Validation
    "solve_membrane_element",
    "simulate_ro",
    "SimulationResult",
    "validate_physical_bounds",
]
