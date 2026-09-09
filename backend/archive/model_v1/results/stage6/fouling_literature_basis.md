# Stage 6: Literature Basis and Parameter Provenance for Dynamic Membrane Fouling

**Project**: AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Phase**: Stage 6 — Literature-Grounded Dynamic Membrane Fouling Model  
**Author / Engineering Role**: Process Systems & Membrane Modeling Group  
**Audited System**: Two-Stage Industrial Reverse Osmosis Train (15 Toray TML20D-400 Elements, 555 m²)  

---

## 1. Executive Context & Objectives

In real-world textile wastewater reclamation, membrane performance declines over operating time due to the progressive accumulation of foulants on the membrane active layer and within feed spacer channels. In biologically treated textile effluents (MBR permeates), foulants comprise a complex matrix of:
1. **Soluble Microbial Products (SMPs)**: Biopolymers, polysaccharides, and proteinaceous residuals from upstream biological oxidation.
2. **Refractory Azo / Reactive Dyes & Surfactants**: Low-molecular-weight organic auxiliaries not fully degraded by biological treatment.
3. **Inorganic Dissolved Salts**: Calcium, sulfate, silica, chloride, and carbonate ions subject to severe concentration polarization.

Stage 6 implements a **dynamic mechanistic fouling model** that tracks the time-dependent degradation of membrane hydraulic permeability ($A_{\text{eff}}(t)$) and growth of fouling hydraulic resistance ($R_f(t)$) across each individual element of the 15-element industrial train.

---

## 2. Literature Parameter Provenance Ledger

All parameters utilized in the Stage 6 dynamic simulation framework are classified according to strict scientific provenance:
- **`SOURCE_REPORTED`**: Directly stated in primary experimental/industrial literature.
- **`SOURCE_DERIVED`**: Rigorously calculated from reported physical relationships without uncalibrated free parameters.
- **`CALIBRATED`**: Adjusted via reproducible mathematical optimization to match published experimental fouling trajectories.
- **`ASSUMED`**: Assigned based on standard physical membrane transport literature and clearly flagged with uncertainty limits.

| Parameter Name | Symbol | Value | Unit | Classification | Literature Source & DOI | Primary Transferability Limitation |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Clean Water Permeability** | $A_w$ | $1.0232 \times 10^{-6}$ | $\text{m}/(\text{bar}\cdot\text{s})$ | **SOURCE_DERIVED** | Toray Datasheet / Stage 1 Validation | Clean water baseline; neglects historical compaction |
| **Clean Salt Permeability** | $A_s$ | $1.7827 \times 10^{-8}$ | $\text{m/s}$ | **SOURCE_DERIVED** | Sowgath et al. (2025) (10.3303/CET25117013) | Apparent single-solute NaCl transport proxy |
| **Mass Transfer Coefficient** | $k$ | $5.0 \times 10^{-5}$ | $\text{m/s}$ | **ASSUMED** | Film Theory (10.1016/j.memsci.2007.08.016) | Assumes uniform crossflow along 34-mil spacer |
| **Element Membrane Area** | $S_m$ | $37.0$ | $\text{m}^2$ | **SOURCE_REPORTED** | Toray TML20D-400 Datasheet | Standard manufactured module area ($\pm 1.0\,\text{m}^2$) |
| **Active Element Count** | $N_{\text{elem}}$ | $15$ | elements | **SOURCE_DERIVED** | Sowgath et al. (2025) (Stage 1=3x3, Stage 2=2x3) | Specific to Nice Cotton $30\,\text{m}^3/\text{h}$ train layout |
| **Feed Flow Rate** | $Q_f$ | $30.0$ | $\text{m}^3/\text{h}$ | **SOURCE_REPORTED** | Sowgath et al. (2025) | Design operating disturbance baseline |
| **Feed Salinity (TDS)** | $C_f$ | $2041.0$ | $\text{mg/L}$ | **SOURCE_REPORTED** | Sowgath et al. (2025) Table 1 | Composite conductivity TDS; subject to batch shifts |
| **Feed Residual COD** | $\text{COD}_f$ | $51.0$ | $\text{mg/L}$ | **SOURCE_REPORTED** | Sowgath et al. (2025) Table 1 | Tracked as Level B organic water quality descriptor |
| **Clean Membrane Resistance** | $R_m$ | $1.098 \times 10^{14}$ | $\text{m}^{-1}$ | **SOURCE_DERIVED** | Calculated: $R_m = 1/(\mu(25^\circ\text{C}) \cdot A_{\text{clean}})$ | Temperature-dependent via water dynamic viscosity |
| **Empirical Anchor Volume** | $v_{\text{spec, ref}}$| $625.0$ | $\text{L/m}^2$ | **SOURCE_REPORTED** | Textile RO Fouling Literature (10.3390/membranes12080789)| Benchmark cumulative permeate exposure |
| **Empirical Permeability Decline**| $\Delta A_w / A_{w,0}$| $15.0$ | $\%$ | **SOURCE_REPORTED** | Textile RO Fouling Literature (10.3390/membranes12080789)| Threshold defining significant fouling onset |
| **Specific Fouling Resistance**| $r_{\text{spec}}$ | $2.45 \times 10^{13}$ | $\text{m}^{-1}/(\text{m}^3/\text{m}^2)$| **CALIBRATED** | Calibrated to $625\,\text{L/m}^2 \to 15\%$ decline | Single empirical anchor; requires multi-point validation |
| **Polarization Exponent** | $\alpha$ | $1.0$ | — | **ASSUMED** | Convective Deposition Theory | Assumes linear drag force deposition coupling |
| **Concentration Exponent** | $\gamma$ | $1.0$ | — | **ASSUMED** | Cake Layer Solute Trapping Theory | Assumes deposition scales with local wall salinity |
| **Nominal Cleaning Efficiency** | $\eta_{\text{clean}}$ | $0.90$ | — | **ASSUMED** | CIP Literature (10.1016/j.memsci.2019.01.032) | Depends on chemical recipe (NaOH/EDTA vs acid) |

---

## 3. Primary Empirical Anchor

The empirical anchor is drawn from pilot-scale investigations of reverse osmosis membranes treating biologically treated textile wastewater effluent:
- **Cumulative Production Exposure**: Producing approximately **$v_{\text{spec}} = 625\,\text{L/m}^2$** ($0.625\,\text{m}^3/\text{m}^2$) of permeate through a low-fouling polyamide RO membrane at approximately **$60\%$ recovery** results in a **$\ge 15.0\%$ decline in effective water permeability** ($A_{\text{eff}} / A_{\text{clean}} \le 0.85$).

### Calibration Interpretation
In Darcy resistance terms, an $A_{\text{eff}} / A_{\text{clean}} = 0.85$ corresponds to an overall hydraulic resistance of:
$$\frac{R_{\text{total}}}{R_m} = \frac{1}{0.85} = 1.17647 \implies \frac{R_f}{R_m} = 0.17647$$
Given clean membrane resistance $R_m = 1.098 \times 10^{14}\,\text{m}^{-1}$, the required accumulated fouling resistance at $625\,\text{L/m}^2$ is:
$$R_f(625\,\text{L/m}^2) = 0.17647 \times 1.098 \times 10^{14} = 1.938 \times 10^{13}\,\text{m}^{-1}$$

The single specific fouling resistance coefficient is thus calibrated to match this exact physical benchmark under the standard reference operating state.

---

## 4. Scientific Boundaries & Validation Limitations

> [!CAUTION]
> **Scientific Integrity Disclosure**:
> 1. **Single Empirical Anchor Limitation**: Because exact multi-time-point fouling curves for the specific Nice Cotton dyehouse effluent are not published in Sowgath et al. (2025), the dynamic model is strictly classified as a **literature-calibrated dynamic model requiring independent experimental validation**.
> 2. **Sensitivity Testing Mandatory**: To account for variability in upstream biological pretreatment efficiency and dyehouse batch chemistry, parametric uncertainty sweeps of $\pm 25\%$ around the calibrated fouling rate constant $r_{\text{spec}}$ are conducted systematically in Section 21.
