"""answer_question — STUB implementation of rag_generate (free-form Q&A
half).

Rule-based: matches a small set of question intents by keyword and
answers from the already-assembled path/profile/gap context — no retrieval
step, no LLM call. No ANTHROPIC_API_KEY is configured (same situation as
services/intake-profiling/extract.py and rationale.py in this directory).
Recognizes: duration/timeline questions, "why is X in my plan" questions
(via generate_step_rationale), "what's first/prerequisite" questions, and
milestone questions. Anything else gets an honest "I don't understand
that" answer naming what it does understand, rather than a guessed one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from rationale import generate_step_rationale

STUB_LLM_GENERATION = True

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_UNDERSTOOD_PATTERNS = (
    "duration/timeline ('how long will this take')",
    "rationale for a specific skill or course ('why is SQL in my plan')",
    "what comes first ('what should I start with')",
    "milestones ('what are the milestones')",
)


def answer_question(
    question: str,
    steps: list[dict[str, Any]],
    profile: dict[str, Any],
    gaps: list[dict[str, Any]],
    target_role: str,
) -> str:
    q = question.lower()

    if any(k in q for k in ["how long", "how many weeks", "when will i", "total time", "duration"]):
        if not steps:
            return "There's no path yet to estimate a duration for."
        last = steps[-1]
        weekly = profile.get("time_budget_hours_per_week") or 5.0
        return (
            f"At your current pace ({weekly} hrs/week), the full plan is about "
            f"{last['cumulative_hours']:.0f} hours, projected to finish around "
            f"week {last['estimated_completion_week']}."
        )

    if any(k in q for k in ["why", "reason", "rationale"]):
        for step in steps:
            if step["skill_gap_addressed"].lower() in q:
                gap = next((g for g in gaps if g["skill"] == step["skill_gap_addressed"]), {})
                return generate_step_rationale(step, gap, target_role)
        return "Ask me about a specific course or skill (e.g. 'why is SQL in my plan?') and I can explain why it's there."

    if any(k in q for k in ["prerequisite", "before", "first", "start"]):
        if steps:
            first = steps[0]
            return f"Your plan starts with {first['title']} ({first['provider']}), addressing {first['skill_gap_addressed']}."
        return "There's no path yet to describe a starting point for."

    if "milestone" in q:
        milestones = [s for s in steps if s.get("milestone")]
        if milestones:
            names = ", ".join(s["title"] for s in milestones)
            return f"Your milestones are: {names}."
        return "No milestones are set in this plan yet."

    understood = "; ".join(_UNDERSTOOD_PATTERNS)
    return (
        "This is a rule-based stand-in for a real Q&A agent - no LLM is currently "
        f"configured, so it only recognizes a few question patterns: {understood}. "
        "Try rephrasing around one of those, or set GROQ_API_KEY to replace this with a real answer."
    )


_SYSTEM_PROMPT = (
    "You are the Q&A layer of a personalized learning path system. Answer the learner's "
    "question using ONLY the plan context given below (their remaining path steps, their "
    "profile, and their ranked skill gaps for the target role). Be concise and specific. "
    "If the question can't be answered from the given context, say so plainly rather than "
    "guessing or inventing details."
)


def answer_question_llm(
    question: str,
    steps: list[dict[str, Any]],
    profile: dict[str, Any],
    gaps: list[dict[str, Any]],
    target_role: str,
) -> str:
    """Real implementation of rag_generate (free-form Q&A half), via Groq
    (see common/llm.py). Same signature and return type as
    answer_question() above."""
    from common.llm import chat_text

    context = {
        "target_role": target_role,
        "time_budget_hours_per_week": profile.get("time_budget_hours_per_week"),
        "remaining_path_steps": [
            {
                "step_index": s["step_index"],
                "title": s["title"],
                "provider": s["provider"],
                "milestone": bool(s.get("milestone")),
                "cumulative_hours": s.get("cumulative_hours"),
                "estimated_completion_week": s.get("estimated_completion_week"),
                "skill_gap_addressed": s.get("skill_gap_addressed"),
            }
            for s in steps
        ],
        "ranked_skill_gaps": gaps,
    }
    user_prompt = f"Plan context (JSON):\n{json.dumps(context, indent=2)}\n\nLearner's question: {question}"
    return chat_text(_SYSTEM_PROMPT, user_prompt)
