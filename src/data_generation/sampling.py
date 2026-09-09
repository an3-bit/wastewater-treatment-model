"""
Sampling Module for Stage 3 Simulation-Based Dataset Development.

Implements Latin Hypercube Sampling (LHS) via scipy.stats.qmc.LatinHypercube
for broad, space-filling coverage of the 7-dimensional industrial operating domain.

Features:
- feed_flow_m3h: 20.0 - 40.0 m³/h
- feed_tds_mgL: 1500.0 - 3000.0 mg/L
- feed_cod_mgL: 25.0 - 100.0 mg/L [NON-CAUSAL DESCRIPTOR]
- feed_pH: 6.5 - 9.5 [NON-CAUSAL DESCRIPTOR]
- temperature_C: 20.0 - 35.0 °C
- stage1_pressure_bar: 10.0 - 20.0 bar
- stage2_pressure_bar: 14.0 - 28.0 bar (constrained by P2 >= P1, P <= 41 bar)

Also provides Out-Of-Distribution (OOD) scenario generation for future surrogate stress testing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import qmc


FEATURE_ROLES: Dict[str, str] = {
    "feed_flow_m3h": "MECHANISTIC_CAUSAL_INPUT",
    "feed_tds_mgL": "MECHANISTIC_CAUSAL_INPUT",
    "feed_cod_mgL": "NON-CAUSAL DESCRIPTOR IN CURRENT MECHANISTIC MODEL",
    "feed_pH": "NON-CAUSAL DESCRIPTOR IN CURRENT MECHANISTIC MODEL",
    "temperature_C": "MECHANISTIC_CAUSAL_INPUT",
    "stage1_pressure_bar": "MECHANISTIC_CAUSAL_INPUT",
    "stage2_pressure_bar": "MECHANISTIC_CAUSAL_INPUT",
}

NON_CAUSAL_FEATURES: List[str] = [
    "feed_cod_mgL",
    "feed_pH",
]


@dataclass
class OperatingDomainBounds:
    """Defines the bounding box for sampling the 7 operating variables."""
    flow_min: float = 20.0
    flow_max: float = 40.0
    tds_min: float = 1500.0
    tds_max: float = 3000.0
    cod_min: float = 25.0
    cod_max: float = 100.0
    ph_min: float = 6.5
    ph_max: float = 9.5
    temp_min: float = 20.0
    temp_max: float = 35.0
    p1_min: float = 10.0
    p1_max: float = 20.0
    p2_min: float = 14.0
    p2_max: float = 28.0
    p_limit_max: float = 41.0


@dataclass
class OODDomainBounds:
    """Defines Out-Of-Distribution (OOD) boundaries for stress testing."""
    flow_min: float = 42.0
    flow_max: float = 45.0
    tds_min: float = 3200.0
    tds_max: float = 3500.0
    cod_min: float = 110.0
    cod_max: float = 150.0
    ph_min: float = 6.0
    ph_max: float = 10.0
    temp_min: float = 36.0
    temp_max: float = 38.0
    p1_min: float = 12.0
    p1_max: float = 20.0
    p2_min: float = 16.0
    p2_max: float = 30.0
    p_limit_max: float = 41.0


class LatinHypercubeSampler:
    """
    Generates multidimensional space-filling operating scenarios using
    scipy.stats.qmc.LatinHypercube.
    """

    def __init__(
        self,
        bounds: Optional[OperatingDomainBounds] = None,
        seed: int = 42,
    ):
        self.bounds = bounds or OperatingDomainBounds()
        self.seed = seed
        self.dim = 7  # 7 sampled input features

    def generate_samples(self, n_samples: int = 5000) -> pd.DataFrame:
        """
        Generate n_samples using Latin Hypercube Sampling.
        
        Guarantees P2 >= P1 and P2 <= 28.0 bar (and <= 41.0 bar).
        """
        sampler = qmc.LatinHypercube(d=self.dim, seed=self.seed)
        sample_unit = sampler.random(n=n_samples)

        # Map unit cube [0, 1]^7 to physical space
        feed_flow = self.bounds.flow_min + sample_unit[:, 0] * (
            self.bounds.flow_max - self.bounds.flow_min
        )
        feed_tds = self.bounds.tds_min + sample_unit[:, 1] * (
            self.bounds.tds_max - self.bounds.tds_min
        )
        feed_cod = self.bounds.cod_min + sample_unit[:, 2] * (
            self.bounds.cod_max - self.bounds.cod_min
        )
        feed_ph = self.bounds.ph_min + sample_unit[:, 3] * (
            self.bounds.ph_max - self.bounds.ph_min
        )
        temperature = self.bounds.temp_min + sample_unit[:, 4] * (
            self.bounds.temp_max - self.bounds.temp_min
        )
        p1 = self.bounds.p1_min + sample_unit[:, 5] * (
            self.bounds.p1_max - self.bounds.p1_min
        )

        # Enforce P2 >= P1 while keeping P2 in [14.0, 28.0]
        # p2_lower is max(bounds.p2_min, p1)
        p2_lower = np.maximum(self.bounds.p2_min, p1)
        p2_upper = np.maximum(p2_lower, self.bounds.p2_max)
        p2 = p2_lower + sample_unit[:, 6] * (p2_upper - p2_lower)

        # Clip against hard mechanical limit
        p2 = np.minimum(p2, self.bounds.p_limit_max)

        df = pd.DataFrame(
            {
                "feed_flow_m3h": np.round(feed_flow, 4),
                "feed_tds_mgL": np.round(feed_tds, 2),
                "feed_cod_mgL": np.round(feed_cod, 2),
                "feed_pH": np.round(feed_ph, 2),
                "temperature_C": np.round(temperature, 2),
                "stage1_pressure_bar": np.round(p1, 3),
                "stage2_pressure_bar": np.round(p2, 3),
            }
        )

        return df


def generate_ood_samples(
    n_samples: int = 200,
    bounds: Optional[OODDomainBounds] = None,
    seed: int = 101,
) -> pd.DataFrame:
    """
    Generate Out-Of-Distribution (OOD) candidate scenarios outside the normal training domain.
    """
    b = bounds or OODDomainBounds()
    sampler = qmc.LatinHypercube(d=7, seed=seed)
    sample_unit = sampler.random(n=n_samples)

    feed_flow = b.flow_min + sample_unit[:, 0] * (b.flow_max - b.flow_min)
    feed_tds = b.tds_min + sample_unit[:, 1] * (b.tds_max - b.tds_min)
    feed_cod = b.cod_min + sample_unit[:, 2] * (b.cod_max - b.cod_min)
    feed_ph = b.ph_min + sample_unit[:, 3] * (b.ph_max - b.ph_min)
    temperature = b.temp_min + sample_unit[:, 4] * (b.temp_max - b.temp_min)
    p1 = b.p1_min + sample_unit[:, 5] * (b.p1_max - b.p1_min)

    p2_lower = np.maximum(b.p2_min, p1)
    p2_upper = np.maximum(p2_lower, b.p2_max)
    p2 = p2_lower + sample_unit[:, 6] * (p2_upper - p2_lower)
    p2 = np.minimum(p2, b.p_limit_max)

    df = pd.DataFrame(
        {
            "feed_flow_m3h": np.round(feed_flow, 4),
            "feed_tds_mgL": np.round(feed_tds, 2),
            "feed_cod_mgL": np.round(feed_cod, 2),
            "feed_pH": np.round(feed_ph, 2),
            "temperature_C": np.round(temperature, 2),
            "stage1_pressure_bar": np.round(p1, 3),
            "stage2_pressure_bar": np.round(p2, 3),
        }
    )

    return df
