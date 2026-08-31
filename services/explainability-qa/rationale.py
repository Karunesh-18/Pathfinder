"""generate_step_rationale — STUB implementation of rag_generate (per-step
rationale half).

Per explicit precedent set in services/intake-profiling/extract.py: no
ANTHROPIC_API_KEY is configured, so this is a template, not a real Claude
call. It still does what the plan's card 06 asks structurally — names the
skill gap a step closes and the profile signal that triggered it — just
with a fixed sentence template instead of generated language. Swap this
function for a real LLM call later; callers only see the returned string,
so nothing downstream needs to change.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

STUB_LLM_GENERATION = True

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def generate_step_rationale(step: dict[str, Any], gap: dict[str, Any], target_role: str) -> str:
    skill = step.get("skill_gap_addressed", "this skill")
    current = gap.get("current_level", "none")
    required = gap.get("required_level", "unspecified")
    priority = gap.get("priority_rank", "?")
    weight = gap.get("weight", "?")

    signal = (
        f"you didn't mention any experience with {skill} in your intake"
        if current in ("none", "unspecified")
        else f"you rated yourself '{current}' at {skill}"
    )

    return (
        f"{step.get('title', 'This course')} ({step.get('provider', 'unknown provider')}) "
        f"targets your {skill} gap: {signal}, and the {target_role} role needs "
        f"'{required}'-level {skill}. It's priority #{priority} in your plan "
        f"(weight {weight} out of the role's tracked requirements)."
    )


_SYSTEM_PROMPT = (
    "You are the explainability layer of a personalized learning path system. Given one "
    "step of a learner's plan and the skill gap it addresses, write a short (1-3 sentence), "
    "plain-language, encouraging rationale explaining why this course is in the learner's "
    "plan. Name the specific skill gap it closes and the profile signal that triggered it "
    "(what the learner said or didn't say about that skill). Do not invent facts beyond what "
    "is given below."
)


def generate_step_rationale_llm(step: dict[str, Any], gap: dict[str, Any], target_role: str) -> str:
    """Real implementation of rag_generate (per-step half), via Groq (see
    common/llm.py). Same signature and return type as
    generate_step_rationale() above."""
    from common.llm import chat_text

    user_prompt = (
        f"Target role: {target_role}\n"
        f"Course: {step.get('title')} ({step.get('provider')})\n"
        f"Skill this step addresses: {step.get('skill_gap_addressed')}\n"
        f"Required level for this role: {gap.get('required_level', 'unspecified')}\n"
        f"Learner's current level: {gap.get('current_level', 'none')}\n"
        f"Priority rank in the plan: #{gap.get('priority_rank', '?')}\n"
        f"Requirement weight: {gap.get('weight', '?')}"
    )
    return chat_text(_SYSTEM_PROMPT, user_prompt)
