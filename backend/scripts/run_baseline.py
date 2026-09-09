"""
Baseline Reverse Osmosis Simulation and Sensitivity Analysis Execution Script.

This script:
1. Loads baseline parameters from config/baseline.yaml.
2. Executes the mechanistic RO model for the baseline single membrane element.
3. Prints full diagnostic, thermodynamic, and mass-balance reports.
4. Conducts a feed pressure sensitivity sweep (10 - 35 bar).
5. Exports structured summary tables (CSV, Markdown) to results/tables/.
6. Generates high-resolution scientific figures in results/figures/.

Citation:
Sowgath, Sarker & Mujtaba (2025). Chem. Eng. Trans., Vol. 117.
"""

import os
import sys
from pathlib import Path
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure local src/ directory is in Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from ro_model import (
    simulate_ro,
    MembraneElementProperties,
    SimulationConfig,
    validate_physical_bounds,
    pa_to_bar,
    m3_per_s_to_m3_per_hr,
    kg_per_m3_to_mg_per_l,
    m_per_s_to_lmh
)


def load_configuration(config_path: Path) -> dict:
    """Load YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_output_directories(project_dir: Path):
    """Ensure output directories exist."""
    (project_dir / "results" / "figures").mkdir(parents=True, exist_ok=True)
    (project_dir / "results" / "tables").mkdir(parents=True, exist_ok=True)
    (project_dir / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (project_dir / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (project_dir / "data" / "generated").mkdir(parents=True, exist_ok=True)


def run_baseline_simulation(config: dict):
    """Run baseline simulation and save table results."""
    src = config["source_reported"]
    
    mem_props = MembraneElementProperties.from_config_dict(config)
    sim_cfg = SimulationConfig.from_config_dict(config)
    
    result = simulate_ro(
        feed_flow=src["feed_flow"],
        feed_tds=src["feed_concentration"],
        pressure=src["feed_pressure_bar"],
        temperature=src["temperature_celsius"],
        pressure_unit="bar",
        membrane_properties=mem_props,
        config=sim_cfg
    )
    
    # Print formatted summary table to console
    print(result.format_summary_table())
    
    # Run physical sanity checks
    checks = validate_physical_bounds(result)
    print("\n" + "=" * 78)
    print("                    AUTOMATED SCIENTIFIC CHECKS")
    print("=" * 78)
    all_passed = True
    for check_name, passed in checks.items():
        status = "PASSED [OK]" if passed else "FAILED [X]"
        if not passed:
            all_passed = False
        print(f"  - {check_name:<38} : {status}")
    print(f"\nOverall Sanity Validation: {'ALL CHECKS PASSED' if all_passed else 'WARNING: CHECKS FAILED'}")
    print("=" * 78 + "\n")
    
    # Save baseline summary table to CSV & Markdown
    df_res = result.to_dataframe()
    tables_dir = project_root / "results" / "tables"
    df_res.to_csv(tables_dir / "baseline_summary.csv", index=False)
    
    with open(tables_dir / "baseline_summary.md", "w", encoding="utf-8") as f:
        f.write("# Baseline Simulation Results\n\n")
        f.write("```\n")
        f.write(result.format_summary_table())
        f.write("\n```\n")
        
    return result, mem_props, sim_cfg


def run_pressure_sensitivity_sweep(
    config: dict,
    mem_props: MembraneElementProperties,
    sim_cfg: SimulationConfig,
    p_min_bar: float = 10.0,
    p_max_bar: float = 35.0,
    n_points: int = 26
) -> pd.DataFrame:
    """Evaluate performance across pressure sweep (10 - 35 bar)."""
    pressures = np.linspace(p_min_bar, p_max_bar, n_points)
    src = config["source_reported"]
    
    rows = []
    for p in pressures:
        res = simulate_ro(
            feed_flow=src["feed_flow"],
            feed_tds=src["feed_concentration"],
            pressure=p,
            temperature=src["temperature_celsius"],
            pressure_unit="bar",
            membrane_properties=mem_props,
            config=sim_cfg
        )
        rows.append(res.to_dict())
        
    df_sweep = pd.DataFrame(rows)
    tables_dir = project_root / "results" / "tables"
    df_sweep.to_csv(tables_dir / "pressure_sensitivity.csv", index=False)
    print(f"Pressure sensitivity sweep ({p_min_bar:.1f} - {p_max_bar:.1f} bar, {n_points} points) saved.")
    return df_sweep


def generate_scientific_plots(baseline_res, df_sweep: pd.DataFrame, figures_dir: Path):
    """Generate all required high-resolution scientific plots."""
    
    # Styling configuration
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.dpi": 300
    })
    
    # --------------------------------------------------------------------------
    # Plot 1: Feed / Permeate / Concentrate TDS Bar Chart
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    streams = ["Feed (Cf)", "Permeate (Cp)", "Concentrate (Cr)", "Membrane Surface (Cm)"]
    tds_values = [
        baseline_res.feed_tds_mg_l,
        baseline_res.permeate_tds_mg_l,
        baseline_res.concentrate_tds_mg_l,
        baseline_res.membrane_surface_tds_mg_l
    ]
    colors = ["#2b5c8f", "#2ca02c", "#d62728", "#ff7f0e"]
    
    bars = ax.bar(streams, tds_values, color=colors, width=0.55, edgecolor="black", linewidth=1.2)
    ax.set_ylabel("TDS Concentration (mg/L)")
    ax.set_title("Stream Salinity Distribution & Concentration Polarization")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    # Add value annotations
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f} mg/L",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")
                    
    plt.tight_layout()
    fig.savefig(figures_dir / "01_tds_distribution.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Plot 2: Feed / Permeate / Concentrate Flow Chart
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    flow_labels = ["Feed (Qf)", "Permeate (Qp)", "Concentrate (Qr)"]
    flow_values = [
        baseline_res.feed_flow_m3_hr,
        baseline_res.permeate_flow_m3_hr,
        baseline_res.concentrate_flow_m3_hr
    ]
    flow_colors = ["#1f77b4", "#2ca02c", "#d62728"]
    
    bars = ax.bar(flow_labels, flow_values, color=flow_colors, width=0.5, edgecolor="black", linewidth=1.2)
    ax.set_ylabel("Volumetric Flow Rate (m³/h)")
    ax.set_title("Volumetric Stream Mass Balance (Single Element)")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.3f} m³/h",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")
                    
    plt.tight_layout()
    fig.savefig(figures_dir / "02_flow_distribution.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Plot 3: Water Recovery and Salt Rejection Summary
    # --------------------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(7, 5))
    metrics = ["Water Recovery (%)", "Salt Rejection (%)"]
    vals = [baseline_res.water_recovery_percent, baseline_res.salt_rejection_percent]
    m_colors = ["#17becf", "#9467bd"]
    
    bars = ax1.bar(metrics, vals, color=m_colors, width=0.45, edgecolor="black", linewidth=1.2)
    ax1.set_ylabel("Percentage (%)")
    ax1.set_ylim(0, 110)
    ax1.set_title("Baseline Separation Performance (Toray TML20D-400)")
    ax1.grid(axis="y", linestyle="--", alpha=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"{height:.2f} %",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontweight="bold")
                     
    plt.tight_layout()
    fig.savefig(figures_dir / "03_recovery_rejection.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Plot 4: Pressure Sensitivity: Feed Pressure vs Permeate Flux
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(df_sweep["feed_pressure_bar"], df_sweep["water_flux_lmh"],
            color="#1f77b4", marker="o", linewidth=2.2, markersize=5, label="Model Jw (LMH)")
    
    # Highlight baseline point
    ax.scatter([baseline_res.feed_pressure_bar], [baseline_res.water_flux_lmh],
               color="red", s=100, zorder=5, label=f"Baseline (15.51 bar, {baseline_res.water_flux_lmh:.1f} LMH)")
               
    ax.set_xlabel("Feed Operating Pressure (bar)")
    ax.set_ylabel("Permeate Water Flux (LMH)")
    ax.set_title("Transmembrane Pressure vs. Permeate Water Flux")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    fig.savefig(figures_dir / "04_pressure_vs_flux.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Plot 5: Pressure Sensitivity: Feed Pressure vs Water Recovery
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(df_sweep["feed_pressure_bar"], df_sweep["water_recovery_percent"],
            color="#2ca02c", marker="s", linewidth=2.2, markersize=5, label="Water Recovery (%)")
    
    ax.scatter([baseline_res.feed_pressure_bar], [baseline_res.water_recovery_percent],
               color="red", s=100, zorder=5, label=f"Baseline (15.51 bar, {baseline_res.water_recovery_percent:.2f}%)")
               
    ax.set_xlabel("Feed Operating Pressure (bar)")
    ax.set_ylabel("Single-Element Water Recovery (%)")
    ax.set_title("Feed Operating Pressure vs. Single-Element Recovery")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    fig.savefig(figures_dir / "05_pressure_vs_recovery.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Plot 6: Pressure Sensitivity: Feed Pressure vs Specific Energy Consumption (SEC)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(df_sweep["feed_pressure_bar"], df_sweep["sec_kwh_per_m3"],
            color="#d62728", marker="^", linewidth=2.2, markersize=5, label="SEC (kWh/m³ permeate)")
    
    ax.scatter([baseline_res.feed_pressure_bar], [baseline_res.sec_kwh_per_m3],
               color="blue", s=100, zorder=5, label=f"Baseline (15.51 bar, {baseline_res.sec_kwh_per_m3:.2f} kWh/m³)")
               
    ax.set_xlabel("Feed Operating Pressure (bar)")
    ax.set_ylabel("Specific Energy Consumption (kWh/m³ permeate)")
    ax.set_title("Feed Pressure vs. Specific Energy Consumption")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    fig.savefig(figures_dir / "06_pressure_vs_sec.png")
    plt.close(fig)
    
    # --------------------------------------------------------------------------
    # Combined Multi-Panel Dashboard
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # Panel (0,0) - TDS
    axes[0, 0].bar(streams, tds_values, color=colors, edgecolor="black")
    axes[0, 0].set_ylabel("TDS (mg/L)")
    axes[0, 0].set_title("(a) Stream Salinity & Polarization")
    axes[0, 0].grid(axis="y", linestyle="--", alpha=0.5)
    axes[0, 0].tick_params(axis="x", rotation=20)
    
    # Panel (0,1) - Flows
    axes[0, 1].bar(flow_labels, flow_values, color=flow_colors, edgecolor="black")
    axes[0, 1].set_ylabel("Flow Rate (m³/h)")
    axes[0, 1].set_title("(b) Stream Mass Balances")
    axes[0, 1].grid(axis="y", linestyle="--", alpha=0.5)
    
    # Panel (0,2) - Recovery & Rejection
    axes[0, 2].bar(metrics, vals, color=m_colors, edgecolor="black")
    axes[0, 2].set_ylabel("Percentage (%)")
    axes[0, 2].set_title("(c) Separation Performance")
    axes[0, 2].set_ylim(0, 110)
    axes[0, 2].grid(axis="y", linestyle="--", alpha=0.5)
    
    # Panel (1,0) - Pressure vs Flux
    axes[1, 0].plot(df_sweep["feed_pressure_bar"], df_sweep["water_flux_lmh"], "b-o", markersize=4)
    axes[1, 0].scatter([baseline_res.feed_pressure_bar], [baseline_res.water_flux_lmh], color="red", s=60, zorder=5)
    axes[1, 0].set_xlabel("Feed Pressure (bar)")
    axes[1, 0].set_ylabel("Flux (LMH)")
    axes[1, 0].set_title("(d) Pressure vs. Permeate Flux")
    axes[1, 0].grid(True, linestyle="--", alpha=0.5)
    
    # Panel (1,1) - Pressure vs Recovery
    axes[1, 1].plot(df_sweep["feed_pressure_bar"], df_sweep["water_recovery_percent"], "g-s", markersize=4)
    axes[1, 1].scatter([baseline_res.feed_pressure_bar], [baseline_res.water_recovery_percent], color="red", s=60, zorder=5)
    axes[1, 1].set_xlabel("Feed Pressure (bar)")
    axes[1, 1].set_ylabel("Water Recovery (%)")
    axes[1, 1].set_title("(e) Pressure vs. Recovery")
    axes[1, 1].grid(True, linestyle="--", alpha=0.5)
    
    # Panel (1,2) - Pressure vs SEC
    axes[1, 2].plot(df_sweep["feed_pressure_bar"], df_sweep["sec_kwh_per_m3"], "r-^", markersize=4)
    axes[1, 2].scatter([baseline_res.feed_pressure_bar], [baseline_res.sec_kwh_per_m3], color="blue", s=60, zorder=5)
    axes[1, 2].set_xlabel("Feed Pressure (bar)")
    axes[1, 2].set_ylabel("SEC (kWh/m³)")
    axes[1, 2].set_title("(f) Pressure vs. Specific Energy Cons.")
    axes[1, 2].grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Mechanistic Reverse Osmosis Simulation Summary (Toray TML20D-400)", fontsize=16, y=0.98)
    plt.tight_layout()
    fig.savefig(figures_dir / "00_baseline_dashboard.png")
    plt.close(fig)
    
    print(f"All 7 figures generated and saved to {figures_dir}")


def main():
    print("\n" + "=" * 78)
    print("  RUNNING MECHANISTIC REVERSE OSMOSIS BASELINE SIMULATION (STAGE 1)")
    print("=" * 78 + "\n")
    
    setup_output_directories(project_root)
    config_path = project_root / "config" / "baseline.yaml"
    config = load_configuration(config_path)
    
    # 1. Run baseline simulation
    baseline_result, mem_props, sim_cfg = run_baseline_simulation(config)
    
    # 2. Run pressure sweep
    df_sweep = run_pressure_sensitivity_sweep(config, mem_props, sim_cfg, p_min_bar=10.0, p_max_bar=35.0, n_points=26)
    
    # 3. Generate figures
    figures_dir = project_root / "results" / "figures"
    generate_scientific_plots(baseline_result, df_sweep, figures_dir)
    
    print("\nBaseline simulation and analysis successfully completed.")


if __name__ == "__main__":
    main()
