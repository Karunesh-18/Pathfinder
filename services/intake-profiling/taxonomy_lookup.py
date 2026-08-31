"""skills_taxonomy_lookup — interim implementation.

The full Skills Taxonomy Graph (dependency edges, seeded from O*NET/ESCO,
curated per role — see stores/skills-taxonomy-graph) doesn't exist yet.
Until it does, this derives a flat skill vocabulary for a role directly
from the Course & Skills Knowledge Base already built: the union of
skills_taught across that role's courses. That's real seed data, not
invented — but it's a flat list, not a graph, and it has no
prerequisite/dependency edges between skills. Closing that gap is the
Skills Taxonomy Graph's job, not this stub's.
"""

from __future__ import annotations

import sys
from pathlib import Path

_CKB_PATH = Path(__file__).resolve().parents[2] / "stores" / "course-knowledge-base"
if str(_CKB_PATH) not in sys.path:
    sys.path.insert(0, str(_CKB_PATH))

import db as course_kb_db  # noqa: E402


def lookup_skills_for_role(role: str) -> list[str]:
    """Return the flat set of skills tagged against `role` in the Course &
    Skills Knowledge Base. Case-insensitive match against target_roles."""
    courses = course_kb_db.list_courses()
    skills: set[str] = set()
    for c in courses:
        target_roles = c.get("target_roles", []) or []
        if any(r.lower() == role.lower() for r in target_roles):
            skills.update(c.get("skills_taught", []) or [])
    return sorted(skills)
