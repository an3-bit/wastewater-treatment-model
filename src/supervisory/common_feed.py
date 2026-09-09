"""
Common Exogenous Feed Generator and Manager for Stage 8B.

Ensures all supervisory policies face the EXACT same exogenous feed trajectory:
- Q_feed_available(t) [m3/h]
- C_feed(t) [mg/L TDS]
- Temp(t) [deg C]
for an authoritative 8,000 clock-hour horizon.
"""

from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import pandas as pd


def generate_and_save_common_feed(
    output_csv_path: Optional[Path] = None,
    total_clock_hours: int = 8000,
    seed: int = 42,
    variability_mode: str = "MEDIUM",
    fouling_multiplier: float = 1.0,
) -> pd.DataFrame:
    """
    Generate a reproducible synthetic industrial feed trajectory and save it to disk.
    
    Includes:
    - Base nominals: Qf=30.0 m3/h, Cf=2041 mg/L TDS, T=25.0 deg C
    - 24h Diurnal cycle on flow and temperature
    - 168h Weekly cycle on salinity
    - Bounded industrial disturbance pulses (dye batch wash spikes, cold shocks)
    - Stochastic bounded Gaussian variations
    """
    if output_csv_path is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        output_csv_path = project_root / "results" / "stage8b" / "common_feed_trajectory.csv"
    
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.RandomState(seed)
    t = np.arange(total_clock_hours, dtype=float)

    # Base nominal conditions
    base_qf = 30.0
    base_cf = 2041.0
    base_temp = 25.0

    # Variability scaling
    if variability_mode == "LOW":
        q_noise_std = 0.3
        c_noise_std = 25.0
        temp_noise_std = 0.2
        q_diurnal_amp = 0.7
        temp_diurnal_amp = 1.0
        c_weekly_amp = 50.0
    elif variability_mode == "HIGH":
        q_noise_std = 1.5
        c_noise_std = 120.0
        temp_noise_std = 1.0
        q_diurnal_amp = 3.0
        temp_diurnal_amp = 4.0
        c_weekly_amp = 250.0
    else:  # MEDIUM (Standard Nominal)
        q_noise_std = 0.8
        c_noise_std = 60.0
        temp_noise_std = 0.5
        q_diurnal_amp = 1.5
        temp_diurnal_amp = 2.0
        c_weekly_amp = 120.0

    # Deterministic cycles
    diurnal_q = q_diurnal_amp * np.sin(2 * np.pi * t / 24.0)
    diurnal_temp = temp_diurnal_amp * np.sin(2 * np.pi * (t - 6) / 24.0)
    weekly_c = c_weekly_amp * np.sin(2 * np.pi * t / 168.0)

    # Stochastic bounded noise
    noise_q = rng.normal(0.0, q_noise_std, total_clock_hours)
    noise_c = rng.normal(0.0, c_noise_std, total_clock_hours)
    noise_temp = rng.normal(0.0, temp_noise_std, total_clock_hours)

    q_feed_avail = base_qf + diurnal_q + noise_q
    c_feed = base_cf + weekly_c + noise_c
    temp_c = base_temp + diurnal_temp + noise_temp

    # Specific industrial disturbance pulses
    # Pulse 1: Salinity Spike +35% (Dyeing batch wash) at hours 1500 to 1540
    c_feed[1500:1540] += 700.0 * (1.5 if variability_mode == "HIGH" else (0.5 if variability_mode == "LOW" else 1.0))
    # Pulse 2: Hydraulic Peak +15% at hours 3800 to 3824
    q_feed_avail[3800:3824] += 4.5 * (1.5 if variability_mode == "HIGH" else (0.5 if variability_mode == "LOW" else 1.0))
    # Pulse 3: Winter Cold Shock (-5 deg C) at hours 5200 to 5280
    temp_c[5200:5280] -= 5.0 * (1.5 if variability_mode == "HIGH" else (0.5 if variability_mode == "LOW" else 1.0))
    # Pulse 4: Second Salinity Spike at hours 6900 to 6930
    c_feed[6900:6930] += 650.0 * (1.5 if variability_mode == "HIGH" else (0.5 if variability_mode == "LOW" else 1.0))

    # Physical bounding
    q_feed_avail = np.clip(q_feed_avail, 18.0, 42.0)
    c_feed = np.clip(c_feed, 1000.0, 4000.0)
    temp_c = np.clip(temp_c, 12.0, 38.0)

    df = pd.DataFrame({
        "clock_hour": np.arange(total_clock_hours, dtype=int),
        "q_feed_available_m3_h": np.round(q_feed_avail, 4),
        "c_feed_mg_l": np.round(c_feed, 2),
        "temp_c": np.round(temp_c, 2),
    })

    df.to_csv(output_csv_path, index=False)
    return df


def load_common_feed_trajectory(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the authoritative common feed trajectory from CSV."""
    if csv_path is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        csv_path = project_root / "results" / "stage8b" / "common_feed_trajectory.csv"
    
    if not csv_path.exists():
        return generate_and_save_common_feed(csv_path)
    
    return pd.read_csv(csv_path)
