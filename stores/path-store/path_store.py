"""Storage backend for the Path Store.

Same dual-backend pattern as the other three stores (Postgres/Supabase
when configured, SQLite fallback otherwise), sharing common/env.py. Named
path_store.py to keep the same "no bare 'db'" convention as
profile_store.py / taxonomy_store.py.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.env import get_database_url  # noqa: E402

HERE = Path(__file__).resolve().parent
SQLITE_PATH = HERE / "path_store.db"
SCHEMA_PATH = HERE / "schema.sql"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS learning_path_steps (
    learner_id                 TEXT NOT NULL,
    step_index                 INTEGER NOT NULL,
    course_id                  TEXT NOT NULL,
    title                      TEXT NOT NULL,
    provider                   TEXT NOT NULL,
    skill_gap_addressed        TEXT NOT NULL,
    milestone                  INTEGER NOT NULL DEFAULT 0,
    estimated_hours            REAL NOT NULL DEFAULT 0,
    cumulative_hours           REAL NOT NULL DEFAULT 0,
    estimated_completion_week  INTEGER,
    target_role                TEXT,
    PRIMARY KEY (learner_id, step_index)
);
"""

_pg_schema_applied = False


def backend_name() -> str:
    return "Postgres/Supabase" if get_database_url() else "SQLite (fallback)"


def _pg_connect(db_url: str):
    import psycopg2

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


def save_path(learner_id: str, target_role: str, steps: list[dict[str, Any]]) -> int:
    """Replace whatever path is currently stored for `learner_id` with
    `steps` (each a LearningPathStep.model_dump()-shaped dict). Returns
    the number of steps written."""
    db_url = get_database_url()

    if db_url:
        _ensure_schema_postgres(db_url)
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM learning_path_steps WHERE learner_id = %s", (learner_id,))
                for s in steps:
                    cur.execute(
                        """
                        INSERT INTO learning_path_steps
                            (learner_id, step_index, course_id, title, provider,
                             skill_gap_addressed, milestone, estimated_hours,
                             cumulative_hours, estimated_completion_week, target_role)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            learner_id,
                            s["step_index"],
                            s["course_id"],
                            s["title"],
                            s["provider"],
                            s["skill_gap_addressed"],
                            s["milestone"],
                            s["estimated_hours"],
                            s["cumulative_hours"],
                            s["estimated_completion_week"],
                            target_role,
                        ),
                    )
            conn.commit()
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.execute(SQLITE_SCHEMA)
            conn.execute("DELETE FROM learning_path_steps WHERE learner_id = ?", (learner_id,))
            conn.executemany(
                """
                INSERT INTO learning_path_steps
                    (learner_id, step_index, course_id, title, provider,
                     skill_gap_addressed, milestone, estimated_hours,
                     cumulative_hours, estimated_completion_week, target_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        learner_id,
                        s["step_index"],
                        s["course_id"],
                        s["title"],
                        s["provider"],
                        s["skill_gap_addressed"],
                        int(s["milestone"]),
                        s["estimated_hours"],
                        s["cumulative_hours"],
                        s["estimated_completion_week"],
                        target_role,
                    )
                    for s in steps
                ],
            )
            conn.commit()
        finally:
            conn.close()

    return len(steps)


def get_path(learner_id: str) -> list[dict[str, Any]]:
    db_url = get_database_url()
    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM learning_path_steps WHERE learner_id = %s ORDER BY step_index",
                    (learner_id,),
                )
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            conn.close()
        # psycopg2 returns NUMERIC as decimal.Decimal, not float — same
        # normalization as course-knowledge-base/db.py, for the same reason.
        for row in rows:
            for key in ("estimated_hours", "cumulative_hours"):
                if row.get(key) is not None:
                    row[key] = float(row[key])
        return rows
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(SQLITE_SCHEMA)
            rows = conn.execute(
                "SELECT * FROM learning_path_steps WHERE learner_id = ? ORDER BY step_index",
                (learner_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
