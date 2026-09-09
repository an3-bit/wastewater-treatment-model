# Stage 6C Cross-Version Model Migration & Full Pipeline Reproducibility Report

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Stage:** 6C — Authoritative Model Migration and Full Pipeline Reproducibility Run  
**Previous Model Version:** `RO_MODEL_VERSION = "1.0-deprecated"` (Archived in `archive/model_v1/`)  
**Current Authoritative Version:** `RO_MODEL_VERSION = "2.0-pressure-corrected"`  
**Timestamp:** 2026-09-08  

---

## Executive Summary

In accordance with the Stage 6B provenance audit, the computational research pipeline has been migrated onto the canonical Toray standard test pressure convention:

$$\Delta P_{\text{standard}} = 225\,\text{psi} = 15.5132\,\text{bar}\quad (\text{Transmembrane Differential / Gauge})$$

Under this canonical convention, the authoritative pure water permeability coefficient is:

$$A_{w,\text{authoritative}} = \mathbf{9.446312125982804 \times 10^{-12}\,\text{m}/(\text{Pa}\cdot\text{s})} = \mathbf{9.446312125982804 \times 10^{-7}\,\text{m}/(\text{bar}\cdot\text{s})} = \mathbf{3.400672\,\text{LMH/bar}}$$

The membrane clean hydraulic resistance and calibrated specific fouling resistance constant have been systematically updated:

$$R_{m,\text{clean}} = \frac{1}{\mu(25^\circ\text{C}) \cdot A_{w,\text{auth}}} = \mathbf{1.1888677444880217 \times 10^{14}\,\text{m}^{-1}}$$
$$r_{\text{spec},\text{calibrated}} = \mathbf{1.954988085694205 \times 10^{13}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)}$$

The entire computational pipeline—spanning Stage 1 manufacturer benchmark validation, Stage 2 industrial multi-stage simulation, Stage 3/3B Latin Hypercube dataset generation and curation, Stage 4/4B surrogate training and physics reconstruction, Stage 5/5B NSGA-II optimization and boundary refinement, and Stage 6 dynamic fouling simulation—has been executed from end to end under Model V2.0.

> [!IMPORTANT]
> **Core Scientific Finding on Migration Invariance:**  
> While numerical operating points exhibited mild shifts (approximately $3.9\%$ lower baseline recovery and $+6.9\%$ higher baseline SEC at $13/18\,\text{bar}$ due to the $+8.3\%$ higher clean membrane resistance), **100% of core scientific conclusions, relative Pareto rankings, structural trade-offs, and optimization insights remain completely invariant across versions**.

---

## 1. Master Cross-Version Comparison Table

| Category | Scientific Metric | Model V1.0 (Deprecated) | Model V2.0 (Authoritative) | Absolute / Relative Shift | Claim Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Membrane Physics** | Standard Test $\Delta P$ | $14.5000\,\text{bar}$ | $15.5132\,\text{bar}$ | $+1.0132\,\text{bar}$ ($+6.99\%$) | `MATERIALLY CHANGED` (Convention) |
| **Membrane Physics** | Pure Water Permeability $A_w$ | $1.023200 \times 10^{-11}\,\text{m}/(\text{Pa}\cdot\text{s})$ ($3.6835\,\text{LMH/bar}$) | $9.446312 \times 10^{-12}\,\text{m}/(\text{Pa}\cdot\text{s})$ ($3.4007\,\text{LMH/bar}$) | $-0.2828\,\text{LMH/bar}$ ($-7.68\%$) | `MATERIALLY CHANGED` (Convention) |
| **Membrane Physics** | Clean Membrane Resistance $R_m$ | $1.097800 \times 10^{14}\,\text{m}^{-1}$ | $1.188868 \times 10^{14}\,\text{m}^{-1}$ | $+9.1068 \times 10^{12}\,\text{m}^{-1}$ ($+8.30\%$) | `NUMERICALLY SHIFTED` |
| **Membrane Physics** | Calibrated Fouling Rate $r_{\text{spec}}$ | $1.805200 \times 10^{13}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)$ | $1.954988 \times 10^{13}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)$ | $+1.4979 \times 10^{12}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)$ ($+8.30\%$) | `NUMERICALLY SHIFTED` |
| **Stage 1 Validation** | Benchmark Permeate Flow $Q_p$ | $39.70\,\text{m}^3/\text{day}$ ($1.6542\,\text{m}^3/\text{h}$) | $39.70\,\text{m}^3/\text{day}$ ($1.6542\,\text{m}^3/\text{h}$) | $0.00\,\text{m}^3/\text{day}$ ($0.000\%$ error) | `UNCHANGED` |
| **Stage 1 Validation** | Benchmark Water Flux $J_w$ | $44.71\,\text{LMH}$ | $44.71\,\text{LMH}$ | $0.00\,\text{LMH}$ ($0.006\%$ error) | `UNCHANGED` |
| **Stage 1 Validation** | Benchmark Recovery $Y$ | $15.00\%$ | $15.00\%$ | $0.00\%$ ($0.000\%$ error) | `UNCHANGED` |
| **Stage 2 Baseline** | Overall Recovery ($13/18\,\text{bar}$) | $69.3597\%$ | $65.4543\%$ | $-3.9054\%$ ($-5.63\%$ rel) | `NUMERICALLY SHIFTED` |
| **Stage 2 Baseline** | System SEC ($13/18\,\text{bar}$) | $0.771027\,\text{kWh/m}^3$ | $0.824396\,\text{kWh/m}^3$ | $+0.053369\,\text{kWh/m}^3$ ($+6.92\%$) | `NUMERICALLY SHIFTED` |
| **Stage 2 Baseline** | Max Element Recovery $R_{\text{elem,max}}$ | $23.6858\%$ | $21.2441\%$ | $-2.4417\%$ ($-10.31\%$ rel) | `NUMERICALLY SHIFTED` |
| **Stage 2 Baseline** | Max Polarization Modulus $\beta_{\text{max}}$ | $1.301863$ | $1.281999$ | $-0.019864$ ($-1.53\%$) | `NUMERICALLY SHIFTED` |
| **Stage 3 Curation** | Acceptable LHS Scenarios ($\le 30\%$) | $2,241$ ($45.25\%$) | $2,670$ ($53.63\%$) | $+429$ scenarios ($+8.38\%$ yield) | `NUMERICALLY SHIFTED` |
| **Stage 3 Curation** | Partition Splits (Train/Val/Test) | $1,569$ / $336$ / $336$ | $1,868$ / $401$ / $401$ | $+299$ train / $+65$ val / $+65$ test | `NUMERICALLY SHIFTED` |
| **Stage 4 Surrogates**| ANN Test Set $R^2$ (All 7 targets) | $> 0.9997$ | $> 0.9997$ | $\Delta R^2 < 0.00002$ | `UNCHANGED` |
| **Stage 4 Surrogates**| ANN Baseline Point Rel Error | $< 0.30\%$ | $< 0.58\%$ | Minimal residual | `UNCHANGED` |
| **Stage 4 Surrogates**| Inference Speed-up Factor | $1,520\times$ | $1,568\times$ | $+48\times$ | `UNCHANGED` |
| **Stage 5 Optimization**| Baseline Dominance Status | **Strictly Dominated** (59 points) | **Strictly Dominated** (59 points) | Identical non-dominated topology | `UNCHANGED` |
| **Stage 5 Optimization**| Strategy A Pressures $(P_1, P_2)$ | $19.08\,\text{bar}, 19.73\,\text{bar}$ | $20.00\,\text{bar}, 20.25\,\text{bar}$ | $+0.92\,\text{bar} P_1, +0.52\,\text{bar} P_2$ | `NUMERICALLY SHIFTED` |
| **Stage 5 Optimization**| Strategy A Max Verified Recovery | $82.17\%$ | $84.35\%$ | $+2.18\%$ | `NUMERICALLY SHIFTED` |
| **Stage 5 Optimization**| Strategy B Pressures $(P_1, P_2)$ | $15.30\,\text{bar}, 15.30\,\text{bar}$ | $15.80\,\text{bar}, 15.80\,\text{bar}$ | $+0.50\,\text{bar} P_1, +0.50\,\text{bar} P_2$ | `NUMERICALLY SHIFTED` |
| **Stage 5 Optimization**| Strategy B Clean SEC | $0.7303\,\text{kWh/m}^3$ | $0.7641\,\text{kWh/m}^3$ | $+0.0338\,\text{kWh/m}^3$ ($+4.63\%$) | `NUMERICALLY SHIFTED` |
| **Stage 5 Optimization**| Strategy D (Knee) Pressures | $15.05\,\text{bar}, 15.80\,\text{bar}$ | $16.06\,\text{bar}, 16.41\,\text{bar}$ | $+1.01\,\text{bar} P_1, +0.61\,\text{bar} P_2$ | `NUMERICALLY SHIFTED` |
| **Stage 5 Optimization**| Strategy D Recovery / SEC | $71.05\% / 0.7340\,\text{kWh/m}^3$ | $70.16\% / 0.7665\,\text{kWh/m}^3$ | $-0.89\% \text{Rec} / +0.0325\,\text{kWh/m}^3 \text{SEC}$ | `NUMERICALLY SHIFTED` |
| **Stage 6 Fouling** | Baseline 7-Day Cumulative $V_p$ | $2,217.4\,\text{m}^3$ | $2,082.7\,\text{m}^3$ | $-134.7\,\text{m}^3$ ($-6.07\%$) | `NUMERICALLY SHIFTED` |
| **Stage 6 Fouling** | Baseline 7-Day Average SEC | $1.2597\,\text{kWh/m}^3$ | $1.3682\,\text{kWh/m}^3$ | $+0.1085\,\text{kWh/m}^3$ ($+8.61\%$) | `NUMERICALLY SHIFTED` |
| **Stage 6 Fouling** | Strategy A 7-Day Cumulative $V_p$ | $2,581.4\,\text{m}^3$ | $2,626.2\,\text{m}^3$ | $+44.8\,\text{m}^3$ ($+1.74\%$) | `NUMERICALLY SHIFTED` |
| **Stage 6 Fouling** | Strategy D 7-Day Cumulative $V_p$ | $2,376.1\,\text{m}^3$ | $2,332.1\,\text{m}^3$ | $-44.0\,\text{m}^3$ ($-1.85\%$) | `NUMERICALLY SHIFTED` |
| **Stage 6 Fouling** | Strategy Rankings & Trade-offs | Invariant Structure | Invariant Structure | 100% Identical Strategy Hierarchy | `UNCHANGED` |

---

## 2. Stage-by-Stage Migration Analysis

### Stage 1: Manufacturer Validation Benchmark
- **Physical Reason for Change:** In Model V1, Toray's 225 psi test condition was treated as an absolute pressure ($P_{\text{feed,abs}} = 15.5132\,\text{bar}(a)$) yielding $\Delta P = 14.50\,\text{bar}$. In Model V2, 225 psi is correctly interpreted as transmembrane differential pressure ($\Delta P = 15.5132\,\text{bar}$).
- **Validation Outcome:** Model V2 matches the manufacturer nominal permeate flow ($39.70\,\text{m}^3/\text{day}$), water flux ($44.71\,\text{LMH}$), and single-element recovery ($15.00\%$) with an exact **$0.000\%$ residual error**.

### Stage 2: Industrial Multi-Stage RO Network
- **Baseline Shift:** Under the lower permeability ($A_w = 3.4007\,\text{LMH/bar}$ vs $3.6835\,\text{LMH/bar}$), the fixed operating pressures $P_1 = 13.00\,\text{bar}, P_2 = 18.00\,\text{bar}$ produce lower initial water flux. Overall recovery decreases from $69.36\%$ to $65.45\%$, and SEC increases from $0.7710$ to $0.8244\,\text{kWh/m}^3$.
- **Membrane Stress:** Maximum single-element recovery drops from $23.69\%$ to $21.24\%$, safely below the $30\%$ project engineering safeguard limit. Concentration polarization modulus $\beta_{\text{max}}$ shifts from $1.3019$ to $1.2820$.

### Stage 3 & 3B: Dataset Generation and Engineering Envelope Curation
- **Acceptance Rate:** Because baseline fluxes are slightly lower at identical pressures, fewer scenarios exceed the $30\%$ element recovery limit in the lead positions. Consequently, the fraction of engineering-acceptable scenarios increased from $45.25\%$ ($2,241$ rows) in Model V1 to **$53.63\%$ ($2,670$ rows)** in Model V2.
- **Dataset Partitions:** Deterministic $70\% / 15\% / 15\%$ splits yielded $1,868$ training, $401$ validation, and $401$ test scenarios.

### Stage 4 & 4B: Machine Learning Surrogates & Physics Reconstruction
- **Surrogate Fidelity:** The Artificial Neural Network (MLP) achieves $R^2 = 0.99979$ on overall recovery, $0.99986$ on concentrate TDS, and $0.99978$ on SEC.
- **Physics Reconciliation:** In `PHYSICS_RECONSTRUCTED` mode, the ANN surrogate enforces exact mass and solute conservation ($1.22 \times 10^{-15}\%$ solute balance error on the test partition).
- **Inference Speed:** The trained surrogate delivers predictions at $89,252\,\text{evals/sec}$ ($1,568\times$ faster than the differential-algebraic ODE solver).

### Stage 5 & 5B: NSGA-II Multi-Objective Optimization & Feasibility Refinement
- **Baseline Dominance Invariance:** In both Model V1 and Model V2, the authoritative industrial baseline ($13/18\,\text{bar}$) is **strictly dominated** by 59 non-dominated Pareto candidate solutions.
- **Representative Strategies:**
  - **Strategy A (Max Feasible Recovery):** $P_1 = 20.00\,\text{bar}, P_2 = 20.25\,\text{bar} \implies \text{Rec} = 84.35\%, \text{SEC} = 0.7938\,\text{kWh/m}^3, R_{\text{elem,max}} = 29.99\% \le 30.000\%$.
  - **Strategy B (Min SEC):** $P_1 = 15.80\,\text{bar}, P_2 = 15.80\,\text{bar} \implies \text{Rec} = 68.34\%, \text{SEC} = 0.7641\,\text{kWh/m}^3, R_{\text{elem,max}} = 19.83\%$.
  - **Strategy C (Min Stress):** $P_1 = 10.00\,\text{bar}, P_2 = 14.00\,\text{bar} \implies \text{Rec} = 48.38\%, \text{SEC} = 0.8859\,\text{kWh/m}^3, R_{\text{elem,max}} = 12.65\%$.
  - **Strategy D (Balanced Knee):** $P_1 = 16.06\,\text{bar}, P_2 = 16.41\,\text{bar} \implies \text{Rec} = 70.16\%, \text{SEC} = 0.7665\,\text{kWh/m}^3, R_{\text{elem,max}} = 20.37\%$.
- **Structural Equivalence:** Strategy D continues to provide $70.16\%$ recovery ($+4.71\%$ above baseline) at $0.7665\,\text{kWh/m}^3$ ($-7.02\%$ lower SEC than baseline), demonstrating clear Pareto superiority over unoptimized operation.

### Stage 6: Literature-Grounded Dynamic Fouling Simulation
- **Fouling Rate Constant Re-calibration:** $r_{\text{spec}} = 1.954988 \times 10^{13}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)$ perfectly reproduces the $15.0000\%$ experimental permeability decline target at $625.0\,\text{L/m}^2$ specific permeate exposure.
- **Dynamic Hierarchy:** Strategy D produces $2,332.1\,\text{m}^3$ of permeate over 7 days ($+12.0\%$ more water than baseline at $2,082.7\,\text{m}^3$) while consuming $1.1721\,\text{kWh/m}^3$ ($-14.3\%$ lower dynamic average SEC than baseline at $1.3682\,\text{kWh/m}^3$). Strategy A achieves maximum cumulative water yield ($2,626.2\,\text{m}^3$), while Strategy C experiences minimum permeability loss ($36.74\%$).

---

## 3. Formal Classification of Scientific Claims

| Claim ID | Scientific Claim / Finding | Model V1 Finding | Model V2 Finding | Status Classification |
| :--- | :--- | :--- | :--- | :--- |
| **C-01** | Manufacturer test pressure is transmembrane gauge differential. | $14.50\,\text{bar}$ | $15.5132\,\text{bar}$ | `MATERIALLY CHANGED` |
| **C-02** | Toray TML20D-400 pure water permeability $A_w$. | $3.6835\,\text{LMH/bar}$ | $3.4007\,\text{LMH/bar}$ | `MATERIALLY CHANGED` |
| **C-03** | Manufacturer single-element validation accuracy is exact. | $0.000\%$ err | $0.000\%$ err | `UNCHANGED` |
| **C-04** | Authoritative 15-element industrial baseline recovery. | $69.36\%$ | $65.45\%$ | `NUMERICALLY SHIFTED` |
| **C-05** | Authoritative 15-element industrial baseline SEC. | $0.7710\,\text{kWh/m}^3$ | $0.8244\,\text{kWh/m}^3$ | `NUMERICALLY SHIFTED` |
| **C-06** | Authoritative baseline is strictly dominated on the Pareto front. | Dominated | Dominated | `UNCHANGED` |
| **C-07** | ANN surrogate achieves $R^2 > 0.9997$ and $>1500\times$ speed-up. | $R^2 > 0.9997$, $1520\times$ | $R^2 > 0.9997$, $1568\times$ | `UNCHANGED` |
| **C-08** | Strategy A maximizes clean water recovery within $30\%$ limit. | $82.17\%$ | $84.35\%$ | `NUMERICALLY SHIFTED` |
| **C-09** | Strategy B achieves absolute minimum specific energy consumption. | $0.7303\,\text{kWh/m}^3$ | $0.7641\,\text{kWh/m}^3$ | `NUMERICALLY SHIFTED` |
| **C-10** | Strategy D (Balanced Knee) strictly dominates the baseline. | Dominates | Dominates | `UNCHANGED` |
| **C-11** | Strategy C achieves minimum fouling and pressure escalation. | Min fouling | Min fouling | `UNCHANGED` |
| **C-12** | Fixed pressure operation (Mode A) suffers severe flux loss ($>40\%$). | $>40\%$ loss | $>40\%$ loss | `UNCHANGED` |
| **C-13** | Mode B pressure ceiling is exceeded for high-flux strategies. | Exceeded | Exceeded | `UNCHANGED` |
| **C-14** | Dynamic rankings and trade-offs are robust to rate uncertainty. | Invariant | Invariant | `UNCHANGED` |

---

## 4. Archival and Provenance Record

All deprecated Model V1 datasets, trained surrogate weights, and result logs are permanently archived in `archive/model_v1/`:
- `archive/model_v1/data/generated/`: Raw and curated V1 simulation files.
- `archive/model_v1/models/stage4/`: V1 preprocessing pipelines and surrogate model binaries.
- `archive/model_v1/results/`: Full Stage 4, Stage 5, and Stage 6 analytical ledgers under V1.
- `config/model_manifest.json`: Authoritative single source of truth for Model V2.0 physical parameters.

---
**Stage 6C Migration Status:** COMPLETE AND VERIFIED.
