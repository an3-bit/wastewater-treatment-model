# AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse
## Stage 1: Mechanistic Reverse Osmosis Baseline Model

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](tests/)

---

## 1. Project Purpose & Scope

This software repository contains the foundational development stages of a research initiative aimed at building an **AI-Enabled Digital Twin for Fouling-Aware Multi-Objective Optimization of Textile Wastewater Reuse**.

The purpose of this software is to establish, verify, and validate a **first-principles, physics-based Reverse Osmosis (RO) mechanistic model**, and use it to generate structured simulation data for machine learning surrogate models (Random Forest, XGBoost, ANNs), explainable AI (SHAP), multi-objective optimization (NSGA-II), and digital twin simulation.

> [!IMPORTANT]
> **Scientific Notice on Simulation-Derived Data:**
> The Stage 3 dataset is simulation-derived. Machine-learning models trained on this dataset will initially learn the behaviour of the mechanistic simulator. Agreement between the ML surrogate and this dataset demonstrates surrogate fidelity, not independent validation against an industrial plant.
>
> The base two-stage RO model is **mechanistically verified and suitable for simulation-based AI development, subject to later external/industrial validation**. The 3:2 vessel staging array is a **model-derived feasible configuration**, not the confirmed Nice Cotton plant configuration.

---

## 2. Scientific Background & Citation

The model equations, membrane specifications, and baseline parameter estimation values are based on the published industrial wastewater study:

```bibtex
@article{sowgath2025design,
  title={Design of Multi Stage Reverse Osmosis Process for Reuse of Textile Wastewater},
  author={Sowgath, M. and Sarker, N. and Mujtaba, I. M.},
  journal={Chemical Engineering Transactions},
  volume={117},
  year={2025},
  publisher={AIDIC}
}
```

The study examines an industrial Membrane Bioreactor – Reverse Osmosis (MBR–RO) wastewater treatment plant associated with **Nice Cotton Limited** in Gazipur, Bangladesh.

---

## 3. Mathematical Formulation & Governing Equations

The model solves the coupled nonlinear algebraic system of equations describing solution-diffusion mass transport, film-theory concentration polarization, electrolyte thermodynamics, and macroscopic mass balances.

```
       Feed Stream (Qf, Cf, Pf)
  ==============================================> Concentrate (Qr, Cr)
           |                |             |
           | Jw (Water)     |             |
           v Js (Salt)      v             v
  ----------------------------------------------  Membrane Active Layer
  ==============================================
                    ||||||||| Permeate Channel
                    v
            Permeate Stream (Qp, Cp, Pp)
```

### 3.1. Water Volumetric Flux ($J_w$)
Based on solution-diffusion theory:
$$J_w = A_w (\Delta P - \Delta \pi)$$
where:
- $A_w$: Membrane pure water permeability coefficient $[\text{m}/(\text{Pa}\cdot\text{s})]$ or $[\text{m}/(\text{bar}\cdot\text{s})]$
- $\Delta P = P_{\text{bulk,avg}} - P_{\text{permeate}}$: Transmembrane hydraulic driving pressure $[\text{Pa}]$
- $P_{\text{bulk,avg}} = P_f - \frac{1}{2} \Delta P_{\text{element}}$: Mean feed-side hydraulic pressure $[\text{Pa}]$
- $\Delta \pi = \pi(C_m) - \pi(C_p)$: Transmembrane osmotic pressure difference $[\text{Pa}]$

### 3.2. Solute Mass Flux ($J_s$)
$$J_s = A_s (C_m - C_p)$$
where:
- $A_s$: Membrane solute permeability coefficient $[\text{m/s}]$
- $C_m$: Solute mass concentration at the membrane surface active layer $[\text{kg/m}^3]$
- $C_p$: Solute mass concentration in the permeate $[\text{kg/m}^3]$

### 3.3. Concentration Polarization (Film Theory)
Accumulation of rejected solute at the membrane surface creates a boundary layer modeled via stagnant film theory:
$$C_m = C_p + (C_b - C_p) \exp\left(\frac{J_w}{k}\right)$$
where:
- $C_b = \frac{C_f + C_r}{2}$: Average bulk cross-flow solute concentration $[\text{kg/m}^3]$
- $k$: Mass-transfer coefficient in the feed spacer channel $[\text{m/s}]$
  - **Mode A**: User-specified $k$
  - **Mode B**: Correlation-based $k$ via Sherwood number:
    $$Sh = \frac{k \, d_h}{D_{AB}} = 0.065 \, Re^{0.875} \, Sc^{0.25}$$

### 3.4. Permeate Solute Concentration ($C_p$)
From the local active layer solute flux balance $J_s = J_w C_p = A_s (C_m - C_p)$:
$$C_p = \frac{A_s \, C_m}{J_w + A_s}$$

### 3.5. Electrolyte Thermodynamics (van 't Hoff Osmotic Pressure)
$$\pi = i \, C_{\text{molar}} \, R \, T = i \, \left(\frac{C_{\text{mass}}}{M_w}\right) \, R \, T$$
where:
- $i$: van 't Hoff dissociation factor ($i = 2.0$ for NaCl equivalent)
- $R = 8.314462618\ \text{J}/(\text{mol}\cdot\text{K})$: Universal gas constant
- $T$: Absolute temperature $[\text{K}]$
- $M_w = 0.058443\ \text{kg/mol}$: Molar mass of NaCl equivalent

### 3.6. Overall Element Mass Balances
$$\text{Total Fluid Balance: } \quad Q_f = Q_p + Q_r = (J_w A_m) + Q_r$$
$$\text{Solute Conservation: } \quad Q_f C_f = Q_p C_p + Q_r C_r = (J_w A_m C_p) + (Q_f - J_w A_m) C_r$$

### 3.7. High-Pressure Pump Energy Model
$$\text{Hydraulic Power: } \quad P_{\text{hyd}} = Q_f \, (P_f - P_{\text{inlet}}) \quad [\text{kW}]$$
$$\text{Electrical Power: } \quad P_{\text{elec}} = \frac{P_{\text{hyd}}}{\eta_{\text{pump}}} \quad [\text{kW}]$$
$$\text{Specific Energy Consumption: } \quad SEC = \frac{P_{\text{elec}}}{Q_p} \quad [\text{kWh/m}^3\text{ permeate}]$$

---

## 4. Parameter Ledger: Reported Values vs. Modeling Assumptions

For academic transparency, all parameters are strictly categorized:

| Parameter | Symbol | Value | Unit | Classification | Source / Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Membrane Area | $A_m$ | 37.0 | $\text{m}^2$ | **Manufacturer Derived** | Toray TML20D-400 Datasheet / Sowgath et al. (2025) |
| Module Diameter | $d$ | 0.201 | $\text{m}$ | **Manufacturer Derived** | 8-inch nominal element outer diameter |
| Reconciled Water Permeability | $A_w$ | $1.0232 \times 10^{-6}$ | $\text{m}/(\text{bar}\cdot\text{s})$ | **Manufacturer Derived** | Back-calculated from Toray nominal test point ($3.68\ \text{LMH/bar}$) |
| Nominal Salt Permeability | $A_{s,\text{mfr}}$ | $1.7827 \times 10^{-8}$ | $\text{m/s}$ | **Manufacturer Derived** | Reconciled against $99.8\%$ nominal salt rejection |
| Literature Salt Permeability | $A_{s,\text{lit}}$ | $1.1834 \times 10^{-9}$ | $\text{m/s}$ | **Literature Reported** | Parameter estimation reported in Sowgath et al. (2025) |
| Feed Flow | $Q_f$ | 30.0 | $\text{m}^3/\text{h}$ | **Source Reported** | Baseline operational feed flow condition |
| Feed TDS | $C_f$ | 2041.0 | $\text{mg/L}$ | **Source Reported** | Published MBR effluent salinity |
| Feed Pressure | $P_f$ | 225.0 / 15.51 | $\text{psi}$ / $\text{bar}$ | **Source Reported** | Nominal test pressure |
| Temperature | $T$ | 25.0 | $^\circ\text{C}$ | **Source Reported** | Baseline operational temperature ($298.15\ \text{K}$) |
| Max Operating Pressure | $P_{\max}$ | 41.0 | $\text{bar}$ | **Manufacturer Limit** | Mechanical element limit |
| Pump Efficiency | $\eta_{\text{pump}}$ | 0.80 | $-$ | **Modeling Assumption** | Typical industrial high-pressure centrifugal pump |
| van 't Hoff Factor | $i$ | 2.0 | $-$ | **Modeling Assumption** | Complete dissociation of 1:1 NaCl-equivalent salt |
| Mass Transfer Coeff. | $k$ | $5.0 \times 10^{-5}$ | $\text{m/s}$ | **Modeling Assumption** | Feed spacer channel mass-transfer velocity |

---

## 5. Multi-Stage Plant Architecture (Stage 2)

In Stage 2, the single element was scaled to a multi-element pressure vessel ($3$ elements in series) and an industrial two-stage system:
- **Topology A (Concentrate Staging):** Stage 1 concentrate feeds Stage 2. Stage 1 and Stage 2 permeates combine for total plant product.
- **Model-Derived Feasible Configuration:** 3 vessels in Stage 1, 2 vessels in Stage 2 ($15$ elements, $555\ \text{m}^2$). Operating at $P_1 = 13.0\ \text{bar}$ and $P_2 = 18.0\ \text{bar}$, this achieves $69.71\%$ overall recovery with a permeate TDS of $7.24\ \text{mg/L}$ (which is below the $18\ \text{mg/L}$ permeate TDS reported in the industrial reference case).

---

## 6. Software Architecture

```
textile_water_ai/
│
├── README.md                      # Academic documentation & usage guide
├── requirements.txt               # Dependencies
├── pyproject.toml                 # Package build & pytest configuration
│
├── config/
│   ├── baseline.yaml              # Single-element configuration
│   ├── manufacturer_validation.yaml # Toray validation configuration
│   └── textile_baseline.yaml      # Multi-stage industrial textile configuration
│
├── data/
│   ├── raw/                       # Published Nice Cotton Ltd. stream ledger
│   ├── processed/                 # Curated datasets
│   └── generated/                 # Stage 3 LHS simulation dataset
│
├── src/
│   ├── ro_model/                  # Mechanistic reverse osmosis core
│   │   ├── units.py               # Unit conversions
│   │   ├── osmotic.py             # van 't Hoff thermodynamics
│   │   ├── hydraulics.py          # k and channel ΔP
│   │   ├── transport.py           # Solution-diffusion and film theory
│   │   ├── energy.py              # HP pump and booster power & SEC
│   │   ├── membrane.py            # MembraneProperties & ElementOperatingConditions
│   │   ├── solver.py              # Coupled algebraic solver
│   │   ├── validation.py          # Sanity checks & mass balance audit
│   │   ├── water_quality.py       # Level B non-TDS species tracking
│   │   ├── element.py             # MembraneElement class
│   │   ├── vessel.py              # PressureVessel (3 elements in series)
│   │   ├── stage.py               # ROStage (parallel vessels)
│   │   └── system.py              # ROSystem (multi-stage network)
│   │
│   └── data_generation/           # Stage 3 simulation dataset generation
│       ├── sampling.py            # Latin Hypercube Sampling (scipy.stats.qmc)
│       ├── feasibility.py         # Failure categorization
│       ├── quality_control.py     # Automated quality verification flags
│       ├── simulator_runner.py    # Batch execution wrapper
│       └── dataset.py             # Data provenance, split labeling, and export
│
├── notebooks/
│   ├── 01_single_element_validation.ipynb
│   ├── 02_textile_industrial_baseline.ipynb
│   └── 03_dataset_exploration.ipynb
│
├── scripts/
│   ├── run_baseline.py
│   ├── run_manufacturer_validation.py
│   ├── run_textile_baseline.py
│   ├── run_stage2_full_study.py
│   ├── generate_stage3_dataset.py
│   └── analyze_stage3_dataset.py
│
├── results/
│   ├── stage2/                    # Stage 2 results, tables, and figures
│   └── stage3/                    # Stage 3 dataset summary, tables, and figures
│
└── tests/
    ├── test_units.py
    ├── test_osmotic.py
    ├── test_mass_balance.py
    ├── test_baseline.py
    ├── test_element_series.py
    ├── test_stage_balance.py
    ├── test_system_balance.py
    ├── test_textile_baseline.py
    ├── test_sampling.py
    ├── test_dataset_generation.py
    └── test_quality_control.py
```

---

## 7. Development Roadmap

- [x] **Stage 1**: Mechanistic single-element formulation & Toray TML20D-400 manufacturer validation.
- [x] **Stage 2**: Multi-element pressure vessel, 2-stage network topologies, and 70% recovery feasibility search.
- [x] **Stage 3**: Simulation-based dataset generation via Latin Hypercube Sampling (5,000 scenarios), quality control, and split preparation.
- [ ] **Stage 4**: Machine learning surrogate modeling (Random Forest, XGBoost, ANN).
- [ ] **Stage 5**: Explainable AI (SHAP analysis) & surrogate verification.
- [ ] **Stage 6**: Multi-objective optimization (NSGA-II) for energy vs. recovery vs. quality.
- [ ] **Stage 7**: Digital Twin integration & dynamic fouling simulation.

