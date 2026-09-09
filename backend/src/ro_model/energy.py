"""
High-Pressure Pump Energy Model and Specific Energy Consumption (SEC) Module.

Calculates:
1. Hydraulic Power:
       P_hydraulic = Q_feed * ΔP_pump  [Watts or kW]
   where:
       ΔP_pump = P_feed - P_inlet_feed
2. Electrical Pump Power:
       P_electric = P_hydraulic / η_pump  [Watts or kW]
3. Specific Energy Consumption (SEC):
       SEC = P_electric / Q_permeate  [kWh/m³ of permeate]

Modeling Assumptions:
    - Default pump isentropic/motor efficiency η_pump = 0.80 (configurable).
    - Energy Recovery Devices (ERDs like isobaric PX or turbines) are omitted in the
      baseline model and can be configured as future extensions.
    - Suction inlet pressure is assumed atmospheric (1.01325 bar) unless specified.
"""

from typing import Optional
from dataclasses import dataclass
from ro_model.units import watts_to_kw, specific_energy_j_to_kwh_per_m3


@dataclass
class PumpEnergyResult:
    """Dataclass holding high-pressure pump energy calculation results."""
    feed_flow_m3_s: float
    permeate_flow_m3_s: float
    delta_p_pump_pa: float
    pump_efficiency: float
    hydraulic_power_w: float
    hydraulic_power_kw: float
    electrical_power_w: float
    electrical_power_kw: float
    sec_kwh_per_m3: float


def calculate_pump_energy(
    feed_flow_m3_s: float,
    permeate_flow_m3_s: float,
    feed_pressure_pa: float,
    inlet_feed_pressure_pa: float = 101325.0,
    pump_efficiency: float = 0.80,
    erd_efficiency: Optional[float] = None,
) -> PumpEnergyResult:
    """
    Calculate high-pressure pump hydraulic power, electrical power, and SEC.

    Args:
        feed_flow_m3_s: Total feed volumetric flow rate [m³/s].
        permeate_flow_m3_s: Permeate volumetric flow rate [m³/s].
        feed_pressure_pa: Feed discharge pressure from HP pump [Pa].
        inlet_feed_pressure_pa: Feed suction pressure before HP pump [Pa] (Default: 101325 Pa).
        pump_efficiency: Pump mechanical/electrical efficiency [-] (Default assumption: 0.80).
        erd_efficiency: Optional Energy Recovery Device efficiency [-] (Default: None).

    Returns:
        PumpEnergyResult dataclass containing all power metrics.

    Raises:
        ValueError: If flows or efficiency are non-physical.
    """
    if feed_flow_m3_s < 0:
        raise ValueError(f"Feed flow must be non-negative, got {feed_flow_m3_s}")
    if permeate_flow_m3_s < 0:
        raise ValueError(f"Permeate flow must be non-negative, got {permeate_flow_m3_s}")
    if pump_efficiency <= 0 or pump_efficiency > 1.0:
        raise ValueError(f"Pump efficiency must be in (0, 1.0], got {pump_efficiency}")

    delta_p_pump = max(feed_pressure_pa - inlet_feed_pressure_pa, 0.0)
    
    # Hydraulic power [W] = Q_f [m³/s] * ΔP [Pa]
    hydraulic_power_w = feed_flow_m3_s * delta_p_pump
    hydraulic_power_kw = watts_to_kw(hydraulic_power_w)
    
    # Electrical power [W] = Hydraulic Power / η_pump
    electrical_power_w = hydraulic_power_w / pump_efficiency
    electrical_power_kw = watts_to_kw(electrical_power_w)
    
    # SEC [kWh/m³] = (P_electric [kW]) / (Q_p [m³/h])
    if permeate_flow_m3_s > 0:
        sec_kwh_per_m3 = (electrical_power_kw) / (permeate_flow_m3_s * 3600.0)
    else:
        sec_kwh_per_m3 = float('inf')
        
    return PumpEnergyResult(
        feed_flow_m3_s=feed_flow_m3_s,
        permeate_flow_m3_s=permeate_flow_m3_s,
        delta_p_pump_pa=delta_p_pump,
        pump_efficiency=pump_efficiency,
        hydraulic_power_w=hydraulic_power_w,
        hydraulic_power_kw=hydraulic_power_kw,
        electrical_power_w=electrical_power_w,
        electrical_power_kw=electrical_power_kw,
        sec_kwh_per_m3=sec_kwh_per_m3
    )
