"""Verify DB connection script for local development.

Usage (PowerShell):
  # either set DATABASE_URL or POSTGRES_* env vars in your session, or create a .env in repo root
  python scripts\verify_connection.py

This script prints which DSN the app will use and, if Postgres is configured,
attempts to open a direct connection using `get_connection()` from `database.py`.
"""
import sys
import os

from sqlalchemy.engine.url import make_url

try:
    from database import DATABASE_URL, engine, get_connection
except Exception as exc:
    print("Failed to import database module:", exc)
    sys.exit(2)


def main():
    print("DATABASE_URL env value:", os.getenv("DATABASE_URL"))
    print("POSTGRES_DSN env value:", os.getenv("POSTGRES_DSN"))
    print("POSTGRES_* env vars:")
    for k in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB"):
        print(f"  {k}={os.getenv(k)}")

    # Show SQLAlchemy engine URL if available
    try:
        print("engine.url:", getattr(engine, "url", None))
    except Exception:
        print("Could not read engine.url")

    # Try to infer backend from DATABASE_URL
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("No explicit DSN found in env. The app will fallback to sqlite if no env is set.")
    else:
        try:
            url = make_url(dsn)
            backend = url.get_backend_name()
        except Exception:
            backend = None

        print("Inferred backend:", backend)

        if backend in ("postgresql", "postgres"):
            print("Attempting direct psycopg2 connection via database.get_connection()...")
            try:
                conn = get_connection()
                print("Connected to Postgres OK. dsn=", getattr(conn, "dsn", "(no dsn attr)"))
                conn.close()
            except Exception as exc:
                print("Failed to open direct Postgres connection:", exc)


if __name__ == "__main__":
    main()
