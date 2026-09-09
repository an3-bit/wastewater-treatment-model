"""
Operational Decision Mapping Module for Stage 5.

Generates 2D contour operating maps across the admissible (P1, P2) pressure space,
overlaying physical constraint boundaries, authoritative baseline, and Pareto front.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ml.inference import Stage4Surrogate
from ml.domain_guard import OptimizationDomainGuard
from optimization.pareto import AUTHORITATIVE_BASELINE


def generate_operating_grid(
    surrogate: Stage4Surrogate,
    domain_guard: OptimizationDomainGuard,
    feed_flow_m3h: float = 30.0,
    feed_tds_mgL: float = 2041.0,
    temperature_C: float = 25.0,
    n_p1: int = 120,
    n_p2: int = 120,
) -> Dict[str, Any]:
    """
    Evaluate 2D grid across authoritative Stage 1 and Stage 2 pressure domain.
    """
    p1_vals = np.linspace(domain_guard.bounds.p1_min, domain_guard.bounds.p1_max, n_p1)
    p2_vals = np.linspace(domain_guard.bounds.p2_min, domain_guard.bounds.p2_max, n_p2)
    P1_grid, P2_grid = np.meshgrid(p1_vals, p2_vals)

    p1_flat = P1_grid.ravel()
    p2_flat = P2_grid.ravel()
    n_total = len(p1_flat)

    df_in = pd.DataFrame({
        "feed_flow_m3h": np.full(n_total, feed_flow_m3h),
        "feed_tds_mgL": np.full(n_total, feed_tds_mgL),
        "temperature_C": np.full(n_total, temperature_C),
        "stage1_pressure_bar": p1_flat,
        "stage2_pressure_bar": p2_flat,
    })

    preds = surrogate.predict_physics_reconstructed(df_in)

    rec_grid = preds["overall_recovery_pct"].to_numpy().reshape(P1_grid.shape)
    sec_grid = preds["SEC_kWh_m3"].to_numpy().reshape(P1_grid.shape)
    elem_rec_grid = preds["maximum_element_recovery_pct"].to_numpy().reshape(P1_grid.shape)
    cp_grid = preds["permeate_tds_mgL"].to_numpy().reshape(P1_grid.shape)
    beta_grid = preds["maximum_polarization_modulus"].to_numpy().reshape(P1_grid.shape)

    # Feasibility mask: P2 >= P1 and elem_rec <= 30.0 and cp <= 18.0
    feasible_mask = (P2_grid >= P1_grid) & (elem_rec_grid <= 30.0) & (cp_grid <= 18.0)

    return {
        "P1_grid": P1_grid,
        "P2_grid": P2_grid,
        "recovery": rec_grid,
        "SEC": sec_grid,
        "max_element_rec": elem_rec_grid,
        "permeate_tds": cp_grid,
        "polarization_modulus": beta_grid,
        "feasible_mask": feasible_mask,
        "feed_conditions": {
            "feed_flow_m3h": feed_flow_m3h,
            "feed_tds_mgL": feed_tds_mgL,
            "temperature_C": temperature_C,
        }
    }


def plot_operational_decision_map(
    grid_data: Dict[str, Any],
    df_pareto: Optional[pd.DataFrame] = None,
    baseline_point: Optional[Dict[str, float]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    Render comprehensive 6-panel 2D operating map in P1-P2 space.
    """
    if baseline_point is None:
        baseline_point = AUTHORITATIVE_BASELINE

    P1 = grid_data["P1_grid"]
    P2 = grid_data["P2_grid"]
    feed_cond = grid_data["feed_conditions"]

    fig, axes = plt.subplots(2, 3, figsize=(19, 11), dpi=300)
    plt.subplots_adjust(hspace=0.32, wspace=0.32)

    plots_cfg = [
        (axes[0, 0], grid_data["recovery"], "Water Recovery (%)", "viridis", 12, "%0.1f"),
        (axes[0, 1], grid_data["SEC"], "Specific Energy Consumption (kWh/m³)", "plasma", 12, "%0.3f"),
        (axes[0, 2], grid_data["max_element_rec"], "Max Element Recovery (%)", "magma", 12, "%0.1f"),
        (axes[1, 0], grid_data["permeate_tds"], "Permeate TDS (mg/L)", "cividis", 12, "%0.1f"),
        (axes[1, 1], grid_data["polarization_modulus"], "Max Polarization Modulus (β)", "inferno", 12, "%0.2f"),
        (axes[1, 2], grid_data["feasible_mask"].astype(float), "Feasibility & Operating Window", "Blues", 2, None),
    ]

    for ax, data_field, title, cmap_name, n_levels, fmt in plots_cfg:
        ax.set_facecolor("#f9f9fb")

        if fmt is not None:
            cs = ax.contourf(P1, P2, data_field, levels=n_levels, cmap=cmap_name, alpha=0.88)
            cbar = plt.colorbar(cs, ax=ax, fraction=0.046, pad=0.05)
            cbar.ax.tick_params(labelsize=8)
            # Contour lines
            clines = ax.contour(P1, P2, data_field, levels=n_levels, colors="black", linewidths=0.5, alpha=0.5)
            ax.clabel(clines, inline=True, fontsize=8, fmt=fmt)
        else:
            # Feasibility panel
            ax.contourf(P1, P2, data_field, levels=[-0.5, 0.5, 1.5], colors=["#ffd5d5", "#d4edda"], alpha=0.8)
            ax.text(0.15, 0.82, "FEASIBLE WINDOW\n(P2 ≥ P1 & ElemRec ≤ 30%)", transform=ax.transAxes,
                    fontsize=8.5, fontweight="bold", color="#155724", bbox=dict(boxstyle="round,pad=0.3", fc="#e2f0d9", ec="#155724", lw=1))
            ax.text(0.65, 0.15, "INADMISSIBLE\n(P2 < P1)", transform=ax.transAxes,
                    fontsize=8.5, fontweight="bold", color="#721c24", bbox=dict(boxstyle="round,pad=0.3", fc="#f8d7da", ec="#721c24", lw=1))

        # Physical constraint lines
        # 1. P2 = P1 line
        p_min = max(P1.min(), P2.min())
        p_max = min(P1.max(), P2.max())
        ax.plot([p_min, p_max], [p_min, p_max], "r--", linewidth=1.8, label="P2 = P1 Boundary" if ax == axes[0, 0] else "")

        # 2. 30% element recovery safeguard contour
        elem_rec_contour = ax.contour(P1, P2, grid_data["max_element_rec"], levels=[30.0], colors="#dc3545", linewidths=2.0, linestyles="-.")

        # 3. Optional beta = 1.40 safeguard contour
        beta_contour = ax.contour(P1, P2, grid_data["polarization_modulus"], levels=[1.40], colors="#fd7e14", linewidths=1.8, linestyles=":")

        # Shading for P2 < P1
        ax.fill_between(P1[0, :], P2.min(), P1[0, :], color="gray", alpha=0.25, hatch="//")

        # Baseline marker
        ax.plot(
            baseline_point["stage1_pressure_bar"],
            baseline_point["stage2_pressure_bar"],
            marker="*", markersize=14, color="#ffeb3b", markeredgecolor="black", markeredgewidth=1.5,
            label="Authoritative Baseline (13/18 bar)" if ax == axes[0, 0] else ""
        )

        # Pareto front overlay
        if df_pareto is not None and not df_pareto.empty:
            ax.plot(
                df_pareto["stage1_pressure_bar"],
                df_pareto["stage2_pressure_bar"],
                color="#00ffcc", linewidth=2.5, marker="o", markersize=3.5, markeredgecolor="#006655",
                label="NSGA-II Pareto Front" if ax == axes[0, 0] else ""
            )

        ax.set_xlim(P1.min(), P1.max())
        ax.set_ylim(P2.min(), P2.max())
        ax.set_xlabel("Stage 1 Feed Pressure P1 (bar)", fontsize=9.5, fontweight="bold")
        ax.set_ylabel("Stage 2 Feed Pressure P2 (bar)", fontsize=9.5, fontweight="bold")
        ax.set_title(title, fontsize=10.5, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)

    axes[0, 0].legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.suptitle(
        f"Stage 5 RO Operational Decision Map (Qf = {feed_cond['feed_flow_m3h']:.1f} m³/h, "
        f"TDS = {feed_cond['feed_tds_mgL']:.0f} mg/L, T = {feed_cond['temperature_C']:.1f} °C)",
        fontsize=14, fontweight="bold", y=0.98
    )

    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, bbox_inches="tight", dpi=300)

    return fig
