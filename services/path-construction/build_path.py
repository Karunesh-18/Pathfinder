"""Path Construction Service — build_path orchestration.

Per ARCHITECTURE.md Section 03, card 05: builds the prerequisite graph
across chosen candidates, topologically sorts it, inserts milestone
checkpoints, and fits the sequence to the learner's time budget.
Deterministic — no LLM call anywhere in this file.

Pipeline:
  1. For each ranked SkillGap, pick the best-fit, not-yet-used course from
     the Course & Skills Knowledge Base that teaches that skill, via
     tfidf_rank (services/retrieval-ranking) — the same general-purpose
     ranker built in Phase 02, reused here rather than duplicated.
  2. Translate the Skills Taxonomy Graph's skill-level dependency edges
     into course-level edges, for just the courses actually selected.
  3. dag_builder + topo_sort (dag.py) order those courses, breaking ties
     by skill-gap priority rank.
  4. Walk the ordered list accumulating estimated_hours, flag a step as a
     milestone at each 25/50/75/100% cumulative-hours threshold, and
     project a completion week from the learner's weekly time budget (or
     DEFAULT_WEEKLY_HOURS if unspecified).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dag import dag_builder, topo_sort  # noqa: E402
from pathconstruction_schema import LearningPathStep  # noqa: E402

_CKB_PATH = Path(__file__).resolve().parents[2] / "stores" / "course-knowledge-base"
if str(_CKB_PATH) not in sys.path:
    sys.path.insert(0, str(_CKB_PATH))
import db as course_kb_db  # noqa: E402

_RANK_PATH = Path(__file__).resolve().parents[2] / "services" / "retrieval-ranking"
if str(_RANK_PATH) not in sys.path:
    sys.path.insert(0, str(_RANK_PATH))
from rank import tfidf_rank  # noqa: E402

_TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "stores" / "skills-taxonomy-graph"
if str(_TAXONOMY_PATH) not in sys.path:
    sys.path.insert(0, str(_TAXONOMY_PATH))
import taxonomy_store  # noqa: E402

# Used only when the learner's time_budget_hours_per_week is unspecified
# (e.g. an underspecified intake, per Phase 01's follow-up-question path).
DEFAULT_WEEKLY_HOURS = 5.0


def _select_candidate_courses(gaps: list[dict[str, Any]], courses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """For each skill gap, in priority order, pick the best-fit course
    that teaches that skill and hasn't already been claimed by an earlier
    (higher-priority) gap. Returns {skill: course_dict}."""
    selected: dict[str, dict[str, Any]] = {}
    used_course_ids: set[str] = set()

    for gap in gaps:
        skill = gap["skill"]
        candidates = [
            c for c in courses
            if skill in (c.get("skills_taught") or []) and c["id"] not in used_course_ids
        ]
        if not candidates:
            continue  # no course in the KB currently teaches this skill — a real gap in coverage
        query = f"learn {skill} at {gap['required_level']} level"
        ranked = tfidf_rank(query, candidates)
        best_course, _score = ranked[0]
        selected[skill] = best_course
        used_course_ids.add(best_course["id"])

    return selected


def _course_level_edges(
    selected: dict[str, dict[str, Any]], skill_dependencies: list[dict[str, str]]
) -> list[tuple[str, str]]:
    """Translate skill-level dependency edges into course-id edges, for
    just the skills that actually got a selected course."""
    edges: list[tuple[str, str]] = []
    for dep in skill_dependencies:
        skill, prerequisite = dep["skill"], dep["prerequisite"]
        if skill in selected and prerequisite in selected:
            edges.append((selected[prerequisite]["id"], selected[skill]["id"]))
    return edges


def build_path(
    gaps: list[dict[str, Any]],
    target_role: str,
    time_budget_hours_per_week: float | None,
) -> list[LearningPathStep]:
    # Filter to this role's courses before candidate selection. Harmless
    # to skip when only one role was ever seeded (every course WAS that
    # role), but with multiple roles sharing one courses table, an
    # unfiltered list lets a same-named skill (e.g. "Python") pull in a
    # course tagged for a different role entirely — a real regression
    # caught during the multi-role rework's regression testing.
    courses = [c for c in course_kb_db.list_courses() if target_role in (c.get("target_roles") or [])]
    selected = _select_candidate_courses(gaps, courses)
    if not selected:
        return []

    id_to_course = {c["id"]: c for c in selected.values()}
    skill_by_course_id = {c["id"]: skill for skill, c in selected.items()}
    course_ids = list(id_to_course.keys())

    priority_by_skill = {g["skill"]: g["priority_rank"] for g in gaps}
    tie_break = {cid: priority_by_skill.get(skill_by_course_id[cid], 999) for cid in course_ids}

    skill_dependencies = taxonomy_store.get_dependencies(target_role)
    edges = _course_level_edges(selected, skill_dependencies)
    adjacency = dag_builder(course_ids, edges)

    try:
        ordered_ids = topo_sort(course_ids, adjacency, tie_break=tie_break)
    except ValueError:
        # A cycle in the hand-curated dependency graph shouldn't happen,
        # but fall back to pure gap-priority order rather than failing
        # the whole path if it ever does.
        ordered_ids = sorted(course_ids, key=lambda cid: tie_break.get(cid, 999))

    weekly_budget = time_budget_hours_per_week or DEFAULT_WEEKLY_HOURS
    total_hours = sum((id_to_course[cid].get("estimated_hours") or 0) for cid in ordered_ids)
    milestone_thresholds = [total_hours * frac for frac in (0.25, 0.5, 0.75, 1.0)] if total_hours else []

    steps: list[LearningPathStep] = []
    cumulative_hours = 0.0
    next_threshold_idx = 0

    for i, cid in enumerate(ordered_ids, start=1):
        course = id_to_course[cid]
        hours = course.get("estimated_hours") or 0
        cumulative_hours += hours

        is_milestone = False
        while next_threshold_idx < len(milestone_thresholds) and cumulative_hours >= milestone_thresholds[next_threshold_idx]:
            is_milestone = True
            next_threshold_idx += 1

        steps.append(
            LearningPathStep(
                step_index=i,
                course_id=cid,
                title=course["title"],
                provider=course["provider"],
                skill_gap_addressed=skill_by_course_id[cid],
                milestone=is_milestone,
                estimated_hours=hours,
                cumulative_hours=cumulative_hours,
                estimated_completion_week=math.ceil(cumulative_hours / weekly_budget) if weekly_budget else None,
            )
        )

    return steps
