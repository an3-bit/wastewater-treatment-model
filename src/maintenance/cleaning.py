"""
Maintenance and Chemical Cleaning-In-Place (CIP) Event Engine for Stage 8.

Models discrete chemical cleaning events, tracking resistance removal, chemical costs,
energy consumption, flush water demand, and downtime duration.
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
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


class MembraneCleaningManager:
    """
    Manages and executes CIP cleaning events on physical and virtual membrane states.
    """
    def __init__(
        self,
        config: EconomicConfig,
        nominal_efficiency: float = 0.90,
        cleaning_duration_hours: float = 4.0,
    ) -> None:
        self.config = config
        self.nominal_efficiency = max(0.1, min(1.0, float(nominal_efficiency)))
        self.cleaning_duration_hours = max(0.5, float(cleaning_duration_hours))
        self.history: List[CleaningEventExecution] = []

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
        """Trigger cleaning when permeability decline exceeds a configured benchmark threshold."""
        return current_permeability_decline_pct >= decline_threshold_pct

    def execute_cleaning(
        self,
        element_rf_values: np.ndarray,
        current_hour: float,
        trigger_reason: str = "Supervisory Decision",
        efficiency_override: Optional[float] = None,
    ) -> Tuple[np.ndarray, CleaningEventExecution]:
        """
        Execute cleaning event on array of 15 element Rf values or 6-zone Rf values.
        
        Rf_after = Rf_before * (1 - eta_clean)
        """
        eta = self.nominal_efficiency if efficiency_override is None else max(0.1, min(1.0, float(efficiency_override)))
        rf_before_mean = float(np.mean(element_rf_values))
        
        # Apply physical resistance recovery
        rf_after = element_rf_values * (1.0 - eta)
        rf_after_mean = float(np.mean(rf_after))

        event_id = len(self.history) + 1
        cost_breakdown = calculate_single_cip_cost(event_id, current_hour, self.config)

        execution = CleaningEventExecution(
            event_id=event_id,
            trigger_hour=current_hour,
            trigger_reason=trigger_reason,
            rf_before_mean=rf_before_mean,
            rf_after_mean=rf_after_mean,
            efficiency=eta,
            duration_hours=self.cleaning_duration_hours,
            cost=cost_breakdown,
        )
        self.history.append(execution)
        return rf_after, execution
