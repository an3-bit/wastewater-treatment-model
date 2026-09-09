# Stage 5B Report: Mechanistic Feasibility Boundary Refinement

**Project**: AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Phase**: Stage 5B — Mechanistic Feasibility Boundary Refinement & Safeguard Margin Audit  
**Author / Engineering Role**: Process Systems & Membrane Modeling Group  
**Audited Simulator**: Toray TML20D-400 Two-Stage Mechanistic Simulator (15 Total Elements)  

---

## Executive Summary

Stage 5B executes the final feasibility boundary refinement for the two-stage industrial reverse osmosis (RO) textile wastewater reuse system. During Stage 5, multi-objective NSGA-II optimization identified a surrogate candidate at $P_1 = 19.19\,\text{bar}, P_2 = 19.63\,\text{bar}$ with predicted single-element recovery of $29.9998\%$. Subsequent ground-truth mechanistic verification revealed that this candidate slightly exceeded the $30.0\%$ project safeguard ($R_{\text{elem, max}} = 30.28\%$), demonstrating subtle surrogate boundary exploitation.

In Stage 5B, direct high-resolution mechanistic simulations were conducted across the high-recovery Pareto corridor to establish the exact physical operating boundary where $R_{\text{elem, max}} \le 30.000\%$.

```
========================================================================================================================
                          STAGE 5B MAXIMUM MECHANISTICALLY VERIFIED FEASIBLE RECOVERY
========================================================================================================================
Optimal Operating Pressures:           P1* = 19.08 bar, P2* = 19.73 bar (Boost = +0.65 bar)
Overall Water Recovery:                85.08% (85.0763%)
Maximum Element Recovery:              29.99% (29.9932% <= 30.000%, Margin = 0.0068 percentage points)
Specific Energy Consumption:           0.7561 kWh/m3 (0.756051 kWh/m3)
Permeate TDS Quality:                  9.24 mg/L (<= 18.0 mg/L reference limit)
Concentrate Salinity:                  13623.5 mg/L
Average Trans-Membrane Flux:           45.99 LMH
Maximum Polarization Modulus:          beta = 1.3675 (<= 1.40 safeguard)
Volumetric Production:                 Permeate Qp = 25.52 m3/h | Concentrate Qr = 4.48 m3/h
Electrical Power Consumption:          19.30 kW
========================================================================================================================
Verification & Safeguard Status:       100% FEASIBLE, MECHANISTICALLY VALIDATED, ZERO SOLUTE BALANCE ERROR
========================================================================================================================
```

---

## 1. Authoritative System Configuration Audit

To ensure complete scientific precision across all documentation, the authoritative membrane module counts were re-verified:
- **Stage 1**: 3 parallel pressure vessels x 3 membrane elements in series = **9 elements** (333.0 m2 active area)
- **Stage 2**: 2 parallel pressure vessels x 3 membrane elements in series = **6 elements** (222.0 m2 active area)
- **Total System**: **15 Toray TML20D-400 membrane elements** (555.0 m2 total active area)

---

## 2. Refined Four Representative Operating Strategies

With the true physical 30% boundary identified, the four representative operating strategies are finalized as follows:

| Strategy | Pressures ($P_1 / P_2$) | Recovery (%) | SEC (kWh/m³) | Max Elem Rec (%) | Permeate TDS (mg/L) | Flux (LMH) | $\beta_{\max}$ | Power (kW) | Operational Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Authoritative Baseline** | $13.00 / 18.00\,\text{bar}$ | $69.36\%$ | $0.7710$ | $23.69\%$ | $7.23$ | $37.49$ | $1.302$ | $16.05$ | Published Starting Point (**DOMINATED**) |
| **Strategy A (Max Feasible Recovery)** | **19.08 / 19.73 bar** | **85.08%** | **0.7561** | **29.99%** | **9.24** | **45.99** | **1.368** | **19.30** | **Refined Upper Physical Limit ($R_{\text{elem, max}} \le 30\%$)** |
| **Strategy B (Min Energy)** | $15.30 / 15.30\,\text{bar}$ | $69.82\%$ | $0.7224$ | $20.63\%$ | $7.64$ | $37.74$ | $1.273$ | $15.13$ | Lowest Energy Consumption ($-6.3\%$ SEC) |
| **Strategy C (Min Stress)** | $10.00 / 14.00\,\text{bar}$ | $51.68\%$ | $0.8239$ | $13.99\%$ | $7.53$ | $27.93$ | $1.223$ | $12.77$ | Lowest Membrane Stress ($-40.9\%$ Stress) |
| **Strategy D (Balanced Knee)** | **15.05 / 15.80 bar** | **70.22%** | **0.7269** | **20.10%** | **7.59** | **37.96** | **1.267** | **15.31** | **Optimal Compromise Operating Point** |

### Audit Artifact Preservation
The surrogate candidate $P_1 = 19.19\,\text{bar}, P_2 = 19.63\,\text{bar}$ ($R_{\text{elem, max}} = 30.28\%$) is officially archived in `pareto_verified_candidates.csv` under the label:
`SURROGATE_MAX_REC_CANDIDATE_INFEASIBLE`
as a permanent benchmark of surrogate boundary approximation error.

---

## 3. Engineering Safeguard Margins & Buffer Recommendations

Because real-world plant operation involves measurement noise, membrane compaction, and surrogate prediction tolerance, operating right at $R_{\text{elem, max}} = 30.000\%$ is not recommended in open-loop plant dispatch.

The maximum mechanistically achievable water recoveries under conservative safeguard thresholds are summarized below:

| Safeguard Limit ($R_{\text{elem, max}}$) | Optimal $P_1$ (bar) | Optimal $P_2$ (bar) | Max Recovery (%) | SEC (kWh/m³) | Permeate TDS (mg/L) | Max $\beta$ | Permeate Flow $Q_p$ (m³/h) | Power (kW) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **<= 27.0%** | 17.90 | 18.30 | 81.09% | 0.7397 | 8.50 | 1.337 | 24.33 | 17.99 |
| **<= 28.0%** | 18.30 | 18.70 | 82.41% | 0.7442 | 8.71 | 1.347 | 24.72 | 18.40 |
| **<= 29.0%** | 18.70 | 19.20 | 83.80% | 0.7498 | 8.96 | 1.358 | 25.14 | 18.85 |
| **<= 30.0%** | 19.08 | 19.73 | 85.08% | 0.7561 | 9.24 | 1.368 | 25.52 | 19.30 |

### Safety Buffer Recommendation
Based on the observed surrogate element-recovery prediction error (~0.28 percentage points), it is recommended that future surrogate-based evolutionary searches enforce an internal screening safeguard of:
$$\text{predicted } R_{\text{elem, max}} \le 29.5\% \quad (\text{or } 29.0\%)$$
This ensures that any surrogate optimization candidate will strictly satisfy the true physical 30.0% threshold before post-optimization mechanistic re-simulation.

---

## 4. Re-Verification of Baseline Dominance

The authoritative baseline ($P_1=13.00\,\text{bar}, P_2=18.00\,\text{bar}$) was re-evaluated against the mechanistically verified solutions:
- **Baseline Performance**: $R = 69.3597\%$, $\text{SEC} = 0.771027\,\text{kWh/m}^3$, $R_{\text{elem, max}} = 23.6858\%$
- **Strategy D (Balanced Knee)**: $R = 70.2171\% > R_{\text{base}}$, $\text{SEC} = 0.726876\,\text{kWh/m}^3 < \text{SEC}_{\text{base}}$, $R_{\text{elem, max}} = 20.1032\% < R_{\text{elem, max, base}}$
- **Strategy B (Minimum Energy)**: $R = 69.8242\% > R_{\text{base}}$, $\text{SEC} = 0.722429\,\text{kWh/m}^3 < \text{SEC}_{\text{base}}$, $R_{\text{elem, max}} = 20.6259\% < R_{\text{elem, max, base}}$

Both Strategy D and Strategy B strictly dominate the baseline across all three objective dimensions simultaneously under 100% mechanistic differential-algebraic simulation.

---

## 5. Answers to the 8 Stage 5B Final Questions

1. **What is the refined maximum mechanistically verified feasible recovery?**  
   **85.08%** (85.0763%).

2. **At what P1/P2 does it occur?**  
   $$P_1^* = 19.08\,\text{bar}, \quad P_2^* = 19.73\,\text{bar} \quad (\Delta P_{\text{boost}} = +0.65\,\text{bar})$$

3. **How close is max element recovery to 30%?**  
   Maximum element recovery is **29.9932%**, which is within **0.0068 percentage points** of 30.000% (well within the <= 0.05 target threshold) and strictly feasible.

4. **What recovery is available with 27%, 28%, 29% and 30% safeguards?**  
   - <= 27% limit: **81.09%** recovery ($P_1=17.90, P_2=18.30\,\text{bar}$, $\text{SEC}=0.7397$)  
   - <= 28% limit: **82.41%** recovery ($P_1=18.30, P_2=18.70\,\text{bar}$, $\text{SEC}=0.7442$)  
   - <= 29% limit: **83.80%** recovery ($P_1=18.70, P_2=19.20\,\text{bar}$, $\text{SEC}=0.7498$)  
   - <= 30% limit: **85.08%** recovery ($P_1=19.08, P_2=19.73\,\text{bar}$, $\text{SEC}=0.7561$).

5. **What surrogate safety margin is recommended?**  
   A constraint of **predicted $R_{\text{elem, max}} \le 29.5\%$** (a 0.5% buffer) is recommended during surrogate screening to comfortably absorb the observed ~0.28% surrogate approximation error before final mechanistic verification.

6. **What are the corrected four representative strategies?**  
   - **A (Max Feasible Recovery)**: 19.08 / 19.73 bar -> R = 85.08%, SEC = 0.7561 kWh/m3, MaxElemRec = 29.99%  
   - **B (Min Energy)**: 15.30 / 15.30 bar -> R = 69.82%, SEC = 0.7224 kWh/m3, MaxElemRec = 20.63%  
   - **C (Min Stress)**: 10.00 / 14.00 bar -> R = 51.68%, SEC = 0.8239 kWh/m3, MaxElemRec = 13.99%  
   - **D (Balanced Knee)**: 15.05 / 15.80 bar -> R = 70.22%, SEC = 0.7269 kWh/m3, MaxElemRec = 20.10%.

7. **Is the baseline still mechanistically dominated?**  
   **Yes.** Both Strategy D and Strategy B strictly dominate the baseline in full differential-algebraic simulation across all three objectives.

8. **Is Stage 5 now closed and ready for the next research stage?**  
   **Yes.** Stage 5 and Stage 5B are fully reconciled, audited, and closed with 100% passing tests and verified mechanistic numbers.
