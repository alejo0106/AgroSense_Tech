from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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


@app.get("/")
async def root():
    """Redirect root to the HTML dashboard view."""
    return RedirectResponse(url="/dashboard/view")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

