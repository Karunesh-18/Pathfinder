"""explain_agent.py — Explainability & Q&A Agent orchestration.

Per ARCHITECTURE.md Section 03, card 06: generates a plain-language
rationale per step, naming the skill gap it closes and the profile signal
that triggered it; answers free-form learner questions about the plan.

Both halves (rationale.py, qa.py) are rule-based stubs standing in for
rag_generate — see their docstrings. This file's job is just assembling
the real context they run against: the stored LearningPath (path_store),
the stored LearnerProfile (profile_store), and a freshly recomputed
SkillGap list (services/skill-gap — not persisted anywhere, so it's
recomputed here exactly as services/path-construction/test_harness.py
does).

Named explain_agent.py, not agent.py — see
services/intake-profiling/intake_agent.py's docstring for why.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from common.llm import is_llm_configured  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa import answer_question, answer_question_llm  # noqa: E402
from rationale import generate_step_rationale, generate_step_rationale_llm  # noqa: E402

_PATHSTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "path-store"
if str(_PATHSTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PATHSTORE_PATH))
import path_store  # noqa: E402

_PROFILESTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "learner-profile-store"
if str(_PROFILESTORE_PATH) not in sys.path:
    sys.path.insert(0, str(_PROFILESTORE_PATH))
import profile_store  # noqa: E402

_SKILLGAP_PATH = Path(__file__).resolve().parents[2] / "services" / "skill-gap"
if str(_SKILLGAP_PATH) not in sys.path:
    sys.path.insert(0, str(_SKILLGAP_PATH))
from gap import compute_skill_gaps  # noqa: E402


def _load_context(learner_id: str, target_role: str) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    steps = path_store.get_path(learner_id)
    profile = profile_store.get_profile(learner_id)
    if profile is None:
        raise ValueError(f"No profile found for learner_id={learner_id}")
    gaps = [g.model_dump() for g in compute_skill_gaps(profile, target_role)]
    return steps, profile, gaps


def _rationale_for(step: dict[str, Any], gap: dict[str, Any], target_role: str) -> str:
    if is_llm_configured():
        try:
            return generate_step_rationale_llm(step, gap, target_role)
        except Exception as exc:  # network error, rate limit, etc.
            print(f"[explain_agent] Groq call failed ({exc!r}); falling back to rule-based stub.")
    return generate_step_rationale(step, gap, target_role)


def explain_path(learner_id: str, target_role: str) -> list[dict[str, Any]]:
    """Returns [{"step": ..., "rationale": "..."}] for every step in the
    learner's stored path."""
    steps, _profile, gaps = _load_context(learner_id, target_role)
    gap_by_skill = {g["skill"]: g for g in gaps}

    explained = []
    for step in steps:
        gap = gap_by_skill.get(step["skill_gap_addressed"], {})
        rationale = _rationale_for(step, gap, target_role)
        explained.append({"step": step, "rationale": rationale})
    return explained


def ask(learner_id: str, target_role: str, question: str) -> str:
    steps, profile, gaps = _load_context(learner_id, target_role)
    if is_llm_configured():
        try:
            return answer_question_llm(question, steps, profile, gaps, target_role)
        except Exception as exc:
            print(f"[explain_agent] Groq call failed ({exc!r}); falling back to rule-based stub.")
    return answer_question(question, steps, profile, gaps, target_role)
