"""
API v1 Router Aggregator
"""

from fastapi import APIRouter
from app.api.v1 import (
    economics,
    forecast,
    health,
    maintenance,
    membranes,
    policies,
    sensors,
    simulation,
    twin,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(twin.router, prefix="/twin", tags=["Digital Twin"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
api_router.include_router(membranes.router, prefix="/membranes", tags=["Membranes"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(economics.router, prefix="/economics", tags=["Economics"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
