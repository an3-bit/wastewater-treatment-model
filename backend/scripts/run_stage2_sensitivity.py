"""
Stage 2 Parametric Sensitivity Analysis & Engineering Visualization.

Generates 7 publication-quality engineering sensitivity plots for Stage 2:
1. Pressure vs Recovery (15-35 bar)
2. Pressure vs Flux (15-35 bar)
3. Pressure vs SEC (15-35 bar)
4. Recovery vs Concentrate TDS (50-85%)
5. Recovery vs SEC (50-85%)
6. Feed TDS vs Osmotic Pressure (1500-3000 mg/L)
7. Feed TDS vs Achievable Recovery (1500-3000 mg/L)
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Ensure package import
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from ro_model.osmotic import calculate_osmotic_pressure_bar
from ro_model.membrane import MembraneElementProperties, SimulationConfig
from ro_model.stage import ROStage
from ro_model.system import ROSystem

# Set clean scientific plotting style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300


def run_sensitivities():
    fig_dir = ROOT_DIR / "results" / "stage2" / "figures"
    os.makedirs(fig_dir, exist_ok=True)

    props = MembraneElementProperties(
        membrane_area_m2=37.0,
        Aw_m_pa_s=1.0232e-11,  # 3.6835 LMH/bar
        As_m_s=1.7827e-8       # Manufacturer derived As
    )

    feed_q = 30.0  # m3/h
    feed_tds = 2041.0  # mg/L

    # =========================================================================
    # 1. Pressure Sweeps (12 to 24 bar)
    # =========================================================================
    pressures = np.linspace(12.0, 24.0, 13)
    rec_list = []
    flux_list = []
    sec_list = []

    for p in pressures:
        # 2-stage configuration: Stage 1 = p bar, Stage 2 = p + 4 bar (capped at 38 bar)
        p1 = p
        p2 = min(p + 4.0, 38.0)
        
        s1 = ROStage(name="S1", parallel_vessels=3, elements_per_vessel=3, element_properties=props)
        s2 = ROStage(name="S2", parallel_vessels=2, elements_per_vessel=3, element_properties=props)
        sys_model = ROSystem(stages=[s1, s2], topology="concentrate_to_stage2")
        
        try:
            res = sys_model.solve(
                feed_flow_m3_hr=feed_q,
                feed_tds_mg_l=feed_tds,
                stage_pressures_bar=[p1, p2],
                temperature_celsius=25.0
            )
            rec_list.append(res.overall_water_recovery_percent)
            flux_list.append(res.average_system_flux_lmh)
            sec_list.append(res.system_sec_kwh_per_m3)
        except Exception:
            rec_list.append(np.nan)
            flux_list.append(np.nan)
            sec_list.append(np.nan)

    # Plot 1: Pressure vs Recovery
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pressures, rec_list, "o-", color="#1f77b4", linewidth=2, markersize=5, label="2-Stage System (3:2 array)")
    ax.axhline(70.0, color="#d62728", linestyle="--", linewidth=1.5, label="Target Benchmark (70%)")
    ax.set_title("Stage 2: Operating Pressure vs Overall Water Recovery", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Stage 1 Feed Pressure (bar)", fontsize=10)
    ax.set_ylabel("Overall Water Recovery (%)", fontsize=10)
    ax.set_ylim(40, 90)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "01_pressure_vs_recovery.png")
    plt.close(fig)

    # Plot 2: Pressure vs Flux
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pressures, flux_list, "s-", color="#2ca02c", linewidth=2, markersize=5, label="Average System Flux")
    ax.axhspan(20, 45, color="#2ca02c", alpha=0.15, label="Sustainable Industrial Envelope (20-45 LMH)")
    ax.set_title("Stage 2: Operating Pressure vs Average Membrane Flux", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Stage 1 Feed Pressure (bar)", fontsize=10)
    ax.set_ylabel("Average Water Flux (LMH)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "02_pressure_vs_flux.png")
    plt.close(fig)

    # Plot 3: Pressure vs SEC
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pressures, sec_list, "^-", color="#ff7f0e", linewidth=2, markersize=5, label="Specific Energy Consumption")
    ax.set_title("Stage 2: Operating Pressure vs Specific Energy Consumption", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Stage 1 Feed Pressure (bar)", fontsize=10)
    ax.set_ylabel("Specific Energy Consumption (kWh/m3 permeate)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "03_pressure_vs_sec.png")
    plt.close(fig)

    # =========================================================================
    # 2. Recovery Sweeps (50% to 85%)
    # =========================================================================
    recs = np.linspace(0.50, 0.85, 36)
    cp_nom = 18.0
    cr_mass_balance = [(feed_tds - r * cp_nom) / (1.0 - r) for r in recs]

    # Plot 4: Recovery vs Concentrate TDS
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(recs * 100.0, cr_mass_balance, "-", color="#9467bd", linewidth=2.5, label="Theoretical Solute Conservation")
    ax.scatter([70.0], [6761.33], color="#2ca02c", s=80, zorder=5, label="Mass Balance at 70% Rec (6761 mg/L)")
    ax.scatter([70.0], [3064.0], color="#d62728", marker="x", s=90, linewidth=2.5, zorder=5, label="Published Reject TDS (3064 mg/L - 54.7% Deficit)")
    ax.set_title("Stage 2: System Water Recovery vs Concentrate TDS", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Water Recovery (%)", fontsize=10)
    ax.set_ylabel("Concentrate Salinity Cr (mg/L)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "04_recovery_vs_concentrate_tds.png")
    plt.close(fig)

    # Plot 5: Recovery vs SEC
    fig, ax = plt.subplots(figsize=(7, 4.5))
    valid_mask = ~np.isnan(rec_list)
    ax.plot(np.array(rec_list)[valid_mask], np.array(sec_list)[valid_mask], "d-", color="#8c564b", linewidth=2, markersize=5, label="2-Stage System SEC")
    ax.set_title("Stage 2: Achieved Recovery vs Specific Energy Consumption", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Overall Water Recovery (%)", fontsize=10)
    ax.set_ylabel("Specific Energy Consumption (kWh/m3)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "05_recovery_vs_sec.png")
    plt.close(fig)

    # =========================================================================
    # 3. Feed TDS Sweeps (1500 to 3000 mg/L)
    # =========================================================================
    tds_range = np.linspace(1500.0, 3000.0, 31)
    temps = [20.0, 25.0, 30.0, 35.0]

    # Plot 6: Feed TDS vs Osmotic Pressure
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for t in temps:
        pi_vals = [calculate_osmotic_pressure_bar(c * 1e-3, 273.15 + t, 2.0, 0.05844) for c in tds_range]
        ax.plot(tds_range, pi_vals, linewidth=1.8, label=f"T = {t:.0f} C")
    ax.set_title("Stage 2: Feed TDS vs Osmotic Pressure (van 't Hoff)", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Feed TDS (mg/L)", fontsize=10)
    ax.set_ylabel("Osmotic Pressure (bar)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "06_feed_tds_vs_osmotic_pressure.png")
    plt.close(fig)

    # Plot 7: Feed TDS vs Achievable Recovery at different Stage 1 pressures
    fig, ax = plt.subplots(figsize=(7, 4.5))
    pressures_eval = [12.0, 14.0, 16.0]
    for p_eval in pressures_eval:
        tds_recs = []
        for tds_val in tds_range:
            s1 = ROStage(name="S1", parallel_vessels=3, elements_per_vessel=3, element_properties=props)
            s2 = ROStage(name="S2", parallel_vessels=2, elements_per_vessel=3, element_properties=props)
            sys_model = ROSystem(stages=[s1, s2], topology="concentrate_to_stage2")
            try:
                res_tds = sys_model.solve(
                    feed_flow_m3_hr=feed_q,
                    feed_tds_mg_l=tds_val,
                    stage_pressures_bar=[p_eval, p_eval + 5.0],
                    temperature_celsius=25.0
                )
                tds_recs.append(res_tds.overall_water_recovery_percent)
            except Exception:
                tds_recs.append(np.nan)
        ax.plot(tds_range, tds_recs, linewidth=2, label=f"Stage 1 Pressure = {p_eval:.0f} bar")
        
    ax.axhline(70.0, color="#d62728", linestyle="--", linewidth=1.5, label="Target Benchmark (70%)")
    ax.set_title("Stage 2: Feed TDS vs Achievable Overall Water Recovery", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Feed TDS (mg/L)", fontsize=10)
    ax.set_ylabel("Overall Water Recovery (%)", fontsize=10)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "07_feed_tds_vs_achievable_recovery.png")
    plt.close(fig)

    print("Successfully generated all 7 Stage 2 sensitivity plots in: results/stage2/figures/")


if __name__ == "__main__":
    run_sensitivities()
