"""
Endpoint de resumen para el dashboard (JSON).

Relación con otros módulos:
- Reutiliza `process_data` de `analytics.py` para calcular métricas.
- Sirve como backend JSON para frontends que no usan la plantilla HTML directa.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Sensor
from routers.analytics import process_data

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Devuelve conteo y métricas agregadas de todas las lecturas.

    Relación con el bloque siguiente: consulta ORM, transforma a dicts simples,
    llama a `process_data` y fusiona resultados con el conteo total.
    """
    sensors = db.query(Sensor).all()
    readings = [
        {"temperature": s.temperature, "humidity": s.humidity, "ph": s.ph, "light": s.light}
        for s in sensors
    ]
    if not readings:
        return {"count": 0, "metrics": {}}
    processed = process_data(readings)
    return {"count": len(readings), **processed}
