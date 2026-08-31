"""feedback_agent.py — Progress & Feedback Agent orchestration.

Per ARCHITECTURE.md Section 03, card 07: ingests completions, scores and
explicit feedback; updates the skill vector and preference weights;
triggers a re-plan when the gap picture has materially changed.

progress_ingest.py's free-text interpretation is a rule-based stub (see
its docstring). Everything after that — updating the LearnerProfile,
comparing total skill-gap score before and after, and deciding whether to
trigger a replan — is deterministic, matching the plan's own "Hybrid"
framing for this agent.

Named feedback_agent.py, not agent.py — see
services/intake-profiling/intake_agent.py's docstring for why.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress_ingest import interpret_progress_event  # noqa: E402
from progress_schema import ReplanResult  # noqa: E402

_PROFILESTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "learner-profile-store"
if str(_PROFILESTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PROFILESTORE_PATH))
import profile_store  # noqa: E402

_CKB_PATH = Path(__file__).resolve().parents[2] / "stores" / "course-knowledge-base"
if str(_CKB_PATH) not in sys.path:
    sys.path.insert(0, str(_CKB_PATH))
import db as course_kb_db  # noqa: E402

_SKILLGAP_PATH = Path(__file__).resolve().parents[2] / "services" / "skill-gap"
if str(_SKILLGAP_PATH) not in sys.path:
    sys.path.insert(0, str(_SKILLGAP_PATH))
from gap import compute_skill_gaps  # noqa: E402

_PATHCONSTRUCTION_PATH = Path(__file__).resolve().parents[2] / "services" / "path-construction"
if str(_PATHCONSTRUCTION_PATH) not in sys.path:
    sys.path.insert(0, str(_PATHCONSTRUCTION_PATH))
from build_path import build_path  # noqa: E402

_PATHSTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "path-store"
if str(_PATHSTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PATHSTORE_PATH))
import path_store  # noqa: E402

LEVEL_ORDER = {"none": 0, "unspecified": 0, "beginner": 1, "intermediate": 2, "advanced": 3}

# A replan is triggered when total gap score drops by at least this
# fraction of its pre-event value — the plan's "materially changed",
# made concrete as a deterministic threshold.
REPLAN_THRESHOLD_FRACTION = 0.05


def _bump_skill(current_skills: list[dict[str, str]], skill: str, new_level: str) -> list[dict[str, str]]:
    """Return current_skills with `skill` raised to at least `new_level`
    — a progress event never lowers a skill level."""
    updated = [dict(s) for s in current_skills]
    existing = next((s for s in updated if s["skill"] == skill), None)
    new_value = LEVEL_ORDER.get(new_level, 0)

    if existing is None:
        updated.append({"skill": skill, "level": new_level})
        return updated

    if new_value > LEVEL_ORDER.get(existing["level"], 0):
        existing["level"] = new_level
    return updated


def apply_progress_event(learner_id: str, target_role: str, raw_text: str) -> ReplanResult:
    profile = profile_store.get_profile(learner_id)
    if profile is None:
        raise ValueError(f"No profile found for learner_id={learner_id}")

    courses = course_kb_db.list_courses()
    known_skills = sorted({s for c in courses for s in (c.get("skills_taught") or [])})
    interpreted = interpret_progress_event(raw_text, known_skills, courses)

    gaps_before = compute_skill_gaps(profile, target_role)
    total_gap_before = sum(g.gap_score for g in gaps_before)

    updated_skills = profile.get("current_skills", [])
    updated_courses = list(profile.get("completed_courses", []))

    completed_course = interpreted["completed_course"]
    if completed_course:
        if completed_course["id"] not in updated_courses:
            updated_courses.append(completed_course["id"])
        # Completing a course is treated as reaching at least that
        # course's own level for every skill it teaches.
        for skill in completed_course.get("skills_taught", []) or []:
            updated_skills = _bump_skill(updated_skills, skill, completed_course.get("level") or "beginner")

    for mention in interpreted["skill_level_mentions"]:
        updated_skills = _bump_skill(updated_skills, mention["skill"], mention["level"])

    profile["current_skills"] = updated_skills
    profile["completed_courses"] = updated_courses
    profile_store.save_profile(profile)

    gaps_after = compute_skill_gaps(profile, target_role)
    total_gap_after = sum(g.gap_score for g in gaps_after)

    gap_drop = total_gap_before - total_gap_after
    should_replan = total_gap_before > 0 and (gap_drop / total_gap_before) >= REPLAN_THRESHOLD_FRACTION

    new_path_step_count = 0
    if should_replan:
        steps = build_path([g.model_dump() for g in gaps_after], target_role, profile.get("time_budget_hours_per_week"))
        path_store.save_path(learner_id, target_role, [s.model_dump() for s in steps])
        new_path_step_count = len(steps)

    return ReplanResult(
        learner_id=learner_id,
        completed_course_id=completed_course["id"] if completed_course else None,
        skill_updates=interpreted["skill_level_mentions"],
        total_gap_before=total_gap_before,
        total_gap_after=total_gap_after,
        replan_triggered=should_replan,
        new_path_step_count=new_path_step_count,
    )
