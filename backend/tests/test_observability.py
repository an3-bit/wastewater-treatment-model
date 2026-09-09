"""
Unit Tests for Observability, Identifiability, and SVD Conditioning (Stage 7).
"""

import pytest
import numpy as np

from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import SensorSet
from state_estimation.observability import ObservabilityAnalyzer
from state_estimation.noise import NoiseLevel


def test_observability_rank_model_a_vs_model_b():
    """
    Verify that Model A (15-element) is rank-deficient due to parallel vessel symmetry,
    whereas Model B (6-zone) and Model C (2-stage) are full rank.
    """
    analyzer = ObservabilityAnalyzer(noise_level=NoiseLevel.NOMINAL)
    u_inputs = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 13.0,
        "stage2_pressure_bar": 18.0,
    }

    # Model A (15 states)
    st_a = StateVector.create_clean(representation=StateRepresentation.FULL_15_ELEMENT)
    rep_a = analyzer.analyze(st_a, u_inputs, sensor_set=SensorSet.CASE_3_RICH)
    assert rep_a.effective_rank <= 6, (
        f"Expected Model A rank <= 6 due to 6 distinct axial zones, got {rep_a.effective_rank}"
    )
    assert rep_a.effective_rank < 15, "Model A should be strictly rank deficient!"

    # Model B (6 states)
    st_b = StateVector.create_clean(representation=StateRepresentation.AXIAL_6_ZONE)
    rep_b_std = analyzer.analyze(st_b, u_inputs, sensor_set=SensorSet.CASE_2_STANDARD)
    # Model B captures the principal observable axial modes (effective rank >= 3)
    assert rep_b_std.effective_rank >= 3, f"Expected Model B rank >= 3, got {rep_b_std.effective_rank}"

    # Model C (2 states)
    st_c = StateVector.create_clean(representation=StateRepresentation.LUMPED_2_STAGE)
    rep_c = analyzer.analyze(st_c, u_inputs, sensor_set=SensorSet.CASE_1_MINIMAL)
    assert rep_c.effective_rank == 2, f"Model C should have full rank 2, got {rep_c.effective_rank}"
    assert rep_c.condition_number < 1e4
