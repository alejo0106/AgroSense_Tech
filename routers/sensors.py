from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import SensorCreate, Sensor
from database import get_db

router = APIRouter()


@router.post("/sensor-data")
async def receive_sensor(data: SensorCreate, db: Session = Depends(get_db)):
    """Receive sensor JSON and persist to the configured database via SQLAlchemy."""
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
