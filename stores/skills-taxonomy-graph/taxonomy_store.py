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


# Every taxonomy seed file, in the order ingest_all() loads them. New
# roles added for the multi-role rework go here — see
# stores/course-knowledge-base/ingest.py's ROLE_SEEDS for the matching
# course-side list.
SEED_FILES = [
    HERE / "seed_data_engineer_taxonomy.json",
    HERE / "seed_data_scientist_taxonomy.json",
    HERE / "seed_ml_engineer_taxonomy.json",
    HERE / "seed_frontend_developer_taxonomy.json",
]

# Short blurb shown on the Explore Roles page. A role present in the DB
# with no entry here just gets an empty blurb, not an error.
ROLE_BLURBS: dict[str, str] = {
    "Data Engineer": "Build and operate the pipelines, warehouses, and infrastructure that move and shape data at scale.",
    "Data Scientist": "Turn data into insight and predictions using statistics, machine learning, and experimentation.",
    "ML Engineer": "Take machine learning models from notebook to production: training pipelines, serving, and monitoring.",
    "Frontend Developer": "Build the user-facing interfaces of web applications with modern JavaScript frameworks and tooling.",
}


def _load_seed(seed_path: Path) -> dict[str, Any]:
    return json.loads(seed_path.read_text(encoding="utf-8"))


def ingest(seed_path: Path = SEED_PATH) -> tuple[int, int]:
    """Load one taxonomy seed file into whichever backend is configured.
    Returns (n_requirements, n_dependencies)."""
    seed = _load_seed(seed_path)
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


def ingest_all(seed_paths: list[Path] = SEED_FILES) -> list[tuple[str, int, int]]:
    """Loads every taxonomy seed file that exists on disk (silently skips
    ones that haven't been authored yet, so new roles can be added one at a
    time). Returns [(role, n_requirements, n_dependencies), ...]."""
    results = []
    for seed_path in seed_paths:
        if not seed_path.exists():
            continue
        role = json.loads(seed_path.read_text(encoding="utf-8"))["role"]
        n_req, n_dep = ingest(seed_path)
        results.append((role, n_req, n_dep))
    return results


def list_roles() -> list[dict[str, Any]]:
    """[{"role", "blurb"}] for every role currently seeded, for the
    Explore Roles page."""
    db_url = get_database_url()
    if db_url:
        conn = _pg_connect(db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT role FROM skill_requirements ORDER BY role")
                roles = [r[0] for r in cur.fetchall()]
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.executescript(SQLITE_SCHEMA)
            roles = [r[0] for r in conn.execute("SELECT DISTINCT role FROM skill_requirements ORDER BY role")]
        finally:
            conn.close()
    return [{"role": role, "blurb": ROLE_BLURBS.get(role, "")} for role in roles]


def compute_skill_tiers(role: str) -> dict[str, int]:
    """Longest-path-from-a-root tiering over the role's skill dependency
    graph (Kahn's algorithm), so the Course Tree page can lay itself out in
    columns without a client-side graph-layout library. A skill with no
    prerequisites is tier 0; a skill depending on it is tier 1, etc."""
    requirements = get_role_requirements(role)
    dependencies = get_dependencies(role)

    all_skills = {r["skill"] for r in requirements}
    prereqs_of: dict[str, set[str]] = {skill: set() for skill in all_skills}
    dependents_of: dict[str, set[str]] = {skill: set() for skill in all_skills}
    for dep in dependencies:
        skill, prerequisite = dep["skill"], dep["prerequisite"]
        all_skills.add(skill)
        all_skills.add(prerequisite)
        prereqs_of.setdefault(skill, set()).add(prerequisite)
        dependents_of.setdefault(prerequisite, set()).add(skill)
        prereqs_of.setdefault(prerequisite, set())
        dependents_of.setdefault(skill, set())

    tiers = {skill: 0 for skill in all_skills}
    remaining_prereqs = {skill: set(prereqs) for skill, prereqs in prereqs_of.items()}
    ready = [skill for skill, prereqs in remaining_prereqs.items() if not prereqs]
    visited = set()
    while ready:
        skill = ready.pop()
        if skill in visited:
            continue
        visited.add(skill)
        for dependent in dependents_of.get(skill, ()):
            tiers[dependent] = max(tiers[dependent], tiers[skill] + 1)
            remaining_prereqs[dependent].discard(skill)
            if not remaining_prereqs[dependent] and dependent not in visited:
                ready.append(dependent)
    return tiers


if __name__ == "__main__":
    for role, n_req, n_dep in ingest_all():
        print(f"Ingested {role}: {n_req} skill requirements and {n_dep} dependency edges (backend: {backend_name()})")
