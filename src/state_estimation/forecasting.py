"""
Virtual Sensor Engine & Remaining-Time Threshold Forecasting (Stage 7).

Provides:
1. Virtual sensor trajectory forward projection from current state estimate
2. Dynamic estimation of remaining time to 5%, 10%, and 15% permeability decline analysis thresholds
3. Lead-time forecasting accuracy evaluation (1h, 3h, 6h, 12h before crossing)
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np

from state_estimation.state_model import (
    StateRepresentation,
    StateVector,
    StateTransitionModel,
)
from fouling.model import FoulingParameters


@dataclass
class ForecastResult:
    forecast_origin_time_hours: float
    current_permeability_decline_pct: float
    forecast_timestamps_hours: List[float]
    predicted_decline_pct_trajectory: List[float]
    predicted_t5_hours: Optional[float] = None
    predicted_t10_hours: Optional[float] = None
    predicted_t15_hours: Optional[float] = None
    remaining_time_to_5pct_hours: Optional[float] = None
    remaining_time_to_10pct_hours: Optional[float] = None
    remaining_time_to_15pct_hours: Optional[float] = None


class VirtualSensorForecaster:
    """
    Simulates projected forward dynamic trajectory from estimated state to forecast threshold arrival.
    """
    def __init__(
        self,
        parameters: Optional[FoulingParameters] = None,
        max_horizon_hours: float = 240.0,
        dt_hours: float = 1.0,
    ) -> None:
        self.parameters = parameters or FoulingParameters.create_default()
        self.max_horizon_hours = float(max_horizon_hours)
        self.dt_hours = float(dt_hours)
        self.transition_model = StateTransitionModel(
            parameters=self.parameters,
            representation=StateRepresentation.AXIAL_6_ZONE,
        )

    def forecast(
        self,
        current_state_estimate: StateVector,
        u_forecast_inputs: Dict[str, float],
        current_time_hours: float = 0.0,
    ) -> ForecastResult:
        """
        Forward project fouling trajectory and determine predicted threshold crossing times.
        """
        # Convert state estimate to AXIAL_6_ZONE for forecasting
        st_curr = StateVector.from_15_element_array(
            current_state_estimate.to_15_element_array(),
            representation=StateRepresentation.AXIAL_6_ZONE,
        )

        temp_c = float(u_forecast_inputs.get("temperature_C", 25.0))
        init_decline = st_curr.get_average_permeability_decline_pct(temp_c)

        timestamps = [current_time_hours]
        declines = [init_decline]

        t5_abs: Optional[float] = current_time_hours if init_decline >= 5.0 else None
        t10_abs: Optional[float] = current_time_hours if init_decline >= 10.0 else None
        t15_abs: Optional[float] = current_time_hours if init_decline >= 15.0 else None

        sim_t = current_time_hours
        while sim_t < (current_time_hours + self.max_horizon_hours):
            st_next = self.transition_model.predict_next_state(
                current_state=st_curr,
                u_inputs=u_forecast_inputs,
                delta_t_hours=self.dt_hours,
            )
            sim_t += self.dt_hours
            next_decline = st_next.get_average_permeability_decline_pct(temp_c)

            timestamps.append(sim_t)
            declines.append(next_decline)

            # Check threshold crossings via linear interpolation
            prev_dec = declines[-2]
            if t5_abs is None and next_decline >= 5.0:
                frac = (5.0 - prev_dec) / (next_decline - prev_dec) if (next_decline > prev_dec) else 0.0
                t5_abs = (sim_t - self.dt_hours) + frac * self.dt_hours

            if t10_abs is None and next_decline >= 10.0:
                frac = (10.0 - prev_dec) / (next_decline - prev_dec) if (next_decline > prev_dec) else 0.0
                t10_abs = (sim_t - self.dt_hours) + frac * self.dt_hours

            if t15_abs is None and next_decline >= 15.0:
                frac = (15.0 - prev_dec) / (next_decline - prev_dec) if (next_decline > prev_dec) else 0.0
                t15_abs = (sim_t - self.dt_hours) + frac * self.dt_hours

            st_curr = st_next

            # If all 3 thresholds crossed, can terminate forecast early
            if t5_abs is not None and t10_abs is not None and t15_abs is not None:
                break

        rem_5 = (t5_abs - current_time_hours) if (t5_abs is not None and t5_abs >= current_time_hours) else 0.0 if t5_abs is not None else None
        rem_10 = (t10_abs - current_time_hours) if (t10_abs is not None and t10_abs >= current_time_hours) else 0.0 if t10_abs is not None else None
        rem_15 = (t15_abs - current_time_hours) if (t15_abs is not None and t15_abs >= current_time_hours) else 0.0 if t15_abs is not None else None

        return ForecastResult(
            forecast_origin_time_hours=current_time_hours,
            current_permeability_decline_pct=init_decline,
            forecast_timestamps_hours=timestamps,
            predicted_decline_pct_trajectory=declines,
            predicted_t5_hours=t5_abs,
            predicted_t10_hours=t10_abs,
            predicted_t15_hours=t15_abs,
            remaining_time_to_5pct_hours=rem_5,
            remaining_time_to_10pct_hours=rem_10,
            remaining_time_to_15pct_hours=rem_15,
        )
