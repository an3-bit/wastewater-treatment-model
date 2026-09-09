# Stage 2 System Modeling & Industrial Baseline Report

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Reference Study:** Sowgath, Sarker & Mujtaba (2025), Chemical Engineering Transactions, Vol. 117  
**Industrial Case:** Nice Cotton Ltd. MBR-RO Effluent Reclamation Train  

---

## 1. Scientific Classification of Parameters & Data

### A. SOURCE-REPORTED DATA
- **Feed Stream Quality (MBR Effluent):** TDS = 2041.0 mg/L, COD = 51.0 mg/L, BOD = 7.0 mg/L, TSS = 3.0 mg/L, Colour = 300.0 Pt-Co, pH = 8.0.
- **Feed Flow Rate:** Qf = 30.0 m³/h (operational feed flow condition).
- **Target Performance Benchmarks:** Overall water recovery ≈ 70%, Narrative salt rejection benchmark ≈ 73%.
- **Reported Product Streams:** Permeate TDS = 18.0 mg/L (COD = 5, BOD = 2, TSS = 0, Colour = BDL, pH = 7.5); Reject TDS = 3064.0 mg/L.

### B. MANUFACTURER-DERIVED PARAMETERS
- **Physical Water Permeability:** Aw = 1.0232e-6 m/(bar·s) (3.6835 LMH/bar) [Derived from Toray TML20D-400 datasheet test].
- **Nominal Salt Permeability:** As_manufacturer = 1.7827e-8 m/s (0.06418 LMH) [Back-calculated from 99.8% nominal test rejection].
- **Membrane Element Geometry:** Area = 37.0 m² (400 ft²), Diameter = 0.201 m (8-inch).

### C. LITERATURE-REPORTED PARAMETER
- **Literature Salt Permeability:** As_literature = 1.1834e-9 m/s (0.00426 LMH).
- **Literature Water Permeability:** Aw_literature = 9.08e-5 m/(bar·s) (326.88 LMH/bar). Incompatible when interpreted directly in conventional solution-diffusion formulation.

### D. MODEL ASSUMPTIONS
- **Level A van 't Hoff Electrolyte Model:** TDS modeled as equivalent NaCl (i = 2.0, Mw = 58.44 g/mol).
- **Mass Transfer Velocity (k):** k = 5.0e-5 m/s (180.0 LMH, Mode A).
- **Element Pressure Drop:** ΔP_elem = 0.15 bar per element.
- **High-Pressure Pump Efficiency:** η_pump = 0.80.

### E. DESIGN VARIABLES
- **Topology:** Topology A (Concentrate Staging) vs Topology B (Permeate Polishing).
- **Staging Configuration:** Number of parallel vessels N1 (Stage 1) and N2 (Stage 2), with 3 elements/vessel in series.
- **Stage Operating Pressures:** P1 and P2 (subject to P <= 41 bar).

---

## 2. Uncalibrated Simulation Results

Under standard baseline operating pressure (P1 = P2 = 15.51 bar, As = Literature 1.1834e-9 m/s):

- **Topology A (Concentrate Staging, 3:2 array):**
  - Recovery: **71.09%** (Qp = 21.33 m³/h, Qr = 8.67 m³/h)
  - Permeate Salinity: **0.5120 mg/L** (Rejection = 99.9749%)
  - Concentrate Salinity: **7058.20 mg/L**
  - Average Flux: **38.43 LMH**
  - System SEC: **0.7200 kWh/m³**

- **Topology B (Permeate Polishing, 3:1 array):**
  - Recovery: **19.56%** (Pass 2 permeate / raw feed)
  - Permeate Salinity: **0.000050 mg/L** (Ultra-pure)
  - Concentrate Salinity: **2537.20 mg/L**
  - System SEC: **3.7711 kWh/m³**

---

## 3. 70% Recovery Feasibility Analysis

Searching across 300+ pressure-array combinations identified that **approximately 70% recovery is physically and hydraulically achievable via system design without altering physical membrane parameters**:

- **Recommended Best Configuration:**
  - **Topology:** Concentrate Staging (Topology A)
  - **Staging Array:** 3 parallel vessels (Stage 1) : 2 parallel vessels (Stage 2) (15 total elements, 555 m²)
  - **Stage Pressures:** P1 = 15.0 bar, P2 = 25.0 bar (+10.0 bar interstage boost)
  - **Achieved Recovery:** **69.03%** (Qp = 20.71 m³/h)
  - **Permeate TDS:** **5.96 mg/L** (Matches industrial reuse standard < 20 mg/L)
  - **Concentrate TDS:** **6575.97 mg/L** (Closes steady-state solute conservation against theoretical 6761 mg/L)
  - **Average System Flux:** **46.64 LMH**
  - **System SEC:** **0.9942 kWh/m³**
  - **Maximum Element Recovery:** **20.13%** (Safe within 30% anti-scaling guideline)
  - **Maximum Polarization Modulus:** **1.4733** (Well controlled)

---

## 4. Master Comparison Table

| Performance Metric | Published Industrial Value | Uncalibrated Model (15.5 bar) | Best Feasible Design (P1=15, P2=25 bar) | Deviation (Best vs Published) | Scientific Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall Recovery** | 70.0% | 71.09% | **69.03%** | -0.97% | Achieved via 3:2 staging and interstage boosting. |
| **Permeate TDS** | 18.0 mg/L | 0.51 mg/L | **5.96 mg/L** | -12.04 mg/L | Consistent with high-grade reuse standard (< 20 mg/L). |
| **Concentrate TDS** | 3064.0 mg/L (Inconsistent) | 7058.20 mg/L | **6575.97 mg/L** | +3511.97 mg/L | Model enforces exact solute conservation. Published 3064 mg/L is 54.7% below steady-state mass balance. |
| **Salt Rejection** | 73.0% text / 99.12% calc | 99.97% | **99.71%** | +0.59% vs calc | Model matches calculated stream rejection (99.12%); narrative 73% is inconsistent. |
| **Average Flux** | Not reported | 38.43 LMH | **46.64 LMH** | N/A | Sustainable low-fouling industrial envelope. |
| **Stage 1 Pressure** | 15.51 bar (225 psi) | 15.51 bar | **15.00 bar** | -0.51 bar | Controls lead element flux. |
| **Stage 2 Pressure** | Not reported | 15.51 bar | **25.00 bar** | N/A | Overcomes Stage 2 osmotic pressure. |
| **System SEC** | Not reported | 0.72 kWh/m³ | **0.99 kWh/m³** | N/A | Realistic specific energy consumption for 2-stage RO. |
