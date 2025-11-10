from fastapi.testclient import TestClient
from main import app
import os

# ensure a clean DB
db_path = os.path.join(os.path.dirname(__file__), "..", "agrosense.db")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

client = TestClient(app)


def test_dashboard_flow():
    # ensure clean DB state
    from database import SessionLocal
    from models import Sensor
    db = SessionLocal()
    db.query(Sensor).delete()
    db.commit()
    db.close()

    payloads = [
        {"sensor_id": "s1", "temperature": 20.0, "humidity": 50.0, "ph": 6.5, "light": 200},
        {"sensor_id": "s2", "temperature": 22.0, "humidity": 55.0, "ph": 6.8, "light": 220},
    ]
    for p in payloads:
        r = client.post("/sensor-data", json=p)
        assert r.status_code == 200

    r = client.get("/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert "metrics" in data
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_returns_valid_data():
    """Verifica que el dashboard devuelva métricas procesadas correctamente"""
    response = client.get("/dashboard")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "avg_temp" in data or "metrics" in data
