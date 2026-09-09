# Stage 3B Engineering Envelope Audit & Dataset Curation Report

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Stage:** 3B — Engineering Envelope Audit and Dataset Curation  
**Target Model:** Two-Stage Concentrate Staging (3:2 Vessel Array, 15 Toray TML20D-400 Elements, 555 m²)  

> [!IMPORTANT]
> **Scientific Notice on Curation & Operational Safeguards:**
> The 30% single-element recovery limit is designated as a **project engineering safeguard**, established to protect the primary machine-learning training domain from extreme lead-element concentration polarization, localized scaling, and hydraulic overloading. It is not claimed to be an absolute Toray manufacturer limit.
>
> Converged boundary stress cases (> 30% element recovery) are preserved in `data/generated/stage3_boundary_stress.csv` for constraint classification, safety envelopes, and digital twin warning logic.

---

## 1. Operating Classification Summary

- **Total Raw LHS Scenarios:** 5,000 (100.0%)
- **Physically Valid (Converged):** 4,979 (99.58%)
- **Engineering Acceptable (<= 30% Elem Rec):** 2,670 (**53.63%** of feasible, **53.40%** of all candidate points)
- **Boundary Stress (> 30% Elem Rec):** 2,309 (**46.37%** of feasible)
- **Physically Infeasible (Numerical/Pressure Limit):** 21 (0.42%)
- **Deterministic Curated Splits:** Train: 1,869 (70%), Val: 400 (15%), Test: 401 (15%)

---

## 2. Element Recovery Safeguard Sensitivity Study

| Safeguard Threshold | Accepted Scenarios | % of Feasible Set | % of 5,000 Candidates | Boundary Stress Scenarios |
| :--- | :--- | :--- | :--- | :--- |
| `<= 20%` | 1,006 | 20.20% | 20.12% | 3,973 |
| `<= 25%` | 1,833 | 36.81% | 36.66% | 3,146 |
| `<= 30%` | 2,670 | 53.63% | 53.40% | 2,309 |
| `<= 35%` | 3,399 | 68.27% | 67.98% | 1,580 |

---

## 3. Overall Recovery Domain Bands Analysis

| Recovery Band | Count | % of Feasible | Mean Recovery (%) | Mean SEC (kWh/m³) | Mean Conc TDS (mg/L) | Mean Max Elem Rec (%) | Mean Pol Modulus |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LOW (< 50%)** | 201 | 4.04% | 46.13% | 1.1123 | 4578.40 | 11.97% | 1.2499 |
| **NORMAL (50–80%)** | 2,843 | 57.10% | 68.05% | 0.9304 | 7607.06 | 24.01% | 1.3407 |
| **HIGH (80–90%)** | 1,403 | 28.18% | 85.02% | 0.7902 | 15426.97 | 37.89% | 1.3686 |
| **EXTREME (> 90%)** | 532 | 10.68% | 92.16% | 0.7360 | 24953.89 | 48.70% | 1.3678 |

---

## 4. Curated Input Domain Coverage

| Mechanistic Feature | Full Range (Sampled) | Curated Range (Acceptable) | Curated Median | Unit | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `feed_flow_m3h` | [20.00, 40.00] | [20.00, 40.00] | 33.62 | m³/h | Fully Covered |
| `feed_tds_mgL` | [1500.27, 2999.76] | [1501.80, 2999.70] | 2394.95 | mg/L | Fully Covered |
| `temperature_C` | [20.00, 35.00] | [20.00, 35.00] | 27.63 | °C | Fully Covered |
| `stage1_pressure_bar` | [10.00, 20.00] | [10.00, 20.00] | 14.07 | bar | Fully Covered |
| `stage2_pressure_bar` | [14.00, 28.00] | [14.00, 27.99] | 19.77 | bar | Fully Covered |

---

## 5. Answers to the 10 Stage 3B Questions

1. **How many of the 4,979 physically valid scenarios are engineering acceptable?**  
   **2,670 scenarios** (53.63% of physically valid simulations) satisfy the $\le 30\%$ single-element recovery safeguard.

2. **How many become boundary/stress cases?**  
   **2,309 scenarios** (46.37% of physically valid simulations) exhibit maximum element recovery $> 30\%$ and are sequestered into `data/generated/stage3_boundary_stress.csv`.

3. **What percentage of data is removed from the primary training domain?**  
   **46.37%** of the physically valid data is filtered out of the primary surrogate training set, ensuring the AI model only learns high-integrity, anti-fouling operational regimes.

4. **How sensitive is dataset size to 20%, 25%, 30%, 35% element-recovery safeguards?**  
   - At `<= 20%`: 1,006 scenarios (20.20% of feasible set)
   - At `<= 25%`: 1,833 scenarios (36.81% of feasible set)
   - At `<= 30%`: 2,670 scenarios (53.63% of feasible set)
   - At `<= 35%`: 3,399 scenarios (68.27% of feasible set)

5. **What operating conditions most commonly cause >30% element recovery?**  
   Aggressive single-element recoveries (>30%) are predominantly triggered by **high Stage 1 and Stage 2 operating pressures ($P_1 > 16\ \text{bar}, P_2 > 24\ \text{bar}$)** combined with **lower feed flow rates ($Q_f < 28\ \text{m}^3/\text{h}$)**, which force lead and second-stage elements into excessive local water fluxes.

6. **Does the curated dataset still cover the Stage 2 baseline region?**  
   **Yes.** The Stage 2 model-derived baseline (Qf = 30 m3/h, Cf = 2041 mg/L, T = 25 °C, P1 = 13 bar, P2 = 18 bar) yields an overall recovery of 65.45% and a maximum element recovery of 21.24%, sitting safely within the `ENGINEERING_ACCEPTABLE` training domain.

7. **What are the final mechanistic input ranges in the curated set?**  
   - `feed_flow_m3h`: 20.00 - 40.00 m³/h (median: 33.62 m³/h)
   - `feed_tds_mgL`: 1501.80 - 2999.70 mg/L (median: 2394.95 mg/L)
   - `temperature_C`: 20.00 - 35.00 °C (median: 27.63 °C)
   - `stage1_pressure_bar`: 10.00 - 20.00 bar (median: 14.07 bar)
   - `stage2_pressure_bar`: 14.00 - 27.99 bar (median: 19.77 bar)

8. **How many OOD cases remain engineering acceptable?**  
   **200 out of 200 (100.0%)** of the Out-Of-Distribution scenarios are engineering acceptable. Because OOD scenarios were sampled at elevated feed flows ($Q_f \in [42, 45]\ \mathrm{m}^3/\mathrm{h}$), cross-flow velocities were higher, naturally maintaining single-element recoveries below $30\%$ across all cases.

9. **Is the curated dataset sufficiently large and diverse for ML surrogate training?**  
   **Yes.** With **2,670 high-quality scenarios** (1,869 train / 400 val / 401 test) spanning full multidimensional Latin Hypercube coverage of the 5-dimensional causal parameter space, the dataset provides ample statistical power and smoothness for training XGBoost, Random Forest, and ANN surrogate models.

10. **What exact features should Stage 4 use?**  
   - **Surrogate Inputs (5):** `feed_flow_m3h`, `feed_tds_mgL`, `temperature_C`, `stage1_pressure_bar`, `stage2_pressure_bar`
   - **Primary Output Targets (5):** `overall_recovery_pct`, `permeate_tds_mgL`, `concentrate_tds_mgL`, `average_flux_LMH`, `SEC_kWh_m3`
   - **Secondary State Targets (2):** `maximum_element_recovery_pct`, `maximum_polarization_modulus`
   - **Excluded from Inputs:** `feed_cod_mgL`, `feed_pH` (non-causal descriptors) and derived flow rates.
