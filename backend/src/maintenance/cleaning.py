"""
Maintenance and Chemical Cleaning-In-Place (CIP) Event Engine for Stage 8 and Stage 8B.

Models discrete chemical cleaning events, tracking resistance removal, chemical costs,
energy consumption, flush water demand, downtime duration, cleaning hysteresis, and lockout.
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import numpy as np

from fouling.model import ElementFoulingState, FoulingParameters, resistance_to_permeability
from economics.cost_config import EconomicConfig
from economics.cleaning_cost import CIPEventCost, calculate_single_cip_cost


@dataclass
class CleaningEventExecution:
    event_id: int
    trigger_hour: float
    trigger_reason: str
    rf_before_mean: float
    rf_after_mean: float
    efficiency: float
    duration_hours: float
    cost: CIPEventCost
    interval_since_last_cip_h: Optional[float] = None
    irreversible_rf_added: float = 0.0


@dataclass
class CIPAuditStatistics:
    total_cleanings: int
    total_downtime_hours: float
    mean_interval_hours: float
    median_interval_hours: float
    min_interval_hours: float
    max_interval_hours: float
    mean_decline_before_pct: float
    mean_rf_before: float
    mean_rf_after: float
    total_chemical_cost_kes: float
    total_cip_cost_kes: float


class MembraneCleaningManager:
    """
    Manages and executes CIP cleaning events on physical and virtual membrane states.
    Supports hysteresis, post-CIP lockout, and exploratory irreversible fouling.
    """
    def __init__(
        self,
        config: EconomicConfig,
        nominal_efficiency: float = 0.90,
        cleaning_duration_hours: float = 4.0,
        min_time_between_cip_hours: float = 0.0,
        post_cip_lockout_hours: float = 0.0,
        irreversible_fraction: float = 0.0,
    ) -> None:
        self.config = config
        self.nominal_efficiency = max(0.1, min(1.0, float(nominal_efficiency)))
        self.cleaning_duration_hours = max(0.5, float(cleaning_duration_hours))
        self.min_time_between_cip_hours = max(0.0, float(min_time_between_cip_hours))
        self.post_cip_lockout_hours = max(0.0, float(post_cip_lockout_hours))
        self.irreversible_fraction = max(0.0, min(0.3, float(irreversible_fraction)))
        self.history: List[CleaningEventExecution] = []
        self.last_cleaning_hour: float = -9999.0

    def should_trigger_fixed_interval(
        self,
        current_hour: float,
        last_cleaning_hour: float,
        interval_hours: float = 720.0,  # e.g. monthly ~30 days * 24h
    ) -> bool:
        """Trigger cleaning every fixed operating interval."""
        return (current_hour - last_cleaning_hour) >= interval_hours

    def should_trigger_reactive_threshold(
        self,
        current_permeability_decline_pct: float,
        decline_threshold_pct: float = 15.0,  # t15 threshold benchmark
    ) -> bool:
        """Legacy unconstrained reactive trigger (used to audit threshold chattering)."""
        return current_permeability_decline_pct >= decline_threshold_pct

    def should_trigger_reactive_condition_based(
        self,
        current_hour: float,
        last_cleaning_hour: float,
        current_permeability_decline_pct: float,
        decline_threshold_pct: float = 15.0,
        min_interval_hours: float = 168.0,  # 1 week minimum spacing
        lockout_hours: float = 24.0,        # 24h post-CIP stabilization lockout
    ) -> bool:
        """
        Industrial condition-based cleaning trigger with realistic hysteresis & lockout.
        Prevents rapid chattering while honoring physical decline benchmarks.
        """
        elapsed = current_hour - last_cleaning_hour
        if elapsed < lockout_hours or elapsed < min_interval_hours:
            return False
        return current_permeability_decline_pct >= decline_threshold_pct

    def execute_cleaning(
        self,
        element_rf_values: np.ndarray,
        current_hour: float,
        trigger_reason: str = "Supervisory Decision",
        efficiency_override: Optional[float] = None,
        irreversible_fraction_override: Optional[float] = None,
    ) -> Tuple[np.ndarray, CleaningEventExecution]:
        """
        Execute cleaning event on array of 15 element Rf values or 6-zone Rf values.
        
        Rf_after = Rf_before * (1 - eta_clean) + gamma_irrev * Rf_before
        """
        eta = self.nominal_efficiency if efficiency_override is None else max(0.1, min(1.0, float(efficiency_override)))
        gamma = self.irreversible_fraction if irreversible_fraction_override is None else max(0.0, float(irreversible_fraction_override))
        
        rf_before_mean = float(np.mean(element_rf_values))
        
        # Apply physical resistance recovery with optional irreversible residual
        rf_after = element_rf_values * (1.0 - eta + gamma)
        rf_after = np.maximum(0.0, rf_after)
        rf_after_mean = float(np.mean(rf_after))

        event_id = len(self.history) + 1
        cost_breakdown = calculate_single_cip_cost(event_id, current_hour, self.config)

        interval = (current_hour - self.last_cleaning_hour) if self.history else current_hour

        execution = CleaningEventExecution(
            event_id=event_id,
            trigger_hour=current_hour,
            trigger_reason=trigger_reason,
            rf_before_mean=rf_before_mean,
            rf_after_mean=rf_after_mean,
            efficiency=eta,
            duration_hours=self.cleaning_duration_hours,
            cost=cost_breakdown,
            interval_since_last_cip_h=interval,
            irreversible_rf_added=rf_before_mean * gamma,
        )
        self.history.append(execution)
        self.last_cleaning_hour = current_hour
        return rf_after, execution

    def get_audit_statistics(self) -> CIPAuditStatistics:
        """Compute summary statistical distribution of CIP events."""
        if not self.history:
            return CIPAuditStatistics(
                total_cleanings=0,
                total_downtime_hours=0.0,
                mean_interval_hours=0.0,
                median_interval_hours=0.0,
                min_interval_hours=0.0,
                max_interval_hours=0.0,
                mean_decline_before_pct=0.0,
                mean_rf_before=0.0,
                mean_rf_after=0.0,
                total_chemical_cost_kes=0.0,
                total_cip_cost_kes=0.0,
            )

        intervals = [e.interval_since_last_cip_h for e in self.history if e.interval_since_last_cip_h is not None]
        rf_befores = [e.rf_before_mean for e in self.history]
        rf_afters = [e.rf_after_mean for e in self.history]
        chem_costs = [e.cost.chemical_cost_kes for e in self.history]
        tot_costs = [e.cost.total_cost_kes for e in self.history]

        return CIPAuditStatistics(
            total_cleanings=len(self.history),
            total_downtime_hours=len(self.history) * self.cleaning_duration_hours,
            mean_interval_hours=float(np.mean(intervals)) if intervals else 0.0,
            median_interval_hours=float(np.median(intervals)) if intervals else 0.0,
            min_interval_hours=float(np.min(intervals)) if intervals else 0.0,
            max_interval_hours=float(np.max(intervals)) if intervals else 0.0,
            mean_decline_before_pct=0.0,  # Will be populated from simulator
            mean_rf_before=float(np.mean(rf_befores)),
            mean_rf_after=float(np.mean(rf_afters)),
            total_chemical_cost_kes=float(np.sum(chem_costs)),
            total_cip_cost_kes=float(np.sum(tot_costs)),
        )
