"""Integration tests for /dashboard JSON endpoint to improve coverage."""
from fastapi.testclient import TestClient


def test_dashboard_json_empty(client: TestClient):
    r = client.get("/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
    assert data["metrics"] == {}


def test_dashboard_json_with_data(client: TestClient):
    for p in (
        {"sensor_id": "dj1", "temperature": 20.0, "humidity": 50.0, "ph": 6.5, "light": 200},
        {"sensor_id": "dj2", "temperature": 22.0, "humidity": 55.0, "ph": 6.7, "light": 220},
    ):
        assert client.post("/sensor-data", json=p).status_code == 200

    r = client.get("/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert "avg_temp" in data
    assert "metrics" in data
