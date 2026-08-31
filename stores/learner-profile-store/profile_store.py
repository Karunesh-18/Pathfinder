"""Storage backend for the Learner Profile Store.

Mirrors stores/course-knowledge-base/db.py's dual-backend pattern:
Postgres/Supabase if SUPABASE_DB_URL or DATABASE_URL is set (same .env
already used for the Course & Skills Knowledge Base), SQLite fallback
otherwise. Uses common/env.py so the env-loading logic isn't duplicated a
third time.

Named profile_store.py rather than db.py deliberately: a module named
plain "db" already exists in stores/course-knowledge-base, and Python
caches imports by bare module name in sys.modules — two same-named
modules loaded from different directories in the same process silently
collide, with the second import returning the first module instead of its
own (this bit the initial version of this file; renaming fixed it).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.env import get_database_url  # noqa: E402

HERE = Path(__file__).resolve().parent
SQLITE_PATH = HERE / "learner_profiles.db"
SCHEMA_PATH = HERE / "schema.sql"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS learner_profiles (
    learner_id                  TEXT PRIMARY KEY,
    target_role                 TEXT,
    current_skills               TEXT NOT NULL,  -- JSON-encoded list of {skill, level}
    completed_courses            TEXT NOT NULL,  -- JSON-encoded list
    time_budget_hours_per_week   REAL,
    format_preference            TEXT,
    missing_fields                TEXT NOT NULL,  -- JSON-encoded list
    follow_up_questions           TEXT NOT NULL,  -- JSON-encoded list
    raw_text                     TEXT,
    extraction_method             TEXT NOT NULL DEFAULT 'rule-based-stub'
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


def save_profile(profile: dict[str, Any]) -> str:
    """Upsert a LearnerProfile dict (as produced by
    services/intake-profiling/schema.py's LearnerProfile.model_dump()).
    Returns the learner_id."""
    skills = profile.get("current_skills", [])
    db_url = get_database_url()

    if db_url:
        _ensure_schema_postgres(db_url)
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO learner_profiles
                        (learner_id, target_role, current_skills, completed_courses,
                         time_budget_hours_per_week, format_preference, missing_fields,
                         follow_up_questions, raw_text, extraction_method)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (learner_id) DO UPDATE SET
                        target_role = EXCLUDED.target_role,
                        current_skills = EXCLUDED.current_skills,
                        completed_courses = EXCLUDED.completed_courses,
                        time_budget_hours_per_week = EXCLUDED.time_budget_hours_per_week,
                        format_preference = EXCLUDED.format_preference,
                        missing_fields = EXCLUDED.missing_fields,
                        follow_up_questions = EXCLUDED.follow_up_questions,
                        raw_text = EXCLUDED.raw_text,
                        extraction_method = EXCLUDED.extraction_method,
                        updated_at = now()
                    """,
                    (
                        profile["learner_id"],
                        profile.get("target_role"),
                        json.dumps(skills),
                        profile.get("completed_courses", []),
                        profile.get("time_budget_hours_per_week"),
                        profile.get("format_preference"),
                        profile.get("missing_fields", []),
                        profile.get("follow_up_questions", []),
                        profile.get("raw_text", ""),
                        profile.get("extraction_method", "rule-based-stub"),
                    ),
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
                INSERT INTO learner_profiles
                    (learner_id, target_role, current_skills, completed_courses,
                     time_budget_hours_per_week, format_preference, missing_fields,
                     follow_up_questions, raw_text, extraction_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(learner_id) DO UPDATE SET
                    target_role=excluded.target_role,
                    current_skills=excluded.current_skills,
                    completed_courses=excluded.completed_courses,
                    time_budget_hours_per_week=excluded.time_budget_hours_per_week,
                    format_preference=excluded.format_preference,
                    missing_fields=excluded.missing_fields,
                    follow_up_questions=excluded.follow_up_questions,
                    raw_text=excluded.raw_text,
                    extraction_method=excluded.extraction_method
                """,
                (
                    profile["learner_id"],
                    profile.get("target_role"),
                    json.dumps(skills),
                    json.dumps(profile.get("completed_courses", [])),
                    profile.get("time_budget_hours_per_week"),
                    profile.get("format_preference"),
                    json.dumps(profile.get("missing_fields", [])),
                    json.dumps(profile.get("follow_up_questions", [])),
                    profile.get("raw_text", ""),
                    profile.get("extraction_method", "rule-based-stub"),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    return profile["learner_id"]


def get_profile(learner_id: str) -> dict[str, Any] | None:
    db_url = get_database_url()
    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM learner_profiles WHERE learner_id = %s", (learner_id,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d.name for d in cur.description]
                result = dict(zip(cols, row))
                # psycopg2 returns NUMERIC as decimal.Decimal, not float —
                # same normalization as course-knowledge-base/db.py.
                if result.get("time_budget_hours_per_week") is not None:
                    result["time_budget_hours_per_week"] = float(result["time_budget_hours_per_week"])
                return result
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT * FROM learner_profiles WHERE learner_id = ?", (learner_id,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            d["current_skills"] = json.loads(d["current_skills"])
            d["completed_courses"] = json.loads(d["completed_courses"])
            d["missing_fields"] = json.loads(d["missing_fields"])
            d["follow_up_questions"] = json.loads(d["follow_up_questions"])
            return d
        finally:
            conn.close()
