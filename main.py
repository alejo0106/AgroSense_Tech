from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
from fastapi import FastAPI
from database import init_db
from routers import sensors, dashboard, analytics, dashboard_html


app = FastAPI(title="AgroSense Tech API")


def create_app() -> FastAPI:
    # Initialize DB and include routers
    init_db()
    app.include_router(sensors.router)
    app.include_router(dashboard.router)
    app.include_router(analytics.router)
    app.include_router(dashboard_html.router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

