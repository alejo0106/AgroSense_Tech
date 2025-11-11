"""Integration tests for dashboard endpoints."""
from fastapi.testclient import TestClient


def test_dashboard_load(client: TestClient):
    # Ensure redirect root works
    r = client.get("/")
    assert r.status_code in (200, 307, 308)
    # Directly load the dashboard HTML view
    r2 = client.get("/dashboard/view")
    assert r2.status_code == 200
    assert "AgroSense Tech" in r2.text


def test_dashboard_empty_state(client: TestClient):
    # No data; analytics should return empty metric shapes
    r = client.get("/analytics")
    assert r.status_code == 200
    data = r.json()
    for k in ("temperature", "humidity", "ph", "light"):
        assert k in data
        # empty dicts on empty DB condition
        assert isinstance(data[k], dict)
        assert data[k] == {} or set(data[k].keys()).issubset({"avg", "max", "min"})
