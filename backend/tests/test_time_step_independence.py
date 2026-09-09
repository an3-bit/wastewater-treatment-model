"""
Unit tests for numerical time-step independence across dynamic RO simulation runs.
"""

import pytest
import numpy as np

from fouling.dynamics import DynamicROSimulator


def test_time_step_independence():
    """Verify numerical convergence across delta_t = 0.5h, 1.0h, and 2.0h over a 24h horizon."""
    sim = DynamicROSimulator()

    res_dt05 = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=24.0,
        time_step_hours=0.5,
    )

    res_dt10 = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=24.0,
        time_step_hours=1.0,
    )

    res_dt20 = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=24.0,
        time_step_hours=2.0,
    )

    # Compare 24h cumulative permeate volume
    v05 = res_dt05.total_cumulative_permeate_m3
    v10 = res_dt10.total_cumulative_permeate_m3
    v20 = res_dt20.total_cumulative_permeate_m3

    # Relative difference between dt=0.5h and dt=1.0h must be < 0.1%
    rel_diff_05_10 = abs(v05 - v10) / v05 * 100.0
    assert rel_diff_05_10 < 0.1, f"Time step discrepancy dt=0.5 vs 1.0: {rel_diff_05_10:.4f}%"

    # Relative difference between dt=1.0h and dt=2.0h must be < 0.2%
    rel_diff_10_20 = abs(v10 - v20) / v10 * 100.0
    assert rel_diff_10_20 < 0.2, f"Time step discrepancy dt=1.0 vs 2.0: {rel_diff_10_20:.4f}%"
