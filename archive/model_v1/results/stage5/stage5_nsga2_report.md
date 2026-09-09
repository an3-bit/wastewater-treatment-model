# Stage 5 Technical Report: Multi-Objective RO Operating Optimization Using NSGA-II

**Project**: AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Phase**: Stage 5 — AI-Assisted Steady-State Multi-Objective Operating Optimization  
**Author / Engineering Role**: Process Systems & Membrane Modeling Group  
**Surrogate Engine**: Artificial Neural Network (MLP) in `PHYSICS_RECONSTRUCTED` Mode  
**Optimizer**: NSGA-II (`pymoo` v0.6.2)  
**Safety & Safeguards**: `OptimizationDomainGuard`, $P_2 \ge P_1$, $R_{\text{elem, max}} \le 30\%$, Reference Quality $C_p \le 18\,\text{mg/L}$, Mandatory Mechanistic Ground-Truth Verification  

---

## Executive Summary

Stage 5 solves the multi-objective operating pressure optimization problem for the two-stage industrial reverse osmosis (RO) textile wastewater reuse system (MBR–RO configuration). Using the validated Stage 4 Feed-Forward Artificial Neural Network (ANN / MLP) in **`PHYSICS_RECONSTRUCTED` inference mode** as a high-throughput screening engine ($1,218\times$ speed-up, 27,685 evaluations/s), the non-dominated Pareto frontier was mapped across three conflicting objectives:
1. **Maximizing Overall Water Recovery** ($f_1 = -R\,\%$)
2. **Minimizing Specific Energy Consumption** ($f_2 = \text{SEC}\,\text{kWh/m}^3$)
3. **Minimizing Peak Membrane Operating Stress** ($f_3 = R_{\text{elem, max}}\,\%$, maximum single-element recovery proxy)

Across 5 independent stochastic seeds ($100,000$ surrogate evaluations), NSGA-II demonstrated near-perfect algorithmic convergence ($\text{Mean Hypervolume} = 2002.955 \pm 0.758$, $\text{CoV} = 0.038\%$), producing a global non-dominated frontier of **424 unique operating pressure strategies** bounded within the curated engineering domain ($P_1 \in [10.00, 20.00]\,\text{bar}, P_2 \in [14.00, 27.69]\,\text{bar}$).

```
========================================================================================================================
                                    STAGE 5 MULTI-OBJECTIVE OPERATING OPTIMIZATION SUMMARY
========================================================================================================================
Baseline Operating Point (13/18 bar):          Recovery = 69.36%, SEC = 0.7710 kWh/m³, MaxElemRec = 23.69% (DOMINATED)
Balanced Knee Operating Strategy (15.05/15.80): Recovery = 70.22%, SEC = 0.7269 kWh/m³, MaxElemRec = 20.10% (-5.7% SEC, -15.1% Stress)
Minimum Energy Strategy (15.30/15.30):         Recovery = 69.82%, SEC = 0.7224 kWh/m³, MaxElemRec = 20.63% (-6.3% SEC)
Minimum Stress Strategy (10.00/14.00):         Recovery = 51.68%, SEC = 0.8239 kWh/m³, MaxElemRec = 13.99% (-40.9% Stress)
Strategy A — Max Feasible Recovery (19.08/19.73): Recovery = 85.08%, SEC = 0.7561 kWh/m³, MaxElemRec = 29.99% (+22.7% Recovery)
========================================================================================================================
Mechanistic Verification Status:               16 Candidates Rerun; Mean Rec Error = 0.121%, Mean SEC Error = 0.0008 kWh/m³
Solute Balance Residual in Verification:       0.000% Exact Global Closure by Construction
========================================================================================================================
```

---

## 1. Problem Formulation & Variable Classification

### 1.1 Decision Variables vs. Fixed Feed Disturbances
In industrial RO operations, the operator directly manipulates high-pressure pump speeds and booster pump throttle valves, while raw feed characteristics fluctuate as external disturbances:

| Variable Type | Variable Name | Symbol | Units | Baseline / Bounds | Source / Authority |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Decision Variable** | Stage 1 Feed Pressure | $P_1$ | $\text{bar}$ | $[10.001, 19.998]$ | `OptimizationDomainGuard` Training Bounds |
| **Decision Variable** | Stage 2 Booster Pressure | $P_2$ | $\text{bar}$ | $[14.001, 27.691]$ | `OptimizationDomainGuard` Training Bounds |
| **Fixed Disturbance** | Feed Flow Rate | $Q_f$ | $\text{m}^3/\text{h}$ | $30.0$ | Authoritative Stage 4B Baseline |
| **Fixed Disturbance** | Feed Salinity (TDS) | $C_f$ | $\text{mg/L}$ | $2041.0$ | Industrial Reference Case |
| **Fixed Disturbance** | Operating Temperature | $T$ | $^\circ\text{C}$ | $25.0$ | Standard Reference Temperature |
| **Fixed State** | Organic Carbon (COD) | $\text{COD}$ | $\text{mg/L}$ | $51.0$ | MBR Effluent Characterization |
| **Fixed State** | Feed pH | $\text{pH}$ | — | $8.0$ | Neutral / Slightly Alkaline Standard |

### 1.2 Mathematical Formulation
The optimization problem is formulated in standard minimization form:
$$\min_{\mathbf{x} = [P_1, P_2]^T} \mathbf{F}(\mathbf{x}) = \begin{bmatrix} f_1(\mathbf{x}) \\ f_2(\mathbf{x}) \\ f_3(\mathbf{x}) \end{bmatrix} = \begin{bmatrix} - \text{overall\_recovery\_pct}(\mathbf{x}) \\ \text{SEC\_kWh\_m3}(\mathbf{x}) \\ \text{maximum\_element\_recovery\_pct}(\mathbf{x}) \end{bmatrix}$$

Subject to the following hard engineering inequality constraints ($g_j(\mathbf{x}) \le 0$):
1. **Inter-Stage Pressure Ordering**:
   $$g_1(\mathbf{x}) = P_1 - P_2 \le 0 \iff P_2 \ge P_1$$
2. **Single-Element Recovery Safeguard** ($\le 30.0\%$ project limit):
   $$g_2(\mathbf{x}) = R_{\text{elem, max}}(\mathbf{x}) - 30.0 \le 0$$
3. **Published Reference-Case Permeate Quality Constraint** ($\le 18.0\,\text{mg/L}$):
   $$g_3(\mathbf{x}) = C_p(\mathbf{x}) - 18.0 \le 0$$
4. **Domain Boundary Box**:
   $$P_{1,\min} \le P_1 \le P_{1,\max}, \quad P_{2,\min} \le P_2 \le P_{2,\max}$$
5. **Surrogate Domain Proximity Guard**:
   $$\text{DomainProximityStatus}(\mathbf{x}) \neq \text{OUT\_OF\_DOMAIN} \iff d_z(\mathbf{x}) \le 3.5$$
6. **Physical Non-Negativity & Mass Envelopes**:
   $$\text{SEC} > 0, \quad 0 < R < 100\%$$

> [!NOTE]
> Permeate quality $C_p \le 18\,\text{mg/L}$ is explicitly labeled as the **published reference-case permeate quality** from Sowgath et al. (2025), not a universal mandatory textile reuse standard.

---

## 2. NSGA-II Multi-Seed Convergence Study

To ensure that the discovered Pareto frontier is numerically stable and independent of stochastic initialization, NSGA-II was executed across **5 independent random seeds** ($42, 101, 2024, 777, 999$) with identical algorithm hyper-parameters:
- **Population Size ($N_{\text{pop}}$)**: $100$
- **Generations ($N_{\text{gen}}$)**: $200$
- **Total Evaluations per Run**: $20,100$
- **Crossover**: Simulated Binary Crossover ($\text{SBX}, p_c = 0.90, \eta_c = 15.0$)
- **Mutation**: Polynomial Mutation ($\text{PM}, p_m = 0.50, \eta_m = 20.0$)
- **Hypervolume Reference Point**: $\mathbf{r}_{\text{ref}} = [0.0\,\%, 2.0\,\text{kWh/m}^3, 35.0\,\%]$

### Multi-Seed Convergence Table
| Random Seed | Elapsed Time (s) | Total Evaluations | Final Hypervolume | Non-Dominated Count |
| :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | $13.00$ | $20,100$ | $2002.50$ | $100$ |
| **Seed 101** | $14.68$ | $20,100$ | $2002.89$ | $100$ |
| **Seed 2024** | $10.36$ | $20,100$ | $2002.43$ | $100$ |
| **Seed 777** | $4.87$ | $20,100$ | $2004.44$ | $100$ |
| **Seed 999** | $5.55$ | $20,100$ | $2002.51$ | $100$ |
| **Mean $\pm$ Std** | $\mathbf{9.69 \pm 4.31}$ | $\mathbf{20,100}$ | $\mathbf{2002.955 \pm 0.758}$ | $\mathbf{100}$ |

The hypervolume convergence trajectories are depicted below:

![Multi-Seed Hypervolume Convergence](stage5_03_hypervolume_convergence.png)

**Convergence Audit**: As demonstrated in the figure, all 5 independent runs rapidly advance through early generations ($g < 40$) and achieve complete asymptotic stagnation by generation $120$. The coefficient of variation across seeds is $\text{CoV} = 0.038\%$, confirming that $N_{\text{gen}} = 200$ is fully sufficient to capture the stable surrogate-generated non-dominated frontier without genetic drift or local entrapment.

---

## 3. Pareto Frontier Analysis & Representative Strategies

Combining all non-dominated candidates across seeds produces a global Pareto frontier of 424 unique operating points. The 2D projections and 3D surface are illustrated below:

![2D Pareto Trade-Offs](stage5_01_pareto_tradeoffs_2d.png)

![3D Pareto Surface](stage5_02_pareto_3d_surface.png)

### 3.1 Representative Operating Strategies
To translate the continuous Pareto front into actionable engineering decisions, four distinct operational strategies were extracted:
- **Strategy A (Maximum Mechanistically Verified Feasible Recovery)**: Refined upper physical operating boundary ($P_1=19.08\,\text{bar}, P_2=19.73\,\text{bar}$) strictly satisfying $R_{\text{elem, max}} \le 30.000\%$.
- **Strategy B (Minimum Energy)**: Lowest specific energy consumption ($\text{SEC}$).
- **Strategy C (Minimum Membrane Stress)**: Lowest single-element hydraulic/concentration loading.
- **Strategy D (Balanced Knee Solution)**: Mathematically identified by minimizing the normalized Euclidean distance to the ideal objective point:
  $$d_i = \sqrt{\left(\frac{f_{1,i} - f_{1,\min}}{f_{1,\max} - f_{1,\min}}\right)^2 + \left(\frac{f_{2,i} - f_{2,\min}}{f_{2,\max} - f_{2,\min}}\right)^2 + \left(\frac{f_{3,i} - f_{3,\min}}{f_{3,\max} - f_{3,\min}}\right)^2}$$

### Representative Solutions Ledger (Surrogate Reconstructed vs Mechanistic Ground Truth)
| Metric / Parameter | Authoritative Baseline | Strategy A (Max Feasible Recovery) | Strategy B (Min Energy) | Strategy C (Min Stress) | Strategy D (Balanced Knee) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stage 1 Pressure $P_1$ (bar)** | $13.00$ | $19.08$ | $15.30$ | $10.00$ | $15.05$ |
| **Stage 2 Pressure $P_2$ (bar)** | $18.00$ | $19.73$ | $15.30$ | $14.00$ | $15.80$ |
| **Inter-Stage Boost $\Delta P_{\text{boost}}$ (bar)** | $+5.00$ | $+0.65$ | $+0.00$ | $+4.00$ | $+0.75$ |
| **Surrogate Recovery (%)** | $69.36$ | $84.85$ | $69.96$ | $52.02$ | $70.39$ |
| **Mechanistic Recovery (%)** | $\mathbf{69.36}$ | $\mathbf{85.08}$ | $\mathbf{69.82}$ | $\mathbf{51.68}$ | $\mathbf{70.22}$ |
| **Surrogate SEC (kWh/m³)** | $0.7710$ | $0.7530$ | $0.7220$ | $0.8231$ | $0.7273$ |
| **Mechanistic SEC (kWh/m³)** | $\mathbf{0.7710}$ | $\mathbf{0.7561}$ | $\mathbf{0.7224}$ | $\mathbf{0.8239}$ | $\mathbf{0.7269}$ |
| **Surrogate Max Elem Rec (%)** | $23.69$ | $30.13$ | $20.54$ | $14.06$ | $20.17$ |
| **Mechanistic Max Elem Rec (%)**| $\mathbf{23.69}$ | $\mathbf{29.99}$ | $\mathbf{20.63}$ | $\mathbf{13.99}$ | $\mathbf{20.10}$ |
| **Mechanistic Permeate TDS (mg/L)**| $7.23$ | $9.24$ | $7.64$ | $7.53$ | $7.59$ |
| **Mechanistic Concentrate TDS (mg/L)**| $6644.8$ | $13623.5$ | $6746.0$ | $4215.7$ | $6835.0$ |
| **Mechanistic Average Flux (LMH)**| $37.49$ | $45.99$ | $37.74$ | $27.93$ | $37.96$ |
| **Mechanistic Max Polarization $\beta$**| $1.302$ | $1.368$ | $1.273$ | $1.223$ | $1.267$ |
| **Permeate Flow $Q_p$ (m³/h)** | $20.81$ | $25.52$ | $20.95$ | $15.50$ | $21.07$ |
| **Concentrate Flow $Q_r$ (m³/h)** | $9.19$ | $4.48$ | $9.05$ | $14.50$ | $8.93$ |
| **Hourly Power Consumption (kW)**| $16.05$ | $19.30$ | $15.13$ | $12.77$ | $15.31$ |
| **Domain Proximity Status** | `IN_DOMAIN` | `IN_DOMAIN` | `IN_DOMAIN` | `NEAR_BOUNDARY` | `IN_DOMAIN` |
| **Mechanistic Feasibility Audit** | **PASS** | **PASS ($29.99\% \le 30.0\%$)** | **PASS** | **PASS** | **PASS** |

> [!NOTE]
> The initial unrefined surrogate candidate ($P_1 = 19.19\,\text{bar}, P_2 = 19.63\,\text{bar}$) had predicted $R_{\text{elem, max}} = 29.9998\%$, but evaluated to $30.28\%$ in differential-algebraic simulation, failing the $30.0\%$ safeguard. It is formally archived as `SURROGATE_MAX_REC_CANDIDATE_INFEASIBLE` as benchmark evidence of surrogate boundary exploitation. Strategy A above reflects the refined feasible boundary ($19.08 / 19.73\,\text{bar}$).

---

## 4. Authoritative Baseline Dominance Analysis

A formal dominance check was conducted comparing the authoritative Stage 4B baseline ($P_1=13.0\,\text{bar}, P_2=18.0\,\text{bar}$) against all candidates in the global Pareto frontier.

```
========================================================================================================================
                                     BASELINE DOMINANCE AUDIT RESULTS
========================================================================================================================
Baseline Coordinates:                  P1 = 13.00 bar, P2 = 18.00 bar
Baseline Physical State:               Recovery = 69.3597%, SEC = 0.771027 kWh/m³, MaxElemRec = 23.6858%
Dominance Classification:              DOMINATED
Total Dominating Candidates on Front:  71 Solutions
Total Candidates Dominated by Baseline: 0 Solutions
Closest Non-Dominated Distance:        0.0988 (Normalized relative distance)
========================================================================================================================
```

### Physical Root Cause for Baseline Sub-Optimality
Why is the $13/18\,\text{bar}$ baseline sub-optimal?
1. **Severe Inter-Stage Pressure Asymmetry**: The baseline imposes a large $5.0\,\text{bar}$ pressure jump between Stage 1 ($13\,\text{bar}$) and Stage 2 ($18\,\text{bar}$).
2. **Under-Utilization of Stage 1**: At $13\,\text{bar}$, the net driving pressure in Stage 1 is low, resulting in modest recovery and lower flux in the first stage.
3. **Overloading Stage 2 Elements**: Because Stage 1 achieves modest recovery, the remaining feed enters Stage 2 at elevated salinity, where the $18\,\text{bar}$ booster forces heavy permeation in the lead elements of Stage 2. This inflates the peak single-element recovery to $23.69\%$ and drives the maximum polarization modulus to $\beta = 1.302$.
4. **Flux-Equalized Optimization**: The optimizer discovers that raising $P_1$ to $\sim 15.05–15.30\,\text{bar}$ while operating $P_2$ at $\sim 15.30–15.80\,\text{bar}$ ($\Delta P_{\text{boost}} \le 0.75\,\text{bar}$) distributes the trans-membrane flux uniformly across all 15 membrane elements (3 vessels Stage 1 + 2 vessels Stage 2 x 3 elements = 15 total elements). This flux-leveling reduces peak local salinity build-up, cuts specific energy consumption by **$5.7\%$** ($0.7269$ vs $0.7710\,\text{kWh/m}^3$), and drops membrane stress by **$15.1\%$** ($20.10\%$ vs $23.69\%$) while actually increasing overall water recovery.

---

## 5. Optional Polarization Safeguard ($\beta \le 1.40$) Impact

To evaluate whether an optional project engineering polarization modulus safeguard ($\beta_{\max} \le 1.40$) restricts the Pareto front, Case A (unconstrained $\beta$) was compared directly against Case B (constrained $\beta \le 1.40$):

![Case A vs Case B Polarization](stage5_04_case_a_vs_case_b_polarization.png)

### Key Findings
1. **Unconstrained Maximum Polarization**: Across the entire unconstrained Case A Pareto front, the maximum polarization modulus ranges between $\beta = 1.223$ (at $51.7\%$ recovery) and $\beta = 1.370$ (at $85.1\%$ recovery).
2. **Safeguard Inactivity**: Because the maximum polarization modulus never exceeds $\beta = 1.370$ even at maximum achievable recovery, the condition $\beta \le 1.40$ is **non-binding across the entire admissible engineering domain**.
3. **Front Identity**: The Pareto fronts for Case A and Case B are identical. The $30\%$ single-element recovery constraint and the training bounds act as the primary active constraints governing membrane safety.

---

## 6. Mechanistic Ground-Truth Verification & Surrogate Exploitation Audit

Following **Optimizer Safety Policy Rule 5 & 6**, surrogate Pareto points were not accepted as final authority. Sixteen candidates—including the 4 representative strategies and 12 distributed points across the recovery range—were re-evaluated through the full mechanistic differential-algebraic RO simulator.

![Mechanistic Verification Parity](stage5_05_mechanistic_verification_parity.png)

![Surrogate Error vs Pareto Position](stage5_08_surrogate_error_vs_pareto_position.png)

### Detailed Ground-Truth Error Matrix (16 Verified Pareto Candidates)
| Candidate Rank / Name | $P_1$ (bar) | $P_2$ (bar) | Mech $R$ (%) | Reconstructed $R$ (%) | Abs Error $R$ (%) | Mech SEC (kWh/m³) | Reconstructed SEC | Abs Error SEC | Mech ElemRec (%) | Reconstructed ElemRec | Abs Error ElemRec | Full Feasibility |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Strategy A (Max Rec)**| $19.19$ | $19.63$ | $85.10$ | $84.92$ | $0.18$ | $0.7567$ | $0.7530$ | $0.0037$ | $30.28$ | $30.00$ | $0.28$ | **FAIL (Stress)** |
| **Strategy B (Min Energy)**| $15.30$ | $15.30$ | $69.82$ | $69.96$ | $0.13$ | $0.7224$ | $0.7220$ | $0.0004$ | $20.63$ | $20.54$ | $0.09$ | **PASS** |
| **Strategy C (Min Stress)**| $10.00$ | $14.00$ | $51.68$ | $52.02$ | $0.34$ | $0.8239$ | $0.8231$ | $0.0007$ | $13.99$ | $14.06$ | $0.07$ | **PASS** |
| **Strategy D (Knee)** | $15.05$ | $15.80$ | $70.22$ | $70.39$ | $0.17$ | $0.7269$ | $0.7273$ | $0.0005$ | $20.10$ | $20.17$ | $0.06$ | **PASS** |
| Pareto Point 05 | $10.40$ | $14.00$ | $52.92$ | $53.16$ | $0.24$ | $0.8075$ | $0.8075$ | $0.0000$ | $14.18$ | $14.22$ | $0.04$ | **PASS** |
| Pareto Point 06 | $10.93$ | $14.00$ | $54.59$ | $54.73$ | $0.14$ | $0.7879$ | $0.7871$ | $0.0008$ | $14.43$ | $14.44$ | $0.01$ | **PASS** |
| Pareto Point 07 | $11.50$ | $14.00$ | $56.33$ | $56.41$ | $0.08$ | $0.7703$ | $0.7698$ | $0.0004$ | $14.70$ | $14.65$ | $0.04$ | **PASS** |
| Pareto Point 08 | $12.17$ | $14.00$ | $58.34$ | $58.39$ | $0.05$ | $0.7531$ | $0.7518$ | $0.0012$ | $15.01$ | $14.96$ | $0.05$ | **PASS** |
| Pareto Point 09 | $13.23$ | $14.07$ | $61.62$ | $61.52$ | $0.10$ | $0.7334$ | $0.7344$ | $0.0009$ | $16.21$ | $16.14$ | $0.07$ | **PASS** |
| Pareto Point 10 | $13.93$ | $14.92$ | $65.41$ | $65.42$ | $0.01$ | $0.7309$ | $0.7318$ | $0.0009$ | $17.65$ | $17.83$ | $0.18$ | **PASS** |
| Pareto Point 11 | $14.63$ | $15.27$ | $68.03$ | $68.21$ | $0.18$ | $0.7264$ | $0.7270$ | $0.0006$ | $19.14$ | $19.21$ | $0.06$ | **PASS** |
| Pareto Point 12 | $15.36$ | $15.80$ | $71.03$ | $71.16$ | $0.13$ | $0.7252$ | $0.7252$ | $0.0000$ | $20.78$ | $20.80$ | $0.01$ | **PASS** |
| Pareto Point 13 | $16.06$ | $16.43$ | $73.95$ | $74.01$ | $0.06$ | $0.7266$ | $0.7262$ | $0.0004$ | $22.39$ | $22.43$ | $0.05$ | **PASS** |
| Pareto Point 14 | $16.85$ | $17.35$ | $77.40$ | $77.42$ | $0.02$ | $0.7313$ | $0.7317$ | $0.0004$ | $24.50$ | $24.45$ | $0.06$ | **PASS** |
| Pareto Point 15 | $17.65$ | $18.12$ | $80.34$ | $80.43$ | $0.09$ | $0.7376$ | $0.7381$ | $0.0006$ | $26.55$ | $26.60$ | $0.05$ | **PASS** |
| Pareto Point 16 | $18.47$ | $18.72$ | $82.72$ | $82.75$ | $0.02$ | $0.7456$ | $0.7450$ | $0.0005$ | $28.36$ | $28.29$ | $0.07$ | **PASS** |
| **Mean Absolute Error** | — | — | — | — | $\mathbf{0.121\%}$ | — | — | $\mathbf{0.0008}$ | — | — | $\mathbf{0.075\%}$ | **15/16 Pass** |

### 6.1 Surrogate Exploitation Audit
An audit was conducted to test whether NSGA-II exploited surrogate approximation artifacts:
1. **Overall Accuracy**: Across 15 of the 16 points, the surrogate predictions agree with the mechanistic simulator with high fidelity (Mean Recovery Error = $0.121\%$, Mean SEC Error = $0.0008\,\text{kWh/m}^3$).
2. **Boundary Stress Exploitation**: At the upper extreme of the Pareto frontier, NSGA-II selected $P_1=19.19\,\text{bar}$ and $P_2=19.63\,\text{bar}$ where the surrogate predicted $R_{\text{elem, max}} = 29.9998\%$ (right against the $30.0\%$ safeguard). When re-simulated in the differential-algebraic model, the true physical single-element recovery was **$30.28\%$**, slightly exceeding the safeguard. This point is retained as `SURROGATE_MAX_REC_CANDIDATE_INFEASIBLE`.
3. **Engineering Action & Refinement**: Through Stage 5B local mechanistic refinement, the true maximum allowable recovery under mechanistic verification was accurately identified as **$85.08\%$** ($P_1=19.08\,\text{bar}, P_2=19.73\,\text{bar}$), where true $R_{\text{elem, max}} = 29.9932\% \le 30.000\%$ (within $0.0068\%$ of the physical threshold).

---

## 7. 2D Operational Decision Maps for Plant Operators

To convert the optimization findings into an operator-readable decision dashboard, a $120 \times 120$ grid across $(P_1, P_2)$ space was mapped:

![2D Operational Decision Map](stage5_06_operational_decision_map.png)

### Key Operational Takeaways for Plant Engineers
1. **Forbidden Lower Triangle ($P_2 < P_1$)**: The region where $P_2 < P_1$ requires negative booster pressure, which is physically impossible and prohibited by the booster pump configuration.
2. **High-Stress Infeasible Zone ($P_2 > 20\,\text{bar}, P_1 < 14\,\text{bar}$)**: Operating with a low primary feed pressure and high inter-stage boost concentrates hydraulic flux excessively in the second stage, violating the $30\%$ single-element recovery limit.
3. **Optimal Operating Corridor ($P_2 \approx P_1 + 0.0\text{ to }0.75\,\text{bar}$)**: The entire Pareto frontier aligns along a narrow diagonal corridor where $P_2 \approx P_1$. By maintaining approximately equal pressures in both stages, flux distribution is balanced across all pressure vessels.

---

## 8. Disturbance Sensitivity Scenarios (Feed TDS & Flow Fluctuations)

To determine how optimal pressure setpoints should shift during upstream plant disturbances, six scenarios were evaluated:

![Disturbance Sensitivity Pareto Shifts](stage5_07_disturbance_sensitivity_pareto.png)

### Disturbance Scenario Comparison Table
| Scenario | $Q_f$ (m³/h) | $C_f$ (mg/L) | Knee $P_1$ (bar) | Knee $P_2$ (bar) | Knee $R$ (%) | Knee SEC (kWh/m³) | Knee Stress (%) | Max $R$ (%) | Min SEC (kWh/m³) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Low Salinity** | $30.0$ | $1500.0$ | $14.43$ | $14.56$ | $70.92$ | $0.6729$ | $21.09$ | $82.67$ | $0.6719$ |
| **Base Case** | $30.0$ | $2041.0$ | $15.05$ | $15.80$ | $70.39$ | $0.7273$ | $20.17$ | $84.92$ | $0.7221$ |
| **High Salinity**| $30.0$ | $3000.0$ | $15.90$ | $17.94$ | $68.56$ | $0.8273$ | $18.86$ | $84.51$ | $0.8107$ |
| **Low Flow** | $20.0$ | $2041.0$ | $12.69$ | $14.26$ | $79.33$ | $0.5552$ | $25.09$ | $85.64$ | $0.5538$ |
| **Base Flow** | $30.0$ | $2041.0$ | $15.05$ | $15.80$ | $70.39$ | $0.7273$ | $20.17$ | $84.92$ | $0.7221$ |
| **High Flow** | $40.0$ | $2041.0$ | $17.62$ | $18.34$ | $66.27$ | $0.9102$ | $18.20$ | $79.10$ | $0.9033$ |

### Disturbance Insights
1. **Salinity Variations ($1500 \to 3000\,\text{mg/L}$)**: Increasing salinity raises feed osmotic pressure ($\pi_f$), requiring higher operating pressures ($P_1: 14.43 \to 15.90\,\text{bar}, P_2: 14.56 \to 17.94\,\text{bar}$) and increasing SEC from $0.6729$ to $0.8273\,\text{kWh/m}^3$ (+23.0%).
2. **Flow Variations ($20 \to 40\,\text{m}^3/\text{h}$)**: Lower feed flow increases residence time and achievable recovery ($79.33\%$ at $20\,\text{m}^3/\text{h}$ vs $66.27\%$ at $40\,\text{m}^3/\text{h}$), while specific energy drops significantly to $0.5552\,\text{kWh/m}^3$.

---

## 9. Answers to Specific Research Questions

### Question 1: What is the recovery-energy-stress Pareto trade-off?
**Answer**: The trade-off exhibits a clear three-way structure:
- **Recovery vs. Stress**: Overall water recovery and maximum single-element recovery are strongly positively correlated ($R=51.7\% \implies R_{\text{elem, max}}=14.0\%$; $R=85.1\% \implies R_{\text{elem, max}}=30.3\%$). Increasing water recovery inevitably elevates concentration polarization and local hydraulic loading in lead elements.
- **Recovery vs. Energy**: Minimum specific energy consumption occurs at an intermediate recovery of $\sim 69.8–70.4\%$ ($\text{SEC} \approx 0.722–0.727\,\text{kWh/m}^3$). Below $70\%$, lower recovery reduces permeate production volume relative to fixed hydraulic feed pumping, which increases per-$\text{m}^3$ energy. Above $70\%$, osmotic back-pressure escalates, requiring higher operating pressures that inflate pump power.

### Question 2: What are the four representative operating strategies?
**Answer**:
1. **Strategy A (Maximum Mechanistically Verified Feasible Recovery)**: $P_1 = 19.08\,\text{bar}, P_2 = 19.73\,\text{bar} \implies R = 85.08\%, \text{SEC} = 0.7561\,\text{kWh/m}^3, R_{\text{elem, max}} = 29.9932\% \le 30.000\%$.
2. **Strategy B (Minimum Energy)**: $P_1 = 15.30\,\text{bar}, P_2 = 15.30\,\text{bar} \implies R = 69.82\%, \text{SEC} = 0.7224\,\text{kWh/m}^3, R_{\text{elem, max}} = 20.63\%$.
3. **Strategy C (Minimum Stress)**: $P_1 = 10.00\,\text{bar}, P_2 = 14.00\,\text{bar} \implies R = 51.68\%, \text{SEC} = 0.8239\,\text{kWh/m}^3, R_{\text{elem, max}} = 13.99\%$.
4. **Strategy D (Balanced Knee Solution)**: $P_1 = 15.05\,\text{bar}, P_2 = 15.80\,\text{bar} \implies R = 70.22\%, \text{SEC} = 0.7269\,\text{kWh/m}^3, R_{\text{elem, max}} = 20.10\%$.

### Question 3: Is the current 13/18 bar baseline Pareto-optimal?
**Answer**: **No. The 13/18 bar baseline is strictly DOMINATED.** Seventy-one non-dominated candidate solutions on the Pareto front achieve higher recovery, lower specific energy, and lower peak element stress simultaneously.

### Question 4: Can recovery be increased without increasing SEC or membrane stress?
**Answer**: **Yes.** Moving from the baseline ($13/18\,\text{bar}, R=69.36\%, \text{SEC}=0.7710\,\text{kWh/m}^3, R_{\text{elem, max}}=23.69\%$) to the Balanced Knee Point ($15.05/15.80\,\text{bar}$):
- Recovery increases by **$+0.86\%$** ($70.22\%$)
- SEC decreases by **$-5.7\%$** ($0.7269\,\text{kWh/m}^3$)
- Max element stress decreases by **$-15.1\%$** ($20.10\%$).

### Question 5: What is the balanced/knee operating point?
**Answer**: The mathematically selected knee point is:
$$\mathbf{P}_1 = 15.05\,\text{bar}, \quad \mathbf{P}_2 = 15.80\,\text{bar}$$
Yielding $R = 70.22\%$, $\text{SEC} = 0.7269\,\text{kWh/m}^3$, $R_{\text{elem, max}} = 20.10\%$, $C_p = 7.59\,\text{mg/L}$, and $\beta = 1.267$.

### Question 6: Does the 18 mg/L permeate quality constraint bind?
**Answer**: **No.** Across the entire Pareto frontier, permeate TDS ranges from $7.43\,\text{mg/L}$ to $9.28\,\text{mg/L}$, well below the $18.0\,\text{mg/L}$ reference constraint. The constraint is non-binding.

### Question 7: Does beta <= 1.40 materially change the Pareto front?
**Answer**: **No.** Maximum polarization modulus across the unconstrained front reaches a maximum of $\beta = 1.370$. The $\beta \le 1.40$ constraint is non-binding and does not alter the Pareto front.

### Question 8: How accurately does the mechanistic model verify the ANN Pareto candidates?
**Answer**: The agreement is high:
- **Recovery Error**: Mean absolute error of **$0.121\%$** (Max $0.341\%$).
- **SEC Error**: Mean absolute error of **$0.0008\,\text{kWh/m}^3$** (Max $0.0037\,\text{kWh/m}^3$).
- **Max Element Recovery Error**: Mean absolute error of **$0.075\%$** (Max $0.281\%$).
- **Solute Balance Residual**: **$0.000\%$** exact closure across all verified candidates.

### Question 9: Is there evidence that NSGA-II exploits surrogate error?
**Answer**: **Yes, slightly near active boundary limits.** At Strategy A, the optimizer pushed the surrogate right to the $30.0\%$ limit ($29.9998\%$), but mechanistic re-simulation revealed a true value of $30.28\%$. This confirms that near boundary constraints, slight surrogate under-prediction can be exploited, validating the mandatory post-optimization mechanistic verification policy.

### Question 10: How do optimal pressures change with feed TDS?
**Answer**: As feed TDS rises from $1500$ to $3000\,\text{mg/L}$, optimal knee pressures increase from $P_1/P_2 = 14.43/14.56\,\text{bar}$ to $15.90/17.94\,\text{bar}$ to overcome increased osmotic pressure, while SEC increases from $0.6729$ to $0.8273\,\text{kWh/m}^3$.

### Question 11: How do optimal pressures change with feed flow?
**Answer**: As feed flow increases from $20$ to $40\,\text{m}^3/\text{h}$, required knee pressures increase from $12.69/14.26\,\text{bar}$ to $17.62/18.34\,\text{bar}$ to maintain permeation across higher volumetric crossflow, increasing SEC from $0.5552$ to $0.9102\,\text{kWh/m}^3$.

### Question 12: What operating region should an industrial operator avoid?
**Answer**:
1. **$P_2 < P_1$**: Physically prohibited booster condition.
2. **High Boost ($P_2 > 20\,\text{bar}, P_1 < 14\,\text{bar}$)**: Induces severe Stage 2 flux maldistribution and exceeds the $30\%$ single-element recovery limit.
3. **Low Pressure ($P_1 < 12\,\text{bar}, P_2 < 14\,\text{bar}$)**: Recovery collapses below $60\%$ while per-$\text{m}^3$ SEC escalates due to under-utilized feed pumping.

### Question 13: Is the optimization sufficiently reliable for later economic optimization and dynamic/fouling development?
**Answer**: **Yes.** The methodology combines ultra-fast surrogate screening ($1,218\times$ acceleration) with strict physics-reconstructed mass conservation, rigorous domain guards, and mandatory ground-truth mechanistic verification. This provides a robust, physically verified foundation for Stage 6 techno-economic analysis and subsequent dynamic digital-twin development.

---

## 10. Archival Artifacts & Data Index

All data and publication-grade figure artifacts have been generated, validated, and archived:

1. **Surrogate Pareto Front**: `results/stage5/pareto_front_surrogate.csv` ($N = 424$)
2. **Mechanistically Verified Solutions**: `results/stage5/pareto_verified_candidates.csv` ($N = 16$)
3. **Multi-Seed Convergence Ledger**: `results/stage5/convergence_summary.csv` ($N = 5$)
4. **Disturbance Scenario Ledger**: `results/stage5/disturbance_scenario_summary.csv` ($N = 6$)
5. **Figure 1 (2D Trade-Offs)**: `results/stage5/figures/stage5_01_pareto_tradeoffs_2d.png`
6. **Figure 2 (3D Pareto Surface)**: `results/stage5/figures/stage5_02_pareto_3d_surface.png`
7. **Figure 3 (HV Convergence)**: `results/stage5/figures/stage5_03_hypervolume_convergence.png`
8. **Figure 4 (Polarization Safeguard)**: `results/stage5/figures/stage5_04_case_a_vs_case_b_polarization.png`
9. **Figure 5 (Mechanistic Parity)**: `results/stage5/figures/stage5_05_mechanistic_verification_parity.png`
10. **Figure 6 (Decision Operating Map)**: `results/stage5/figures/stage5_06_operational_decision_map.png`
11. **Figure 7 (Disturbance Shifts)**: `results/stage5/figures/stage5_07_disturbance_sensitivity_pareto.png`
12. **Figure 8 (Surrogate Error Diagnostic)**: `results/stage5/figures/stage5_08_surrogate_error_vs_pareto_position.png`
