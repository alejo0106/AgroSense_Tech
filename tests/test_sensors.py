from fastapi.testclient import TestClient
from main import app
import os

# ensure a clean DB for tests
db_path = os.path.join(os.path.dirname(__file__), "..", "agrosense.db")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

client = TestClient(app)


def test_post_sensor_data_success():
    payload = {"sensor_id": "t1", "temperature": 23.5, "humidity": 60.0, "ph": 6.5, "light": 300}
    r = client.post("/sensor-data", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "success"
