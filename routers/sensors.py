"""
Endpoints de ingestión de datos de sensores.

Relación con otros módulos:
- Usa `models.Sensor` (ORM) para persistir la lectura recibida.
- Obtiene una sesión de DB con `database.get_db` (dependency de FastAPI).
- Complementa a `analytics.py` y `dashboard*` que leen estos datos para mostrar métricas.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import SensorCreate, Sensor
from database import get_db

router = APIRouter()


@router.post("/sensor-data")
async def receive_sensor(data: SensorCreate, db: Session = Depends(get_db)):
    """Recibe JSON de una lectura y la persiste en la base de datos configurada.

    Relación con el siguiente bloque: tras construir la entidad `Sensor`,
    se añade a la sesión y se hace `commit`; si todo sale bien, devolvemos éxito.
    Si hay error, hacemos rollback y propagamos 500.
    """
    ts = data.timestamp if data.timestamp else datetime.now(timezone.utc)
    sensor = Sensor(
        sensor_id=data.sensor_id,
        temperature=data.temperature,
        humidity=data.humidity,
        ph=data.ph,
        light=data.light,
        timestamp=ts,
    )
    try:
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
