"""
Unit tests for Stage 3 Latin Hypercube Sampling and OOD generator.
"""

import pytest
import numpy as np
import pandas as pd
from data_generation.sampling import (
    LatinHypercubeSampler,
    generate_ood_samples,
    OperatingDomainBounds,
    OODDomainBounds,
    FEATURE_ROLES,
    NON_CAUSAL_FEATURES,
)


def test_lhs_sampler_dimensions_and_reproducibility():
    """Verify that LHS generates requested sample count, columns, and is deterministic."""
    sampler1 = LatinHypercubeSampler(seed=42)
    df1 = sampler1.generate_samples(n_samples=100)

    sampler2 = LatinHypercubeSampler(seed=42)
    df2 = sampler2.generate_samples(n_samples=100)

    assert len(df1) == 100
    assert len(df1.columns) == 7
    pd.testing.assert_frame_equal(df1, df2)


def test_lhs_bounds_and_constraints():
    """Verify that all sampled variables lie within declared physical bounds and P2 >= P1."""
    bounds = OperatingDomainBounds()
    sampler = LatinHypercubeSampler(bounds=bounds, seed=123)
    df = sampler.generate_samples(n_samples=500)

    assert df["feed_flow_m3h"].min() >= bounds.flow_min
    assert df["feed_flow_m3h"].max() <= bounds.flow_max

    assert df["feed_tds_mgL"].min() >= bounds.tds_min
    assert df["feed_tds_mgL"].max() <= bounds.tds_max

    assert df["feed_cod_mgL"].min() >= bounds.cod_min
    assert df["feed_cod_mgL"].max() <= bounds.cod_max

    assert df["feed_pH"].min() >= bounds.ph_min
    assert df["feed_pH"].max() <= bounds.ph_max

    assert df["temperature_C"].min() >= bounds.temp_min
    assert df["temperature_C"].max() <= bounds.temp_max

    assert df["stage1_pressure_bar"].min() >= bounds.p1_min
    assert df["stage1_pressure_bar"].max() <= bounds.p1_max

    assert df["stage2_pressure_bar"].min() >= bounds.p2_min
    assert df["stage2_pressure_bar"].max() <= bounds.p_limit_max

    # Constraint check: P2 >= P1 across all rows
    assert (df["stage2_pressure_bar"] >= df["stage1_pressure_bar"]).all()


def test_ood_sample_generation():
    """Verify Out-Of-Distribution (OOD) scenarios fall into extreme ranges."""
    b = OODDomainBounds()
    df_ood = generate_ood_samples(n_samples=50, bounds=b, seed=99)

    assert len(df_ood) == 50
    assert df_ood["feed_tds_mgL"].min() >= 3200.0
    assert df_ood["feed_flow_m3h"].min() >= 42.0
    assert df_ood["temperature_C"].min() >= 36.0
    assert (df_ood["stage2_pressure_bar"] >= df_ood["stage1_pressure_bar"]).all()


def test_non_causal_feature_annotations():
    """Verify that COD and pH are explicitly designated as non-causal descriptors."""
    assert "feed_cod_mgL" in NON_CAUSAL_FEATURES
    assert "feed_pH" in NON_CAUSAL_FEATURES
    assert "NON-CAUSAL" in FEATURE_ROLES["feed_cod_mgL"]
    assert "NON-CAUSAL" in FEATURE_ROLES["feed_pH"]
