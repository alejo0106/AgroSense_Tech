"""Seed the sensor_data table with example rows using SQLAlchemy session.

This script works with either the configured DATABASE_URL (Postgres) or the
fallback Sqlite. Run it from the project root:

    python scripts/seed_db.py

It will create the tables (if needed) and insert 5 sample readings.
"""
import sys
import os
from datetime import datetime, timezone
# Ensure project root is on sys.path so imports work when running this script
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import random
from database import engine, SessionLocal, init_db
from models import Sensor


def make_sample(sensor_id: str, ts: datetime):
    return Sensor(
        sensor_id=sensor_id,
        temperature=round(random.uniform(15.0, 35.0), 1),
        humidity=round(random.uniform(30.0, 90.0), 1),
        ph=round(random.uniform(5.5, 7.5), 2),
        light=random.randint(100, 2000),
        timestamp=ts,
    )


def main():
    init_db()
    session = SessionLocal()
    try:
        # insert 5 readings spaced 1 minute apart
        now = datetime.now(timezone.utc)
        samples = [make_sample(f"demo-{i+1}", now) for i in range(5)]
        session.add_all(samples)
        session.commit()
        print("Inserted sample sensor readings")
    finally:
        session.close()


if __name__ == "__main__":
    main()
