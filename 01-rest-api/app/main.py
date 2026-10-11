"""REST API для IoT-системы «Умная теплица».

Путь данных: виртуальный датчик (Postman) -> REST API -> база данных -> JSON-ответ клиенту.
Запуск: uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .rules import check_rules
from .schemas import DeviceCreate, DeviceOut, ReadingCreate, ReadingOut, ReadingSaved


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Создаём таблицы при старте, если их ещё нет (то же, что migrations/001_init.sql)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="IoT Greenhouse API",
    description="Приём показаний виртуальных датчиков теплицы, хранение и история измерений.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------- Понятный формат ошибок валидации (HTTP 422) ----------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # loc выглядит как ("body", "value"): берём имя поля без префикса
        field = ".".join(str(part) for part in err["loc"] if part != "body")
        errors.append({"field": field or "body", "error": err["msg"]})
    return JSONResponse(
        status_code=422,
        content={"message": "Validation failed", "errors": errors},
    )


def get_device_or_404(device_id: int, db: Session) -> models.Device:
    device = db.get(models.Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return device


# ---------- Часть A. Устройства ----------

@app.post("/api/devices", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, tags=["devices"])
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    device = models.Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@app.get("/api/devices", response_model=list[DeviceOut], tags=["devices"])
def list_devices(db: Session = Depends(get_db)):
    return db.scalars(select(models.Device).order_by(models.Device.id)).all()


@app.get("/api/devices/{device_id}", response_model=DeviceOut, tags=["devices"])
def get_device(device_id: int, db: Session = Depends(get_db)):
    return get_device_or_404(device_id, db)


# ---------- Часть B + C. Показания и автоматизация ----------

@app.post(
    "/api/devices/{device_id}/readings",
    response_model=ReadingSaved,
    status_code=status.HTTP_201_CREATED,
    tags=["readings"],
)
def create_reading(device_id: int, payload: ReadingCreate, db: Session = Depends(get_db)):
    get_device_or_404(device_id, db)  # устройство должно существовать, иначе 404

    reading = models.SensorReading(device_id=device_id, **payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)

    warning, action = check_rules(reading.sensor_type, reading.value)
    return ReadingSaved(saved=True, reading=reading, warning=warning, action=action)


@app.get("/api/devices/{device_id}/readings", response_model=list[ReadingOut], tags=["readings"])
def list_readings(
    device_id: int,
    limit: int = Query(default=100, ge=1, le=1000, description="Сколько последних записей вернуть"),
    db: Session = Depends(get_db),
):
    get_device_or_404(device_id, db)
    stmt = (
        select(models.SensorReading)
        .where(models.SensorReading.device_id == device_id)
        .order_by(models.SensorReading.created_at.desc(), models.SensorReading.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


@app.get("/", include_in_schema=False)
def root():
    return {"service": "IoT Greenhouse API", "docs": "/docs"}
