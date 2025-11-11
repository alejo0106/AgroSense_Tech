import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DB_PATH = os.path.join(os.path.dirname(__file__), "agrosense.db")
# Prefer DATABASE_URL (e.g. postgres://...) otherwise fallback to sqlite file
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# If using sqlite we need check_same_thread; otherwise pass no special connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

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

    This is a convenience for code that needs a raw connection (cursor) instead
    of SQLAlchemy sessions. It reads the connection string from POSTGRES_DSN or
    DATABASE_URL environment variables. Raise RuntimeError if psycopg2 is not
    installed or no Postgres DSN is available.
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except Exception as exc:
        raise RuntimeError("psycopg2 is required for direct Postgres connections") from exc

    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn or "postgres" not in dsn:
        raise RuntimeError("Postgres DSN not found in POSTGRES_DSN or DATABASE_URL")

    # psycopg2 accepts libpq-style URIs like postgresql://user:pass@host:port/db
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)
