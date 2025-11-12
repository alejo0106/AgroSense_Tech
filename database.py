"""
Infraestructura de base de datos (SQLAlchemy + Postgres/SQLite)

Relación con el resto del proyecto:
- `models.py` define las entidades ORM y hereda de `Base` definida aquí.
- Los routers usan `get_db()` (Dependency Injection de FastAPI) para obtener
    una sesión de base de datos por request.
- `init_db()` crea las tablas a partir de los modelos y se invoca desde `main.py`
    al iniciar la aplicación.

Selección del motor de base de datos:
- En tiempo de importación resolvemos `DATABASE_URL` usando esta prioridad:
    1) `POSTGRES_DSN` (DSN explícito) > 2) `DATABASE_URL` > 3) fallback SQLite.
    Esto evita que, en entornos de prueba, se "autoconstruya" un DSN Postgres
    inesperado cuando no hay `DATABASE_URL`.
- Para conexiones directas (diagnóstico) `get_connection()` sí permite construir
    un DSN a partir de `POSTGRES_*` si es necesario.
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.engine.url import make_url

# Optional: load environment variables from a local .env file if python-dotenv is
# installed. This makes it easy to put POSTGRES_* or DATABASE_URL into a
# non-committed `.env` during local development without changing system env.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # dotenv is optional; if not present we simply rely on existing env vars
    pass

DB_PATH = os.path.join(os.path.dirname(__file__), "agrosense.db")

def build_postgres_dsn_from_parts() -> str | None:
    """Build a Postgres DSN from individual POSTGRES_* env vars if they exist.

    Returns a libpq URI in the form postgresql://user:pass@host:port/dbname or None
    if the required minimum variables are not present.
    """
    # Este helper se usa en `get_connection()` (diagnóstico). No se usa para
    # fijar `DATABASE_URL` en tiempo de importación para no sorprender a los tests.
    user = os.getenv("POSTGRES_USER")
    # Legacy behavior: some tests/scripts used env key 'root' for the password.
    # To preserve compatibility, prefer 'root' if present; otherwise fall back
    # to the conventional POSTGRES_PASSWORD variable.
    legacy_pw = os.getenv("root")
    password = legacy_pw if legacy_pw is not None else os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    dbname = os.getenv("POSTGRES_DB")
    if not (user and host and dbname):
        return None
    auth = f"{user}:{password}@" if password else f"{user}@"
    port_part = f":{port}" if port else ""
    return f"postgresql://{auth}{host}{port_part}/{dbname}"

# Resolution precedence for SQLAlchemy engine (import-time):
# 1. POSTGRES_DSN (explicit full DSN)
# 2. DATABASE_URL
# 3. Local sqlite file fallback
# Note: We intentionally do NOT auto-build from POSTGRES_* here to avoid
# surprising behavior in test environments that expect sqlite fallback when
# DATABASE_URL is absent.
DATABASE_URL = (
    os.getenv("POSTGRES_DSN")
    or os.getenv("DATABASE_URL")
    or f"sqlite:///{DB_PATH}"
)

# Parse the DATABASE_URL to detect backend (robust vs startswith)
try:
    _parsed_url = make_url(DATABASE_URL)
    _backend = _parsed_url.get_backend_name()
except Exception:
    _parsed_url = None
    _backend = None

# Si usamos SQLite necesitamos `check_same_thread=False` (uvicorn multiproceso)
# Para Postgres no se requieren `connect_args` especiales.
connect_args = {"check_same_thread": False} if _backend == "sqlite" else {}

# Crear el engine (conexión pool) y la factoría de sesiones.
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    """Crea las tablas a partir de los modelos declarados en `models.py`.

    Importamos dentro de la función para registrar los modelos en `Base`
    antes de ejecutar `create_all`.
    """
    # Import models here to ensure they are registered on Base before create_all
    from models import Sensor  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency de FastAPI: abre una sesión por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_connection():
    """Return a direct psycopg2 connection to Postgres.

    Resolution order mirrors DATABASE_URL construction. Raises RuntimeError if
    the resolved DSN is missing or not Postgres. Uses RealDictCursor for easy
    dict row access.
    """
    try:
        import importlib

        psycopg2 = importlib.import_module("psycopg2")
        RealDictCursor = importlib.import_module("psycopg2.extras").RealDictCursor
    except Exception as exc:
        raise RuntimeError("psycopg2 is required for direct Postgres connections") from exc

    # Para diagnóstico aceptamos: POSTGRES_DSN > DATABASE_URL > construir desde POSTGRES_*.
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL") or build_postgres_dsn_from_parts()
    if not dsn:
        raise RuntimeError("Postgres DSN not found. Set POSTGRES_* or DATABASE_URL/POSTGRES_DSN.")

    try:
        url = make_url(dsn)
        backend = url.get_backend_name()
    except Exception:
        backend = None
    if backend not in ("postgresql", "postgres"):
        raise RuntimeError("Provided DSN does not appear to be Postgres")

    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)
