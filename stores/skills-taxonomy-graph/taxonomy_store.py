"""Storage backend for the Skills Taxonomy Graph.

Same dual-backend pattern as the other two stores (Postgres/Supabase when
configured, SQLite fallback otherwise), sharing common/env.py. Named
taxonomy_store.py — not db.py — for the same reason
stores/learner-profile-store/profile_store.py isn't named db.py: bare
module names collide across directories in one Python process.
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
SQLITE_PATH = HERE / "taxonomy.db"
SCHEMA_PATH = HERE / "schema.sql"
SEED_PATH = HERE / "seed_data_engineer_taxonomy.json"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS skill_requirements (
    role           TEXT NOT NULL,
    skill          TEXT NOT NULL,
    required_level TEXT NOT NULL,
    weight         REAL NOT NULL DEFAULT 1,
    PRIMARY KEY (role, skill)
);
CREATE TABLE IF NOT EXISTS skill_dependencies (
    role         TEXT NOT NULL,
    skill        TEXT NOT NULL,
    prerequisite TEXT NOT NULL,
    PRIMARY KEY (role, skill, prerequisite)
);
"""

_pg_schema_applied = False


def backend_name() -> str:
    return "Postgres/Supabase" if get_database_url() else "SQLite (fallback)"


def _pg_connect(db_url: str):
    import psycopg2

    return psycopg2.connect(db_url)


def _load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def ingest() -> tuple[int, int]:
    """Load seed_data_engineer_taxonomy.json into whichever backend is
    configured. Returns (n_requirements, n_dependencies)."""
    seed = _load_seed()
    role = seed["role"]
    requirements = seed["required_skills"]
    dependencies = seed["dependencies"]
    db_url = get_database_url()

    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
                cur.execute("DELETE FROM skill_requirements WHERE role = %s", (role,))
                cur.execute("DELETE FROM skill_dependencies WHERE role = %s", (role,))
                for r in requirements:
                    cur.execute(
                        "INSERT INTO skill_requirements (role, skill, required_level, weight) VALUES (%s, %s, %s, %s)",
                        (role, r["skill"], r["required_level"], r["weight"]),
                    )
                for d in dependencies:
                    cur.execute(
                        "INSERT INTO skill_dependencies (role, skill, prerequisite) VALUES (%s, %s, %s)",
                        (role, d["skill"], d["prerequisite"]),
                    )
            conn.commit()
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.executescript(SQLITE_SCHEMA)
            conn.execute("DELETE FROM skill_requirements WHERE role = ?", (role,))
            conn.execute("DELETE FROM skill_dependencies WHERE role = ?", (role,))
            conn.executemany(
                "INSERT INTO skill_requirements (role, skill, required_level, weight) VALUES (?, ?, ?, ?)",
                [(role, r["skill"], r["required_level"], r["weight"]) for r in requirements],
            )
            conn.executemany(
                "INSERT INTO skill_dependencies (role, skill, prerequisite) VALUES (?, ?, ?)",
                [(role, d["skill"], d["prerequisite"]) for d in dependencies],
            )
            conn.commit()
        finally:
            conn.close()

    return len(requirements), len(dependencies)


def get_role_requirements(role: str) -> list[dict[str, Any]]:
    """Ranked by weight descending: [{"skill", "required_level", "weight"}]."""
    db_url = get_database_url()
    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT skill, required_level, weight FROM skill_requirements WHERE role = %s ORDER BY weight DESC",
                    (role,),
                )
                return [{"skill": s, "required_level": lvl, "weight": float(w)} for s, lvl, w in cur.fetchall()]
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.executescript(SQLITE_SCHEMA)  # no-op if already applied; safe for a fresh file
            rows = conn.execute(
                "SELECT skill, required_level, weight FROM skill_requirements WHERE role = ? ORDER BY weight DESC",
                (role,),
            ).fetchall()
            return [{"skill": s, "required_level": lvl, "weight": w} for s, lvl, w in rows]
        finally:
            conn.close()


def get_dependencies(role: str) -> list[dict[str, str]]:
    """[{"skill", "prerequisite"}] — skill depends on prerequisite."""
    db_url = get_database_url()
    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT skill, prerequisite FROM skill_dependencies WHERE role = %s", (role,))
                return [{"skill": s, "prerequisite": p} for s, p in cur.fetchall()]
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.executescript(SQLITE_SCHEMA)
            rows = conn.execute(
                "SELECT skill, prerequisite FROM skill_dependencies WHERE role = ?", (role,)
            ).fetchall()
            return [{"skill": s, "prerequisite": p} for s, p in rows]
        finally:
            conn.close()


if __name__ == "__main__":
    n_req, n_dep = ingest()
    print(f"Ingested {n_req} skill requirements and {n_dep} dependency edges (backend: {backend_name()})")
