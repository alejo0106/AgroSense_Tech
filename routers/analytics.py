from statistics import mean
from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Sensor

router = APIRouter()


def process_data(sensor_data: List[Dict]) -> Dict:
    """
    Procesa una lista de lecturas de sensores y calcula métricas básicas.
    Cada elemento debe ser un diccionario con keys:
    'temperature', 'humidity' y 'light'.

    Devuelve top-level avg/max/min y una clave `metrics` anidada para compatibilidad.
    """
    if not sensor_data:
        return {"error": "No hay datos disponibles"}

    temperatures = [d.get("temperature", 0) for d in sensor_data]
    humidities = [d.get("humidity", 0) for d in sensor_data]
    lights = [d.get("light", 0) for d in sensor_data]

    avg_temp = round(mean(temperatures), 1)
    avg_humidity = round(mean(humidities), 1)
    max_light = max(lights)
    min_light = min(lights)

    metrics = {
        "avg_temp": avg_temp,
        "avg_humidity": avg_humidity,
        "max_light": max_light,
        "min_light": min_light,
    }

    def make_nested(arr):
        return {"avg": round(mean(arr), 1), "max": max(arr), "min": min(arr)}

    metrics["metrics"] = {
        "temperature": make_nested(temperatures) if temperatures else {},
        "humidity": make_nested(humidities) if humidities else {},
        "light": make_nested(lights) if lights else {},
    }

    return metrics


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Return processed metrics for all sensor readings in the DB."""
    sensors = db.query(Sensor).all()
    readings = [
        {"temperature": s.temperature, "humidity": s.humidity, "ph": s.ph, "light": s.light}
        for s in sensors
    ]
    if not readings:
        # return empty metric shapes
        return {
            "temperature": {},
            "humidity": {},
            "ph": {},
            "light": {},
        }
    processed = process_data(readings)
    # process_data returns a 'metrics' nested dict with temperature/humidity/light
    return processed.get("metrics", {})
