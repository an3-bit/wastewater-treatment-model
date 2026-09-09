"""
Cleaning Cost Module for Stage 8 Techno-Economic Analysis.

Itemizes chemical, flush water, electrical energy, direct labor, and downtime costs for CIP events.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from economics.cost_config import EconomicConfig


@dataclass
class CIPEventCost:
    event_index: int
    time_hours: float
    chemical_cost_kes: float
    water_cost_kes: float
    energy_cost_kes: float
    labour_cost_kes: float
    downtime_cost_kes: float
    total_cost_kes: float


@dataclass
class AnnualCleaningCostResult:
    number_of_cleanings: int
    total_chemical_cost_kes: float
    total_water_cost_kes: float
    total_energy_cost_kes: float
    total_labour_cost_kes: float
    total_downtime_cost_kes: float
    total_cip_cost_kes: float
    total_downtime_hours: float
    events: List[CIPEventCost]


def calculate_single_cip_cost(
    event_index: int,
    time_hours: float,
    config: EconomicConfig,
) -> CIPEventCost:
    """
    Calculate the itemized cost for a single Cleaning-in-Place procedure.
    """
    chem = config.cip_chemical_cost_per_event_kes
    water = config.cip_water_volume_m3 * config.water_purchase_cost_kes_m3
    energy = config.cip_energy_kwh * config.electricity_rate_kes_kwh
    labour = config.cip_labour_hours * config.cip_labour_rate_kes_h
    downtime = config.cleaning_duration_hours * config.downtime_lost_revenue_rate_kes_h
    total = chem + water + energy + labour + downtime

    return CIPEventCost(
        event_index=event_index,
        time_hours=time_hours,
        chemical_cost_kes=chem,
        water_cost_kes=water,
        energy_cost_kes=energy,
        labour_cost_kes=labour,
        downtime_cost_kes=downtime,
        total_cost_kes=total,
    )


def calculate_annual_cleaning_costs(
    cleaning_times_hours: List[float],
    config: EconomicConfig,
) -> AnnualCleaningCostResult:
    """
    Compute cumulative annual CIP costs across all cleaning events.
    """
    events: List[CIPEventCost] = []
    total_chem = 0.0
    total_water = 0.0
    total_energy = 0.0
    total_labour = 0.0
    total_downtime = 0.0
    total_cost = 0.0

    for idx, t_h in enumerate(cleaning_times_hours):
        ev = calculate_single_cip_cost(idx + 1, t_h, config)
        events.append(ev)
        total_chem += ev.chemical_cost_kes
        total_water += ev.water_cost_kes
        total_energy += ev.energy_cost_kes
        total_labour += ev.labour_cost_kes
        total_downtime += ev.downtime_cost_kes
        total_cost += ev.total_cost_kes

    num_events = len(cleaning_times_hours)
    total_downtime_h = num_events * config.cleaning_duration_hours

    return AnnualCleaningCostResult(
        number_of_cleanings=num_events,
        total_chemical_cost_kes=total_chem,
        total_water_cost_kes=total_water,
        total_energy_cost_kes=total_energy,
        total_labour_cost_kes=total_labour,
        total_downtime_cost_kes=total_downtime,
        total_cip_cost_kes=total_cost,
        total_downtime_hours=total_downtime_h,
        events=events,
    )
