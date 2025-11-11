"""Unit tests for process_data function (ISO/IEC 29119 naming).

Cases:
- CP-PROC-01: process_data_correctness
- CP-PROC-02: process_data_empty
"""
from routers.analytics import process_data


def test_process_data_correctness():
    sample = [
        {"temperature": 25.0, "humidity": 60.0, "ph": 6.7, "light": 400},
        {"temperature": 27.0, "humidity": 65.0, "ph": 6.9, "light": 420},
        {"temperature": 26.0, "humidity": 63.0, "ph": 6.8, "light": 410},
    ]
    result = process_data(sample)
    assert result["avg_temp"] == 26.0
    assert result["avg_humidity"] == 62.7  # mean(60,65,63)=62.666.. rounded 62.7
    assert result["metrics"]["temperature"]["max"] == 27.0
    assert result["metrics"]["light"]["min"] == 400


def test_process_data_empty():
    result = process_data([])
    assert "error" in result
    assert result["error"].lower().startswith("no hay")
