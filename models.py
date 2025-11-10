from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from database import Base


class Sensor(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    light = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SensorCreate(BaseModel):
    sensor_id: Optional[str] = None
    temperature: float
    humidity: float
    ph: float
    light: float
    timestamp: Optional[datetime] = None


class SensorOut(BaseModel):
    id: int
    sensor_id: Optional[str] = None
    temperature: float
    humidity: float
    ph: float
    light: float
    timestamp: Optional[datetime] = None
    # Pydantic v2: replace class-based Config and `orm_mode` with ConfigDict
    model_config = ConfigDict(from_attributes=True)
