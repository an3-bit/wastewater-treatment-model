# WaterTwin AI — Backend Application & Scientific Research Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/pytest-185%20passed-brightgreen.svg)](tests/)
[![Model Version](https://img.shields.io/badge/model-2.0--pressure--corrected-orange.svg)](src/ro_model/)
[![Scientific Status](https://img.shields.io/badge/stage-8C--frozen-purple.svg)](results/)

The `backend/` directory encapsulates both the **frozen first-principles scientific research engine** and the **FastAPI REST/WebSocket application layer** powering the **WaterTwin AI** digital twin for textile wastewater reuse.

---

## 1. Architectural Design & Boundaries

To preserve scientific reproducibility and production modularity, the backend strictly adheres to a **three-tier decoupled architecture**:

```
                  ┌─────────────────────────────────────────┐
                  │          Next.js Frontend Client        │
                  └────────────────────┬────────────────────┘
                                       │ REST / WebSocket
                  ┌────────────────────▼────────────────────┐
                  │       FastAPI Application Layer         │
                  │              (backend/app/)             │
                  │   • Routes & CORS                       │
                  │   • Pydantic v2 Request/Response Schemas│
                  │   • Typed Application Service Layer     │
                  │   • ResultRepository (Stage 8C cache)   │
                  │   • WaterTwinEngine Dependency Runtime  │
                  └────────────────────┬────────────────────┘
                                       │ Python Function Calls
                  ┌────────────────────▼────────────────────┐
                  │    Framework-Agnostic Scientific Engine │
                  │              (backend/src/)             │
                  │   • Mechanistic RO Model V2.0           │
                  │   • 6-Zone Axial Extended Kalman Filter │
                  │   • 24h Proactive Fouling Forecaster    │
                  │   • Predictive CIP Decision Support     │
                  │   • Techno-Economic Optimization & LCOW │
                  └─────────────────────────────────────────┘
```

### Strict Framework Independence Rule
- **`backend/src/`** contains **pure, framework-agnostic Python scientific code**. It does **NOT** import FastAPI, HTTP exceptions, Starlette, or frontend dependencies, and does not perform JSON serialization.
- **`backend/app/`** handles all web routing, dependency injection, CORS, request validation, Pydantic schemas, and HTTP error translation.

---

## 2. Directory Layout

```
backend/
├── app/                                 # FastAPI Web & Service Layer
│   ├── main.py                          # Application entrypoint, CORS, lifespan, WebSocket
│   ├── core/
│   │   ├── config.py                    # Environment settings, CORS parser, physical constants
│   │   ├── logging.py                   # Structured logging configuration
│   │   └── exceptions.py                # Domain HTTP exceptions & error handlers
│   │
│   ├── schemas/                         # Pydantic v2 domain & API schemas
│   │   ├── common.py                    # APIResponse envelope, Health, Error schemas
│   │   ├── twin.py                      # TwinState, TwinMetadata, SimulationAdvance schemas
│   │   ├── sensors.py                   # SensorReading, SensorHistory schemas
│   │   ├── membranes.py                 # MembraneZone, MembraneElement (15-element map)
│   │   ├── forecast.py                  # ForecastPoint, ForecastResponse schemas
│   │   ├── maintenance.py               # MaintenanceRecommendation, CIPHistory schemas
│   │   ├── economics.py                 # EconomicSummary, ValueDecomposition, Scenario schemas
│   │   ├── policies.py                  # PolicyComparison (Cases A–F) schemas
│   │   └── simulation.py                # Interactive simulation request & result schemas
│   │
│   ├── services/                        # Business logic & scientific adapters
│   │   ├── result_repository.py         # Cached loader for Stage 8C CSV/JSON artifacts
│   │   ├── twin_service.py              # Real-time state aggregation & metadata
│   │   ├── sensor_service.py            # 10-sensor telemetry feed & time-series history
│   │   ├── membrane_service.py          # 6-zone EKF state & 15-element visualization mapping
│   │   ├── forecast_service.py          # Multi-horizon (6–72h) lookahead generator
│   │   ├── maintenance_service.py       # Predictive CIP decision engine & lockout rules
│   │   ├── economics_service.py         # Stage 8C economic summaries & waterfall breakdowns
│   │   ├── policy_service.py            # Case A through Case F policy benchmarking
│   │   └── simulation_service.py        # Controlled interactive RO scenario analysis
│   │
│   ├── dependencies/
│   │   └── engine.py                    # WaterTwinEngine singleton runtime dependency
│   │
│   └── api/
│       ├── router.py                    # Aggregated /api/v1 router
│       └── v1/                          # 10 modular API route handlers
│           ├── health.py                # Health checks & uptime
│           ├── twin.py                  # State, metadata, clock advance/reset
│           ├── sensors.py               # 10-sensor telemetry & history
│           ├── membranes.py             # 6-zone EKF & 15-element visualization
│           ├── forecast.py              # Proactive fouling & hydraulic forecasting
│           ├── maintenance.py           # Predictive CIP decision support
│           ├── economics.py             # Techno-economic summary & value waterfall
│           ├── policies.py              # Case A through Case F benchmark comparison
│           └── simulation.py            # Scenario execution with bounds validation
│
├── src/                                 # Authoritative Scientific Engine
│   ├── ro_model/                        # Mechanistic RO solution-diffusion & thermodynamics
│   ├── state_estimation/                # 6-zone Extended Kalman Filter (EKF)
│   ├── prediction/                      # Proactive dynamic fouling projection
│   ├── supervisory/                     # Annual simulation benchmarks (Cases A–F)
│   ├── fouling/                         # Stage 6 fouling kinetics & resistance equations
│   ├── economics/                       # LCOW calculation, tariffs, chemical costs
│   └── ml/                              # Neural surrogate verification & safeguards
│
├── config/                              # YAML configuration files for models & simulation
├── scripts/                             # Standalone scientific runners & audit scripts
├── tests/                               # Complete test suite (185 tests)
├── results/                             # Frozen Stage 7, 8, 8B, 8C artifacts & figures
├── data/                                # Synthetic textile wastewater feed profiles
├── models/                              # Pre-trained ML surrogate weights & configs
├── notebooks/                           # Research Jupyter notebooks
├── pyproject.toml                       # Python package build & pytest configuration
├── requirements.txt                     # Backend dependencies
├── .env.example                         # Environment variable template
└── .env                                 # Local development environment configuration
```

---

## 3. Authoritative Scientific Engine (Frozen Research)

The underlying scientific engine is frozen at **Model V2.0** and **Stage 8C**. The model incorporates the following physical constants and mechanics:

### 3.1. Mechanistic RO Parameters (Model V2.0)
- **Water Permeability ($A_w$):** $9.446312125982804 \times 10^{-12}\text{ m}/(\text{Pa}\cdot\text{s})$
- **Clean Membrane Resistance ($R_{m,clean}$):** $1.1888677444880217 \times 10^{14}\text{ m}^{-1}$
- **Specific Cake Resistance ($r_{spec}$):** $1.954988085694205 \times 10^{13}\text{ m}^{-1}/(\text{m}^3/\text{m}^2)$
- **Solute Permeability ($A_s$):** $1.7827 \times 10^{-8}\text{ m}/\text{s}$
- **Thermodynamic Corrections:** Temperature-dependent viscosity $\mu(T)$ and osmotic pressure $\pi(C, T)$ according to van 't Hoff equations with pressure-corrected net driving pressure (NDP).

### 3.2. 6-Zone Extended Kalman Filter (EKF)
- **Observability:** Axial spatial discretization into **6 authoritative state zones** (Stage 1 Lead, Middle, Tail; Stage 2 Lead, Middle, Tail), satisfying SVD rank 4–5 observability under standard skid instrumentation.
- **Visualization Mapping:** The 15 membrane elements displayed in the UI are mapped directly from the 6 EKF zones with the flag `estimated_from_zone: true` to clearly disclose estimator resolution.

### 3.3. Stage 8C Frozen Techno-Economic Results
The annual simulation study across 8,000 operating hours yielded the authoritative baseline vs. digital twin results:

| Metric | Baseline (Case A) | WaterTwin Digital Twin (Case E) | Delta / Impact |
| :--- | :--- | :--- | :--- |
| **Annual Useful Permeate** | $65,279.7\text{ m}^3/\text{yr}$ | $109,737.3\text{ m}^3/\text{yr}$ | **$+44,457.6\text{ m}^3/\text{yr}$ ($+68.10\%$)** |
| **Total Annual Electricity** | $65,054.4\text{ kWh/yr}$ | $102,583.2\text{ kWh/yr}$ | **$+57.69\%$** (due to $+68.1\%$ water volume) |
| **Specific Energy (SEC)** | $0.9965\text{ kWh/m}^3$ | $0.9348\text{ kWh/m}^3$ | **$-6.19\%$ reduction** in energy per $\text{m}^3$ |
| **Net Economic Value** | $\text{KES } 7.11\text{M/yr}$ | $\text{KES } 11.50\text{M/yr}$ | **$+\text{KES } 4,391,948.14/\text{yr}$** ($+61.79\%$) |
| **Pure Prediction Value ($D-C$)** | $-$ | $-$ | **$+\text{KES } 424,164.72/\text{yr}$ ($9.66\%$)** |
| **Condition-Based Value ($C-B$)** | $-$ | $-$ | **$+\text{KES } 3,902,797.57/\text{yr}$ ($88.86\%$)** |
| **Dynamic Pressure MPC ($E-D$)** | $-$ | $-$ | **$+\text{KES } 2,782.42/\text{yr}$ ($0.06\%$)** |
| **Treatment LCOW** | $\text{KES } 19.11/\text{m}^3$ | $\text{KES } 23.20/\text{m}^3$ | Competes favorably against $\text{KES } 120/\text{m}^3$ grid |

---

## 4. REST & WebSocket API Specification

All REST endpoints are prefixed under `/api/v1`.

### 4.1. Endpoint Inventory

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status, model version, and mode |
| `GET` | `/api/v1/twin/metadata` | Frozen model metadata, estimator specs, and caveats |
| `GET` | `/api/v1/twin/state` | Current digital twin telemetry, recovery, SEC, and health |
| `POST` | `/api/v1/twin/advance` | Advance virtual simulation clock by $N$ hours (demo mode) |
| `POST` | `/api/v1/twin/reset` | Reset virtual simulation clock to baseline ($t = 0$) |
| `GET` | `/api/v1/sensors` | Standard 10-sensor skid telemetry readings |
| `GET` | `/api/v1/sensors/history` | Historical time-series telemetry for charting (`sensor_id`, `hours`) |
| `GET` | `/api/v1/membranes/zones` | Authoritative 6-zone EKF fouling resistance & health |
| `GET` | `/api/v1/membranes/elements` | 15-element visual mapped health from 6 EKF zones |
| `GET` | `/api/v1/forecast` | Proactive dynamic forecast (horizon: 6, 12, **24**, 48, 72h) |
| `GET` | `/api/v1/maintenance/recommendation` | Predictive CIP decision support with lockout enforcement |
| `GET` | `/api/v1/maintenance/history` | Historical CIP logs, pre/post clean resistance, downtime |
| `GET` | `/api/v1/economics/summary` | Authoritative Stage 8C techno-economic summary |
| `GET` | `/api/v1/economics/value-decomposition` | Mathematical value waterfall ($B-A, C-B, D-C, E-D, E-A$) |
| `GET` | `/api/v1/economics/scenarios` | Conservative, Base, and Favourable sensitivity analysis |
| `GET` | `/api/v1/policies` | Policy matrix benchmark across Case A through Case F (Oracle) |
| `POST` | `/api/v1/simulation/run` | Controlled interactive scenario analysis with boundary checks |
| `WS` | `/ws/twin` | Real-time WebSocket telemetry stream (virtual plant pulse) |

### 4.2. API Response Envelope

Standard successful responses are returned within a structured envelope:

```json
{
  "data": {
    "timestamp": "2026-09-09T16:00:00Z",
    "feed_flow_m3_h": 25.0,
    "recovery_percent": 75.2,
    "sec_kwh_m3": 0.9348,
    "membrane_health_score": 88.4
  },
  "meta": {
    "timestamp": "2026-09-09T16:00:00Z",
    "model_version": "2.0-pressure-corrected",
    "stage": "8C-frozen",
    "mode": "virtual-plant"
  }
}
```

---

## 5. Environment Configuration

Create a `.env` file in `backend/` based on `.env.example`:

```ini
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

# Comma-separated or JSON list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

MODEL_VERSION=2.0-pressure-corrected
DATA_MODE=virtual
DEFAULT_FORECAST_HORIZON_H=24
```

---

## 6. Installation & Execution

### 6.1. Prerequisites
- Python 3.11+
- `venv` or `conda`

### 6.2. Setup Virtual Environment

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate

# Upgrade pip and install dependencies:
pip install -r requirements.txt
```

### 6.3. Run FastAPI Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 7. Automated Testing Suite

The backend contains **185 passing automated tests**, spanning the 174 regression tests for the scientific engine and 11 integration tests for FastAPI:

```bash
cd backend
python -m pytest tests/ -v
```

### Test Suite Breakdown:
1. **Mechanistic Physics & Thermodynamics (`test_model_v2.py`, `test_ro_physics.py`):** Mass conservation, pressure drop equations, osmotic pressure, temperature correction.
2. **State Estimation & EKF (`test_stage7_ekf.py`):** 6-zone state convergence, SVD observability, covariance bounds.
3. **Supervisory Optimization & Audits (`test_stage8_economics.py`, `test_stage8b_audit.py`, `test_stage8c_freeze.py`):** Policy simulation math, tariff ledgers, CIP cost robustness.
4. **FastAPI Application & Schemas (`test_fastapi_backend.py`):** Health endpoints, metadata verification, Pydantic serialization, Stage 8C value fidelity, simulation bounds checking.

---

## 8. Scientific Integrity & Communication Guidelines

When communicating model outputs through the API or frontend, the following guidelines must be maintained:

1. **Total Electricity vs. Specific Energy (SEC):**
   - Total annual electricity **increases by $+57.69\%$** because the plant produces **$+68.10\%$ more water**.
   - Specific Energy Consumption (SEC) **decreases by $-6.19\%$** ($0.9965 \to 0.9348\text{ kWh/m}^3$).
   - *Never state that total plant energy decreased.*
2. **Economic Attribution:**
   - The total integrated benefit is $\text{KES } 4,391,948.14/\text{yr}$ ($E-A$).
   - The proactive prediction benefit alone is $\text{KES } 424,164.72/\text{yr}$ ($D-C$, $9.66\%$).
   - Dynamic Pressure MPC adds $\text{KES } 2,782.42/\text{yr}$ ($E-D$, $0.06\%$) and is classified as a research feature rather than a commercial driver.
3. **Operational Mode:**
   - Always disclose **"Virtual Plant"** or **"Simulation Mode"** until pilot-scale hardware sensor integration is deployed.
   - Outputs represent **"Decision Support"** recommendations for operators.

---

## 9. License

MIT License. Developed by the Antigravity Research Team.
