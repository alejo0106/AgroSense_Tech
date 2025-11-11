"""Integration tests for /analytics consistency."""
from fastapi.testclient import TestClient


def test_analytics_endpoint_consistency(client: TestClient):
    # Seed two readings through API
    for p in (
        {"sensor_id": "i1", "temperature": 20.0, "humidity": 50.0, "ph": 6.5, "light": 200},
        {"sensor_id": "i2", "temperature": 22.0, "humidity": 55.0, "ph": 6.7, "light": 220},
    ):
        assert client.post("/sensor-data", json=p).status_code == 200

    r = client.get("/analytics")
    assert r.status_code == 200
    data = r.json()
    # Should be nested metrics dict
    assert set(data.keys()) == {"temperature", "humidity", "ph", "light"}
    assert data["temperature"]["max"] >= data["temperature"]["min"]
    assert data["humidity"]["avg"] >= 0
