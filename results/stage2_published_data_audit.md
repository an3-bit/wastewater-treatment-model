# Stage 2 Published Data Consistency Audit

**Project:** AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse  
**Reference Study:** Sowgath, Sarker & Mujtaba (2025), *“Design of Multi Stage Reverse Osmosis Process for Reuse of Textile Wastewater”*, Chemical Engineering Transactions, Vol. 117.  
**Industrial Case:** Nice Cotton Ltd., Bangladesh (MBR–RO Effluent Reclamation)

---

## 1. Published Industrial Stream Data Ledger

Table 1 of Sowgath et al. (2025) provides the following water quality characterization across the textile wastewater reclamation train at Nice Cotton Ltd.:

| Stream Name | TDS ($\text{mg/L}$) | TSS ($\text{mg/L}$) | Colour ($\text{Pt-Co}$) | BOD ($\text{mg/L}$) | COD ($\text{mg/L}$) | pH | Published Data Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Untreated Textile Wastewater** | $2200.0$ | $180.0$ | $2500.0$ | $350.0$ | $1178.0$ | $11.0$ | **SOURCE-REPORTED INDUSTRIAL DATA** |
| **MBR-Treated Water / RO Feed** | $2041.0$ | $3.0$ | $300.0$ | $7.0$ | $51.0$ | $8.0$ | **SOURCE-REPORTED INDUSTRIAL DATA** |
| **RO Permeate** | $18.0$ | $0.0$ | $\text{BDL}^*$ | $2.0$ | $5.0$ | $7.5$ | **SOURCE-REPORTED INDUSTRIAL DATA** |
| **RO Reject / Concentrate** | $3064.0$ | $3.0$ | $550.0$ | $9.0$ | $55.0$ | $7.8$ | **SOURCE-REPORTED INDUSTRIAL DATA** |

$^*$*BDL: Below Detection Limit.*

---

## 2. Mathematical Consistency Audit of Published Data

Prior to mechanistic modeling and digital twin development, an engineering and mathematical quality-control audit of the published data was conducted.

### 2.1. Salt Rejection Consistency Check
* **Published Text Benchmark:** The authors state an overall salt rejection benchmark of approximately **$73\%$**.
* **Mathematical Calculation from Published Stream Data:**
  Using the reported RO feed TDS ($C_f = 2041.0\ \text{mg/L}$) and RO permeate TDS ($C_p = 18.0\ \text{mg/L}$):
  $$SR_{\text{apparent}} = \left(1 - \frac{C_p}{C_f}\right) \times 100\% = \left(1 - \frac{18.0}{2041.0}\right) \times 100\% = \mathbf{99.1181\%} \quad (\approx 99.12\%)$$

> [!WARNING]
> **Audit Finding 1 (Salt Rejection Discrepancy):**
> There is a **$26.12\%$ percentage point discrepancy** between the paper's narrative benchmark ($\sim 73\%$) and the stream concentrations reported in Table 1 ($99.12\%$). A modern polyamide RO membrane (such as the Toray TML20D-400) producing $18\ \text{mg/L}$ permeate from a $2041\ \text{mg/L}$ feed operates at $>99\%$ salt rejection.

---

### 2.2. Global TDS Mass Balance Audit at 70% Recovery
The published study targets an overall water recovery of $WR = 70.0\%$ ($Q_p / Q_f = 0.70$).

By conservation of mass for a steady-state two-stream separator:
$$Q_f C_f = Q_p C_p + Q_r C_r \implies C_r = \frac{C_f - WR \cdot C_p}{1 - WR}$$

Substituting the published values ($C_f = 2041.0\ \text{mg/L}$, $C_p = 18.0\ \text{mg/L}$, $WR = 0.70$):
$$C_{r,\text{theoretical}} = \frac{2041.0 - (0.70 \times 18.0)}{1.0 - 0.70} = \frac{2041.0 - 12.6}{0.30} = \mathbf{6761.33\ \text{mg/L}}$$

* **Theoretical Required Reject TDS:** $\mathbf{6761.33\ \text{mg/L}}$
* **Published Reported Reject TDS:** $\mathbf{3064.00\ \text{mg/L}}$
* **Deficit in Published Reject TDS:** $\mathbf{3697.33\ \text{mg/L}}$ ($54.68\%$ deficit)

Furthermore, if the reported reject TDS of $3064.0\ \text{mg/L}$ and permeate TDS of $18.0\ \text{mg/L}$ were correct, the implied recovery would be:
$$WR_{\text{implied}} = \frac{C_r - C_f}{C_r - C_p} = \frac{3064.0 - 2041.0}{3064.0 - 18.0} = \frac{1023.0}{3046.0} = \mathbf{33.585\%} \quad (\approx 33.59\%)$$

> [!CAUTION]
> **Audit Finding 2 (Solute Balance Interpretation at 70% Recovery):**
> At 70% recovery, a steady-state TDS balance requires a reject concentration of approximately 6761 mg/L. The published reject TDS of 3064 mg/L is approximately 54.7% below this required concentration. Therefore, the reported feed TDS, permeate TDS, reject TDS and 70% recovery cannot all represent the same steady-state operating point.
>
> **Modeling Principle:** Our mechanistic simulation engine strictly enforces global fluid and solute conservation ($0.000000\%$ error) and will not artificially force unphysical reject concentrations.

---

## 3. Water Quality Rejection Descriptors (Level B)

Evaluating apparent observed separations from published MBR feed to RO permeate:

* **COD Rejection:** $R_{\text{COD}} = 1 - \frac{5.0}{51.0} = \mathbf{90.20\%}$
* **BOD Rejection:** $R_{\text{BOD}} = 1 - \frac{2.0}{7.0} = \mathbf{71.43\%}$
* **TSS Rejection:** $R_{\text{TSS}} = 1 - \frac{0.0}{3.0} = \mathbf{100.00\%}$
* **Colour Removal:** Exact colour rejection cannot be calculated because the permeate is reported as Below Detection Limit (BDL) and the numerical analytical detection limit is not provided. (Published: $300.0\ \text{Pt-Co} \to \text{BDL}$).

> [!NOTE]
> These values represent **observed apparent separations** across the published industrial effluent streams, not intrinsic membrane transport parameters. In our model, Level A handles thermodynamic osmotic pressure using NaCl-equivalent TDS, while Level B tracks these pollutant descriptors independently.

---

## 4. Methodological & Provenance Corrections

In accordance with scientific rigor:

1. **Water Permeability Interpretation:**
   The literature-reported water permeability $A_w = 9.08 \times 10^{-5}\ \text{m}/(\text{bar}\cdot\text{s})$ is **incompatible with manufacturer performance when interpreted directly in the present conventional solution-diffusion formulation**. The physically reconciled manufacturer-derived effective permeability is $A_w = 1.0232 \times 10^{-6}\ \text{m}/(\text{bar}\cdot\text{s}) = 3.6835\ \text{LMH/bar}$.
2. **Plant Grouping and Feed Flow:**
   The operational feed flow $Q_f = 30\ \text{m}^3/\text{h}$ is a reported feed condition in the paper. However, whether $30\ \text{m}^3/\text{h}$ represents the entire Nice Cotton plant intake or a specific parallel train grouping cannot be conclusively established from the source text alone without unverified assumptions. The parallel vessel count $N_v$ is therefore treated as a configurable design variable.
