"""Execute the SQL in `scripts/seed_data.sql` against the configured database.

This script uses SQLAlchemy's engine to run the raw SQL. It will run the file
in a single transaction. For Postgres it will execute the DDL/DML as-is. For
Sqlite the `SERIAL` type will be ignored by SQLite and the table will be
created with an integer primary key instead.

Usage:
    # ensure env vars or a .env are set (DATABASE_URL or POSTGRES_*)
    python scripts/seed_from_sql.py

The script will print progress and any SQL errors.
"""
import sys
import os
from sqlalchemy import text

# make project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import engine, init_db


def main():
    sql_path = os.path.join(os.path.dirname(__file__), "seed_data.sql")
    if not os.path.exists(sql_path):
        print("seed_data.sql not found at:", sql_path)
        sys.exit(2)

    with open(sql_path, "r", encoding="utf8") as fh:
        sql = fh.read()

    # Ensure SQLAlchemy has created any needed metadata first (no-op for raw SQL)
    try:
        init_db()
    except Exception:
        # init_db may attempt to create tables via ORM; ignore errors here
        pass

    print("Executing SQL from:", sql_path)
    try:
        # Use a transaction
        with engine.begin() as conn:
            # exec_driver_sql runs the SQL verbatim using the DBAPI
            conn.exec_driver_sql(sql)
        print("Seed SQL executed successfully.")
    except Exception as exc:
        print("Error executing seed SQL:", exc)
        sys.exit(3)


if __name__ == "__main__":
    main()
