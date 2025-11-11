"""Unit tests for database.py helpers to improve coverage.

Focus:
- Config loading with and without DATABASE_URL (simulating .env present/absent)
- get_db() session open/close behavior
- get_connection(): success path (mock psycopg2) and failure on missing psycopg2
- init_db(): creates tables without raising

We load an isolated copy of database.py using importlib.util.spec_from_file_location
to avoid side effects on the app-level imported module.
"""
import os
import types
import importlib.util
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_MODULE_PATH = PROJECT_ROOT / "database.py"


def load_database_isolated(env: dict):
    """Load database.py into an isolated module object under a unique name with given env vars."""
    # Patch environment temporarily
    old_env = os.environ.copy()
    try:
        os.environ.update(env)
        # Create a new module spec and module
        spec = importlib.util.spec_from_file_location("database_isolated", str(DB_MODULE_PATH))
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        return mod
    finally:
        # restore environment
        os.environ.clear()
        os.environ.update(old_env)


def test_config_without_env_uses_sqlite_fallback(tmp_path: Path):
    # Ensure no DATABASE_URL; set a temp cwd so sqlite path resolves predictably
    mod = load_database_isolated(env={"DATABASE_URL": ""})
    assert mod.DATABASE_URL.startswith("sqlite:")
    # Backend detection present
    assert mod._backend in ("sqlite", None)


def test_config_with_env_uses_provided_url():
    url = "sqlite:///:memory:"
    mod = load_database_isolated(env={"DATABASE_URL": url})
    assert mod.DATABASE_URL == url
    assert mod._backend == "sqlite"


def test_get_db_opens_and_closes_session(monkeypatch):
    # Load isolated module with in-memory sqlite
    mod = load_database_isolated(env={"DATABASE_URL": "sqlite:///:memory:"})

    calls = {"opened": False, "closed": False}

    class FakeSession:
        def __init__(self):
            calls["opened"] = True

        def close(self):
            calls["closed"] = True

    def fake_session_local():
        return FakeSession()

    monkeypatch.setattr(mod, "SessionLocal", fake_session_local)

    gen = mod.get_db()
    db = next(gen)
    assert calls["opened"] is True
    # Exhaust generator to trigger finally: db.close()
    with pytest.raises(StopIteration):
        next(gen)
    assert calls["closed"] is True


def test_get_connection_success(monkeypatch):
    # Provide a Postgres DSN via env
    dsn = "postgresql://user:pass@localhost:5432/db"
    mod = load_database_isolated(env={"DATABASE_URL": dsn})

    # Fake psycopg2 modules
    class FakeConn:
        def __init__(self, dsn_arg, cursor_factory=None):
            self.dsn = dsn_arg
            self.cursor_factory = cursor_factory

        def close(self):
            pass

    class FakePsycopgExtras:
        class RealDictCursor:  # placeholder
            pass

    class ImportCatcher:
        def __init__(self):
            self.calls = []

        def import_module(self, name: str):
            self.calls.append(name)
            if name == "psycopg2":
                # return a module-like object with connect
                m = types.SimpleNamespace(connect=lambda dsn, cursor_factory=None: FakeConn(dsn, cursor_factory))
                return m
            if name == "psycopg2.extras":
                return FakePsycopgExtras()
            raise ImportError(name)

    catcher = ImportCatcher()
    monkeypatch.setenv("DATABASE_URL", dsn)
    monkeypatch.setattr("importlib.import_module", catcher.import_module)

    conn = mod.get_connection()
    assert isinstance(conn, FakeConn)
    assert conn.dsn == dsn
    assert conn.cursor_factory is FakePsycopgExtras.RealDictCursor


def test_get_connection_missing_psycopg2(monkeypatch):
    dsn = "postgresql://user:pass@localhost:5432/db"
    mod = load_database_isolated(env={"DATABASE_URL": dsn})

    def boom(name):
        raise ImportError("no psycopg2")

    monkeypatch.setattr("importlib.import_module", boom)
    with pytest.raises(RuntimeError) as ei:
        mod.get_connection()
    assert "psycopg2 is required" in str(ei.value)


def test_init_db_creates_tables(monkeypatch):
    """Use the actual database module so models' Base matches; bind to sqlite memory engine."""
    import importlib
    import database as real_db
    from sqlalchemy import create_engine

    # Swap engine to in-memory sqlite just for this test
    engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(real_db, "engine", engine)
    # Recreate SessionLocal bound to this engine (if present)
    from sqlalchemy.orm import sessionmaker

    monkeypatch.setattr(real_db, "SessionLocal", sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Should not raise
    real_db.init_db()
    # Sensor model table should be in metadata after init
    tables = set(real_db.Base.metadata.tables.keys())
    assert "sensor_data" in tables


def test_get_connection_invalid_backend_raises(monkeypatch):
    # Load isolated with non-postgres DSN
    mod = load_database_isolated(env={"DATABASE_URL": "sqlite:///:memory:"})

    # Provide fake psycopg2 to get past import
    class FakePsycopgExtras:
        class RealDictCursor:
            pass

    def import_module(name: str):
        if name == "psycopg2":
            return types.SimpleNamespace(connect=lambda dsn, cursor_factory=None: None)
        if name == "psycopg2.extras":
            return FakePsycopgExtras()
        raise ImportError(name)

    monkeypatch.setattr("importlib.import_module", import_module)
    # Ensure call-time env points to sqlite DSN
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    with pytest.raises(RuntimeError) as ei:
        mod.get_connection()
    assert "does not appear to be Postgres" in str(ei.value)


def test_get_connection_no_dsn_raises(monkeypatch):
    # No relevant env vars and valid psycopg2 imports
    mod = load_database_isolated(env={})

    class FakePsycopgExtras:
        class RealDictCursor:
            pass

    def import_module(name: str):
        if name == "psycopg2":
            return types.SimpleNamespace(connect=lambda dsn, cursor_factory=None: None)
        if name == "psycopg2.extras":
            return FakePsycopgExtras()
        raise ImportError(name)

    monkeypatch.setattr("importlib.import_module", import_module)
    # Clear env that could provide DSN
    for key in ["POSTGRES_DSN", "DATABASE_URL", "POSTGRES_USER", "root", "POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_PORT"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError) as ei:
        mod.get_connection()
    assert "DSN not found" in str(ei.value)


def test_get_connection_builds_dsn_from_env_vars(monkeypatch):
    # Provide individual POSTGRES_* env vars; note password bug expects key 'root'
    env = {
        "POSTGRES_USER": "u",
        "root": "p",  # current implementation mistakenly reads 'root' instead of POSTGRES_PASSWORD
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5435",
        "POSTGRES_DB": "dbx",
    }
    mod = load_database_isolated(env=env)

    built = "postgresql://u:p@localhost:5435/dbx"

    class FakeConn:
        def __init__(self, dsn_arg, cursor_factory=None):
            self.dsn = dsn_arg
            self.cursor_factory = cursor_factory

    class FakePsycopgExtras:
        class RealDictCursor:
            pass

    def import_module(name: str):
        if name == "psycopg2":
            return types.SimpleNamespace(connect=lambda dsn, cursor_factory=None: FakeConn(dsn, cursor_factory))
        if name == "psycopg2.extras":
            return FakePsycopgExtras()
        raise ImportError(name)

    monkeypatch.setattr("importlib.import_module", import_module)
    # Reapply env vars for call-time since loader restored original env
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # Ensure DATABASE_URL absent so builder path triggers
    monkeypatch.delenv("DATABASE_URL", raising=False)

    conn = mod.get_connection()
    assert isinstance(conn, FakeConn)
    assert conn.dsn == built
