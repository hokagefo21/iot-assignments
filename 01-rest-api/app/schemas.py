"""Pydantic-схемы: что API принимает на вход и что отдаёт в ответе.

Валидация входных данных происходит здесь автоматически: если тело запроса
не подходит под схему, FastAPI сам вернёт HTTP 422.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Устройства ----------

class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Temperature Sensor #1"])
    type: str = Field(min_length=1, max_length=50, examples=["temperature"])
    location: str | None = Field(default=None, max_length=100, examples=["Greenhouse, sector 1"])


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    location: str | None
    created_at: datetime


# ---------- Показания ----------

class ReadingCreate(BaseModel):
    # sensor_type обязателен и не может быть пустой строкой
    sensor_type: str = Field(min_length=1, max_length=50, examples=["temperature"])
    # strict=True: принимается только число (27.5 или 27), строка "27.5" и true/false будут отклонены
    value: float = Field(strict=True, examples=[27.5])
    unit: str | None = Field(default=None, max_length=20, examples=["C"])


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    sensor_type: str
    value: float
    unit: str | None
    created_at: datetime


class ReadingSaved(BaseModel):
    """Ответ на POST /readings: запись сохранена + результат правила автоматизации."""
    saved: bool
    reading: ReadingOut
    warning: str | None = None
    action: str | None = None
