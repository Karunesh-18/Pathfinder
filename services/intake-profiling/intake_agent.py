"""intake_agent.py — Intake & Profiling Agent orchestration.

Named intake_agent.py, not agent.py — "agent" is exactly the kind of
generic name every future reasoning-agent service (orchestrator,
explainability-qa, progress-feedback) will also want; see
profile_schema.py's docstring for why bare generic module names collide
once more than one gets imported in the same process.

Turns free-form learner text into a structured LearnerProfile: runs
profile_schema_extract (extract.py — currently a rule-based stub, see its
docstring for why), validates detected skills against
skills_taxonomy_lookup (taxonomy_lookup.py — currently derived from the
Course & Skills Knowledge Base, not a full graph), flags missing required
fields with follow-up questions ("asks follow-ups when it's
underspecified", per the plan), and persists the result via the Learner
Profile Store.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Project root first, so common.llm/common.env are importable no matter
# what import order follows below.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from common.llm import is_llm_configured  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import extract, extract_llm  # noqa: E402
from profile_schema import LearnerProfile  # noqa: E402
from taxonomy_lookup import lookup_skills_for_role  # noqa: E402

_LPS_PATH = Path(__file__).resolve().parents[2] / "stores" / "learner-profile-store"
if str(_LPS_PATH) not in sys.path:
    sys.path.insert(0, str(_LPS_PATH))
import profile_store as profile_db  # noqa: E402

# Only role currently seeded in the Course & Skills Knowledge Base (see
# stores/course-knowledge-base/seed_data_engineer.json). Once more roles
# are ingested, this should come from the learner's own stated target
# role instead of a fixed default.
DEFAULT_ROLE_FOR_TAXONOMY = "Data Engineer"

REQUIRED_FIELDS = ["target_role", "current_skills", "time_budget_hours_per_week", "format_preference"]

FOLLOW_UP_QUESTIONS = {
    "target_role": "What role or job are you aiming for?",
    "current_skills": "What skills or tools do you already know, and how comfortable are you with each?",
    "time_budget_hours_per_week": "About how many hours per week can you dedicate to learning?",
    "format_preference": "Do you prefer video courses, self-paced material, or live/cohort-based learning?",
}


def profile_from_text(raw_text: str, learner_id: str | None = None) -> LearnerProfile:
    known_skills = lookup_skills_for_role(DEFAULT_ROLE_FOR_TAXONOMY)

    if is_llm_configured():
        try:
            extracted = extract_llm(raw_text, known_skills)
        except Exception as exc:  # network error, bad JSON, rate limit, etc.
            print(f"[intake_agent] Groq call failed ({exc!r}); falling back to rule-based stub.")
            extracted = extract(raw_text, known_skills)
    else:
        extracted = extract(raw_text, known_skills)

    missing: list[str] = []
    if not extracted.get("target_role"):
        missing.append("target_role")
    if not extracted.get("current_skills"):
        missing.append("current_skills")
    if extracted.get("time_budget_hours_per_week") is None:
        missing.append("time_budget_hours_per_week")
    if not extracted.get("format_preference"):
        missing.append("format_preference")

    follow_ups = [FOLLOW_UP_QUESTIONS[field] for field in missing]

    profile = LearnerProfile(
        learner_id=learner_id or str(uuid.uuid4()),
        target_role=extracted.get("target_role"),
        current_skills=extracted.get("current_skills", []),
        completed_courses=extracted.get("completed_courses", []),
        time_budget_hours_per_week=extracted.get("time_budget_hours_per_week"),
        format_preference=extracted.get("format_preference"),
        missing_fields=missing,
        follow_up_questions=follow_ups,
        raw_text=raw_text,
        extraction_method=extracted.get("extraction_method", "rule-based-stub"),
    )

    profile_db.save_profile(profile.model_dump())
    return profile
