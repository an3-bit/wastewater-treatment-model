"""
WaterTwin AI — FastAPI Backend Application
AI-Enabled Digital Twin for Fouling-Aware Optimization of Textile Wastewater Reuse.
"""

import asyncio
from contextlib import asynccontextmanager
import json
from typing import AsyncGenerator
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import WaterTwinException
from app.core.logging import logger
from app.dependencies.engine import get_engine
from app.services.result_repository import result_repository


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle events."""
    logger.info("Initializing WaterTwin AI Backend...")
    logger.info(f"Loaded Scientific Model: {settings.MODEL_VERSION} (Stage: {settings.STAGE_STATUS})")
    logger.info(f"Data Mode: {settings.DATA_MODE}")
    logger.info(f"Configured CORS Origins: {settings.CORS_ORIGINS}")

    # Validate authoritative results repository
    summary = result_repository.get_economic_summary()
    logger.info(f"Authoritative Water Impact: +{summary.water.additional_permeate_m3:,.1f} m³/yr (+{summary.water.water_increase_pct:.2f}%)")
    logger.info(f"Authoritative Integrated Value: KES {summary.economics.integrated_framework_value_kes_year:,.2f}/yr")
    logger.info("WaterTwin AI backend ready.")
    yield
    logger.info("Shutting down WaterTwin AI Backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for the WaterTwin AI Digital Twin and Techno-Economic Supervisory Optimization Engine.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(WaterTwinException)
async def watertwin_exception_handler(request: Request, exc: WaterTwinException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled error processing {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred processing your request.",
                "details": str(exc) if settings.APP_ENV == "development" else {},
            }
        },
    )


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


# WebSocket Streaming Endpoint
@app.websocket("/ws/twin")
async def websocket_twin_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time virtual-plant telemetry streaming.
    Pushes state updates every 2 seconds.
    """
    await websocket.accept()
    logger.info("WebSocket client connected to /ws/twin")
    engine = get_engine()

    try:
        while True:
            state = engine.get_state()
            rec = engine.get_maintenance_recommendation()
            forecast = engine.get_forecast(24)

            payload = {
                "timestamp": state.timestamp.isoformat(),
                "simulation_time_h": state.simulation_time_h,
                "Qf": state.feed_flow_m3_h,
                "Cf": state.feed_tds_mg_l,
                "T": state.temperature_c,
                "P1": state.p1_bar,
                "P2": state.p2_bar,
                "Qp": state.permeate_flow_m3_h,
                "recovery": state.recovery_percent,
                "SEC": state.sec_kwh_m3,
                "power": state.power_kw,
                "membrane_health": state.membrane_health_score_percent,
                "predicted_decline_24h": forecast.trajectory[-1].permeability_decline_percent,
                "recommendation": rec.recommended_action,
                "urgency": rec.urgency,
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from /ws/twin")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/", include_in_schema=False)
async def root_redirect():
    return {
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_v1": "/api/v1/health",
        "mode": settings.DATA_MODE,
        "model_version": settings.MODEL_VERSION,
    }
