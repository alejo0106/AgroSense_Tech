from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Sensor
from routers.analytics import process_data

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    sensors = db.query(Sensor).all()
    readings = [
        {"temperature": s.temperature, "humidity": s.humidity, "ph": s.ph, "light": s.light}
        for s in sensors
    ]
    if not readings:
        return {"count": 0, "metrics": {}}
    processed = process_data(readings)
    return {"count": len(readings), **processed}
