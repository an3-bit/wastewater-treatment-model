"""
Sensor Schemas for WaterTwin AI
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    id: str
    name: str
    description: str
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "NORMAL"
    quality: str = "GOOD"
    source: str = "virtual_plant"
    min_range: Optional[float] = None
    max_range: Optional[float] = None


class SensorListResponse(BaseModel):
    sensors: List[SensorReading]
    total_count: int
    data_mode: str = "virtual"


class SensorHistoryPoint(BaseModel):
    timestamp: datetime
    value: float
    quality: str = "GOOD"


class SensorHistoryResponse(BaseModel):
    sensor_id: str
    sensor_name: str
    unit: str
    history: List[SensorHistoryPoint]
    hours_retrieved: float
