# WaterTwin AI — Digital Twin for Textile Wastewater Reuse

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com)
[![Next.js 15](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Scientific Tests](https://img.shields.io/badge/pytest-185%20passed-brightgreen.svg)](backend/tests/)

---

## 1. Project Purpose & Architecture

**WaterTwin AI** is an AI-enabled digital twin and supervisory optimization platform for industrial membrane bioreactor – reverse osmosis (MBR–RO) textile wastewater treatment plants.

The system integrates a **frozen, first-principles mechanistic RO model (Model V2.0)**, an **authoritative 6-zone Extended Kalman Filter (EKF)** state estimator, and a **24-hour predictive techno-economic optimization framework (Stage 8C)** with a modern **Next.js** dashboard via a high-performance **FastAPI** backend.

```
Next.js Frontend (Port 3000)
       ↓ REST (/api/v1) / WebSocket (/ws/twin)
FastAPI Backend (Port 8000)
       ↓
Application Services & Result Repository
       ↓
WaterTwin Scientific Engine (backend/src/)
  ├── RO Model V2.0 (Mechanistic solution-diffusion & thermodynamics)
  ├── 6-Zone Axial EKF (Dynamic fouling resistance state estimation)
  ├── 24-Hour Proactive Predictive Forecaster (Kinetics forward projection)
  ├── Predictive Maintenance & CIP Decision Support (Lockout enforcement)
  └── Stage 8C Techno-Economic Intelligence (+68.10% water, -6.19% SEC)
```

---

## 2. Authoritative Frozen Scientific Results (Stage 8C)

| Performance / Financial Metric | Baseline Operation (Case A) | WaterTwin Digital Twin (Case E) | Delta / Impact | Scientific Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Annual Useful Permeate** | $65,279.7\text{ m}^3/\text{yr}$ | $109,737.3\text{ m}^3/\text{yr}$ | **$+44,457.6\text{ m}^3/\text{yr}$ ($+68.10\%$)** | $+68.10\%$ more water reclaimed |
| **Total Annual Electricity** | $65,054.4\text{ kWh/yr}$ | $102,583.2\text{ kWh/yr}$ | **$+57.69\%$** | Increases because $68.10\%$ more water produced |
| **Specific Energy (SEC)** | $0.9965\text{ kWh/m}^3$ | $0.9348\text{ kWh/m}^3$ | **$-6.19\%$ reduction** | Energy required per $\text{m}^3$ decreases |
| **Integrated Net Value** | $\text{KES } 7.11\text{M/yr}$ | $\text{KES } 11.50\text{M/yr}$ | **$+\text{KES } 4,391,948.14/\text{yr}$** | Full digital twin framework value |
| **Pure Prediction Value (D-C)** | $-$ | $-$ | **$+\text{KES } 424,164.72/\text{yr}$ ($9.66\%$)** | Look-ahead proactive CIP timing |
| **Condition-Based Value (C-B)** | $-$ | $-$ | **$+\text{KES } 3,902,797.57/\text{yr}$ ($88.86\%$)** | Adaptive fouling-triggered CIP |
| **Dynamic Pressure MPC (E-D)** | $-$ | $-$ | **$+\text{KES } 2,782.42/\text{yr}$ ($0.06\%$)** | Marginal continuous pressure trim |
| **Treatment LCOW** | $\text{KES } 19.11/\text{m}^3$ | $\text{KES } 23.20/\text{m}^3$ | **$\text{KES } 23.20/\text{m}^3$** | Substantially below $\text{KES } 120/\text{m}^3$ tariff |

> [!IMPORTANT]
> **Scientific Integrity & Validation Disclaimer:**
> All telemetry, estimator states, and economic figures represent **Virtual Plant** simulations on synthetic industrial disturbance profiles. Pilot-scale industrial hardware validation is pending. Recommendations are provided for **Operator Decision Support** and do not autonomous override plant safety PLCs.

---

## 3. Target Repository Structure

```
wastewater/
├── backend/                        # Complete Python scientific engine & FastAPI application
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, WebSocket /ws/twin
│   │   ├── core/                   # Config, logging, exceptions
│   │   ├── schemas/                # Pydantic v2 domain & API schemas
│   │   ├── services/               # Typed application services & ResultRepository
│   │   ├── dependencies/           # WaterTwinEngine runtime dependency
│   │   └── api/v1/                 # 17 REST API endpoints
│   │
│   ├── src/                        # Framework-independent scientific engine
│   │   ├── ro_model/               # Solution-diffusion mechanics & thermodynamics
│   │   ├── state_estimation/       # 6-Zone EKF, observability, noise models
│   │   ├── prediction/             # Look-ahead dynamic state forecasting
│   │   ├── supervisory/            # Stage 8C annual & audit simulators
│   │   ├── fouling/                # Stage 6 fouling kinetics & calibration
│   │   ├── economics/              # LCOW, cost configurations, tariffs
│   │   └── ml/                     # ML surrogates & domain safeguards
│   │
│   ├── results/                    # Authoritative Stage 7, 8, 8B, 8C artifacts & figures
│   ├── tests/                      # 185 pytest unit, regression, & API tests
│   ├── requirements.txt            # Python dependencies
│   ├── pyproject.toml              # Build & test configuration
│   └── .env.example
│
├── frontend/                       # Next.js 15 Tailwind & React Dashboard
│   ├── src/
│   │   ├── app/                    # Next.js App Router pages
│   │   ├── components/             # Reusable UI components & charts
│   │   ├── services/api/           # Centralized TypeScript API client
│   │   └── types/                  # TypeScript interface contracts
│   ├── package.json
│   └── .env.local.example
│
└── README.md
```

---

## 4. Quick Start & Execution

### 4.1. Start FastAPI Backend

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Unix:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Backend API:** `http://localhost:8000`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Health Endpoint:** `http://localhost:8000/api/v1/health`

### 4.2. Start Next.js Frontend

```bash
cd frontend
npm install
npm run dev
```
- **Frontend URL:** `http://localhost:3000`
- **Dashboard Overview:** `http://localhost:3000/dashboard`

---

## 5. Automated Test Suites

To execute the complete test suite (174 scientific tests + 11 API integration tests):

```bash
cd backend
python -m pytest tests/ -v
```

To run frontend build and typecheck verification:

```bash
cd frontend
npm run build
```

---

## 6. License & Citation

MIT License. Developed by the Antigravity Research Team.
