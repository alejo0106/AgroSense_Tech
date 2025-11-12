"""
Punto de entrada de la aplicación FastAPI.

Relación con otros módulos:
- Llama a `init_db()` (database.py) para crear tablas si no existen.
- Registra routers: `sensors`, `analytics`, `dashboard`, `dashboard_html`.
- Redirige la raíz `/` hacia la vista HTML del dashboard.
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database import init_db
from routers import sensors, dashboard, analytics, dashboard_html


app = FastAPI(title="AgroSense Tech API")


def create_app() -> FastAPI:
    # Inicializa la BD y registra las rutas de la API y la vista HTML.
    init_db()
    app.include_router(sensors.router)
    app.include_router(dashboard.router)
    app.include_router(analytics.router)
    app.include_router(dashboard_html.router)
    return app


app = create_app()


@app.get("/")
async def root():
    """Redirige la raíz a la vista HTML del dashboard (/dashboard/view)."""
    return RedirectResponse(url="/dashboard/view")


if __name__ == "__main__":
    import uvicorn

    # Arranque de desarrollo con recarga automática
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

