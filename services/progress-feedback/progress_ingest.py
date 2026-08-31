"""interpret_progress_event — STUB implementation of progress_ingest's
"vague self-rating" half.

Per ARCHITECTURE.md Section 03, card 07 (Hybrid: "LLM judgment only
interprets vague self-ratings; the gap math is deterministic"). No
ANTHROPIC_API_KEY is configured — same situation as
services/intake-profiling/extract.py — so this is rule-based: it detects a
mentioned course title (marks it completed) and skill-level language
(the same level-marker keyword approach extract.py uses for intake text,
applied here to progress/feedback text) rather than genuinely interpreting
free-form self-assessment. Swap for a real LLM call later; feedback_agent.py
only consumes the returned dict shape, so nothing downstream changes.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

STUB_LLM_INTERPRETATION = True

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_LEVEL_MARKERS = {
    "advanced": ["expert", "advanced", "very comfortable", "mastered", "confident"],
    "intermediate": ["comfortable", "solid", "good at", "better at", "improved"],
    "beginner": ["a bit better", "starting to get", "still learning"],
}

_COMPLETION_MARKERS = ["finished", "completed", "done with", "wrapped up"]
_LEVEL_RANK = {"beginner": 1, "intermediate": 2, "advanced": 3}


def _find_completed_course(text: str, courses: list[dict[str, Any]]) -> dict[str, Any] | None:
    lowered = text.lower()
    if not any(marker in lowered for marker in _COMPLETION_MARKERS):
        return None
    for course in courses:
        if course["title"].lower() in lowered:
            return course
    return None


def _find_skill_level_mentions(text: str, known_skills: list[str]) -> list[dict[str, str]]:
    """For each known skill, scan *every* occurrence in the text (not just
    the first — a skill mentioned twice, once as a bare noun and once with
    a level marker nearby, was silently missed when this only checked the
    first occurrence's window) and keep the strongest level marker found
    across all of them."""
    lowered = text.lower()
    mentions = []
    for skill in known_skills:
        skill_lower = skill.lower()
        best_level: str | None = None
        start = 0
        while True:
            idx = lowered.find(skill_lower, start)
            if idx == -1:
                break
            window = lowered[max(0, idx - 40) : idx + len(skill_lower) + 15]
            for level, markers in _LEVEL_MARKERS.items():
                if any(marker in window for marker in markers):
                    if best_level is None or _LEVEL_RANK[level] > _LEVEL_RANK[best_level]:
                        best_level = level
                    break
            start = idx + len(skill_lower)
        if best_level:
            mentions.append({"skill": skill, "level": best_level})
    return mentions


def interpret_progress_event(
    raw_text: str, known_skills: list[str], courses: list[dict[str, Any]]
) -> dict[str, Any]:
    """Returns {"completed_course": course_dict | None, "skill_level_mentions": [...], "raw_text": ...}."""
    return {
        "completed_course": _find_completed_course(raw_text, courses),
        "skill_level_mentions": _find_skill_level_mentions(raw_text, known_skills),
        "raw_text": raw_text,
    }


_SYSTEM_PROMPT = (
    "You interpret a learner's free-text progress update for a personalized learning path "
    "system. Given the update and the courses currently in their plan, identify:\n"
    "1. Which course (if any) they say they finished/completed — by its exact id from the "
    "list given.\n"
    "2. Any skill self-ratings they express — only for skills in the given allowed list, "
    "using their exact names.\n\n"
    "Return a JSON object with these exact keys:\n"
    '- completed_course_id: string (must be one of the given course ids) or null\n'
    '- skill_level_mentions: array of {"skill": <exact string from the allowed list>, '
    '"level": "beginner"|"intermediate"|"advanced"}\n\n'
    "Only report what's actually stated or clearly implied. Do not guess."
)


def interpret_progress_event_llm(
    raw_text: str, known_skills: list[str], courses: list[dict[str, Any]]
) -> dict[str, Any]:
    """Real implementation of progress_ingest's "vague self-rating" half,
    via Groq (see common/llm.py). Same return shape as
    interpret_progress_event() above."""
    from common.llm import chat_json

    course_options = [{"id": c["id"], "title": c["title"]} for c in courses]
    courses_by_id = {c["id"]: c for c in courses}

    user_prompt = (
        f"Progress update: {raw_text!r}\n\n"
        f"Courses currently in the plan: {course_options}\n\n"
        f"Allowed skill names: {known_skills}"
    )
    result = chat_json(_SYSTEM_PROMPT, user_prompt)

    completed_id = result.get("completed_course_id")
    completed_course = courses_by_id.get(completed_id) if completed_id else None

    mentions = [
        s
        for s in (result.get("skill_level_mentions") or [])
        if isinstance(s, dict) and s.get("skill") in known_skills
        and s.get("level") in ("beginner", "intermediate", "advanced")
    ]

    return {
        "completed_course": completed_course,
        "skill_level_mentions": mentions,
        "raw_text": raw_text,
    }
