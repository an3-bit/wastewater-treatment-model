"""
Forecast Service
Service layer for look-ahead dynamic state forecasting (6, 12, 24, 48, 72h).
"""

from app.dependencies.engine import WaterTwinEngine, get_engine
from app.schemas.forecast import ForecastResponse


class ForecastService:
    def __init__(self, engine: WaterTwinEngine = None):
        self.engine = engine or get_engine()

    def get_forecast(self, horizon_hours: int = 24) -> ForecastResponse:
        # Validate horizon
        allowed = [6, 12, 24, 48, 72]
        if horizon_hours not in allowed:
            # Snap to closest
            closest = min(allowed, key=lambda x: abs(x - horizon_hours))
            horizon_hours = closest
        return self.engine.get_forecast(horizon_hours=horizon_hours)


forecast_service = ForecastService()
