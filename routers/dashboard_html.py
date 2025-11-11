from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Sensor
from routers.analytics import process_data

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard/view", response_class=HTMLResponse)
async def get_dashboard(request: Request, db: Session = Depends(get_db)):
    """Render the dashboard template and obtain metrics directly from the DB (no HTTP calls)."""
    sensors = db.query(Sensor).all()
    readings = [
        {"temperature": s.temperature, "humidity": s.humidity, "ph": s.ph, "light": s.light}
        for s in sensors
    ]
    if not readings:
        data = {}
    else:
        processed = process_data(readings)
        # processed contains top-level aggregates and nested 'metrics'
        data = processed.get("metrics", {})

    # Starlette >=0.49 expects request as first argument
    return templates.TemplateResponse(request, "dashboard.html", {"data": data})
