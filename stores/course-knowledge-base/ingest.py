"""Ingestion script for the Course & Skills Knowledge Base.

Pulls courses for one target role from every registered provider adapter
(see providers/base.py), normalizes them into the shape schema.sql defines,
and writes them to whichever backend db.py detects:

  - Postgres/Supabase, if SUPABASE_DB_URL or DATABASE_URL is set (in the
    environment or in a project-root .env file)
  - otherwise a local SQLite file (course_kb.db), as before

Provider-agnostic by design: PROVIDERS below is the only place platforms
are listed. Neither Coursera nor Udemy has a live MCP connector configured
in this environment, so both currently fall back to the hand-built sample
rows tagged with their name (see providers/hand_built.py). Adding a third
platform later means writing providers/<name>.py (matching the
CourseProvider contract in providers/base.py) and adding it to PROVIDERS —
nothing else here, in rank.py, or in test_harness.py needs to change.

Usage:
    python stores/course-knowledge-base/ingest.py
"""

from pathlib import Path
from typing import Any

import db
from providers import coursera, hand_built, udemy
from providers.base import ProviderNotConfigured

HERE = Path(__file__).resolve().parent
TARGET_ROLE = "Data Engineer"

# Registered platforms. Add a new provider module to providers/ and list it
# here to bring another platform into scope.
PROVIDERS = [coursera, udemy]


def fetch_all(target_role: str) -> list[dict[str, Any]]:
    """Pull courses for `target_role` from every registered provider,
    falling back to hand-built rows for any provider that isn't
    configured yet."""
    rows: list[dict[str, Any]] = []
    for provider in PROVIDERS:
        try:
            live_rows = provider.fetch(target_role)
            print(f"  {provider.name}: live connector returned {len(live_rows)} rows")
            rows.extend(live_rows)
        except ProviderNotConfigured as exc:
            fallback_rows = hand_built.fetch_for_provider(target_role, provider.name)
            print(f"  {provider.name}: not configured ({exc}) — using {len(fallback_rows)} hand-built rows instead")
            rows.extend(fallback_rows)
    return rows


def ingest() -> int:
    print(f"Storage backend: {db.backend_name()}")
    print(f"Fetching courses for target role: {TARGET_ROLE}")
    courses = fetch_all(TARGET_ROLE)
    return db.upsert_courses(courses, TARGET_ROLE)


if __name__ == "__main__":
    n = ingest()
    print(f"Ingested {n} courses (target role: {TARGET_ROLE}, backend: {db.backend_name()})")
