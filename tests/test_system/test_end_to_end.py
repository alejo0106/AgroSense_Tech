"""System (end-to-end) tests combining ingestion and analytics metrics."""
from fastapi.testclient import TestClient


def test_end_to_end_ingest_and_metrics(client: TestClient):
    # Ingest multiple readings
    readings = [
        {"sensor_id": "sys1", "temperature": 21.0, "humidity": 55.0, "ph": 6.6, "light": 210},
        {"sensor_id": "sys2", "temperature": 23.0, "humidity": 58.0, "ph": 6.7, "light": 230},
        {"sensor_id": "sys3", "temperature": 22.0, "humidity": 57.0, "ph": 6.8, "light": 220},
    ]
    for r in readings:
        assert client.post("/sensor-data", json=r).status_code == 200

    # Fetch analytics and ensure aggregated ranges cover inserted values
    a = client.get("/analytics")
    assert a.status_code == 200
    data = a.json()
    temps = [v["temperature"] for v in readings]
    # Nested metrics present
    assert data["temperature"]["max"] == max(temps)
    assert data["temperature"]["min"] == min(temps)
    assert data["temperature"]["avg"] >= min(temps)
    assert data["temperature"]["avg"] <= max(temps)
