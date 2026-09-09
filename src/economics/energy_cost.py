"""
Energy Cost Module for Stage 8 Techno-Economic Analysis.

Calculates electricity operating expenditure for high-pressure feed pumps and interstage booster pumps.
"""

from dataclasses import dataclass
from economics.cost_config import EconomicConfig


@dataclass
class EnergyCostResult:
    total_energy_kwh: float
    electricity_cost_kes: float
    permeate_volume_m3: float
    sec_kwh_m3: float
    energy_cost_per_m3_kes: float


def calculate_energy_cost(
    total_energy_kwh: float,
    permeate_volume_m3: float,
    config: EconomicConfig,
) -> EnergyCostResult:
    """
    Compute total electricity cost for RO plant operations.
    
    C_energy = E_total * C_electricity
    """
    kwh = max(0.0, float(total_energy_kwh))
    vol = max(0.0, float(permeate_volume_m3))
    cost = kwh * config.electricity_rate_kes_kwh
    sec = (kwh / vol) if vol > 0 else 0.0
    cost_per_m3 = (cost / vol) if vol > 0 else 0.0

    return EnergyCostResult(
        total_energy_kwh=kwh,
        electricity_cost_kes=cost,
        permeate_volume_m3=vol,
        sec_kwh_m3=sec,
        energy_cost_per_m3_kes=cost_per_m3,
    )
