import requests
import random
import time
from datetime import datetime, timezone

URL = "http://127.0.0.1:8000/sensor-data"

def generate_data():
    return {
        "sensor_id": random.choice(["s1", "s2", "s3"]),
        "temperature": round(random.uniform(18, 30), 2),
        "humidity": round(random.uniform(40, 80), 2),
        "ph": round(random.uniform(6.0, 7.5), 2),
        "light": round(random.uniform(200, 800), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def main():
    print("🌱 Simulador de sensores IoT iniciado...")
    try:
        while True:
            data = generate_data()
            try:
                r = requests.post(URL, json=data, timeout=5)
                status = "✅" if r.status_code == 200 else f"❌ ({r.status_code})"
            except Exception as e:
                status = f"❌ ({e})"
            print(f"{status} Enviando: {data}")
            time.sleep(5)  # cada 5 segundos envía una nueva lectura
    except KeyboardInterrupt:
        print("\nSimulador detenido.")


if __name__ == "__main__":
    main()
