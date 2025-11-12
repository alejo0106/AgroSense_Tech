"""
Modelos de datos y esquemas (SQLAlchemy + Pydantic).

Relación con otros módulos:
- `database.Base` se usa como clase base para los modelos ORM.
- Los routers crean/consultan instancias de `Sensor` mediante sesiones de `database.get_db`.
- Los esquemas Pydantic (`SensorCreate`, `SensorOut`) definen el shape de entrada/salida
  en los endpoints, validando y serializando datos.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from database import Base


class Sensor(Base):
    """Entidad persistente para lecturas de sensores.

    Cada fila representa una lectura (temperatura, humedad, pH y luz), con un
    timestamp de creación en servidor. Este modelo mapea a la tabla `sensor_data`.
    """
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    light = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SensorCreate(BaseModel):
    """Esquema de entrada usado por `POST /sensor-data`."""
    sensor_id: Optional[str] = None
    temperature: float
    humidity: float
    ph: float
    light: float
    timestamp: Optional[datetime] = None


class SensorOut(BaseModel):
    """Esquema de salida típico al devolver lecturas persistidas."""
    id: int
    sensor_id: Optional[str] = None
    temperature: float
    humidity: float
    ph: float
    light: float
    timestamp: Optional[datetime] = None
    # Pydantic v2: replace class-based Config and `orm_mode` with ConfigDict
    model_config = ConfigDict(from_attributes=True)
