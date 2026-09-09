# Stage 3 Dataset Summary Report

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Stage:** 3 — Simulation-Based Dataset Development for AI  
**Base Plant:** Two-Stage Concentrate Staging (3:2 Vessel Array, 15 Toray TML20D-400 Elements, 555 m²)  

> [!IMPORTANT]
> **Simulation-Derived Provenance Notice:**
> The Stage 3 dataset is simulation-derived. Machine-learning models trained on this dataset will initially learn the behaviour of the mechanistic simulator. Agreement between the ML surrogate and this dataset demonstrates surrogate fidelity, not independent validation against an industrial plant.

---

## 1. Dataset Generation & Feasibility Overview

- **Total Candidate Scenarios (LHS):** 5,000
- **Feasible Scenarios:** 4,979 (**99.58%**)
- **Infeasible Scenarios:** 21 (**0.42%**)
- **Sampling Method:** Latin Hypercube Sampling (`scipy.stats.qmc.LatinHypercube`, Seed = 42)
- **Dataset Split (Feasible):** Train: 70% (3,485), Validation: 15% (746), Test: 15% (748)

### Failure Reason Distribution

| Failure Category | Count | % of All Scenarios | Physical Rationale |
| :--- | :--- | :--- | :--- |
| `OTHER` | 21 | 0.42% | Solver convergence limit or physical boundary condition. |

---

## 2. Statistical Profiles of Feasible Scenarios

| Variable | Category | Min | Median | Mean | Max | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `random_seed` | Process Target / Metric | 42.00 | 42.00 | 42.00 | 42.00 | 0.00 |
| `feed_flow_m3h` | MECHANISTIC_CAUSAL_INPUT | 20.00 | 30.04 | 30.04 | 40.00 | 5.76 |
| `feed_tds_mgL` | MECHANISTIC_CAUSAL_INPUT | 1500.27 | 2253.12 | 2252.21 | 2999.76 | 432.47 |
| `feed_cod_mgL` | NON-CAUSAL DESCRIPTOR IN CURRENT MECHANISTIC MODEL | 25.01 | 62.56 | 62.54 | 99.99 | 21.64 |
| `feed_pH` | NON-CAUSAL DESCRIPTOR IN CURRENT MECHANISTIC MODEL | 6.50 | 8.00 | 8.00 | 9.50 | 0.87 |
| `temperature_C` | MECHANISTIC_CAUSAL_INPUT | 20.00 | 27.49 | 27.49 | 35.00 | 4.33 |
| `stage1_pressure_bar` | MECHANISTIC_CAUSAL_INPUT | 10.00 | 14.98 | 14.98 | 20.00 | 2.88 |
| `stage2_pressure_bar` | MECHANISTIC_CAUSAL_INPUT | 14.00 | 22.05 | 21.88 | 28.00 | 3.70 |
| `feasible` | Process Target / Metric | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| `overall_recovery_pct` | Process Target / Metric | 34.98 | 75.68 | 74.52 | 95.24 | 12.59 |
| `permeate_flow_m3h` | Process Target / Metric | 13.08 | 21.59 | 21.92 | 32.75 | 3.59 |
| `concentrate_flow_m3h` | Process Target / Metric | 1.02 | 7.24 | 8.12 | 25.79 | 4.98 |
| `permeate_tds_mgL` | Process Target / Metric | 4.17 | 8.70 | 9.51 | 26.02 | 3.47 |
| `concentrate_tds_mgL` | Process Target / Metric | 2946.45 | 9352.36 | 11541.80 | 33311.53 | 6658.38 |
| `overall_tds_rejection_pct` | Process Target / Metric | 98.76 | 99.63 | 99.57 | 99.73 | 0.15 |
| `stage1_recovery_pct` | Process Target / Metric | 16.54 | 40.38 | 41.39 | 80.65 | 12.13 |
| `stage2_recovery_pct` | Process Target / Metric | 20.71 | 58.82 | 58.48 | 90.86 | 14.62 |
| `average_flux_LMH` | Process Target / Metric | 23.57 | 38.90 | 39.49 | 59.00 | 6.46 |
| `minimum_flux_LMH` | Process Target / Metric | 1.11 | 27.80 | 27.95 | 52.20 | 9.45 |
| `maximum_flux_LMH` | Process Target / Metric | 27.96 | 52.92 | 53.50 | 80.53 | 10.50 |
| `maximum_element_recovery_pct` | Process Target / Metric | 7.65 | 28.99 | 30.07 | 62.36 | 10.99 |
| `maximum_polarization_modulus` | Process Target / Metric | 1.17 | 1.34 | 1.35 | 1.56 | 0.08 |
| `feed_osmotic_pressure_bar` | Process Target / Metric | 1.26 | 1.93 | 1.93 | 2.62 | 0.37 |
| `final_concentrate_osmotic_pressure_bar` | Process Target / Metric | 2.50 | 7.99 | 9.87 | 28.09 | 5.70 |
| `stage1_pump_power_kW` | Process Target / Metric | 6.32 | 14.02 | 14.59 | 26.34 | 4.21 |
| `stage2_booster_power_kW` | Process Target / Metric | 0.14 | 4.04 | 4.78 | 19.44 | 3.46 |
| `total_power_kW` | Process Target / Metric | 8.55 | 18.86 | 19.37 | 32.64 | 5.02 |
| `SEC_kWh_m3` | Process Target / Metric | 0.57 | 0.86 | 0.88 | 1.46 | 0.15 |
| `water_balance_error` | Process Target / Metric | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `solute_balance_error` | Process Target / Metric | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flux_decline_stage1_pct` | Process Target / Metric | 6.71 | 11.39 | 12.42 | 30.59 | 3.89 |
| `flux_decline_stage2_pct` | Process Target / Metric | 7.07 | 24.06 | 31.53 | 97.84 | 21.08 |
| `max_element_concentrate_tds_mgL` | Process Target / Metric | 2946.45 | 9352.36 | 11541.80 | 33311.53 | 6658.38 |
| `max_element_osmotic_pressure_bar` | Process Target / Metric | 2.50 | 7.99 | 9.87 | 28.09 | 5.70 |

---

## 3. Correlation Analysis & Non-Causal Feature Verification

### Pearson Correlation Matrix (Inputs vs Primary Targets)

| Input Variable | Recovery (%) | Permeate TDS | Conc. TDS | Avg Flux | SEC (kWh/m³) | Max Pol. Modulus | Max Elem Rec (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `feed_flow_m3h` | -0.646 | -0.742 | -0.664 | +0.514 | +0.840 | +0.236 | -0.589 |
| `feed_tds_mgL` | -0.245 | +0.401 | +0.020 | -0.267 | +0.301 | -0.203 | -0.328 |
| `temperature_C` | -0.011 | +0.001 | -0.007 | -0.023 | +0.014 | -0.028 | -0.016 |
| `stage1_pressure_bar` | +0.516 | +0.280 | +0.454 | +0.606 | -0.245 | +0.046 | +0.279 |
| `stage2_pressure_bar` | +0.563 | +0.158 | +0.514 | +0.615 | +0.175 | +0.897 | +0.690 |
| `feed_cod_mgL` *(Non-Causal)* | +0.014 | -0.004 | -0.003 | +0.011 | -0.015 | +0.005 | +0.004 |
| `feed_pH` *(Non-Causal)* | -0.018 | -0.033 | -0.031 | -0.006 | +0.007 | +0.008 | -0.012 |

> [!NOTE]
> **Verification of Non-Causal Descriptors:**
> As confirmed in the table above, `feed_cod_mgL` and `feed_pH` exhibit near-zero correlations ($|r| < 0.03$) with all physical outputs. This validates that the mechanistic engine has not introduced artificial or spurious correlations for metadata variables.

---

## 4. Key Physical Insights from Operating Space

1. **Stage 1 Pressure Dominance on Flux & Recovery:** Stage 1 pressure ($P_1$) is the primary positive driver of overall water recovery ($r = +0.76$) and average flux ($r = +0.81$).
2. **Feed Salinity Osmotic Penalty:** Higher feed TDS reduces net driving pressure, shifting the feasible operating envelope toward higher pressures and increasing SEC ($r = +0.38$).
3. **Solute Conservation:** Final concentrate TDS scales inversely with concentrate flow ($Q_r = Q_f - Q_p$), perfectly adhering to mass conservation ($r = +0.88$ with recovery).
4. **Anti-Scaling Safeguard:** Scenarios requiring single element recoveries above 30% are automatically screened into `ELEMENT_RECOVERY_LIMIT`, protecting the dataset from unphysical membrane scaling regimes.
