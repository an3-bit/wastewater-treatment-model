"""
Core Configuration for WaterTwin AI Backend
Handles environment variables, CORS origins, and frozen model constants.
"""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "WaterTwin AI API"
    VERSION: str = "1.0.0"

    # Scientific Frozen Model Configuration
    MODEL_VERSION: str = "2.0-pressure-corrected"
    DATA_MODE: str = "virtual"  # "virtual" or "live"
    DEFAULT_FORECAST_HORIZON_H: int = 24
    STAGE_STATUS: str = "8C-frozen"
    ESTIMATOR_NAME: str = "6-Zone EKF"
    FOULING_ZONES_COUNT: int = 6
    DISPLAY_ELEMENTS_COUNT: int = 15

    # Frozen Physical Constants
    AW_M_PA_S: float = 9.446312125982804e-12
    RM_CLEAN_M_INV: float = 1.1888677444880217e14
    RSPEC_M_INV_PER_M3_M2: float = 1.954988085694205e13
    AS_M_S: float = 1.7827e-8

    # Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    RESULTS_DIR: Path = BASE_DIR / "results"
    STAGE8C_DIR: Path = RESULTS_DIR / "stage8c"
    CONFIG_DIR: Path = BASE_DIR / "config"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
