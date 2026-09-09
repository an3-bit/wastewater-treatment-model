"""
Downtime and Availability Loss Module for Stage 8.

Calculates the financial opportunity cost of plant outages, maintenance shutdowns,
and cleaning events.
"""

from dataclasses import dataclass
from economics.cost_config import EconomicConfig


@dataclass
class DowntimeCostResult:
    total_downtime_hours: float
    operating_hours: float
    availability_pct: float
    opportunity_cost_kes: float


def calculate_downtime_cost(
    downtime_hours: float,
    total_scheduled_hours: float,
    config: EconomicConfig,
) -> DowntimeCostResult:
    """
    Compute lost production opportunity cost during shutdown periods.
    """
    dt_h = max(0.0, float(downtime_hours))
    sched_h = max(1.0, float(total_scheduled_hours))
    op_h = max(0.0, sched_h - dt_h)
    avail = (op_h / sched_h) * 100.0
    cost = dt_h * config.downtime_lost_revenue_rate_kes_h

    return DowntimeCostResult(
        total_downtime_hours=dt_h,
        operating_hours=op_h,
        availability_pct=avail,
        opportunity_cost_kes=cost,
    )
