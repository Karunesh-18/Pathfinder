"""Storage backend for the Account Store (user signup/login).

New in the login/multi-role rework. Mirrors stores/learner-profile-store/
profile_store.py's dual-backend pattern: Postgres/Supabase if
SUPABASE_DB_URL or DATABASE_URL is set, SQLite fallback otherwise.

Named account_store.py rather than db.py deliberately, per CLAUDE.md
Convention #1 — a module named plain "db" already exists in
stores/course-knowledge-base, and Python caches imports by bare module
name in sys.modules; two same-named modules loaded from different
directories in the same process silently collide.

Password hashing uses the raw bcrypt package directly (not passlib, whose
bcrypt backend has a known incompatibility with bcrypt>=4.x).
"""

from __future__ import annotations

import sqlite3
import sys
import uuid
from pathlib import Path
from typing import Any

import bcrypt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.env import get_database_url  # noqa: E402

HERE = Path(__file__).resolve().parent
SQLITE_PATH = HERE / "accounts.db"
SCHEMA_PATH = HERE / "schema.sql"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id             TEXT PRIMARY KEY,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    display_name   TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_pg_schema_applied = False


def backend_name() -> str:
    return "Postgres/Supabase" if get_database_url() else "SQLite (fallback)"


def _pg_connect(db_url: str):
    import psycopg2  # imported lazily so SQLite-only usage doesn't need it

    return psycopg2.connect(db_url)


def _ensure_schema_postgres(db_url: str) -> None:
    global _pg_schema_applied
    if _pg_schema_applied:
        return
    conn = _pg_connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    _pg_schema_applied = True


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _row_to_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "password_hash": row["password_hash"],
        "display_name": row.get("display_name"),
    }


def create_user(email: str, password: str, display_name: str | None = None) -> dict[str, Any]:
    """Creates a new user with a freshly generated id. Returns the user
    dict (including password_hash — callers that expose this over the API
    must strip it, see backend/api_schemas.py's UserOut). Raises
    ValueError if the email is already registered."""
    if get_user_by_email(email) is not None:
        raise ValueError(f"Email already registered: {email}")

    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    db_url = get_database_url()

    if db_url:
        _ensure_schema_postgres(db_url)
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, email, password_hash, display_name)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, email, password_hash, display_name),
                )
            conn.commit()
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.execute(SQLITE_SCHEMA)
            conn.execute(
                """
                INSERT INTO users (id, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, email, password_hash, display_name),
            )
            conn.commit()
        finally:
            conn.close()

    return {"id": user_id, "email": email, "password_hash": password_hash, "display_name": display_name}


def get_user_by_email(email: str) -> dict[str, Any] | None:
    db_url = get_database_url()
    if db_url:
        _ensure_schema_postgres(db_url)
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d.name for d in cur.description]
                return _row_to_user(dict(zip(cols, row)))
        finally:
            conn.close()
    else:
        if not SQLITE_PATH.exists():
            return None
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(SQLITE_SCHEMA)
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return _row_to_user(dict(row)) if row else None
        finally:
            conn.close()


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    db_url = get_database_url()
    if db_url:
        _ensure_schema_postgres(db_url)
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d.name for d in cur.description]
                return _row_to_user(dict(zip(cols, row)))
        finally:
            conn.close()
    else:
        if not SQLITE_PATH.exists():
            return None
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(SQLITE_SCHEMA)
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return _row_to_user(dict(row)) if row else None
        finally:
            conn.close()
