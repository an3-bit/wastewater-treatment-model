# Model Version 1 Archive (Deprecated Pressure Convention)

## Provenance Notice
This directory preserves the full dataset, trained surrogate models, and optimization/fouling simulation outputs generated under **Model Version 1 (V1)**.

### Model V1 Specification:
- **Clean Water Permeability**: $A_w = 1.0232 \times 10^{-6}\,\text{m}/(\text{bar}\cdot\text{s}) = 1.0232 \times 10^{-11}\,\text{m}/(\text{Pa}\cdot\text{s}) = 3.6835\,\text{LMH/bar}$
- **Clean Active Layer Resistance**: $R_m = 1.097578 \times 10^{14}\,\text{m}^{-1}$ (at $25^\circ\text{C}$, $\mu = 8.90439 \times 10^{-4}\,\text{Pa}\cdot\text{s}$)
- **Calibrated Specific Fouling Resistance**: $r_{\text{spec}} = 1.804883 \times 10^{13}\,\text{m}^{-1}/(\text{m}^3/\text{m}^2)$
- **Pressure Convention**: Deprecated absolute formulation ($P_{\text{feed}} = 15.5132\,\text{bar(a)}, P_{\text{perm}} = 1.01325\,\text{bar(a)} \implies \Delta P = 14.50\,\text{bar}$).

### Purpose of Archive:
Retained strictly for historical reproducibility, model auditing, and cross-version sensitivity comparisons (Stages 1–6B). All production code and future stages use **Model Version 2.0 (`2.0-pressure-corrected`)**.
