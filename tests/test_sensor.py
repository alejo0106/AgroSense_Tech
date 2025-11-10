from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_sensor_data_success():
    """Verifica que la API reciba correctamente los datos del sensor"""
    payload = {
        "temperature": 25.3,
        "humidity": 70,
        "light": 500,
        "ph": 6.8
    }
    response = client.post("/sensor-data", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_post_sensor_data_invalid():
    """Verifica que la API responda con error si los datos están incompletos"""
    payload = {"temperature": 25.3}
    response = client.post("/sensor-data", json=payload)
    assert response.status_code in [400, 422]
