# Stage 3B Feature Provenance and Data Leakage Audit

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Stage:** 3B — Engineering Envelope Audit and Dataset Curation  
**Document Purpose:** Define the strict categorization of dataset features, establish causal boundaries, and enforce anti-leakage rules prior to Stage 4 machine-learning surrogate model training.

---

## 1. Scientific Governance & Leakage Prevention Rules

To guarantee that machine learning surrogate models (Random Forest, XGBoost, Artificial Neural Networks) emulate the true physics of the mechanistic simulator rather than learning spurious numerical shortcuts, features are segregated into strict functional tiers:

> [!IMPORTANT]
> **Anti-Leakage Rule 1: No Target-Derived Inputs**
> Under no circumstances may stream flow rates ($Q_p, Q_r$), stage powers ($P_{\text{pump}, 1}, P_{\text{booster}, 2}$), or downstream concentrations ($C_p, C_r$) be provided as input features when predicting system recovery, flux, or energy.
>
> **Anti-Leakage Rule 2: Non-Causal Variable Exclusion**
> Although `feed_cod_mgL` and `feed_pH` are tracked in the master dataset, they exert zero mechanistic force in the current NaCl-equivalent transport model. They **must be excluded** from the primary Stage 4 surrogate input feature matrix to prevent decision trees or neural weights from fitting random sampling noise.

---

## 2. Complete Variable Classification Ledger

| Variable Name | Data Type | Units | Feature Role | Causal Status | Stage 4 ML Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `feed_flow_m3h` | Float | $\text{m}^3/\text{h}$ | **Input Feature** | Mechanistically Causal | **Primary Surrogate Input** |
| `feed_tds_mgL` | Float | $\text{mg/L}$ | **Input Feature** | Mechanistically Causal | **Primary Surrogate Input** |
| `temperature_C` | Float | $^\circ\text{C}$ | **Input Feature** | Mechanistically Causal | **Primary Surrogate Input** |
| `stage1_pressure_bar` | Float | $\text{bar}$ | **Input Feature** | Mechanistically Causal | **Primary Surrogate Input** |
| `stage2_pressure_bar` | Float | $\text{bar}$ | **Input Feature** | Mechanistically Causal | **Primary Surrogate Input** |
| `feed_cod_mgL` | Float | $\text{mg/L}$ | **Descriptor** | Non-Causal (Metadata) | Excluded from primary surrogate |
| `feed_pH` | Float | $-$ | **Descriptor** | Non-Causal (Metadata) | Excluded from primary surrogate |
| `simulation_id` | String | $-$ | **Metadata** | Non-Causal | Identifier only |
| `sampling_method` | String | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `random_seed` | Integer | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `model_version` | String | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `parameter_set` | String | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `topology` | String | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `timestamp` | String | $-$ | **Metadata** | Non-Causal | Provenance tracking |
| `dataset_split` | String | $-$ | **Metadata** | Non-Causal | Data partition (`train`/`val`/`test`) |
| `operating_classification` | String | $-$ | **Classification** | Non-Causal | Data partition label |
| `overall_recovery_pct` | Float | $\%$ | **Primary Target** | Process Output | **Primary Surrogate Output Target** |
| `permeate_tds_mgL` | Float | $\text{mg/L}$ | **Primary Target** | Process Output | **Primary Surrogate Output Target** |
| `concentrate_tds_mgL` | Float | $\text{mg/L}$ | **Primary Target** | Process Output | **Primary Surrogate Output Target** |
| `average_flux_LMH` | Float | $\text{LMH}$ | **Primary Target** | Process Output | **Primary Surrogate Output Target** |
| `SEC_kWh_m3` | Float | $\text{kWh/m}^3$ | **Primary Target** | Process Output | **Primary Surrogate Output Target** |
| `maximum_element_recovery_pct` | Float | $\%$ | **Secondary Target** | Process Output | Secondary State Target / Safeguard |
| `maximum_polarization_modulus` | Float | $-$ | **Secondary Target** | Process Output | Secondary State Target / Risk Index |
| `stage1_recovery_pct` | Float | $\%$ | **Secondary Target** | Process Output | Intermediate Stage State |
| `stage2_recovery_pct` | Float | $\%$ | **Secondary Target** | Process Output | Intermediate Stage State |
| `total_power_kW` | Float | $\text{kW}$ | **Secondary Target** | Process Output | Energy Component |
| `flux_decline_stage1_pct` | Float | $\%$ | **Health Descriptor** | Process Output | Digital Twin State Variable |
| `flux_decline_stage2_pct` | Float | $\%$ | **Health Descriptor** | Process Output | Digital Twin State Variable |
| `permeate_flow_m3h` | Float | $\text{m}^3/\text{h}$ | **Derived Output** | Output Quantity | Derived from $Q_f \times R$ |
| `concentrate_flow_m3h` | Float | $\text{m}^3/\text{h}$ | **Derived Output** | Output Quantity | Derived from $Q_f - Q_p$ |
| `stage1_pump_power_kW` | Float | $\text{kW}$ | **Derived Output** | Output Quantity | Stage 1 Hydraulic/Electrical Power |
| `stage2_booster_power_kW`| Float | $\text{kW}$ | **Derived Output** | Output Quantity | Stage 2 Booster Power |

---

## 3. Stage 4 Machine Learning Surrogate Mapping

For the primary Stage 4 Multi-Input Multi-Output (MIMO) surrogate model:

$$\begin{bmatrix} Q_f \\ C_f \\ T \\ P_1 \\ P_2 \end{bmatrix} \xrightarrow{\quad \text{ML Surrogate} \quad} \begin{bmatrix} R_{\text{overall}} \\ C_p \\ C_r \\ J_{w,\text{avg}} \\ SEC \\ R_{\text{elem},\max} \\ (C_m/C_b)_{\max} \end{bmatrix}$$

This guarantees complete independence from derived flows and preserves the rigorous causal structure of the underlying physical simulation.
