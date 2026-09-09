"""
Stage 5 Master Automation and Optimization Pipeline Script.

Executes:
1. Multi-seed NSGA-II multi-objective optimization (5 seeds, 200 generations, population 100).
2. Convergence analysis with Hypervolume tracking.
3. Case A (Standard) vs Case B (Project Engineering Polarization Safeguard beta <= 1.40).
4. Representative strategy selection (Max Recovery, Min SEC, Min Stress, Knee).
5. Authoritative baseline dominance testing.
6. Mechanistic differential-algebraic ground truth verification on representative + distributed Pareto points.
7. Surrogate exploitation diagnostic.
8. 2D operational decision contour maps.
9. Disturbance sensitivity scenarios (Feed TDS: 1500, 2041, 3000 mg/L; Feed flow: 20, 30, 40 m3/h).
10. Data exports and publication-quality figure generation.
"""

from pathlib import Path
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from ml.inference import Stage4Surrogate
from ml.domain_guard import OptimizationDomainGuard
from optimization.problem import ROOperatingOptimizationProblem
from optimization.nsga2_runner import run_nsga2, run_multi_seed_study
from optimization.pareto import (
    AUTHORITATIVE_BASELINE,
    find_non_dominated_front,
    select_knee_solution,
    select_representative_solutions,
    evaluate_baseline_dominance,
    select_distributed_pareto_candidates,
)
from optimization.verification import (
    verify_pareto_candidates_batch,
    analyze_surrogate_exploitation,
)
from optimization.operating_map import (
    generate_operating_grid,
    plot_operational_decision_map,
)


def run_stage5_pipeline():
    print("=" * 80)
    print("STAGE 5 — MULTI-OBJECTIVE RO OPERATING OPTIMIZATION USING NSGA-II")
    print("=" * 80)

    results_dir = Path("results/stage5")
    fig_dir = results_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load domain guard and surrogate
    print("\n[Step 1/8] Initializing OptimizationDomainGuard and Stage 4 ANN Surrogate...")
    guard = OptimizationDomainGuard.from_training_dataset()
    surrogate = Stage4Surrogate.load(
        model_dir="models/stage4",
        model_name="ann___mlp",
        is_neural_net=True,
    )
    print(f"Domain Bounds: P1 in [{guard.bounds.p1_min:.2f}, {guard.bounds.p1_max:.2f}] bar, "
          f"P2 in [{guard.bounds.p2_min:.2f}, {guard.bounds.p2_max:.2f}] bar")

    # 2. Multi-Seed NSGA-II Optimization on Base Feed Conditions
    print("\n[Step 2/8] Running Multi-Seed NSGA-II Optimization (5 Seeds, 200 Gens, Pop 100)...")
    seeds = [42, 101, 2024, 777, 999]
    ref_point = np.array([0.0, 2.0, 35.0])

    def base_problem_factory():
        return ROOperatingOptimizationProblem(
            surrogate=surrogate,
            domain_guard=guard,
            feed_flow_m3h=30.0,
            feed_tds_mgL=2041.0,
            temperature_C=25.0,
            enforce_polarization_limit=False,
        )

    multi_seed_res = run_multi_seed_study(
        problem_factory=base_problem_factory,
        seeds=seeds,
        pop_size=100,
        n_gen=200,
        ref_point=ref_point,
    )

    df_pareto_surrogate = multi_seed_res["global_pareto_front"]
    conv_summary = multi_seed_res["convergence_summary"]
    print(f"Multi-Seed Optimization Complete! Mean HV = {conv_summary['mean_final_hv']:.3f} +/- {conv_summary['std_final_hv']:.3f}")
    print(f"Total Unique Non-Dominated Solutions in Global Front: {len(df_pareto_surrogate)}")

    # Export Pareto front CSV
    df_pareto_surrogate.to_csv(results_dir / "pareto_front_surrogate.csv", index=False)

    # Export Convergence Summary CSV
    df_conv = pd.DataFrame([{
        "seed": r["seed"],
        "elapsed_seconds": r["elapsed_seconds"],
        "n_evaluations": r["n_evaluations"],
        "final_hypervolume": r["final_hypervolume"],
        "n_pareto_solutions": len(r["pareto_front"]),
    } for r in multi_seed_res["seed_results"]])
    df_conv.to_csv(results_dir / "convergence_summary.csv", index=False)

    # 3. Polarization Safeguard Case Comparison (Case A vs Case B)
    print("\n[Step 3/8] Evaluating Optional Polarization Safeguard (Case A vs Case B: beta <= 1.40)...")
    prob_case_b = ROOperatingOptimizationProblem(
        surrogate=surrogate,
        domain_guard=guard,
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        temperature_C=25.0,
        enforce_polarization_limit=True,
        polarization_limit=1.40,
    )
    res_case_b = run_nsga2(prob_case_b, pop_size=100, n_gen=200, seed=42, ref_point=ref_point)
    df_pareto_case_b = res_case_b["pareto_front"]
    print(f"Case A (Standard) Solutions: {len(df_pareto_surrogate)} | Case B (beta <= 1.40) Solutions: {len(df_pareto_case_b)}")

    # 4. Representative Solutions and Baseline Dominance
    print("\n[Step 4/8] Extracting 4 Representative Strategies and Testing Baseline Dominance...")
    rep_solutions = select_representative_solutions(df_pareto_surrogate)
    dominance_res = evaluate_baseline_dominance(df_pareto_surrogate)

    print(f"Authoritative Baseline Status: {dominance_res['baseline_status']}")
    print(f"Candidates Dominating Baseline: {dominance_res['n_candidates_dominating_baseline']}")
    print(f"Candidates Dominated by Baseline: {dominance_res['n_candidates_dominated_by_baseline']}")
    print(f"Closest Pareto Point Distance to Baseline: {dominance_res['closest_relative_distance']:.4f}")

    for strat_key, strat_val in rep_solutions.items():
        print(f"  Strategy {strat_val['strategy_name']}: "
              f"P1={strat_val['stage1_pressure_bar']:.2f} bar, P2={strat_val['stage2_pressure_bar']:.2f} bar | "
              f"Rec={strat_val['overall_recovery_pct']:.2f}%, SEC={strat_val['SEC_kWh_m3']:.3f} kWh/m3, "
              f"MaxElemRec={strat_val['maximum_element_recovery_pct']:.2f}%, Cp={strat_val['permeate_tds_mgL']:.2f} mg/L")

    # 5. Mechanistic Verification of Representative Points + 10 Distributed Candidates
    print("\n[Step 5/8] Mechanistic Re-Simulation & Verification of Pareto Candidates...")
    candidates_to_verify = select_distributed_pareto_candidates(
        df_pareto=df_pareto_surrogate,
        representative_solutions=rep_solutions,
        n_additional=12,
    )
    print(f"Running full differential-algebraic RO simulator on {len(candidates_to_verify)} candidate points...")
    df_verified = verify_pareto_candidates_batch(
        candidates=candidates_to_verify,
        surrogate=surrogate,
        domain_guard=guard,
    )
    df_verified.to_csv(results_dir / "pareto_verified_candidates.csv", index=False)

    exploit_audit = analyze_surrogate_exploitation(df_verified)
    print(f"Mechanistic Verification Complete! "
          f"Mean Rec Err = {exploit_audit['mean_recovery_abs_error_pct']:.3f}%, "
          f"Mean SEC Err = {exploit_audit['mean_sec_abs_error_kWh_m3']:.4f} kWh/m3, "
          f"Mean MaxElemRec Err = {exploit_audit['mean_elem_rec_abs_error_pct']:.3f}%")
    print(f"False Feasible Candidates (Safeguard Violations): {exploit_audit['n_false_feasible_candidates']}")
    print(f"Evidence of Surrogate Exploitation: {exploit_audit['evidence_of_exploitation']}")

    # 6. 2D Operational Decision Maps
    print("\n[Step 6/8] Generating 2D Operational Decision Maps across (P1, P2) Pressure Space...")
    grid_data = generate_operating_grid(
        surrogate=surrogate,
        domain_guard=guard,
        feed_flow_m3h=30.0,
        feed_tds_mgL=2041.0,
        temperature_C=25.0,
        n_p1=120,
        n_p2=120,
    )
    fig_op_map = plot_operational_decision_map(
        grid_data=grid_data,
        df_pareto=df_pareto_surrogate,
        baseline_point=AUTHORITATIVE_BASELINE,
        output_path=fig_dir / "stage5_06_operational_decision_map.png",
    )
    plt.close(fig_op_map)
    print(f"Saved: {fig_dir / 'stage5_06_operational_decision_map.png'}")

    # 7. Disturbance Scenarios Optimization (TDS and Flow)
    print("\n[Step 7/8] Running Disturbance Sensitivity Scenarios...")
    disturbance_scenarios = [
        {"name": "LOW_SALINITY", "feed_flow_m3h": 30.0, "feed_tds_mgL": 1500.0, "temperature_C": 25.0},
        {"name": "BASE_FEED", "feed_flow_m3h": 30.0, "feed_tds_mgL": 2041.0, "temperature_C": 25.0},
        {"name": "HIGH_SALINITY", "feed_flow_m3h": 30.0, "feed_tds_mgL": 3000.0, "temperature_C": 25.0},
        {"name": "LOW_FLOW", "feed_flow_m3h": 20.0, "feed_tds_mgL": 2041.0, "temperature_C": 25.0},
        {"name": "BASE_FLOW", "feed_flow_m3h": 30.0, "feed_tds_mgL": 2041.0, "temperature_C": 25.0},
        {"name": "HIGH_FLOW", "feed_flow_m3h": 40.0, "feed_tds_mgL": 2041.0, "temperature_C": 25.0},
    ]

    dist_results = []
    dist_pareto_dict = {}

    for d in disturbance_scenarios:
        print(f"  Optimizing disturbance scenario: {d['name']} (Qf={d['feed_flow_m3h']:.1f} m3/h, TDS={d['feed_tds_mgL']:.0f} mg/L)...")
        prob_d = ROOperatingOptimizationProblem(
            surrogate=surrogate,
            domain_guard=guard,
            feed_flow_m3h=d["feed_flow_m3h"],
            feed_tds_mgL=d["feed_tds_mgL"],
            temperature_C=d["temperature_C"],
        )
        res_d = run_nsga2(prob_d, pop_size=100, n_gen=200, seed=42, ref_point=ref_point)
        df_p_d = res_d["pareto_front"]
        dist_pareto_dict[d["name"]] = df_p_d

        reps_d = select_representative_solutions(df_p_d)
        knee_d = reps_d["balanced_knee"]

        dist_results.append({
            "scenario_name": d["name"],
            "feed_flow_m3h": d["feed_flow_m3h"],
            "feed_tds_mgL": d["feed_tds_mgL"],
            "temperature_C": d["temperature_C"],
            "n_pareto_solutions": len(df_p_d),
            "knee_p1_bar": knee_d["stage1_pressure_bar"],
            "knee_p2_bar": knee_d["stage2_pressure_bar"],
            "knee_recovery_pct": knee_d["overall_recovery_pct"],
            "knee_sec_kWh_m3": knee_d["SEC_kWh_m3"],
            "knee_max_element_rec_pct": knee_d["maximum_element_recovery_pct"],
            "knee_permeate_tds_mgL": knee_d["permeate_tds_mgL"],
            "max_recovery_pct": reps_d["max_recovery"]["overall_recovery_pct"],
            "max_recovery_sec_kWh_m3": reps_d["max_recovery"]["SEC_kWh_m3"],
            "min_sec_kWh_m3": reps_d["min_energy"]["SEC_kWh_m3"],
            "min_sec_recovery_pct": reps_d["min_energy"]["overall_recovery_pct"],
            "min_stress_elem_rec_pct": reps_d["min_stress"]["maximum_element_recovery_pct"],
        })

    df_dist_summary = pd.DataFrame(dist_results)
    df_dist_summary.to_csv(results_dir / "disturbance_scenario_summary.csv", index=False)

    # 8. Render All Publication Figures
    print("\n[Step 8/8] Rendering Publication Figures...")
    plot_stage5_figures(
        df_pareto_surrogate=df_pareto_surrogate,
        df_pareto_case_b=df_pareto_case_b,
        rep_solutions=rep_solutions,
        baseline_point=AUTHORITATIVE_BASELINE,
        multi_seed_res=multi_seed_res,
        df_verified=df_verified,
        dist_pareto_dict=dist_pareto_dict,
        fig_dir=fig_dir,
    )

    print("\nSTAGE 5 AUTOMATION PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Results archived in: {results_dir}")


def plot_stage5_figures(
    df_pareto_surrogate: pd.DataFrame,
    df_pareto_case_b: pd.DataFrame,
    rep_solutions: Dict[str, Any],
    baseline_point: Dict[str, float],
    multi_seed_res: Dict[str, Any],
    df_verified: pd.DataFrame,
    dist_pareto_dict: Dict[str, pd.DataFrame],
    fig_dir: Path,
):
    """Generate all 8 publication figures for Stage 5."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "grid.color": "#cccccc",
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
    })

    # -------------------------------------------------------------
    # Fig 1: 2D Pareto Trade-Offs (3 subplots)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    plt.subplots_adjust(wspace=0.25)

    rec = df_pareto_surrogate["overall_recovery_pct"]
    sec = df_pareto_surrogate["SEC_kWh_m3"]
    elem_rec = df_pareto_surrogate["maximum_element_recovery_pct"]
    p2_col = df_pareto_surrogate["stage2_pressure_bar"]

    # Panel 1: Recovery vs SEC
    sc1 = axes[0].scatter(rec, sec, c=p2_col, cmap="viridis", s=45, alpha=0.9, edgecolors="none", label="Pareto Front")
    cbar1 = plt.colorbar(sc1, ax=axes[0], fraction=0.046, pad=0.04)
    cbar1.set_label("Stage 2 Pressure P2 (bar)", fontsize=9, fontweight="bold")
    axes[0].plot(baseline_point["overall_recovery_pct"], baseline_point["SEC_kWh_m3"],
                 marker="*", markersize=14, color="#ffeb3b", markeredgecolor="black", markeredgewidth=1.5, label="Authoritative Baseline")
    axes[0].set_xlabel("Overall Water Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Specific Energy Consumption (kWh/m³)", fontsize=10, fontweight="bold")
    axes[0].set_title("Recovery vs Energy Consumption", fontsize=11, fontweight="bold")

    # Panel 2: Recovery vs Max Element Recovery
    sc2 = axes[1].scatter(rec, elem_rec, c=p2_col, cmap="viridis", s=45, alpha=0.9, edgecolors="none")
    cbar2 = plt.colorbar(sc2, ax=axes[1], fraction=0.046, pad=0.04)
    cbar2.set_label("Stage 2 Pressure P2 (bar)", fontsize=9, fontweight="bold")
    axes[1].plot(baseline_point["overall_recovery_pct"], baseline_point["maximum_element_recovery_pct"],
                 marker="*", markersize=14, color="#ffeb3b", markeredgecolor="black", markeredgewidth=1.5)
    axes[1].axhline(30.0, color="#dc3545", linestyle="-.", linewidth=1.5, label="30% Safeguard Limit")
    axes[1].set_xlabel("Overall Water Recovery (%)", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Maximum Element Recovery (%)", fontsize=10, fontweight="bold")
    axes[1].set_title("Recovery vs Membrane Stress Proxy", fontsize=11, fontweight="bold")

    # Panel 3: SEC vs Max Element Recovery
    sc3 = axes[2].scatter(sec, elem_rec, c=rec, cmap="plasma", s=45, alpha=0.9, edgecolors="none")
    cbar3 = plt.colorbar(sc3, ax=axes[2], fraction=0.046, pad=0.04)
    cbar3.set_label("Water Recovery (%)", fontsize=9, fontweight="bold")
    axes[2].plot(baseline_point["SEC_kWh_m3"], baseline_point["maximum_element_recovery_pct"],
                 marker="*", markersize=14, color="#ffeb3b", markeredgecolor="black", markeredgewidth=1.5)
    axes[2].axhline(30.0, color="#dc3545", linestyle="-.", linewidth=1.5)
    axes[2].set_xlabel("Specific Energy Consumption (kWh/m³)", fontsize=10, fontweight="bold")
    axes[2].set_ylabel("Maximum Element Recovery (%)", fontsize=10, fontweight="bold")
    axes[2].set_title("Energy vs Membrane Stress Proxy", fontsize=11, fontweight="bold")

    # Mark representative solutions on all panels
    rep_markers = [
        ("max_recovery", "D", "#d62728", "Max Recovery (A)"),
        ("min_energy", "s", "#2ca02c", "Min Energy (B)"),
        ("min_stress", "^", "#1f77b4", "Min Stress (C)"),
        ("balanced_knee", "o", "#9467bd", "Balanced Knee (D)"),
    ]
    for key, marker, color, lbl in rep_markers:
        sol = rep_solutions[key]
        axes[0].plot(sol["overall_recovery_pct"], sol["SEC_kWh_m3"], marker=marker, markersize=9, color=color, markeredgecolor="black", label=lbl)
        axes[1].plot(sol["overall_recovery_pct"], sol["maximum_element_recovery_pct"], marker=marker, markersize=9, color=color, markeredgecolor="black", label=lbl)
        axes[2].plot(sol["SEC_kWh_m3"], sol["maximum_element_recovery_pct"], marker=marker, markersize=9, color=color, markeredgecolor="black", label=lbl)

    for ax in axes:
        ax.grid(True)
        ax.set_facecolor("#fafafa")
    axes[0].legend(loc="upper left", fontsize=8, framealpha=0.9)
    axes[1].legend(loc="upper left", fontsize=8, framealpha=0.9)

    fig.suptitle("Stage 5 Multi-Objective RO Operating Optimization: 2D Pareto Trade-Off Projections", fontsize=13, fontweight="bold", y=0.98)
    fig.savefig(fig_dir / "stage5_01_pareto_tradeoffs_2d.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 2: 3D Pareto Surface
    # -------------------------------------------------------------
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111, projection="3d")
    p3d = ax.scatter(
        df_pareto_surrogate["overall_recovery_pct"],
        df_pareto_surrogate["SEC_kWh_m3"],
        df_pareto_surrogate["maximum_element_recovery_pct"],
        c=df_pareto_surrogate["stage2_pressure_bar"],
        cmap="viridis",
        s=50,
        alpha=0.85,
        edgecolors="k",
        linewidths=0.3,
    )
    cbar = fig.colorbar(p3d, ax=ax, fraction=0.03, pad=0.08)
    cbar.set_label("Stage 2 Pressure P2 (bar)", fontsize=9, fontweight="bold")

    # Baseline
    ax.scatter(
        [baseline_point["overall_recovery_pct"]],
        [baseline_point["SEC_kWh_m3"]],
        [baseline_point["maximum_element_recovery_pct"]],
        color="#ffeb3b", s=180, marker="*", edgecolor="black", linewidth=1.5, label="Authoritative Baseline (13/18 bar)"
    )

    # Representative Points
    for key, marker, color, lbl in rep_markers:
        sol = rep_solutions[key]
        ax.scatter(
            [sol["overall_recovery_pct"]],
            [sol["SEC_kWh_m3"]],
            [sol["maximum_element_recovery_pct"]],
            color=color, s=120, marker=marker, edgecolor="black", linewidth=1.2, label=lbl
        )

    ax.set_xlabel("Recovery (%)", fontsize=9, fontweight="bold", labelpad=8)
    ax.set_ylabel("SEC (kWh/m³)", fontsize=9, fontweight="bold", labelpad=8)
    ax.set_zlabel("Max Element Recovery (%)", fontsize=9, fontweight="bold", labelpad=8)
    ax.set_title("Stage 5 Multi-Objective 3D Pareto Frontier\n(Recovery vs Energy vs Membrane Stress)", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.savefig(fig_dir / "stage5_02_pareto_3d_surface.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 3: Hypervolume Convergence Curves across 5 Seeds
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    all_hv_hist = np.array([r["hypervolume_history"] for r in multi_seed_res["seed_results"]])
    gens = multi_seed_res["seed_results"][0]["generations"]

    for i, r in enumerate(multi_seed_res["seed_results"]):
        ax.plot(gens, r["hypervolume_history"], alpha=0.45, linewidth=1.2, label=f"Seed {r['seed']} (Final={r['final_hypervolume']:.2f})")

    mean_hv = np.mean(all_hv_hist, axis=0)
    std_hv = np.std(all_hv_hist, axis=0)
    ax.plot(gens, mean_hv, color="#1f77b4", linewidth=2.5, label="Mean Hypervolume Across 5 Seeds")
    ax.fill_between(gens, mean_hv - std_hv, mean_hv + std_hv, color="#1f77b4", alpha=0.18, label="+/- 1 Std Dev")

    ax.set_xlabel("NSGA-II Generation Number", fontsize=10, fontweight="bold")
    ax.set_ylabel("Hypervolume (ref: [0, 2.0, 35])", fontsize=10, fontweight="bold")
    ax.set_title("Multi-Objective Convergence & Stability Across 5 Independent NSGA-II Seeds", fontsize=11, fontweight="bold")
    ax.grid(True)
    ax.set_facecolor("#fafafa")
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
    fig.savefig(fig_dir / "stage5_03_hypervolume_convergence.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 4: Case A (Standard) vs Case B (Polarization Safeguard beta <= 1.40)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    plt.subplots_adjust(wspace=0.25)

    # Panel 1: Recovery vs SEC
    axes[0].scatter(df_pareto_surrogate["overall_recovery_pct"], df_pareto_surrogate["SEC_kWh_m3"],
                    color="#1f77b4", s=35, alpha=0.7, label="Case A: Standard (No Beta Limit)")
    axes[0].scatter(df_pareto_case_b["overall_recovery_pct"], df_pareto_case_b["SEC_kWh_m3"],
                    color="#d62728", marker="x", s=50, alpha=0.85, label="Case B: Polarization Safeguard (β ≤ 1.40)")
    axes[0].plot(baseline_point["overall_recovery_pct"], baseline_point["SEC_kWh_m3"],
                 marker="*", markersize=13, color="#ffeb3b", markeredgecolor="black", label="Authoritative Baseline")
    axes[0].set_xlabel("Overall Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("SEC (kWh/m³)", fontsize=10, fontweight="bold")
    axes[0].set_title("Pareto Front: Case A vs Case B (Recovery vs Energy)", fontsize=11, fontweight="bold")
    axes[0].grid(True)
    axes[0].set_facecolor("#fafafa")
    axes[0].legend(fontsize=8.5, framealpha=0.9)

    # Panel 2: Recovery vs Max Polarization Modulus
    axes[1].scatter(df_pareto_surrogate["overall_recovery_pct"], df_pareto_surrogate["maximum_polarization_modulus"],
                    color="#1f77b4", s=35, alpha=0.7, label="Case A (Unconstrained β)")
    axes[1].scatter(df_pareto_case_b["overall_recovery_pct"], df_pareto_case_b["maximum_polarization_modulus"],
                    color="#d62728", marker="x", s=50, alpha=0.85, label="Case B (Constrained β ≤ 1.40)")
    axes[1].axhline(1.40, color="#dc3545", linestyle="-.", linewidth=1.5, label="β = 1.40 Safeguard Limit")
    axes[1].plot(baseline_point["overall_recovery_pct"], baseline_point["maximum_polarization_modulus"],
                 marker="*", markersize=13, color="#ffeb3b", markeredgecolor="black", label="Authoritative Baseline")
    axes[1].set_xlabel("Overall Recovery (%)", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Maximum Polarization Modulus β", fontsize=10, fontweight="bold")
    axes[1].set_title("Polarization Modulus vs Recovery", fontsize=11, fontweight="bold")
    axes[1].grid(True)
    axes[1].set_facecolor("#fafafa")
    axes[1].legend(fontsize=8.5, framealpha=0.9)

    fig.suptitle("Impact of Optional Project Engineering Polarization Safeguard (β ≤ 1.40)", fontsize=13, fontweight="bold", y=0.98)
    fig.savefig(fig_dir / "stage5_04_case_a_vs_case_b_polarization.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 5: Mechanistic Verification Parity (Reconstructed ANN vs Ground Truth Simulator)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    plt.subplots_adjust(wspace=0.25)

    # Subplot 1: Recovery Parity
    m_rec = df_verified["mech_overall_recovery_pct"]
    s_rec = df_verified["surr_overall_recovery_pct"]
    axes[0].scatter(m_rec, s_rec, color="#1f77b4", s=55, alpha=0.85, edgecolors="black", linewidths=0.5)
    lims1 = [min(m_rec.min(), s_rec.min()) - 1.0, max(m_rec.max(), s_rec.max()) + 1.0]
    axes[0].plot(lims1, lims1, "k--", linewidth=1.2, label="1:1 Parity Line")
    axes[0].set_xlim(lims1)
    axes[0].set_ylim(lims1)
    axes[0].set_xlabel("Mechanistic Simulator Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Surrogate Predicted Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_title("Recovery Parity (Max Err = {:.2f}%)".format(df_verified["err_recovery_abs_pct"].max()), fontsize=11, fontweight="bold")

    # Subplot 2: SEC Parity
    m_sec = df_verified["mech_SEC_kWh_m3"]
    s_sec = df_verified["surr_SEC_kWh_m3"]
    axes[1].scatter(m_sec, s_sec, color="#2ca02c", s=55, alpha=0.85, edgecolors="black", linewidths=0.5)
    lims2 = [min(m_sec.min(), s_sec.min()) - 0.02, max(m_sec.max(), s_sec.max()) + 0.02]
    axes[1].plot(lims2, lims2, "k--", linewidth=1.2, label="1:1 Parity Line")
    axes[1].set_xlim(lims2)
    axes[1].set_ylim(lims2)
    axes[1].set_xlabel("Mechanistic Simulator SEC (kWh/m³)", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Surrogate Predicted SEC (kWh/m³)", fontsize=10, fontweight="bold")
    axes[1].set_title("SEC Parity (Max Err = {:.4f} kWh/m³)".format(df_verified["err_sec_abs_kWh_m3"].max()), fontsize=11, fontweight="bold")

    # Subplot 3: Max Element Recovery Parity
    m_el = df_verified["mech_max_element_rec_pct"]
    s_el = df_verified["surr_max_element_rec_pct"]
    axes[2].scatter(m_el, s_el, color="#d62728", s=55, alpha=0.85, edgecolors="black", linewidths=0.5)
    lims3 = [min(m_el.min(), s_el.min()) - 1.0, max(m_el.max(), s_el.max()) + 1.0]
    axes[2].plot(lims3, lims3, "k--", linewidth=1.2, label="1:1 Parity Line")
    axes[2].axhline(30.0, color="#dc3545", linestyle="-.", linewidth=1.5, label="30% Safeguard Limit")
    axes[2].axvline(30.0, color="#dc3545", linestyle="-.", linewidth=1.5)
    axes[2].set_xlim(lims3)
    axes[2].set_ylim(lims3)
    axes[2].set_xlabel("Mechanistic Simulator Max Element Rec (%)", fontsize=10, fontweight="bold")
    axes[2].set_ylabel("Surrogate Max Element Rec (%)", fontsize=10, fontweight="bold")
    axes[2].set_title("Max Element Recovery Parity (Max Err = {:.2f}%)".format(df_verified["err_max_elem_rec_abs_pct"].max()), fontsize=11, fontweight="bold")

    for ax in axes:
        ax.grid(True)
        ax.set_facecolor("#fafafa")
        ax.legend(fontsize=8.5, framealpha=0.9)

    fig.suptitle("Stage 5 Mechanistic Ground-Truth Parity Verification of Pareto Candidates", fontsize=13, fontweight="bold", y=0.98)
    fig.savefig(fig_dir / "stage5_05_mechanistic_verification_parity.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 7: Disturbance Sensitivity Pareto Fronts (TDS and Flow Shifts)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), dpi=300)
    plt.subplots_adjust(wspace=0.25)

    # Panel 1: Salinity Shift (1500 vs 2041 vs 3000 mg/L)
    tds_colors = {"LOW_SALINITY": ("#2ca02c", "Low TDS (1500 mg/L)"), "BASE_FEED": ("#1f77b4", "Base TDS (2041 mg/L)"), "HIGH_SALINITY": ("#d62728", "High TDS (3000 mg/L)")}
    for sc_name, (col, lbl) in tds_colors.items():
        if sc_name in dist_pareto_dict:
            df_sc = dist_pareto_dict[sc_name]
            axes[0].scatter(df_sc["overall_recovery_pct"], df_sc["SEC_kWh_m3"], color=col, s=35, alpha=0.75, label=lbl)
    axes[0].set_xlabel("Overall Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("SEC (kWh/m³)", fontsize=10, fontweight="bold")
    axes[0].set_title("Pareto Shift Across Feed Salinity Disturbances (Qf = 30 m³/h)", fontsize=11, fontweight="bold")
    axes[0].grid(True)
    axes[0].set_facecolor("#fafafa")
    axes[0].legend(fontsize=8.5, framealpha=0.9)

    # Panel 2: Flow Rate Shift (20 vs 30 vs 40 m3/h)
    flow_colors = {"LOW_FLOW": ("#9467bd", "Low Flow (20 m³/h)"), "BASE_FLOW": ("#1f77b4", "Base Flow (30 m³/h)"), "HIGH_FLOW": ("#ff7f0e", "High Flow (40 m³/h)")}
    for sc_name, (col, lbl) in flow_colors.items():
        if sc_name in dist_pareto_dict:
            df_sc = dist_pareto_dict[sc_name]
            axes[1].scatter(df_sc["overall_recovery_pct"], df_sc["SEC_kWh_m3"], color=col, s=35, alpha=0.75, label=lbl)
    axes[1].set_xlabel("Overall Recovery (%)", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("SEC (kWh/m³)", fontsize=10, fontweight="bold")
    axes[1].set_title("Pareto Shift Across Feed Flow Disturbances (TDS = 2041 mg/L)", fontsize=11, fontweight="bold")
    axes[1].grid(True)
    axes[1].set_facecolor("#fafafa")
    axes[1].legend(fontsize=8.5, framealpha=0.9)

    fig.suptitle("Sensitivity of Optimal Operating Frontiers to Plant Feed Disturbances", fontsize=13, fontweight="bold", y=0.98)
    fig.savefig(fig_dir / "stage5_07_disturbance_sensitivity_pareto.png", bbox_inches="tight", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Fig 8: Surrogate Exploitation Diagnostic (Prediction Error vs Pareto Position)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    plt.subplots_adjust(wspace=0.25)

    # Panel 1: Recovery Error vs Recovery
    axes[0].scatter(df_verified["mech_overall_recovery_pct"], df_verified["err_recovery_abs_pct"], color="#1f77b4", s=60, alpha=0.85, edgecolors="black", linewidths=0.6)
    axes[0].set_xlabel("Mechanistic Overall Recovery (%)", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Absolute Recovery Prediction Error (%)", fontsize=10, fontweight="bold")
    axes[0].set_title("Surrogate Recovery Error vs Operating Recovery", fontsize=11, fontweight="bold")
    axes[0].grid(True)
    axes[0].set_facecolor("#fafafa")

    # Panel 2: Max Element Recovery Error vs Max Element Recovery
    axes[1].scatter(df_verified["mech_max_element_rec_pct"], df_verified["err_max_elem_rec_abs_pct"], color="#d62728", s=60, alpha=0.85, edgecolors="black", linewidths=0.6)
    axes[1].axvline(30.0, color="#dc3545", linestyle="-.", linewidth=1.5, label="30% Safeguard Boundary")
    axes[1].set_xlabel("Mechanistic Max Element Recovery (%)", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Absolute Max Element Recovery Error (%)", fontsize=10, fontweight="bold")
    axes[1].set_title("Surrogate Stress Error vs Operating Stress", fontsize=11, fontweight="bold")
    axes[1].grid(True)
    axes[1].set_facecolor("#fafafa")
    axes[1].legend(fontsize=8.5, framealpha=0.9)

    fig.suptitle("Surrogate Exploitation & Boundary Error Audit along Pareto Frontier", fontsize=13, fontweight="bold", y=0.98)
    fig.savefig(fig_dir / "stage5_08_surrogate_error_vs_pareto_position.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    run_stage5_pipeline()
