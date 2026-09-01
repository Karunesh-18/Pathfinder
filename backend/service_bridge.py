"""service_bridge.py — the ONLY file in backend/ that reaches into
services/ or stores/.

This project's services live under kebab-case directories
(services/intake-profiling, services/skill-gap, ...), which Python can't
import as real packages, so every existing orchestrator inserts its sibling
directories onto sys.path and does a bare `import <module>` (see
CLAUDE.md Convention #4). A FastAPI app is a single long-lived process
that ends up importing all six orchestrator entry points into one
namespace — a combination no single test_harness.py exercises today
(the closest, services/dashboard/test_harness.py, covers five of six).

Centralizing every cross-directory import in this one file (route modules
never touch sys.path themselves) means there is exactly one place an
import-order bug could ever show up, and it can be smoke-tested in
isolation: `python -c "import backend.service_bridge; print('ok')"`.

Every bare module name below (db, profile_store, path_store,
taxonomy_store, gap, build_path, intake_agent, explain_agent,
feedback_agent, aggregate) is unique across the whole services/+stores/
tree, so — per Convention #1 — there is no sys.modules collision risk.
All directories are pushed onto sys.path before any of the imports run,
so it also doesn't matter that some of these modules do their own
further sys.path.insert calls internally (e.g. explain_agent reaching for
qa/rationale) — anything they could need is already resolvable.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_PATHS = [
    _ROOT,
    Path(__file__).resolve().parent,  # backend/ itself, for auth_token/chat_assistant
    _ROOT / "stores" / "account-store",
    _ROOT / "stores" / "course-knowledge-base",
    _ROOT / "stores" / "learner-profile-store",
    _ROOT / "stores" / "path-store",
    _ROOT / "stores" / "skills-taxonomy-graph",
    _ROOT / "services" / "retrieval-ranking",
    _ROOT / "services" / "skill-gap",
    _ROOT / "services" / "path-construction",
    _ROOT / "services" / "intake-profiling",
    _ROOT / "services" / "explainability-qa",
    _ROOT / "services" / "progress-feedback",
    _ROOT / "services" / "dashboard",
]
for _p in _PATHS:
    _p_str = str(_p)
    if _p_str not in sys.path:
        sys.path.insert(0, _p_str)

from common.llm import is_llm_configured  # noqa: E402

import account_store as _account_store  # noqa: E402
import db as _course_kb_db  # noqa: E402
import profile_store as _profile_store  # noqa: E402
import path_store as _path_store  # noqa: E402
import taxonomy_store as _taxonomy_store  # noqa: E402
from gap import compute_skill_gaps as _compute_skill_gaps  # noqa: E402
from build_path import build_path as _build_path  # noqa: E402
from intake_agent import (  # noqa: E402
    profile_from_text as _profile_from_text,
    DEFAULT_ROLE_FOR_TAXONOMY,
)
from explain_agent import explain_path as _explain_path, ask as _ask  # noqa: E402
from feedback_agent import apply_progress_event as _apply_progress_event  # noqa: E402
from aggregate import build_dashboard as _build_dashboard  # noqa: E402

import auth_token as _auth_token  # noqa: E402
import chat_assistant as _chat_assistant  # noqa: E402

# Single source of truth for the one role currently seeded — never
# re-hardcode the string "Data Engineer" anywhere else in backend/.
DEFAULT_TARGET_ROLE = DEFAULT_ROLE_FOR_TAXONOMY


def create_or_update_profile(raw_text: str, learner_id: str | None) -> dict[str, Any]:
    return _profile_from_text(raw_text, learner_id=learner_id).model_dump()


def get_profile(learner_id: str) -> dict[str, Any] | None:
    return _profile_store.get_profile(learner_id)


def compute_gaps(profile: dict[str, Any], target_role: str) -> list[dict[str, Any]]:
    return [g.model_dump() for g in _compute_skill_gaps(profile, target_role)]


def build_and_save_path(learner_id: str, target_role: str) -> list[dict[str, Any]]:
    profile = get_profile(learner_id)
    if profile is None:
        raise ValueError(f"No profile found for learner_id={learner_id}")
    gaps = compute_gaps(profile, target_role)
    steps = _build_path(gaps, target_role, profile.get("time_budget_hours_per_week"))
    step_dicts = [s.model_dump() for s in steps]
    _path_store.save_path(learner_id, target_role, step_dicts)
    return step_dicts


def get_path(learner_id: str) -> list[dict[str, Any]]:
    return _path_store.get_path(learner_id)


def explain_path(learner_id: str, target_role: str) -> list[dict[str, Any]]:
    return _explain_path(learner_id, target_role)


def ask_question(learner_id: str, target_role: str, question: str) -> str:
    return _ask(learner_id, target_role, question)


def apply_progress(learner_id: str, target_role: str, raw_text: str) -> dict[str, Any]:
    return _apply_progress_event(learner_id, target_role, raw_text).model_dump()


def get_dashboard(learner_id: str, target_role: str) -> dict[str, Any]:
    return _build_dashboard(learner_id, target_role).model_dump()


def list_courses(target_role: str | None = None) -> list[dict[str, Any]]:
    try:
        courses = _course_kb_db.list_courses()
    except SystemExit as exc:
        # list_courses_sqlite() raises SystemExit (not a normal Exception)
        # when the course KB hasn't been seeded yet — convert it so a
        # missing-seed-data mistake surfaces as an ordinary 500 with a
        # clear message instead of tearing down the ASGI worker.
        raise RuntimeError(
            "Course knowledge base is not seeded yet. Run: "
            "python stores/course-knowledge-base/ingest.py"
        ) from exc
    if target_role is None:
        return courses
    return [c for c in courses if target_role in (c.get("target_roles") or [])]


def system_status() -> dict[str, Any]:
    return {
        "profile_store_backend": _profile_store.backend_name(),
        "path_store_backend": _path_store.backend_name(),
        "course_kb_backend": _course_kb_db.backend_name(),
        "taxonomy_store_backend": _taxonomy_store.backend_name(),
        "llm_configured": is_llm_configured(),
    }


# ---------------------------------------------------------------------------
# Auth (new in the login/multi-role rework)
# ---------------------------------------------------------------------------

def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {"id": user["id"], "email": user["email"], "display_name": user.get("display_name")}


def create_user(email: str, password: str, display_name: str | None) -> tuple[str, dict[str, Any]]:
    """Returns (access_token, public_user_dict). Raises ValueError if the
    email is already registered (caller maps this to a 409)."""
    user = _account_store.create_user(email, password, display_name)
    token = _auth_token.create_access_token(user["id"])
    return token, _public_user(user)


def authenticate_user(email: str, password: str) -> tuple[str, dict[str, Any]] | None:
    """Returns (access_token, public_user_dict), or None on bad credentials."""
    user = _account_store.get_user_by_email(email)
    if user is None or not _account_store.verify_password(password, user["password_hash"]):
        return None
    token = _auth_token.create_access_token(user["id"])
    return token, _public_user(user)


def get_user(user_id: str) -> dict[str, Any] | None:
    user = _account_store.get_user_by_id(user_id)
    return _public_user(user) if user else None


# ---------------------------------------------------------------------------
# Profile update (Settings / Explore Roles pages)
# ---------------------------------------------------------------------------

def update_profile_fields(learner_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Partial-updates a learner profile. Raises ValueError if no profile
    exists yet for this learner_id (caller maps this to a 404)."""
    profile = get_profile(learner_id)
    if profile is None:
        raise ValueError(f"No profile found for learner_id={learner_id}")
    for key, value in updates.items():
        if value is not None:
            profile[key] = value
    _profile_store.save_profile(profile)
    return get_profile(learner_id)


# ---------------------------------------------------------------------------
# Roles (Explore Roles page)
# ---------------------------------------------------------------------------

def list_roles() -> list[dict[str, Any]]:
    return _taxonomy_store.list_roles()


# ---------------------------------------------------------------------------
# Course detail / tree
# ---------------------------------------------------------------------------

def get_course(course_id: str) -> dict[str, Any] | None:
    return _course_kb_db.get_course(course_id)


def get_course_tree(target_role: str) -> dict[str, Any]:
    tiers = _taxonomy_store.compute_skill_tiers(target_role)
    dependencies = _taxonomy_store.get_dependencies(target_role)
    required_skills = _taxonomy_store.get_role_requirements(target_role)
    prereqs_by_skill: dict[str, list[str]] = {}
    for dep in dependencies:
        prereqs_by_skill.setdefault(dep["skill"], []).append(dep["prerequisite"])

    courses = list_courses(target_role)
    courses_by_skill: dict[str, list[dict[str, Any]]] = {}
    for course in courses:
        for skill in course.get("skills_taught") or []:
            courses_by_skill.setdefault(skill, []).append(
                {"id": course["id"], "title": course["title"], "provider": course["provider"]}
            )

    skills = [
        {
            "skill": req["skill"],
            "required_level": req["required_level"],
            "weight": req["weight"],
            "tier": tiers.get(req["skill"], 0),
            "prerequisites": prereqs_by_skill.get(req["skill"], []),
            "courses": courses_by_skill.get(req["skill"], []),
        }
        for req in required_skills
    ]
    return {"target_role": target_role, "skills": skills}


# ---------------------------------------------------------------------------
# Chatbot (general assistant)
# ---------------------------------------------------------------------------

def chat_reply(learner_id: str | None, message: str, history: list[dict[str, Any]]) -> str:
    context: dict[str, Any] | None = None
    if learner_id:
        profile = get_profile(learner_id)
        if profile is not None:
            target_role = profile.get("target_role") or DEFAULT_TARGET_ROLE
            remaining_titles = [s["title"] for s in get_path(learner_id)]
            context = {
                "target_role": target_role,
                "current_skills": profile.get("current_skills", []),
                "time_budget_hours_per_week": profile.get("time_budget_hours_per_week"),
                "remaining_path_step_titles": remaining_titles,
            }
    return _chat_assistant.chat_reply(message, history, context)
