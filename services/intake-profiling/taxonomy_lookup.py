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

_TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "stores" / "skills-taxonomy-graph"
if str(_TAXONOMY_PATH) not in sys.path:
    sys.path.insert(0, str(_TAXONOMY_PATH))

import taxonomy_store  # noqa: E402


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


def lookup_skills_for_all_roles() -> list[str]:
    """Union of skills_taught across every course, regardless of role.
    Used by intake_agent's extraction step now that multiple roles are
    seeded — safe to widen, since extraction only ever reports a skill
    that's literally present in the learner's text or in this allowed
    list, so a bigger vocabulary can recognize more, never hallucinate."""
    courses = course_kb_db.list_courses()
    skills: set[str] = set()
    for c in courses:
        skills.update(c.get("skills_taught", []) or [])
    return sorted(skills)


def known_roles() -> list[str]:
    """Every target role currently seeded in the Skills Taxonomy Graph —
    used by intake_agent to validate/normalize a learner's extracted
    target_role against a real, seeded role."""
    return [r["role"] for r in taxonomy_store.list_roles()]
