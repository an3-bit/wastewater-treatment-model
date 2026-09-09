"""
Stage 1 Physical Diagnostic and Parameter-Interpretation Study Script.

Conducts rigorous sensitivity sweeps, unit audits, and parameter classification
for the baseline RO model based on Sowgath, Sarker & Mujtaba (2025).
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure local src/ is on path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from ro_model import (
    simulate_ro,
    MembraneElementProperties,
    SimulationConfig,
    calculate_osmotic_pressure_pa,
    pa_to_bar,
    bar_to_pa,
    m3_per_s_to_m3_per_hr,
    m_per_s_to_lmh,
    kg_per_m3_to_mg_per_l
)


def run_diagnostics():
    tables_dir = project_root / "results" / "tables"
    figures_dir = project_root / "results" / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # --------------------------------------------------------------------------
    # 1. Aw Unit Audit & Pure Water Fluxes
    # --------------------------------------------------------------------------
    aw_source = 9.08e-5  # m/(bar·s)
    aw_pa_s = aw_source / 1.0e5  # 9.08e-10 m/(Pa·s)
    aw_lmh_bar = aw_source * 3.6e6  # 326.88 LMH/bar
    aw_m_s_kpa = aw_source / 100.0  # 9.08e-7 m/(s·kPa)
    aw_gfd_psi = (aw_lmh_bar * 0.58857) / 14.5038  # approx 13.26 GFD/psi
    
    pure_water_flux_1bar_lmh = aw_lmh_bar * 1.0
    pure_water_flux_10bar_lmh = aw_lmh_bar * 10.0
    pure_water_flux_15bar_lmh = aw_lmh_bar * 15.0
    
    # --------------------------------------------------------------------------
    # 2. Manufacturer Test Performance Reconciliation
    # --------------------------------------------------------------------------
    # Toray TML20D-400: Product flow nominal = 39.7 m3/day (10,500 GPD), min = 31.8 m3/day (8,400 GPD)
    # Standard test recovery = 15%, Area = 37 m2
    area_m2 = 37.0
    wr_test = 0.15
    
    qp_nom_m3_day = 39.7
    qp_nom_m3_h = qp_nom_m3_day / 24.0
    qf_nom_m3_day = qp_nom_m3_day / wr_test
    qf_nom_m3_h = qf_nom_m3_day / 24.0
    qr_nom_m3_h = qf_nom_m3_h - qp_nom_m3_h
    jw_nom_lmh = (qp_nom_m3_day * 1000.0 / 24.0) / area_m2
    
    qp_min_m3_day = 31.8
    qp_min_m3_h = qp_min_m3_day / 24.0
    qf_min_m3_day = qp_min_m3_day / wr_test
    qf_min_m3_h = qf_min_m3_day / 24.0
    qr_min_m3_h = qf_min_m3_h - qp_min_m3_h
    jw_min_lmh = (qp_min_m3_day * 1000.0 / 24.0) / area_m2
    
    # --------------------------------------------------------------------------
    # 3. k Sensitivity Analysis
    # --------------------------------------------------------------------------
    k_values = [2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]
    k_rows = []
    for k in k_values:
        cfg = SimulationConfig(mass_transfer_coefficient=k)
        r = simulate_ro(feed_flow=30.0, feed_tds=2000.0, pressure=15.5132, config=cfg)
        k_rows.append({
            "k_m_s": k,
            "Jw_LMH": r.water_flux_lmh,
            "Cm_mg_L": r.membrane_surface_tds_mg_l,
            "Polarization_Modulus_Cm_Cb": r.polarization_modulus,
            "Qp_m3_h": r.permeate_flow_m3_hr,
            "Water_Recovery_pct": r.water_recovery_percent,
            "Cp_mg_L": r.permeate_tds_mg_l,
            "Salt_Rejection_pct": r.salt_rejection_percent,
            "Effective_dP_bar": r.effective_driving_pressure_bar,
            "Surface_Osmotic_pi_m_bar": r.membrane_surface_osmotic_pressure_bar
        })
    df_k = pd.DataFrame(k_rows)
    df_k.to_csv(tables_dir / "stage1_k_sensitivity.csv", index=False)
    
    # --------------------------------------------------------------------------
    # 4. Aw Sensitivity Analysis
    # --------------------------------------------------------------------------
    aw_factors = [0.01, 0.03, 0.1, 0.3, 1.0]
    aw_base = 9.08e-10  # m/(Pa·s)
    aw_rows = []
    for f in aw_factors:
        props = MembraneElementProperties(Aw_m_pa_s=aw_base * f)
        r = simulate_ro(feed_flow=30.0, feed_tds=2000.0, pressure=15.5132, membrane_properties=props)
        aw_rows.append({
            "Aw_Factor": f,
            "Aw_m_bar_s": aw_source * f,
            "Aw_LMH_bar": aw_lmh_bar * f,
            "Jw_LMH": r.water_flux_lmh,
            "Water_Recovery_pct": r.water_recovery_percent,
            "Polarization_Modulus_Cm_Cb": r.polarization_modulus,
            "Cp_mg_L": r.permeate_tds_mg_l,
            "Salt_Rejection_pct": r.salt_rejection_percent,
            "Effective_dP_bar": r.effective_driving_pressure_bar,
            "Cm_mg_L": r.membrane_surface_tds_mg_l,
            "Surface_Osmotic_pi_m_bar": r.membrane_surface_osmotic_pressure_bar
        })
    df_aw = pd.DataFrame(aw_rows)
    df_aw.to_csv(tables_dir / "stage1_aw_sensitivity.csv", index=False)
    
    # --------------------------------------------------------------------------
    # 5. Master Diagnostic Ledger Table
    # --------------------------------------------------------------------------
    diagnostic_ledger = [
        {"Parameter": "Membrane Effective Area (Am)", "Symbol": "Am", "Value": "37.0", "Unit": "m2", "Classification": "SOURCE-REPORTED", "Assessment": "Toray TML20D-400 element effective surface area."},
        {"Parameter": "Module Outer Diameter (d)", "Symbol": "d", "Value": "0.201", "Unit": "m", "Classification": "SOURCE-REPORTED", "Assessment": "Standard 8-inch module outer diameter."},
        {"Parameter": "Water Permeability (Aw)", "Symbol": "Aw", "Value": "9.08e-5", "Unit": "m/(bar·s)", "Classification": "SOURCE-REPORTED", "Assessment": "Parameter estimation value from paper; corresponds to 326.88 LMH/bar (7.2x - 100x higher than standard RO)."},
        {"Parameter": "Salt Permeability (As)", "Symbol": "As", "Value": "1.1834e-9", "Unit": "m/s", "Classification": "SOURCE-REPORTED", "Assessment": "Parameter estimation value from paper; corresponds to 0.00426 LMH."},
        {"Parameter": "Feed Volumetric Flow (Qf)", "Symbol": "Qf", "Value": "30.0", "Unit": "m3/h", "Classification": "SOURCE-REPORTED", "Assessment": "Reported operating feed condition in parameter estimation table; physical grouping (element vs stage) not established."},
        {"Parameter": "Feed Salinity (Cf)", "Symbol": "Cf", "Value": "2000.0", "Unit": "mg/L", "Classification": "SOURCE-REPORTED", "Assessment": "Baseline MBR-treated textile wastewater feed salinity."},
        {"Parameter": "Feed Pressure (Pf)", "Symbol": "Pf", "Value": "15.5132", "Unit": "bar", "Classification": "SOURCE-REPORTED", "Assessment": "Reported as 225 psi."},
        {"Parameter": "Operating Temperature (T)", "Symbol": "T", "Value": "25.0", "Unit": "degC", "Classification": "SOURCE-REPORTED", "Assessment": "298.15 K."},
        {"Parameter": "Nominal Product Flow (Qp,nom)", "Symbol": "Qp,nom", "Value": "39.7", "Unit": "m3/day", "Classification": "SOURCE-REPORTED", "Assessment": "Toray datasheet nominal product/permeate flow (1.654 m3/h, 44.71 LMH at 15% recovery)."},
        {"Parameter": "Minimum Product Flow (Qp,min)", "Symbol": "Qp,min", "Value": "31.8", "Unit": "m3/day", "Classification": "SOURCE-REPORTED", "Assessment": "Toray datasheet minimum product/permeate flow (1.325 m3/h, 35.81 LMH at 15% recovery)."},
        {"Parameter": "Feed Osmotic Pressure (pi_f)", "Symbol": "pi_f", "Value": "1.6968", "Unit": "bar", "Classification": "DERIVED", "Assessment": "Calculated via van 't Hoff equation (i=2.0, Mw=58.44 g/mol)."},
        {"Parameter": "Transmembrane Pressure (dP)", "Symbol": "dP", "Value": "14.5000", "Unit": "bar", "Classification": "DERIVED", "Assessment": "Pf - P_permeate = 15.5132 - 1.01325 = 14.5000 bar."},
        {"Parameter": "Implied Test Feed Flow (Qf,implied)", "Symbol": "Qf,implied", "Value": "11.03", "Unit": "m3/h", "Classification": "DERIVED", "Assessment": "Qp,nom / 0.15 = 39.7 / (24 * 0.15) = 11.028 m3/h."},
        {"Parameter": "Manufacturer Test Flux", "Symbol": "Jw,test", "Value": "44.71", "Unit": "LMH", "Classification": "DERIVED", "Assessment": "Qp,nom / Am = 39.7 m3/day / 37 m2 = 44.707 LMH (Envelope: 35.81 - 44.71 LMH)."},
        {"Parameter": "Mass Transfer Coeff (k)", "Symbol": "k", "Value": "5.0e-5", "Unit": "m/s", "Classification": "ASSUMED", "Assessment": "Mode A baseline film theory velocity (5.0e-5 m/s = 180 LMH)."},
        {"Parameter": "Pump Efficiency (eta_pump)", "Symbol": "eta_pump", "Value": "0.80", "Unit": "-", "Classification": "ASSUMED", "Assessment": "High-pressure pump isentropic/electrical efficiency."},
        {"Parameter": "van 't Hoff Factor (i)", "Symbol": "i", "Value": "2.0", "Unit": "-", "Classification": "ASSUMED", "Assessment": "Complete dissociation for 1:1 NaCl-equivalent electrolyte."},
        {"Parameter": "Feed Channel Delta P", "Symbol": "dP_element", "Value": "0.0", "Unit": "bar", "Classification": "ASSUMED", "Assessment": "Single element feed channel pressure drop."},
        {"Parameter": "Water Volumetric Flux (Jw)", "Symbol": "Jw", "Value": "322.22", "Unit": "LMH", "Classification": "CALCULATED", "Assessment": "Solution-diffusion flux coupled with concentration polarization equilibrium."},
        {"Parameter": "Water Recovery (WR)", "Symbol": "WR", "Value": "39.74", "Unit": "%", "Classification": "CALCULATED", "Assessment": "Model calculated recovery under Qf = 30 m3/h."},
        {"Parameter": "Salt Rejection (SR)", "Symbol": "SR", "Value": "99.9895", "Unit": "%", "Classification": "CALCULATED", "Assessment": "Solute rejection driven by high dilution flux (Jw >> As)."},
        {"Parameter": "Polarization Modulus (Cm/Cb)", "Symbol": "Cm/Cb", "Value": "5.9899", "Unit": "-", "Classification": "CALCULATED", "Assessment": "exp(Jw/k) = exp(8.95e-5 / 5.0e-5) = 5.990."},
        {"Parameter": "Surface Salinity (Cm)", "Symbol": "Cm", "Value": "15929.68", "Unit": "mg/L", "Classification": "CALCULATED", "Assessment": "Surface concentration build-up creating 13.51 bar osmotic backpressure."},
        {"Parameter": "Permeate Salinity (Cp)", "Symbol": "Cp", "Value": "0.21", "Unit": "mg/L", "Classification": "CALCULATED", "Assessment": "Permeate TDS = As*Cm / (Jw + As)."},
        {"Parameter": "Effective Driving Force (dP_eff)", "Symbol": "dP_eff", "Value": "0.9858", "Unit": "bar", "Classification": "CALCULATED", "Assessment": "dP - (pi_m - pi_p) = 14.5000 - (13.5144 - 0.0002) = 0.9858 bar."}
    ]
    df_ledger = pd.DataFrame(diagnostic_ledger)
    df_ledger.to_csv(tables_dir / "stage1_diagnostic.csv", index=False)
    
    # --------------------------------------------------------------------------
    # 6. Generate Diagnostic Plots
    # --------------------------------------------------------------------------
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300
    })
    
    # Plot A: k vs Polarization Modulus
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogx(df_k["k_m_s"], df_k["Polarization_Modulus_Cm_Cb"], "b-o", linewidth=2.2, markersize=6)
    ax.set_xlabel("Mass-Transfer Coefficient k (m/s) [log scale]")
    ax.set_ylabel("Polarization Modulus Cm/Cb (-)")
    ax.set_title("Mass-Transfer Coefficient vs. Polarization Modulus")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(figures_dir / "k_vs_polarization_modulus.png")
    plt.close(fig)
    
    # Plot B: k vs Flux
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogx(df_k["k_m_s"], df_k["Jw_LMH"], "g-s", linewidth=2.2, markersize=6, label="Model Jw (k sweep)")
    ax.axhline(jw_nom_lmh, color="red", linestyle="--", label=f"Toray Nominal Test Flux ({jw_nom_lmh:.1f} LMH)")
    ax.axhspan(jw_min_lmh, jw_nom_lmh, color="red", alpha=0.15, label="Toray Test Flux Envelope (35.8 - 44.7 LMH)")
    ax.set_xlabel("Mass-Transfer Coefficient k (m/s) [log scale]")
    ax.set_ylabel("Permeate Water Flux Jw (LMH)")
    ax.set_title("Mass-Transfer Coefficient vs. Water Flux")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend()
    plt.tight_layout()
    fig.savefig(figures_dir / "k_vs_flux.png")
    plt.close(fig)
    
    # Plot C: k vs Recovery
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogx(df_k["k_m_s"], df_k["Water_Recovery_pct"], "r-^", linewidth=2.2, markersize=6)
    ax.set_xlabel("Mass-Transfer Coefficient k (m/s) [log scale]")
    ax.set_ylabel("Water Recovery (%)")
    ax.set_title("Mass-Transfer Coefficient vs. Water Recovery")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(figures_dir / "k_vs_recovery.png")
    plt.close(fig)
    
    # Plot D: Aw sensitivity vs Flux and Polarization
    fig, ax1 = plt.subplots(figsize=(7.5, 5))
    color1 = "#1f77b4"
    color2 = "#d62728"
    
    ax1.set_xlabel("Aw Multiplier Factor relative to Source [log scale]")
    ax1.set_ylabel("Water Flux Jw (LMH)", color=color1)
    line1 = ax1.semilogx(df_aw["Aw_Factor"], df_aw["Jw_LMH"], color=color1, marker="o", linewidth=2.2, label="Flux Jw (LMH)")
    ax1.axhline(jw_nom_lmh, color="black", linestyle=":", label=f"Toray Nominal Test Flux ({jw_nom_lmh:.1f} LMH)")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.grid(True, which="both", linestyle="--", alpha=0.5)
    
    ax2 = ax1.twinx()
    ax2.set_ylabel("Polarization Modulus Cm/Cb (-)", color=color2)
    line2 = ax2.semilogx(df_aw["Aw_Factor"], df_aw["Polarization_Modulus_Cm_Cb"], color=color2, marker="s", linestyle="--", linewidth=2.2, label="Polarization Cm/Cb")
    ax2.tick_params(axis="y", labelcolor=color2)
    
    lines = line1 + [ax1.get_lines()[-1]] + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center left")
    plt.title("Effect of Aw Scaling on Flux and Concentration Polarization")
    plt.tight_layout()
    fig.savefig(figures_dir / "aw_vs_flux_and_polarization.png")
    plt.close(fig)
    
    # Plot E: Comprehensive Diagnostic Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 0,0: k vs Polarization Modulus
    axes[0, 0].semilogx(df_k["k_m_s"], df_k["Polarization_Modulus_Cm_Cb"], "b-o", linewidth=2, markersize=5)
    axes[0, 0].set_xlabel("k (m/s)")
    axes[0, 0].set_ylabel("Polarization Modulus Cm/Cb")
    axes[0, 0].set_title("(a) Mass Transfer k vs. Polarization Modulus")
    axes[0, 0].grid(True, which="both", linestyle="--", alpha=0.5)
    
    # 0,1: k vs Flux
    axes[0, 1].semilogx(df_k["k_m_s"], df_k["Jw_LMH"], "g-s", linewidth=2, markersize=5, label="Model Jw")
    axes[0, 1].axhline(jw_nom_lmh, color="red", linestyle="--", label="Toray Nom. Test (44.7 LMH)")
    axes[0, 1].set_xlabel("k (m/s)")
    axes[0, 1].set_ylabel("Flux Jw (LMH)")
    axes[0, 1].set_title("(b) Mass Transfer k vs. Permeate Flux")
    axes[0, 1].grid(True, which="both", linestyle="--", alpha=0.5)
    axes[0, 1].legend()
    
    # 1,0: Aw vs Flux
    axes[1, 0].semilogx(df_aw["Aw_Factor"], df_aw["Jw_LMH"], "m-d", linewidth=2, markersize=5, label="Model Jw")
    axes[1, 0].axhline(jw_nom_lmh, color="black", linestyle="--", label="Toray Nom. Test (44.7 LMH)")
    axes[1, 0].set_xlabel("Aw Scaling Factor")
    axes[1, 0].set_ylabel("Flux Jw (LMH)")
    axes[1, 0].set_title("(c) Aw Scaling vs. Permeate Flux")
    axes[1, 0].grid(True, which="both", linestyle="--", alpha=0.5)
    axes[1, 0].legend()
    
    # 1,1: Aw vs Polarization
    axes[1, 1].semilogx(df_aw["Aw_Factor"], df_aw["Polarization_Modulus_Cm_Cb"], "r-^", linewidth=2, markersize=5)
    axes[1, 1].set_xlabel("Aw Scaling Factor")
    axes[1, 1].set_ylabel("Polarization Modulus Cm/Cb")
    axes[1, 1].set_title("(d) Aw Scaling vs. Polarization Modulus")
    axes[1, 1].grid(True, which="both", linestyle="--", alpha=0.5)
    
    plt.suptitle("Stage 1 Physical Diagnostic Sensitivity Dashboard", fontsize=15)
    plt.tight_layout()
    fig.savefig(figures_dir / "diagnostic_dashboard.png")
    plt.close(fig)
    
    print("Diagnostic calculations and figures generated successfully.")


if __name__ == "__main__":
    run_diagnostics()
