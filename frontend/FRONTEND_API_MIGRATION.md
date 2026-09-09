# WaterTwin AI — Frontend API Migration Document

## 1. Overview
This document outlines the migration of the WaterTwin Next.js frontend from static mock data to the authoritative FastAPI backend (`/api/v1`).

## 2. Architecture & Data Flow
```
Next.js Frontend (Port 3000)
       ↓ fetch / WebSocket
FastAPI Backend (Port 8000 /api/v1)
       ↓
Application Service Layer
       ↓
Scientific Engine (Model V2.0, 6-Zone EKF, Stage 8C Economics)
```

## 3. Endpoints & Component Mapping

| Frontend Page / Feature | API Endpoint | Data Mode | Status |
| :--- | :--- | :--- | :--- |
| **Executive Overview** | `GET /twin/state`, `GET /economics/summary`, `GET /maintenance/recommendation` | API-Backed | Migrated |
| **Live Digital Twin** | `GET /twin/state`, `GET /sensors`, `WS /ws/twin` | API-Backed | Migrated |
| **Membrane Health** | `GET /membranes/zones`, `GET /membranes/elements` | API-Backed | Migrated |
| **Telemetry & Sensors** | `GET /sensors`, `GET /sensors/history` | API-Backed | Migrated |
| **Predictive Forecast** | `GET /forecast?hours=24` (6, 12, 24, 48, 72h) | API-Backed | Migrated |
| **Maintenance & CIP** | `GET /maintenance/recommendation`, `GET /maintenance/history` | API-Backed | Migrated |
| **Techno-Economics** | `GET /economics/summary`, `GET /economics/value-decomposition`, `GET /economics/scenarios` | API-Backed | Migrated |
| **Supervisory Policies** | `GET /policies` | API-Backed | Migrated |
| **Scenario Simulation** | `POST /simulation/run` | API-Backed | Migrated |

## 4. Scientific Truth & Disclosure Standards
- **Virtual Plant Badge**: Clear disclosure that the system operates in virtual plant mode with industrial validation pending.
- **6-Zone EKF vs 15 Elements**: 15 elements are explicitly marked as mapped from the 6 authoritative EKF zones (`estimated_from_zone: true`), rather than 15 independent hardware sensors.
- **Energy Display**: Distinguishes between total electricity increase ($+57.69\%$) and specific energy reduction ($-6.19\%$).
- **Economic Attribution**:
  - Integrated Framework Value: $\approx \text{KES } 4.39\text{M/year}$ vs fixed baseline
  - Pure Prediction Value: $\approx \text{KES } 424\text{k/year}$
  - MPC Value: $\approx \text{KES } 2.8\text{k/year}$ ($0.06\%$)
  - Condition-Based Value: $\approx \text{KES } 3.90\text{M/year}$ ($88.86\%$)
