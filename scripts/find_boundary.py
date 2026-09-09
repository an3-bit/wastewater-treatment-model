import numpy as np
import pandas as pd
from data_generation.simulator_runner import run_single_simulation, create_baseline_system

system = create_baseline_system()
print(f"Stage 1: {system.stages[0].parallel_vessels} vessels x {system.stages[0].elements_per_vessel} elements = {system.stages[0].total_elements}")
print(f"Stage 2: {system.stages[1].parallel_vessels} vessels x {system.stages[1].elements_per_vessel} elements = {system.stages[1].total_elements}")
print(f"Total System Elements = {system.total_elements}")

results = []
for p1 in np.linspace(17.0, 19.5, 51):
    for p2 in np.linspace(p1, min(p1 + 1.2, 19.8), 31):
        res = run_single_simulation(
            feed_flow_m3h=30.0,
            feed_tds_mgL=2041.0,
            feed_cod_mgL=51.0,
            feed_pH=8.0,
            temperature_C=25.0,
            stage1_pressure_bar=p1,
            stage2_pressure_bar=p2,
            system=system,
        )
        if res["feasible"]:
            results.append({
                "p1": float(p1),
                "p2": float(p2),
                "recovery": float(res["overall_recovery_pct"]),
                "sec": float(res["SEC_kWh_m3"]),
                "max_elem_rec": float(res["maximum_element_recovery_pct"]),
                "cp": float(res["permeate_tds_mgL"]),
                "cr": float(res["concentrate_tds_mgL"]),
                "flux": float(res["average_flux_LMH"]),
                "beta": float(res["maximum_polarization_modulus"]),
                "qp": float(res["permeate_flow_m3h"]),
                "qr": float(res["concentrate_flow_m3h"]),
                "power": float(res["SEC_kWh_m3"] * res["permeate_flow_m3h"]),
            })

df = pd.DataFrame(results)
print(f"Total feasible points simulated: {len(df)}")

for limit in [27.0, 28.0, 29.0, 30.0]:
    df_sub = df[df["max_elem_rec"] <= limit]
    if not df_sub.empty:
        best_idx = df_sub["recovery"].idxmax()
        best = df_sub.loc[best_idx]
        print(f"Safeguard <= {limit:.1f}%: P1={best['p1']:.4f}, P2={best['p2']:.4f} -> Rec={best['recovery']:.4f}%, MaxElemRec={best['max_elem_rec']:.4f}%, SEC={best['sec']:.6f}, Cp={best['cp']:.2f}, Beta={best['beta']:.4f}, Qp={best['qp']:.2f}, Qr={best['qr']:.2f}, Power={best['power']:.2f} kW")
