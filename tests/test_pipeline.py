from routers.analytics import process_data

def test_process_data_metrics():
    """Verifica que el pipeline calcule correctamente las métricas básicas"""
    sample_data = [
        {"temperature": 25, "humidity": 60, "light": 400},
        {"temperature": 27, "humidity": 65, "light": 420},
        {"temperature": 26, "humidity": 63, "light": 410}
    ]

    result = process_data(sample_data)

    assert "avg_temp" in result
    assert round(result["avg_temp"], 1) == 26.0
    assert result["max_light"] == 420
    assert result["min_light"] == 400
