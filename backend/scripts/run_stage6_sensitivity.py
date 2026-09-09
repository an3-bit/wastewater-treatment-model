"""
Stage 6 Sensitivity and Disturbance Study Script.

Executes:
1. Parametric uncertainty analysis across +/- 25% fouling rate constant (r_spec).
2. Upstream feed salinity disturbance dynamic trajectories (TDS = 1500, 2041, 3000 mg/L).
3. Evaluates strategy ranking stability and threshold crossing sensitivity.
4. Generates publication figures in results/stage6/figures/ and tables in results/stage6/tables/.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fouling.sensitivity import (
    run_fouling_rate_uncertainty_study,
    run_feed_tds_disturbance_study,
)
from fouling.calibration import calibrate_fouling_rate_constant


def run_sensitivity_study():
    print("=" * 80)
    print("STAGE 6: UNCERTAINTY & SENSITIVITY ANALYSIS")
    print("=" * 80)

    figures_dir = Path("results/stage6/figures")
    tables_dir = Path("results/stage6/tables")
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    calib = calibrate_fouling_rate_constant()
    base_r_spec = calib.calibrated_r_spec

    strategies = {
        "Authoritative Baseline": (13.00, 18.00),
        "Strategy A (Max Recovery)": (20.00, 20.25),
        "Strategy B (Min Energy)": (15.80, 15.80),
        "Strategy C (Min Stress)": (10.00, 14.00),
        "Strategy D (Balanced Knee)": (16.06, 16.41),
    }

    # 1. Fouling rate uncertainty sweeps (-25%, baseline, +25%)
    print("\n[Step 1/2] Running +/- 25% Fouling Rate Uncertainty Sweeps (168h)...")
    df_unc = run_fouling_rate_uncertainty_study(
        strategies=strategies,
        base_r_spec=base_r_spec,
        variations=[-0.25, 0.0, 0.25],
        horizon_hours=168.0,
        time_step_hours=1.0,
    )
    df_unc.to_csv(tables_dir / "fouling_rate_uncertainty_summary.csv", index=False)
    print(f"  Saved: {tables_dir / 'fouling_rate_uncertainty_summary.csv'}")

    # 2. Feed TDS disturbance sweeps (1500, 2041, 3000 mg/L)
    print("\n[Step 2/2] Running Feed TDS Disturbance Dynamics Sweeps (168h)...")
    df_tds = run_feed_tds_disturbance_study(
        strategies=strategies,
        tds_levels=[1500.0, 2041.0, 3000.0],
        r_spec=base_r_spec,
        horizon_hours=168.0,
        time_step_hours=1.0,
    )
    df_tds.to_csv(tables_dir / "feed_tds_disturbance_summary.csv", index=False)
    print(f"  Saved: {tables_dir / 'feed_tds_disturbance_summary.csv'}")

    # Generate Figures
    generate_sensitivity_figures(df_unc, df_tds, figures_dir)
    print("Sensitivity study completed successfully!")


def generate_sensitivity_figures(df_unc: pd.DataFrame, df_tds: pd.DataFrame, out_dir: Path):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    colors = {
        "Authoritative Baseline": "#7f7f7f",
        "Strategy A (Max Recovery)": "#d62728",
        "Strategy B (Min Energy)": "#1f77b4",
        "Strategy C (Min Stress)": "#2ca02c",
        "Strategy D (Balanced Knee)": "#9467bd",
    }

    # -------------------------------------------------------------
    # Figure 10: Fouling Rate Uncertainty vs Cumulative Water & Energy
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    variations = [-25.0, 0.0, 25.0]
    strat_names = list(df_unc["strategy_name"].unique())

    for name in strat_names:
        sub = df_unc[df_unc["strategy_name"] == name]
        ax1.plot(sub["variation_pct"], sub["total_cumulative_permeate_m3"], marker="o", lw=2.2, label=name, color=colors.get(name, "black"))
        ax2.plot(sub["variation_pct"], sub["dynamic_average_sec_kwh_m3"], marker="s", lw=2.2, label=name, color=colors.get(name, "black"))

    ax1.set_xlabel("Fouling Rate Uncertainty Variation (%)", fontsize=11, fontweight="bold")
    ax1.set_ylabel(r"7-Day Cumulative Water Recovered ($m^3$)", fontsize=11, fontweight="bold")
    ax1.set_title("Sensitivity of 7-Day Water Yield to Fouling Kinetics", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True, fontsize=8.5, loc="lower left")

    ax2.set_xlabel("Fouling Rate Uncertainty Variation (%)", fontsize=11, fontweight="bold")
    ax2.set_ylabel(r"7-Day Weighted Average SEC ($\mathrm{kWh/m^3}$)", fontsize=11, fontweight="bold")
    ax2.set_title("Sensitivity of Dynamic Energy Efficiency to Fouling Kinetics", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True, fontsize=8.5, loc="upper left")

    fig.suptitle(r"Impact of Fouling Rate Uncertainty ($\pm 25\%$ on $r_{\mathrm{spec}}$) on Strategy Outcomes", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_10_fouling_rate_uncertainty_pareto.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 11: Feed TDS Disturbance Comparison
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    tds_vals = [1500.0, 2041.0, 3000.0]

    for name in strat_names:
        sub = df_tds[df_tds["strategy_name"] == name]
        ax1.plot(sub["feed_tds_mgL"], sub["total_cumulative_permeate_m3"], marker="o", lw=2.2, label=name, color=colors.get(name, "black"))
        ax2.plot(sub["feed_tds_mgL"], sub["dynamic_average_sec_kwh_m3"], marker="s", lw=2.2, label=name, color=colors.get(name, "black"))

    ax1.set_xlabel("Feed TDS Salinity (mg/L)", fontsize=11, fontweight="bold")
    ax1.set_ylabel(r"7-Day Cumulative Water Recovered ($m^3$)", fontsize=11, fontweight="bold")
    ax1.set_title("7-Day Cumulative Permeate vs. Feed Salinity", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True, fontsize=8.5, loc="lower left")

    ax2.set_xlabel("Feed TDS Salinity (mg/L)", fontsize=11, fontweight="bold")
    ax2.set_ylabel(r"7-Day Weighted Average SEC ($\mathrm{kWh/m^3}$)", fontsize=11, fontweight="bold")
    ax2.set_title("7-Day Dynamic SEC vs. Feed Salinity", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True, fontsize=8.5, loc="upper left")

    fig.suptitle("Long-Term Dynamic Performance under Upstream Feed Salinity Disturbances", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_11_feed_salinity_disturbance_dynamics.png")
    plt.close(fig)


if __name__ == "__main__":
    run_sensitivity_study()
