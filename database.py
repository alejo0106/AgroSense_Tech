import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.engine.url import make_url

DB_PATH = os.path.join(os.path.dirname(__file__), "agrosense.db")
# Prefer DATABASE_URL (e.g. postgres://...) otherwise fallback to sqlite file
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# Parse the DATABASE_URL to detect backend (robust vs startswith)
try:
    _parsed_url = make_url(DATABASE_URL)
    _backend = _parsed_url.get_backend_name()
except Exception:
    _parsed_url = None
    _backend = None

# If using sqlite we need check_same_thread; otherwise no special connect_args
connect_args = {"check_same_thread": False} if _backend == "sqlite" else {}

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    # Import models here to ensure they are registered on Base before create_all
    from models import Sensor  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_connection():
    """Return a direct DB-API connection to Postgres using psycopg2.

    This helper accepts either a full DATABASE_URL/POSTGRES_DSN (libpq URI)
    or individual POSTGRES_* environment variables. It uses SQLAlchemy's URL
    parser to robustly detect the driver. Returns a connection with
    RealDictCursor for convenience.
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except Exception as exc:
        raise RuntimeError("psycopg2 is required for direct Postgres connections") from exc

    # Prefer an explicit DSN env var, then DATABASE_URL
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")

    # If no DSN, try to build from individual env vars
    if not dsn:
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        dbname = os.getenv("POSTGRES_DB")
        if user and host and dbname:
            # Build a libpq-style URI
            auth = f"{user}:{password}@" if password else f"{user}@"
            port_part = f":{port}" if port else ""
            dsn = f"postgresql://{auth}{host}{port_part}/{dbname}"

    if not dsn:
        raise RuntimeError("Postgres DSN not found in POSTGRES_DSN/DATABASE_URL or POSTGRES_* env vars")

    # Validate DSN scheme robustly using SQLAlchemy parser
    try:
        url = make_url(dsn)
        backend = url.get_backend_name()
    except Exception:
        backend = None

    if backend not in ("postgresql", "postgres"):
        raise RuntimeError("Provided DSN does not appear to be Postgres")

    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)
