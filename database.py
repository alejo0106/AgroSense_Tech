import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DB_PATH = os.path.join(os.path.dirname(__file__), "agrosense.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
