"""
Stage 6 Master Dynamic Simulation Script.

Executes:
1. Dynamic simulation over 24h, 72h, and 168h (7 days) for:
   - Authoritative Baseline (13.00 / 18.00 bar)
   - Strategy A: Max Feasible Clean Recovery (19.08 / 19.73 bar)
   - Strategy B: Min Energy (15.30 / 15.30 bar)
   - Strategy C: Min Stress (10.00 / 14.00 bar)
   - Strategy D: Balanced Knee (15.05 / 15.80 bar)
2. Mode A (Fixed Pressure) and Mode B (Production-Maintaining Pressure).
3. Element-wise axial profiling across all 15 membrane elements.
4. Generates publication-grade figures in results/stage6/figures/ and tables in results/stage6/tables/.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fouling.model import FoulingParameters
from fouling.dynamics import DynamicROSimulator
from fouling.calibration import calibrate_fouling_rate_constant


def run_stage6_master_study():
    print("=" * 80)
    print("STAGE 6: DYNAMIC MEMBRANE FOULING SIMULATION & STRATEGY EVALUATION")
    print("=" * 80)

    figures_dir = Path("results/stage6/figures")
    tables_dir = Path("results/stage6/tables")
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # 1. Calibrate fouling parameters
    calib = calibrate_fouling_rate_constant()
    params = FoulingParameters.create_default(r_spec=calib.calibrated_r_spec)
    print(f"\n[Step 1/4] Calibrated r_spec = {params.specific_fouling_resistance:.4e} m^-1 / (m^3/m^2)")

    # 2. Operating strategies dictionary (Model V2.0 Representative Points)
    strategies = {
        "Authoritative Baseline": (13.00, 18.00),
        "Strategy A (Max Recovery)": (20.00, 20.25),
        "Strategy B (Min Energy)": (15.80, 15.80),
        "Strategy C (Min Stress)": (10.00, 14.00),
        "Strategy D (Balanced Knee)": (16.06, 16.41),
    }

    sim = DynamicROSimulator(parameters=params)

    # 3. Simulate 168-hour (7 days) trajectories for Mode A (Fixed Pressure)
    print("\n[Step 2/4] Running 168-hour Mode A (Fixed Pressure) dynamic simulations...")
    results_mode_a = {}
    summary_rows_a = []

    for name, (p1, p2) in strategies.items():
        print(f"  Simulating Mode A: {name} (P1={p1:.2f}, P2={p2:.2f} bar)...")
        res = sim.simulate(
            strategy_name=name,
            initial_p1_bar=p1,
            initial_p2_bar=p2,
            horizon_hours=168.0,
            time_step_hours=1.0,
            operating_mode="MODE_A_FIXED_PRESSURE",
        )
        results_mode_a[name] = res

        # Extract snapshots at 24h, 72h, 168h
        s0 = res.states[0]
        s24 = res.states[24]
        s72 = res.states[72]
        s168 = res.states[168]

        summary_rows_a.append({
            "strategy_name": name,
            "mode": "MODE_A_FIXED_PRESSURE",
            "p1_bar": p1,
            "p2_bar": p2,
            "initial_recovery_pct": s0.instantaneous_recovery_pct,
            "recovery_24h_pct": s24.instantaneous_recovery_pct,
            "recovery_72h_pct": s72.instantaneous_recovery_pct,
            "recovery_168h_pct": s168.instantaneous_recovery_pct,
            "initial_sec_kwh_m3": s0.instantaneous_sec_kwh_m3,
            "sec_24h_kwh_m3": s24.instantaneous_sec_kwh_m3,
            "sec_72h_kwh_m3": s72.instantaneous_sec_kwh_m3,
            "sec_168h_kwh_m3": s168.instantaneous_sec_kwh_m3,
            "initial_flux_lmh": s0.instantaneous_permeate_flow_m3_h * 1000.0 / 555.0,
            "final_flux_168h_lmh": s168.instantaneous_permeate_flow_m3_h * 1000.0 / 555.0,
            "permeability_decline_168h_pct": s168.average_permeability_decline_pct,
            "total_cumulative_permeate_m3": res.total_cumulative_permeate_m3,
            "total_cumulative_electricity_kwh": res.total_cumulative_electricity_kwh,
            "dynamic_average_sec_kwh_m3": res.dynamic_average_sec_kwh_m3,
            "specific_cumulative_volume_l_m2": res.specific_cumulative_volume_l_m2,
            "time_to_5pct_decline_hours": res.time_to_5pct_decline_hours,
            "time_to_10pct_decline_hours": res.time_to_10pct_decline_hours,
            "time_to_15pct_decline_hours": res.time_to_15pct_decline_hours,
            "max_water_error_pct": res.max_dynamic_water_error_pct,
            "max_solute_error_pct": res.max_dynamic_solute_error_pct,
        })

    df_summary_a = pd.DataFrame(summary_rows_a)
    df_summary_a.to_csv(tables_dir / "strategy_dynamic_comparison_mode_a.csv", index=False)
    print(f"  Saved: {tables_dir / 'strategy_dynamic_comparison_mode_a.csv'}")

    # 4. Simulate Mode B (Production-Maintaining Pressure)
    print("\n[Step 3/4] Running 168-hour Mode B (Production-Maintaining Pressure) dynamic simulations...")
    results_mode_b = {}
    summary_rows_b = []

    for name, (p1, p2) in strategies.items():
        print(f"  Simulating Mode B: {name}...")
        res = sim.simulate(
            strategy_name=name,
            initial_p1_bar=p1,
            initial_p2_bar=p2,
            horizon_hours=168.0,
            time_step_hours=1.0,
            operating_mode="MODE_B_MAINTAIN_PRODUCTION",
        )
        results_mode_b[name] = res

        s0 = res.states[0]
        s24 = res.states[24]
        s72 = res.states[72]
        s168 = res.states[168]

        summary_rows_b.append({
            "strategy_name": name,
            "mode": "MODE_B_MAINTAIN_PRODUCTION",
            "p1_initial_bar": p1,
            "p2_initial_bar": p2,
            "p1_final_bar": s168.stage1_feed_pressure_bar,
            "p2_final_bar": s168.stage2_feed_pressure_bar,
            "target_permeate_m3h": s0.instantaneous_permeate_flow_m3_h,
            "final_permeate_m3h": s168.instantaneous_permeate_flow_m3_h,
            "initial_sec_kwh_m3": s0.instantaneous_sec_kwh_m3,
            "final_sec_168h_kwh_m3": s168.instantaneous_sec_kwh_m3,
            "total_cumulative_permeate_m3": res.total_cumulative_permeate_m3,
            "total_cumulative_electricity_kwh": res.total_cumulative_electricity_kwh,
            "dynamic_average_sec_kwh_m3": res.dynamic_average_sec_kwh_m3,
            "permeability_decline_168h_pct": s168.average_permeability_decline_pct,
        })

    df_summary_b = pd.DataFrame(summary_rows_b)
    df_summary_b.to_csv(tables_dir / "strategy_dynamic_comparison_mode_b.csv", index=False)
    print(f"  Saved: {tables_dir / 'strategy_dynamic_comparison_mode_b.csv'}")

    # 5. Extract element-wise axial profiles
    print("\n[Step 4/4] Generating Element Axial Profiling and Visualizations...")
    axial_rows = []
    for name, res in results_mode_a.items():
        s_end = res.states[-1]
        for elem in s_end.element_states:
            axial_rows.append({
                "strategy_name": name,
                "stage_index": elem.stage_index,
                "element_index": elem.element_index,
                "global_element_id": elem.global_element_id,
                "r_f_m_inv": elem.r_f_m_inv,
                "permeability_decline_pct": elem.permeability_decline_pct,
                "specific_cumulative_volume_l_m2": elem.specific_cumulative_volume_l_m2,
                "local_flux_lmh": elem.local_flux_lmh,
                "local_polarization_modulus": elem.local_polarization_modulus,
                "local_feed_tds_mg_l": elem.local_feed_tds_mg_l,
                "local_surface_tds_mg_l": elem.local_surface_tds_mg_l,
            })
    df_axial = pd.DataFrame(axial_rows)
    df_axial.to_csv(tables_dir / "element_axial_fouling_profiles.csv", index=False)
    print(f"  Saved: {tables_dir / 'element_axial_fouling_profiles.csv'}")

    # Generate publication figures
    generate_stage6_figures(results_mode_a, results_mode_b, df_axial, figures_dir)
    print("Stage 6 dynamic master study completed successfully!")


def generate_stage6_figures(
    results_a: Dict[str, Any],
    results_b: Dict[str, Any],
    df_axial: pd.DataFrame,
    out_dir: Path,
):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    colors = {
        "Authoritative Baseline": "#7f7f7f",       # Grey
        "Strategy A (Max Recovery)": "#d62728",     # Red
        "Strategy B (Min Energy)": "#1f77b4",       # Blue
        "Strategy C (Min Stress)": "#2ca02c",       # Green
        "Strategy D (Balanced Knee)": "#9467bd",   # Purple
    }

    # -------------------------------------------------------------
    # Figure 1: Permeability Ratio (A_eff / A_clean) vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        ratios = [s.average_permeability_ratio for s in res.states]
        ax.plot(times, ratios, label=name, color=colors.get(name, "black"), lw=2.2)
    
    ax.axhline(0.85, color="red", linestyle="--", alpha=0.7, label="15% Decline Analysis Threshold")
    ax.axhline(0.90, color="orange", linestyle=":", alpha=0.7, label="10% Decline Analysis Threshold")
    ax.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax.set_ylabel(r"Normalized Membrane Permeability ($A_{\mathrm{eff}} / A_{\mathrm{clean}}$)", fontsize=11, fontweight="bold")
    ax.set_title("Time-Dependent Membrane Permeability Decline (Mode A: Fixed Pressure)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 168)
    ax.set_ylim(0.70, 1.02)
    ax.legend(frameon=True, fontsize=9, loc="lower left")
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_01_permeability_decline_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 2: Average Flux vs Time (Mode A)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        fluxes = [s.instantaneous_permeate_flow_m3_h * 1000.0 / 555.0 for s in res.states]
        ax.plot(times, fluxes, label=name, color=colors.get(name, "black"), lw=2.2)
    
    ax.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Average Trans-Membrane Flux (LMH)", fontsize=11, fontweight="bold")
    ax.set_title("Trans-Membrane Flux Decay over 7-Day Continuous Operation", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 168)
    ax.legend(frameon=True, fontsize=9, loc="upper right")
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_02_flux_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 3: Overall Recovery vs Time (Mode A vs Mode B)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        recs = [s.instantaneous_recovery_pct for s in res.states]
        ax1.plot(times, recs, label=name, color=colors.get(name, "black"), lw=2.0)
    
    ax1.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Overall Water Recovery (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Mode A: Fixed Pressure Policy", fontsize=12, fontweight="bold")
    ax1.set_xlim(0, 168)
    ax1.legend(frameon=True, fontsize=8.5, loc="lower left")

    for name, res in results_b.items():
        times = [s.time_hours for s in res.states]
        recs = [s.instantaneous_recovery_pct for s in res.states]
        ax2.plot(times, recs, label=name, color=colors.get(name, "black"), lw=2.0)
    
    ax2.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Overall Water Recovery (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Mode B: Production-Maintaining Pressure Ramp", fontsize=12, fontweight="bold")
    ax2.set_xlim(0, 168)
    ax2.legend(frameon=True, fontsize=8.5, loc="lower left")
    
    fig.suptitle("Long-Term Water Recovery Trajectories across Operating Modes", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_03_recovery_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 4: Specific Energy Consumption (SEC) vs Time
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        secs = [s.instantaneous_sec_kwh_m3 for s in res.states]
        ax1.plot(times, secs, label=name, color=colors.get(name, "black"), lw=2.0)
    
    ax1.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax1.set_ylabel(r"Instantaneous SEC ($\mathrm{kWh/m^3}$)", fontsize=11, fontweight="bold")
    ax1.set_title("Mode A: SEC Shift with Permeate Decline", fontsize=12, fontweight="bold")
    ax1.set_xlim(0, 168)
    ax1.legend(frameon=True, fontsize=8.5, loc="upper left")

    for name, res in results_b.items():
        times = [s.time_hours for s in res.states]
        secs = [s.instantaneous_sec_kwh_m3 for s in res.states]
        ax2.plot(times, secs, label=name, color=colors.get(name, "black"), lw=2.0)
    
    ax2.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax2.set_ylabel(r"Instantaneous SEC ($\mathrm{kWh/m^3}$)", fontsize=11, fontweight="bold")
    ax2.set_title("Mode B: SEC Escalation with Pressure Ramping", fontsize=12, fontweight="bold")
    ax2.set_xlim(0, 168)
    ax2.legend(frameon=True, fontsize=8.5, loc="upper left")

    fig.suptitle("Specific Energy Consumption Dynamics under Membrane Fouling", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_04_sec_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 5: Cumulative Permeate Volume vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        qp_cum = []
        c_vol = 0.0
        for i in range(len(res.states)):
            if i == 0:
                qp_cum.append(0.0)
            else:
                dt = times[i] - times[i-1]
                q_avg = (res.states[i].instantaneous_permeate_flow_m3_h + res.states[i-1].instantaneous_permeate_flow_m3_h) / 2.0
                c_vol += q_avg * dt
                qp_cum.append(c_vol)
        ax.plot(times, qp_cum, label=name, color=colors.get(name, "black"), lw=2.2)

    ax.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax.set_ylabel(r"Cumulative Permeate Water Produced ($m^3$)", fontsize=11, fontweight="bold")
    ax.set_title("7-Day Cumulative Water Production (Mode A)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 168)
    ax.legend(frameon=True, fontsize=9, loc="upper left")
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_05_cumulative_permeate_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 6: Fouling Resistance Rf vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for name, res in results_a.items():
        times = [s.time_hours for s in res.states]
        rf_avg = [np.mean([e.r_f_m_inv for e in s.element_states]) for s in res.states]
        ax.plot(times, np.array(rf_avg) / 1e13, label=name, color=colors.get(name, "black"), lw=2.2)

    ax.set_xlabel("Operating Time (hours)", fontsize=11, fontweight="bold")
    ax.set_ylabel(r"Average Fouling Resistance $R_f$ ($10^{13}\ \mathrm{m^{-1}}$)", fontsize=11, fontweight="bold")
    ax.set_title("Evolution of Average Membrane Fouling Resistance over Time", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 168)
    ax.legend(frameon=True, fontsize=9, loc="upper left")
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_06_fouling_resistance_vs_time.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 7: Specific Permeate Volume vs Permeability Decline
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for name, res in results_a.items():
        v_specs = []
        c_v = 0.0
        times = [s.time_hours for s in res.states]
        for i in range(len(res.states)):
            if i == 0:
                v_specs.append(0.0)
            else:
                dt = times[i] - times[i-1]
                q_avg = (res.states[i].instantaneous_permeate_flow_m3_h + res.states[i-1].instantaneous_permeate_flow_m3_h) / 2.0
                c_v += (q_avg * dt * 1000.0) / 555.0
                v_specs.append(c_v)
        declines = [s.average_permeability_decline_pct for s in res.states]
        ax.plot(v_specs, declines, label=name, color=colors.get(name, "black"), lw=2.2)

    # Add empirical calibration anchor point
    ax.scatter([625.0], [15.0], color="black", s=100, zorder=5, marker="*", label=r"Literature Calibration Anchor ($625\ \mathrm{L/m^2} \to 15\%$)")
    ax.set_xlabel(r"Specific Cumulative Permeate Exposure ($L/\mathrm{m^2}$)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Permeability Decline (%)", fontsize=11, fontweight="bold")
    ax.set_title("Permeability Decline vs. Cumulative Specific Permeate Exposure", fontsize=12, fontweight="bold")
    ax.legend(frameon=True, fontsize=9, loc="upper left")
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_07_specific_permeate_vs_decline.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 8: Element Axial Fouling Profiles (Lead vs Tail)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    # Position labels: S1-E1, S1-E2, S1-E3, S2-E1, S2-E2, S2-E3
    pos_labels = ["S1-Lead", "S1-Mid", "S1-Tail", "S2-Lead", "S2-Mid", "S2-Tail"]
    x_indices = np.arange(len(pos_labels))

    for name in ["Strategy A (Max Recovery)", "Strategy D (Balanced Knee)", "Strategy B (Min Energy)", "Authoritative Baseline"]:
        sub = df_axial[df_axial["strategy_name"] == name]
        rf_profile = []
        decline_profile = []
        
        # Stage 1
        for e_idx in [1, 2, 3]:
            m = sub[(sub["stage_index"] == 1) & (sub["element_index"] == e_idx)]
            rf_profile.append(m["r_f_m_inv"].mean() / 1e13)
            decline_profile.append(m["permeability_decline_pct"].mean())
        # Stage 2
        for e_idx in [1, 2, 3]:
            m = sub[(sub["stage_index"] == 2) & (sub["element_index"] == e_idx)]
            rf_profile.append(m["r_f_m_inv"].mean() / 1e13)
            decline_profile.append(m["permeability_decline_pct"].mean())

        ax1.plot(x_indices, rf_profile, marker="o", lw=2.0, label=name, color=colors.get(name, "black"))
        ax2.plot(x_indices, decline_profile, marker="s", lw=2.0, label=name, color=colors.get(name, "black"))

    ax1.set_xticks(x_indices)
    ax1.set_xticklabels(pos_labels, fontsize=10, fontweight="bold")
    ax1.set_ylabel(r"Fouling Resistance $R_f$ ($10^{13}\ \mathrm{m^{-1}}$)", fontsize=11, fontweight="bold")
    ax1.set_title("Axial Distribution of Fouling Resistance after 168 Hours", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True, fontsize=8.5, loc="upper left")

    ax2.set_xticks(x_indices)
    ax2.set_xticklabels(pos_labels, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Permeability Decline (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Axial Permeability Degradation Profile", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True, fontsize=8.5, loc="upper left")

    fig.suptitle("Stage 1 & Stage 2 Lead-to-Tail Axial Fouling Maldistribution", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_08_axial_element_fouling_profile.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 9: Strategy Comparison Bar Charts (24h / 72h / 168h)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    strat_names = list(results_a.keys())
    short_names = ["Baseline", "Strategy A", "Strategy B", "Strategy C", "Strategy D"]
    x = np.arange(len(strat_names))
    width = 0.25

    # 168h Cumulative Water
    w_24 = [results_a[s].states[24].total_cumulative_permeate_m3 or (results_a[s].states[0].instantaneous_permeate_flow_m3_h * 24.0) for s in strat_names]
    w_72 = [results_a[s].states[72].total_cumulative_permeate_m3 or (results_a[s].states[0].instantaneous_permeate_flow_m3_h * 72.0) for s in strat_names]
    w_168 = [results_a[s].total_cumulative_permeate_m3 for s in strat_names]

    ax1.bar(x - width, [results_a[s].states[24].instantaneous_recovery_pct for s in strat_names], width, label="24 Hours", color="#3498db")
    ax1.bar(x, [results_a[s].states[72].instantaneous_recovery_pct for s in strat_names], width, label="72 Hours", color="#f39c12")
    ax1.bar(x + width, [results_a[s].states[168].instantaneous_recovery_pct for s in strat_names], width, label="168 Hours", color="#e74c3c")
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_names, fontsize=10, fontweight="bold")
    ax1.set_ylabel("Water Recovery (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Recovery Decay over Operational Horizons", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True, fontsize=9)

    ax2.bar(x - width, [results_a[s].states[24].instantaneous_sec_kwh_m3 for s in strat_names], width, label="24 Hours", color="#3498db")
    ax2.bar(x, [results_a[s].states[72].instantaneous_sec_kwh_m3 for s in strat_names], width, label="72 Hours", color="#f39c12")
    ax2.bar(x + width, [results_a[s].states[168].instantaneous_sec_kwh_m3 for s in strat_names], width, label="168 Hours", color="#e74c3c")
    ax2.set_xticks(x)
    ax2.set_xticklabels(short_names, fontsize=10, fontweight="bold")
    ax2.set_ylabel(r"SEC ($\mathrm{kWh/m^3}$)", fontsize=11, fontweight="bold")
    ax2.set_title("SEC Shifts over Operational Horizons", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True, fontsize=9)

    fig.suptitle("Operational Degradation Comparison across Horizons (24h vs 72h vs 168h)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig.savefig(out_dir / "stage6_09_strategy_comparison_radar_bars.png")
    plt.close(fig)


if __name__ == "__main__":
    run_stage6_master_study()
