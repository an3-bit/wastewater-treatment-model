# WaterTwin AI — Backend Application & Scientific Engine

## 1. Overview
The `backend/` package houses the entire Python-based scientific research engine and the FastAPI application layer for the **WaterTwin AI** digital twin.

## 2. Directory Layout
```
backend/
├── app/                            # FastAPI Application Layer
│   ├── main.py                     # App entry point, CORS, WebSocket
│   ├── core/                       # App settings, logging, exceptions
│   ├── schemas/                    # Pydantic v2 schemas for all API payloads
│   ├── services/                   # Business logic, ResultRepository, TwinService
│   ├── dependencies/               # Dependency injection & WaterTwinEngine runtime
│   └── api/v1/                     # 17 REST API Endpoints
│       ├── health.py
│       ├── twin.py
│       ├── sensors.py
│       ├── membranes.py
│       ├── forecast.py
│       ├── maintenance.py
│       ├── economics.py
│       ├── policies.py
│       └── simulation.py
│
├── src/                            # Framework-Agnostic Scientific Engine
│   ├── ro_model/                   # Mechanistic RO physics & thermodynamics
│   ├── state_estimation/           # 6-zone Extended Kalman Filter (EKF)
│   ├── prediction/                 # Proactive fouling forecasting
│   ├── supervisory/                # Stage 8C techno-economic simulators
│   ├── fouling/                    # Stage 6 fouling kinetics & models
│   ├── economics/                  # LCOW, cost models, tariff ledgers
│   └── ml/                         # Neural network surrogates & safeguards
│
├── config/                         # YAML configuration files
├── scripts/                        # Scientific simulation runners
├── tests/                          # Complete pytest regression & API suite
├── results/                        # Frozen Stage 7 & 8C benchmark tables/figures
├── pyproject.toml                  # Build & pytest configuration
└── requirements.txt                # Python dependencies
```

## 3. Strict Architectural Boundary
- **`backend/src/`** is strictly **framework-independent** (zero imports of FastAPI, HTTP responses, or React).
- **`backend/app/`** contains all web, serialization, and FastAPI routing logic.

## 4. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health, model version, and uptime |
| `GET` | `/api/v1/twin/metadata` | Frozen model metadata, estimator architecture |
| `GET` | `/api/v1/twin/state` | Current digital twin telemetry, recovery, SEC, health |
| `POST` | `/api/v1/twin/advance` | Advance virtual simulation clock by specified hours |
| `POST` | `/api/v1/twin/reset` | Reset simulation state to clean baseline |
| `GET` | `/api/v1/sensors` | Standard 10-sensor skid telemetry readings |
| `GET` | `/api/v1/sensors/history` | Historical time-series telemetry for charts |
| `GET` | `/api/v1/membranes/zones` | Authoritative 6-zone EKF fouling states |
| `GET` | `/api/v1/membranes/elements` | 15-element visualization mapping from 6 EKF zones |
| `GET` | `/api/v1/forecast` | Dynamic state look-ahead forecast (default 24h) |
| `GET` | `/api/v1/maintenance/recommendation` | Predictive CIP cleaning decision support |
| `GET` | `/api/v1/maintenance/history` | Historical CIP logs and downtime restoration |
| `GET` | `/api/v1/economics/summary` | Authoritative Stage 8C techno-economic summary |
| `GET` | `/api/v1/economics/value-decomposition` | Mathematical value waterfall ($B-A, C-B, D-C, E-D, E-A$) |
| `GET` | `/api/v1/economics/scenarios` | Conservative, Base, and Favourable sensitivity |
| `GET` | `/api/v1/policies` | Benchmark matrix across Case A through Case F (Oracle) |
| `POST` | `/api/v1/simulation/run` | Interactive scenario simulation with physical bounds |
| `WS` | `/ws/twin` | Real-time virtual plant telemetry streaming |

## 5. Running Tests

```bash
cd backend
python -m pytest tests/ -v
```
All 185 tests must pass (174 scientific tests + 11 API integration tests).
