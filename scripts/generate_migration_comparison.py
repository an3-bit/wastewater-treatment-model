import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path("c:/Users/bruxe/wastewater")
migration_dir = ROOT_DIR / "results/migration"
migration_dir.mkdir(parents=True, exist_ok=True)

comparison_data = [
    # Parameters
    {
        "Category": "Membrane Physics",
        "Metric": "Toray Standard Test Pressure Delta P (bar)",
        "Model_V1": "14.5000",
        "Model_V2": "15.5132",
        "Difference": "+1.0132 bar (+6.99%)",
        "Classification": "MATERIALLY CHANGED (PHYSICAL CONVENTION)",
    },
    {
        "Category": "Membrane Physics",
        "Metric": "Water Permeability Aw (m/(Pa.s))",
        "Model_V1": "1.023200e-11",
        "Model_V2": "9.446312e-12",
        "Difference": "-7.68e-13 m/(Pa.s) (-7.50%)",
        "Classification": "MATERIALLY CHANGED (PHYSICAL CONVENTION)",
    },
    {
        "Category": "Membrane Physics",
        "Metric": "Water Permeability Aw (LMH/bar)",
        "Model_V1": "3.683520",
        "Model_V2": "3.400672",
        "Difference": "-0.282848 LMH/bar (-7.68%)",
        "Classification": "MATERIALLY CHANGED (PHYSICAL CONVENTION)",
    },
    {
        "Category": "Membrane Physics",
        "Metric": "Clean Membrane Resistance Rm (m^-1)",
        "Model_V1": "1.097800e+14",
        "Model_V2": "1.188868e+14",
        "Difference": "+9.1068e+12 m^-1 (+8.30%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Membrane Physics",
        "Metric": "Calibrated Specific Fouling Resistance r_spec (m^-1 / (m^3/m^2))",
        "Model_V1": "1.805200e+13",
        "Model_V2": "1.954988e+13",
        "Difference": "+1.4979e+12 m^-1/(m^3/m^2) (+8.30%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    # Stage 1 Validation
    {
        "Category": "Stage 1 Validation",
        "Metric": "Permeate Flow Qp (m3/day)",
        "Model_V1": "39.70",
        "Model_V2": "39.70",
        "Difference": "0.00 m3/day (0.000%)",
        "Classification": "UNCHANGED (EXACT MATCH)",
    },
    {
        "Category": "Stage 1 Validation",
        "Metric": "Average Flux Jw (LMH)",
        "Model_V1": "44.71",
        "Model_V2": "44.71",
        "Difference": "0.00 LMH (0.006% rel error)",
        "Classification": "UNCHANGED (EXACT MATCH)",
    },
    {
        "Category": "Stage 1 Validation",
        "Metric": "Recovery Y (%)",
        "Model_V1": "15.00%",
        "Model_V2": "15.00%",
        "Difference": "0.00% (0.000% rel error)",
        "Classification": "UNCHANGED (EXACT MATCH)",
    },
    # Stage 2 Baseline
    {
        "Category": "Stage 2 Baseline",
        "Metric": "Baseline Overall Recovery (%)",
        "Model_V1": "69.3597%",
        "Model_V2": "65.4543%",
        "Difference": "-3.9054% (-5.63% rel)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 2 Baseline",
        "Metric": "Baseline SEC (kWh/m3)",
        "Model_V1": "0.771027",
        "Model_V2": "0.824396",
        "Difference": "+0.053369 kWh/m3 (+6.92%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 2 Baseline",
        "Metric": "Baseline Max Element Recovery (%)",
        "Model_V1": "23.6858%",
        "Model_V2": "21.2441%",
        "Difference": "-2.4417% (-10.31% rel)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 2 Baseline",
        "Metric": "Baseline Max Polarization Modulus beta",
        "Model_V1": "1.301863",
        "Model_V2": "1.281999",
        "Difference": "-0.019864 (-1.53%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    # Stage 3 Curation
    {
        "Category": "Stage 3 Dataset",
        "Metric": "Engineering Acceptable Scenarios (<= 30% Elem Rec)",
        "Model_V1": "2,241 (45.25%)",
        "Model_V2": "2,670 (53.63%)",
        "Difference": "+429 scenarios (+8.38% yield)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 3 Dataset",
        "Metric": "Train / Val / Test Partition Sizes",
        "Model_V1": "1,569 / 336 / 336",
        "Model_V2": "1,868 / 401 / 401",
        "Difference": "+299 train / +65 val / +65 test",
        "Classification": "NUMERICALLY SHIFTED",
    },
    # Stage 4 Surrogates
    {
        "Category": "Stage 4 Surrogates",
        "Metric": "ANN Test Set Overall Recovery R2",
        "Model_V1": "0.99978",
        "Model_V2": "0.99979",
        "Difference": "+0.00001",
        "Classification": "UNCHANGED (EXCELLENT FIT)",
    },
    {
        "Category": "Stage 4 Surrogates",
        "Metric": "ANN Inference Speed-up vs Mechanistic Simulator",
        "Model_V1": "1,520x",
        "Model_V2": "1,568x",
        "Difference": "+48x",
        "Classification": "UNCHANGED",
    },
    # Stage 5 Optimization
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Baseline Dominance Status",
        "Model_V1": "STRICTLY DOMINATED (by 59 candidates)",
        "Model_V2": "STRICTLY DOMINATED (by 59 candidates)",
        "Difference": "0 candidates (Identical dominance structure)",
        "Classification": "UNCHANGED (STRUCTURAL TRUTH)",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy A (Max Recovery) Operating Pressures (P1, P2)",
        "Model_V1": "19.08 bar, 19.73 bar",
        "Model_V2": "20.00 bar, 20.25 bar",
        "Difference": "+0.92 bar P1, +0.52 bar P2",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy A Max Feasible Recovery (%)",
        "Model_V1": "82.17%",
        "Model_V2": "84.35%",
        "Difference": "+2.18%",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy B (Min SEC) Operating Pressures (P1, P2)",
        "Model_V1": "15.30 bar, 15.30 bar",
        "Model_V2": "15.80 bar, 15.80 bar",
        "Difference": "+0.50 bar P1, +0.50 bar P2",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy B Clean SEC (kWh/m3)",
        "Model_V1": "0.7303",
        "Model_V2": "0.7641",
        "Difference": "+0.0338 kWh/m3 (+4.63%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy D (Balanced Knee) Operating Pressures (P1, P2)",
        "Model_V1": "15.05 bar, 15.80 bar",
        "Model_V2": "16.06 bar, 16.41 bar",
        "Difference": "+1.01 bar P1, +0.61 bar P2",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 5 Optimization",
        "Metric": "Strategy D Clean Recovery (%) / SEC (kWh/m3)",
        "Model_V1": "71.05% / 0.7340 kWh/m3",
        "Model_V2": "70.16% / 0.7665 kWh/m3",
        "Difference": "-0.89% Rec / +0.0325 kWh/m3 SEC",
        "Classification": "NUMERICALLY SHIFTED",
    },
    # Stage 6 Dynamic Fouling
    {
        "Category": "Stage 6 Dynamic Fouling",
        "Metric": "Baseline 7-Day Cumulative Permeate (m3)",
        "Model_V1": "2,217.4",
        "Model_V2": "2,082.7",
        "Difference": "-134.7 m3 (-6.07%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 6 Dynamic Fouling",
        "Metric": "Baseline 7-Day Dynamic Average SEC (kWh/m3)",
        "Model_V1": "1.2597",
        "Model_V2": "1.3682",
        "Difference": "+0.1085 kWh/m3 (+8.61%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 6 Dynamic Fouling",
        "Metric": "Strategy A 7-Day Cumulative Permeate (m3)",
        "Model_V1": "2,581.4",
        "Model_V2": "2,626.2",
        "Difference": "+44.8 m3 (+1.74%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 6 Dynamic Fouling",
        "Metric": "Strategy D 7-Day Cumulative Permeate (m3)",
        "Model_V1": "2,376.1",
        "Model_V2": "2,332.1",
        "Difference": "-44.0 m3 (-1.85%)",
        "Classification": "NUMERICALLY SHIFTED",
    },
    {
        "Category": "Stage 6 Dynamic Fouling",
        "Metric": "Dynamic Pareto Trade-off Structure & Strategy Ranking",
        "Model_V1": "Strategy D dominates Baseline; Strategy A yields max water; Strategy C yields min fouling",
        "Model_V2": "Strategy D dominates Baseline; Strategy A yields max water; Strategy C yields min fouling",
        "Difference": "Identical ranking, dominance, and structural trade-offs",
        "Classification": "UNCHANGED (STRUCTURAL TRUTH)",
    },
]

df_comp = pd.DataFrame(comparison_data)
csv_out = migration_dir / "model_v1_vs_v2_comparison.csv"
df_comp.to_csv(csv_out, index=False)
print(f"Saved migration comparison CSV to: {csv_out}")
