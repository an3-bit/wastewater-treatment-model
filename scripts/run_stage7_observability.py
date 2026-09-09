"""
Observability and State Dimension Study Script (Stage 7).

Evaluates:
1. Model A (15-Element), Model B (6-Zone), Model C (2-Stage)
2. Case 1 (Minimal), Case 2 (Standard), Case 3 (Rich) Sensor Sets
3. Effective rank, condition numbers, Fisher Information eigenvalues, and collinearity
4. Generates results/stage7/tables/observability_summary.csv and state_dimension_comparison.csv

Authoritative Model Version: "2.0-pressure-corrected"
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
import pandas as pd

from ro_model.membrane import RO_MODEL_VERSION
from state_estimation.state_model import StateRepresentation, StateVector
from state_estimation.measurement_model import SensorSet, SENSOR_SET_MEMBERS
from state_estimation.observability import ObservabilityAnalyzer
from state_estimation.noise import NoiseLevel


def run_stage7_observability_study():
    print("=" * 80)
    print("STAGE 7: OBSERVABILITY & STATE DIMENSION SENSITIVITY STUDY")
    print(f"Model Version: {RO_MODEL_VERSION}")
    print("=" * 80)

    tables_dir = Path("results/stage7/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)

    analyzer = ObservabilityAnalyzer(noise_level=NoiseLevel.NOMINAL)

    nominal_u = {
        "feed_flow_m3h": 30.0,
        "feed_tds_mgL": 2041.0,
        "temperature_C": 25.0,
        "stage1_pressure_bar": 16.06,
        "stage2_pressure_bar": 16.41,
    }

    state_models = [
        (StateRepresentation.FULL_15_ELEMENT, "Model A (Full 15-Element State)"),
        (StateRepresentation.AXIAL_6_ZONE, "Model B (Axial 6-Zone State)"),
        (StateRepresentation.LUMPED_2_STAGE, "Model C (Lumped 2-Stage State)"),
    ]

    sensor_cases = [
        (SensorSet.CASE_1_MINIMAL, "Case 1 (Minimal Sensor Set: 6 sensors)"),
        (SensorSet.CASE_2_STANDARD, "Case 2 (Standard Sensor Set: 10 sensors)"),
        (SensorSet.CASE_3_RICH, "Case 3 (Rich Sensor Set: 13 sensors)"),
    ]

    obs_rows = []
    dim_rows = []

    for s_rep, s_rep_name in state_models:
        st_clean = StateVector.create_clean(representation=s_rep)
        for s_case, s_case_name in sensor_cases:
            print(f"  Analyzing {s_rep_name} under {s_case_name}...")
            rep = analyzer.analyze(st_clean, nominal_u, sensor_set=s_case)

            s_vals = rep.singular_values
            s_top3 = [f"{v:.2e}" for v in s_vals[:min(3, len(s_vals))]]

            obs_rows.append({
                "state_model": s_rep.value,
                "state_model_name": s_rep_name,
                "sensor_set": s_case.value,
                "sensor_set_name": s_case_name,
                "state_dimension": rep.state_dimension,
                "measurement_dimension": rep.measurement_dimension,
                "effective_rank": rep.effective_rank,
                "rank_deficiency": rep.state_dimension - rep.effective_rank,
                "condition_number": rep.condition_number,
                "top_singular_values": ", ".join(s_top3),
                "smallest_singular_value": f"{s_vals[-1]:.2e}",
                "max_fim_eigenvalue": f"{rep.fim_eigenvalues[0]:.2e}",
                "summary": rep.observable_modes_summary,
            })

    df_obs = pd.DataFrame(obs_rows)
    df_obs.to_csv(tables_dir / "observability_summary.csv", index=False)
    print(f"\n[OK] Saved observability summary to {tables_dir / 'observability_summary.csv'}")

    # State Dimension Comparison under Standard Sensor Set
    for s_rep, s_rep_name in state_models:
        st_clean = StateVector.create_clean(representation=s_rep)
        rep = analyzer.analyze(st_clean, nominal_u, sensor_set=SensorSet.CASE_2_STANDARD)
        
        # Determine computational cost relative to Model C
        dim = rep.state_dimension
        comp_cost_relative = (2 * dim + 1) / (2 * 2 + 1) # UKF sigma point ratio

        dim_rows.append({
            "State Representation": s_rep_name,
            "State Dimension (n)": dim,
            "Meas Dimension (m)": rep.measurement_dimension,
            "Effective Rank": rep.effective_rank,
            "Rank Deficient": "YES" if rep.effective_rank < dim else "NO",
            "Condition Number": f"{rep.condition_number:.2e}" if rep.condition_number != float("inf") else "inf",
            "Relative Computational Cost": f"{comp_cost_relative:.1f}x",
            "Axial Diagnostic Fidelity": "High (Element-level)" if dim == 15 else "Medium (Stage Lead/Mid/Tail)" if dim == 6 else "Low (Stage Average)",
            "Recommendation": "Rejected (Unobservable parallel modes)" if dim == 15 else "RECOMMENDED (Primary Digital Twin Model)" if dim == 6 else "Viable Lightweight Fallback",
        })

    df_dim = pd.DataFrame(dim_rows)
    df_dim.to_csv(tables_dir / "state_dimension_comparison.csv", index=False)
    print(f"[OK] Saved state dimension comparison to {tables_dir / 'state_dimension_comparison.csv'}")

    # Print clean summary table
    print("\n" + "=" * 80)
    print("STATE DIMENSION & OBSERVABILITY MATRIX COMPARISON")
    print("=" * 80)
    for row in dim_rows:
        print(f"  * {row['State Representation']}:")
        print(f"      Dim = {row['State Dimension (n)']}, Rank = {row['Effective Rank']}, Cond # = {row['Condition Number']}")
        print(f"      Fidelity = {row['Axial Diagnostic Fidelity']}, Recommendation = {row['Recommendation']}")


if __name__ == "__main__":
    run_stage7_observability_study()
