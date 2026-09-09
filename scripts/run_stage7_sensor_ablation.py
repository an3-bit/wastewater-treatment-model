"""
Sensor Ablation & Information Contribution Study Script (Stage 7).

Executes:
1. Systematic single-sensor removal from Case 3 (Rich Sensor Set)
2. Evaluation of estimation error increase and FIM conditioning loss
3. Ranking of sensors: Essential, High Value, Moderate, Redundant
4. Generates results/stage7/tables/sensor_ablation_ranking.csv

Authoritative Model Version: "2.0-pressure-corrected"
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pickle
import pandas as pd

from ro_model.membrane import RO_MODEL_VERSION
from state_estimation.state_model import StateRepresentation
from state_estimation.measurement_model import SensorSet
from state_estimation.noise import NoiseLevel
from state_estimation.sensor_ablation import SensorAblationStudy


def run_stage7_sensor_ablation():
    print("=" * 80)
    print("STAGE 7: SENSOR ABLATION & INFORMATION CONTRIBUTION STUDY")
    print(f"Model Version: {RO_MODEL_VERSION}")
    print("=" * 80)

    traj_path = Path("results/stage7/trajectories/traj_clean_Strategy_D.pkl")
    if not traj_path.exists():
        print(f"[Error] Required trajectory {traj_path} not found. Run generation script first.")
        return

    with open(traj_path, "rb") as f:
        traj_data = pickle.load(f)

    tables_dir = Path("results/stage7/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)

    ablation_study = SensorAblationStudy(
        base_sensor_set=SensorSet.CASE_3_RICH,
        noise_level=NoiseLevel.NOMINAL,
        state_representation=StateRepresentation.AXIAL_6_ZONE,
    )

    print("  Running sensor ablation across 168h trajectory...")
    df_ablation = ablation_study.run_study(traj_data["records"])

    out_csv = tables_dir / "sensor_ablation_ranking.csv"
    df_ablation.to_csv(out_csv, index=False)
    print(f"\n[OK] Saved sensor ablation ranking to {out_csv}")

    print("\n" + "=" * 80)
    print("SENSOR ABLATION & INFORMATION CONTRIBUTION RANKING")
    print("=" * 80)
    for idx, row in df_ablation.iterrows():
        print(f"  * Removed: {row['ablated_sensor']:<28} | Rank: {row['effective_rank']} | "
              f"RMSE Incr: {row['rmse_increase_pct']:>6.1f}% | Class: {row['information_category']}")


if __name__ == "__main__":
    run_stage7_sensor_ablation()
