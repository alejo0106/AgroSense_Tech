"""Pytest configuration and shared fixtures for AgroSense_Tech.

Organiza fixtures según buenas prácticas (ISO/IEC 29119 - preparación controlada, limpieza).
"""
import os
import shutil
import tempfile
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from main import app
from database import Base, engine, SessionLocal
from models import Sensor


@pytest.fixture(scope="session")
def test_db_dir() -> Generator[str, None, None]:
    """Directorio temporal para aislar cualquier archivo sqlite en caso de fallback.

    Ajuste: se corrige la anotación de tipo (antes str, ahora Generator[str, None, None]) y se usa
    try/finally para garantizar limpieza incluso ante fallos en las pruebas.
    """
    tmp = tempfile.mkdtemp(prefix="agrosense_test_")
    try:
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="function")
def db_session(test_db_dir) -> Generator:
    """Crea una sesión nueva y limpia la tabla antes de cada prueba.

    Aunque el proyecto soporta Postgres vía DATABASE_URL, para pruebas unitarias
    aisladas dejamos que utilice el engine configurado (que puede ser sqlite fallback).
    """
    # Asegurar creación de tablas
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        session.query(Sensor).delete()
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Cliente FastAPI aislado por prueba.

    El fixture db_session asegura limpieza; aquí solo se instancia el TestClient.
    """
    yield TestClient(app)
