"""Storage backend for the Course & Skills Knowledge Base.

Auto-detects a Postgres/Supabase connection from the environment
(SUPABASE_DB_URL or DATABASE_URL). If one is set, ingest.py and
test_harness.py talk to that database, applying schema.sql and using
native Postgres arrays + pgvector. If neither is set, everything falls
back to the local SQLite file (course_kb.db) exactly as before — nothing
breaks for anyone who hasn't supplied credentials yet.

No secrets are ever read from or written into chat/conversation; this
module only reads them from environment variables or a local .env file
(gitignored — see .gitignore) that you create and fill in yourself.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SQLITE_PATH = HERE / "course_kb.db"
SCHEMA_PATH = HERE / "schema.sql"
ENV_PATH = HERE.parent.parent / ".env"  # project root .env


def load_env_file(path: Path = ENV_PATH) -> None:
    """Minimal .env loader (no external dependency). Only sets variables
    that aren't already present in the environment, so real env vars
    always win over the file."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_database_url() -> str | None:
    """Returns the configured Postgres/Supabase connection string, or None
    if the prototype should fall back to SQLite."""
    load_env_file()
    return os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")


# ---------------------------------------------------------------------------
# Postgres / Supabase backend
# ---------------------------------------------------------------------------

def _pg_connect(db_url: str):
    import psycopg2  # imported lazily so SQLite-only usage doesn't need it

    return psycopg2.connect(db_url)


def apply_schema_postgres(db_url: str) -> None:
    conn = _pg_connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def upsert_courses_postgres(db_url: str, courses: list[dict[str, Any]], target_role: str) -> int:
    conn = _pg_connect(db_url)
    try:
        with conn.cursor() as cur:
            for c in courses:
                cur.execute(
                    """
                    INSERT INTO courses
                        (id, title, provider, url, description, skills_taught,
                         level, format, target_roles, prerequisites, estimated_hours, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        provider = EXCLUDED.provider,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        skills_taught = EXCLUDED.skills_taught,
                        level = EXCLUDED.level,
                        format = EXCLUDED.format,
                        target_roles = EXCLUDED.target_roles,
                        prerequisites = EXCLUDED.prerequisites,
                        estimated_hours = EXCLUDED.estimated_hours,
                        source = EXCLUDED.source
                    """,
                    (
                        c["id"],
                        c["title"],
                        c["provider"],
                        c.get("url", ""),
                        c["description"],
                        c.get("skills_taught", []),
                        c.get("level", ""),
                        c.get("format", ""),
                        [target_role],
                        c.get("prerequisites", []),
                        c.get("estimated_hours"),
                        "hand-built-sample",
                    ),
                )
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM courses")
            count = cur.fetchone()[0]
    finally:
        conn.close()
    return count


def list_courses_postgres(db_url: str) -> list[dict[str, Any]]:
    conn = _pg_connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, provider, url, description, skills_taught,
                       level, format, target_roles, prerequisites, estimated_hours, source
                FROM courses
                """
            )
            cols = [d.name for d in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()
    # psycopg2 returns NUMERIC columns as decimal.Decimal, not float —
    # normalize so downstream arithmetic (e.g. path-construction's hours
    # math) doesn't have to special-case the Postgres backend.
    for row in rows:
        if row.get("estimated_hours") is not None:
            row["estimated_hours"] = float(row["estimated_hours"])
    return rows


# ---------------------------------------------------------------------------
# SQLite fallback backend
# ---------------------------------------------------------------------------

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS courses (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    provider      TEXT NOT NULL,
    url           TEXT,
    description   TEXT NOT NULL,
    skills_taught TEXT NOT NULL,   -- JSON-encoded list (no array type in SQLite)
    level         TEXT,
    format        TEXT,
    target_roles  TEXT NOT NULL,   -- JSON-encoded list
    prerequisites TEXT NOT NULL,   -- JSON-encoded list
    estimated_hours REAL,          -- rough hand estimate, not scraped
    source        TEXT NOT NULL DEFAULT 'hand-built-sample'
);
"""


def upsert_courses_sqlite(courses: list[dict[str, Any]], target_role: str) -> int:
    # NOTE: this used to DROP TABLE IF EXISTS before every ingest, which was
    # harmless for a single seeded role but silently wiped every other
    # role's rows once multi-role seeding started (ingest.py loops
    # ROLE_SEEDS calling this once per role). Switched to
    # CREATE TABLE IF NOT EXISTS + INSERT ... ON CONFLICT, mirroring
    # upsert_courses_postgres's already-correct ON CONFLICT logic.
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        conn.execute(SQLITE_SCHEMA)
        conn.executemany(
            """
            INSERT INTO courses
                (id, title, provider, url, description, skills_taught,
                 level, format, target_roles, prerequisites, estimated_hours, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                provider=excluded.provider,
                url=excluded.url,
                description=excluded.description,
                skills_taught=excluded.skills_taught,
                level=excluded.level,
                format=excluded.format,
                target_roles=excluded.target_roles,
                prerequisites=excluded.prerequisites,
                estimated_hours=excluded.estimated_hours,
                source=excluded.source
            """,
            [
                (
                    c["id"],
                    c["title"],
                    c["provider"],
                    c.get("url", ""),
                    c["description"],
                    json.dumps(c.get("skills_taught", [])),
                    c.get("level", ""),
                    c.get("format", ""),
                    json.dumps([target_role]),
                    json.dumps(c.get("prerequisites", [])),
                    c.get("estimated_hours"),
                    "hand-built-sample",
                )
                for c in courses
            ],
        )
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    finally:
        conn.close()
    return count


def list_courses_sqlite() -> list[dict[str, Any]]:
    if not SQLITE_PATH.exists():
        raise SystemExit(
            f"No course_kb.db found at {SQLITE_PATH}.\n"
            "Run: python stores/course-knowledge-base/ingest.py first."
        )
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM courses").fetchall()
    finally:
        conn.close()

    courses = []
    for row in rows:
        course = dict(row)
        course["skills_taught"] = json.loads(course["skills_taught"])
        course["target_roles"] = json.loads(course["target_roles"])
        course["prerequisites"] = json.loads(course["prerequisites"])
        courses.append(course)
    return courses


# ---------------------------------------------------------------------------
# Unified interface — this is what ingest.py and test_harness.py should use
# ---------------------------------------------------------------------------

def backend_name() -> str:
    return "Postgres/Supabase" if get_database_url() else "SQLite (fallback)"


def upsert_courses(courses: list[dict[str, Any]], target_role: str) -> int:
    db_url = get_database_url()
    if db_url:
        apply_schema_postgres(db_url)
        return upsert_courses_postgres(db_url, courses, target_role)
    return upsert_courses_sqlite(courses, target_role)


def list_courses() -> list[dict[str, Any]]:
    db_url = get_database_url()
    if db_url:
        return list_courses_postgres(db_url)
    return list_courses_sqlite()


def get_course(course_id: str) -> dict[str, Any] | None:
    """Simplest correct implementation at this dataset's size (tens of
    rows, not thousands): reuse list_courses() rather than writing a
    second SQL query path per backend."""
    return next((c for c in list_courses() if c["id"] == course_id), None)
