"""
Unit tests verifying active solver feedback of fouling accumulation on process performance.
"""

import pytest
import numpy as np

from fouling.dynamics import DynamicROSimulator


def test_fouling_feedback_mode_a():
    """Verify that in Mode A, increasing Rf causes progressive flux and recovery decline."""
    sim = DynamicROSimulator()
    res = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=48.0,
        time_step_hours=2.0,
        operating_mode="MODE_A_FIXED_PRESSURE",
    )

    # Recovery must strictly decrease over time in Mode A
    rec_init = res.states[0].instantaneous_recovery_pct
    rec_final = res.states[-1].instantaneous_recovery_pct
    assert rec_final < rec_init

    # Permeability decline must strictly increase over time
    decline_init = res.states[0].average_permeability_decline_pct
    decline_final = res.states[-1].average_permeability_decline_pct
    assert decline_init == 0.0
    assert decline_final > 0.0

    # Rf across all elements must be positive at final step
    for elem in res.states[-1].element_states:
        assert elem.r_f_m_inv > 0.0
        assert elem.permeability_ratio < 1.0


def test_axial_fouling_distribution():
    """Verify that downstream tail elements experience elevated polarization and distinct fouling."""
    sim = DynamicROSimulator()
    res = sim.simulate(
        strategy_name="BALANCED_KNEE",
        initial_p1_bar=15.05,
        initial_p2_bar=15.80,
        horizon_hours=72.0,
        time_step_hours=4.0,
    )

    final_elem_states = res.states[-1].element_states
    stg1_lead = [s for s in final_elem_states if s.stage_index == 1 and s.element_index == 1][0]
    stg1_tail = [s for s in final_elem_states if s.stage_index == 1 and s.element_index == 3][0]

    # Tail element has higher feed salinity than lead
    assert stg1_tail.local_feed_tds_mg_l > stg1_lead.local_feed_tds_mg_l
    # Lead element has higher flux than tail element
    assert stg1_lead.local_flux_lmh > stg1_tail.local_flux_lmh
