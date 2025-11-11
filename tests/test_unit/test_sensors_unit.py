"""Unit tests for /sensor-data endpoint (schema-level behaviour)."""
import pytest
from fastapi.testclient import TestClient


def test_sensor_data_post_valid(client: TestClient):
    payload = {
        "sensor_id": "ut-1",
        "temperature": 23.5,
        "humidity": 60.0,
        "ph": 6.7,
        "light": 350,
    }
    r = client.post("/sensor-data", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "success"


@pytest.mark.parametrize(
    "payload",
    [
        {},  # empty body
        {"temperature": 22.1},  # missing required fields
        {"sensor_id": "x", "temperature": "hot", "humidity": 50, "ph": 6.5, "light": 200},  # bad type
    ],
)
def test_sensor_data_post_invalid(client: TestClient, payload):
    r = client.post("/sensor-data", json=payload)
    # FastAPI/Pydantic returns 422 for validation errors
    assert r.status_code in (400, 422)
