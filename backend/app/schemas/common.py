"""
Common Pydantic Schemas and Envelopes
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiMeta(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = "2.0-pressure-corrected"
    stage: str = "8C-frozen"
    mode: str = "virtual-plant"
    scientific_status: str = "Industrial validation pending"


class ResponseEnvelope(BaseModel, Generic[DataT]):
    data: DataT
    meta: ApiMeta = Field(default_factory=ApiMeta)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
    meta: ApiMeta = Field(default_factory=ApiMeta)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "WaterTwin AI API"
    model_version: str = "2.0-pressure-corrected"
    mode: str = "virtual-plant"
    stage: str = "8C-frozen"
    uptime_seconds: float = 0.0
