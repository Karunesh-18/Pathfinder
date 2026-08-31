"""aggregate.py — Dashboard / Reporting Service.

Per ARCHITECTURE.md Section 03, card 08: aggregates profile, path and
progress into skill radar / milestone timeline / next-action views. Pure
aggregation, deterministic — no LLM call, no stub needed (unlike every
other service built in this project so far).

"progress log" (per the plan's card) isn't a separate store — the plan
only defines four stores (learner profile, skills taxonomy, course KB,
path), and the Progress & Feedback Agent (Phase 05) already writes
progress straight back into the LearnerProfile (completed_courses,
current_skills). This reads that, rather than inventing a fifth store the
plan never asked for.

Design note: the Path Store only ever holds the *remaining* plan — Path
Construction and the replan cycle both rebuild it fresh from unmet skill
gaps, so a course whose gap gets fully closed simply drops out rather than
being marked "done" in place. Cross-referencing completed_courses against
the current path would produce a misleading "0 of N complete" the moment a
replan prunes a finished course out, even right after real progress. This
keeps completed and remaining work as two separate lists instead —
completed_history (from the profile's completed_courses, looked up in the
Course KB) and remaining_timeline (the current path, verbatim) — and
normalizes overall progress against their combined hours.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dashboard_schema import (  # noqa: E402
    DashboardViewModel,
    HistoryItem,
    NextAction,
    SkillRadarPoint,
    SummaryStats,
    TimelineStep,
)

_PROFILESTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "learner-profile-store"
if str(_PROFILESTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PROFILESTORE_PATH))
import profile_store  # noqa: E402

_PATHSTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "path-store"
if str(_PATHSTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PATHSTORE_PATH))
import path_store  # noqa: E402

_TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "stores" / "skills-taxonomy-graph"
if str(_TAXONOMY_PATH) not in sys.path:
    sys.path.insert(0, str(_TAXONOMY_PATH))
import taxonomy_store  # noqa: E402

_CKB_PATH = Path(__file__).resolve().parents[2] / "stores" / "course-knowledge-base"
if str(_CKB_PATH) not in sys.path:
    sys.path.insert(0, str(_CKB_PATH))
import db as course_kb_db  # noqa: E402

LEVEL_VALUE = {"none": 0, "unspecified": 0, "beginner": 1, "intermediate": 2, "advanced": 3}


def _skill_radar(profile: dict[str, Any], target_role: str) -> list[SkillRadarPoint]:
    requirements = taxonomy_store.get_role_requirements(target_role)
    current_by_skill = {s["skill"]: s["level"] for s in profile.get("current_skills", [])}
    return [
        SkillRadarPoint(
            skill=req["skill"],
            required_level=req["required_level"],
            current_level=current_by_skill.get(req["skill"], "none"),
            required_value=LEVEL_VALUE[req["required_level"]],
            current_value=LEVEL_VALUE.get(current_by_skill.get(req["skill"], "none"), 0),
        )
        for req in requirements
    ]


def _completed_history(profile: dict[str, Any]) -> list[HistoryItem]:
    completed_ids = set(profile.get("completed_courses", []))
    if not completed_ids:
        return []
    courses_by_id = {c["id"]: c for c in course_kb_db.list_courses()}
    return [
        HistoryItem(
            course_id=cid,
            title=courses_by_id[cid]["title"],
            provider=courses_by_id[cid]["provider"],
            estimated_hours=courses_by_id[cid].get("estimated_hours") or 0,
        )
        for cid in completed_ids
        if cid in courses_by_id  # a completed course could in principle predate the current KB seed
    ]


def _remaining_timeline(steps: list[dict[str, Any]]) -> list[TimelineStep]:
    return [
        TimelineStep(
            step_index=s["step_index"],
            title=s["title"],
            provider=s["provider"],
            milestone=bool(s["milestone"]),
            cumulative_hours=s["cumulative_hours"],
            estimated_completion_week=s["estimated_completion_week"],
        )
        for s in steps
    ]


def _next_action(steps: list[dict[str, Any]]) -> NextAction | None:
    if not steps:
        return None
    first = steps[0]
    return NextAction(
        step_index=first["step_index"],
        title=first["title"],
        provider=first["provider"],
        skill_gap_addressed=first["skill_gap_addressed"],
    )


def _summary(history: list[HistoryItem], timeline: list[TimelineStep]) -> SummaryStats:
    completed_hours = sum(h.estimated_hours for h in history)
    remaining_hours = timeline[-1].cumulative_hours if timeline else 0.0
    total_hours = completed_hours + remaining_hours
    progress_pct = (completed_hours / total_hours * 100) if total_hours else 0.0
    weeks_remaining = timeline[-1].estimated_completion_week if timeline else 0
    return SummaryStats(
        completed_courses=len(history),
        remaining_steps=len(timeline),
        completed_hours=completed_hours,
        remaining_hours=remaining_hours,
        overall_progress_pct=progress_pct,
        weeks_remaining=weeks_remaining,
    )


def build_dashboard(learner_id: str, target_role: str) -> DashboardViewModel:
    profile = profile_store.get_profile(learner_id)
    if profile is None:
        raise ValueError(f"No profile found for learner_id={learner_id}")
    steps = path_store.get_path(learner_id)

    history = _completed_history(profile)
    timeline = _remaining_timeline(steps)

    return DashboardViewModel(
        learner_id=learner_id,
        target_role=target_role,
        skill_radar=_skill_radar(profile, target_role),
        completed_history=history,
        remaining_timeline=timeline,
        next_action=_next_action(steps),
        summary=_summary(history, timeline),
    )
