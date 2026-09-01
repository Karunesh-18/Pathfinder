"""chat_assistant.py — the general-purpose chatbot backing /api/chat.

New in the login/multi-role rework. Deliberately placed in backend/, not
as a new service under services/: it isn't a pipeline stage (the 8-agent
roster in ARCHITECTURE.md/CLAUDE.md is specifically the learning-path
pipeline), doesn't need its own store, and doesn't need
service_bridge.py's sys.path-bridging dance beyond the optional
profile/path context service_bridge.chat_reply() already assembles.

Follows the same real-LLM-call + rule-based-stub dispatch shape as
services/explainability-qa/qa.py + qa_llm.py + explain_agent.py
(CLAUDE.md Convention #3): a *_stub function, an *_llm function using
common.llm.chat_text, and dispatch logic gated on is_llm_configured() with
a try/except fallback that never lets an LLM failure crash the request.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from common.llm import is_llm_configured  # noqa: E402

_STUB_REPLIES: list[tuple[tuple[str, ...], str]] = [
    (("hi", "hello", "hey"), "Hi! I'm the PathFinder assistant. Ask me about your learning plan, courses, or how the recommender works."),
    (("what is pathfinder", "what is this", "what can you do"),
     "PathFinder builds you a personalized learning path toward a target tech role, tracks your progress, and explains why each course is in your plan."),
    (("how do i build a roadmap", "how do i start", "how does onboarding work"),
     "Head to Onboarding and describe your goal in your own words — your background, target role, time budget, and preferred course format. PathFinder extracts a profile and builds an ordered course roadmap from it."),
    (("how do i update", "report progress", "mark complete"),
     "Use the progress update form on your Dashboard to report a completed course or new skill — PathFinder will re-check your plan and replan if your gaps changed materially."),
]


def chat_reply_stub(message: str, history: list[dict[str, Any]], context: dict[str, Any] | None) -> str:
    m = message.lower()
    for keywords, reply in _STUB_REPLIES:
        if any(k in m for k in keywords):
            return reply
    return (
        "I'm a simple rule-based stand-in right now — no LLM is configured, so I only "
        "recognize a few topics (what PathFinder is, how onboarding works, how to report "
        "progress). Set GROQ_API_KEY to replace this with a real open-ended conversation."
    )


_SYSTEM_PROMPT = (
    "You are the PathFinder assistant, a friendly general-purpose helper inside a "
    "personalized learning-path app for tech careers. Answer the learner's question "
    "conversationally. If a JSON 'learner context' block is given below, you may use it "
    "to personalize your answer (their target role, current skills, time budget, and "
    "remaining courses in their plan) — but you are not limited to it; you can also "
    "answer general questions about careers, skills, or how to learn something. Keep "
    "answers concise and friendly. If you don't know something, say so plainly."
)


def chat_reply_llm(message: str, history: list[dict[str, Any]], context: dict[str, Any] | None) -> str:
    from common.llm import chat_text

    parts = []
    if context is not None:
        parts.append(f"Learner context (JSON):\n{json.dumps(context, indent=2)}")
    if history:
        transcript = "\n".join(f"{turn['role']}: {turn['text']}" for turn in history)
        parts.append(f"Conversation so far:\n{transcript}")
    parts.append(f"Learner's new message: {message}")
    user_prompt = "\n\n".join(parts)
    return chat_text(_SYSTEM_PROMPT, user_prompt)


def chat_reply(message: str, history: list[dict[str, Any]], context: dict[str, Any] | None) -> str:
    if is_llm_configured():
        try:
            return chat_reply_llm(message, history, context)
        except Exception as exc:  # network error, rate limit, etc.
            print(f"[chat_assistant] Groq call failed ({exc!r}); falling back to rule-based stub.")
    return chat_reply_stub(message, history, context)
