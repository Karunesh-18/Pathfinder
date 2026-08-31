"""profile_schema_extract — STUB implementation.

Per explicit user choice: this is a rule-based/keyword placeholder standing
in for a real Claude call. The plan (ARCHITECTURE.md Section 03, card 02)
specifies this as a reasoning-agent tool, and the stack section names the
Claude Agent SDK for reasoning agents — but no ANTHROPIC_API_KEY is
configured in this environment, so nothing here is actually calling an
LLM.

Swap extract() for a real LLM call the moment a key is available — same
input/output contract (raw_text + known_skills in, the same dict shape
out) — and nothing in agent.py, taxonomy_lookup.py, or the store needs to
change. Every profile this produces is stamped
extraction_method="rule-based-stub" so stub output is never mistaken for
the real thing downstream.

Known, deliberate weaknesses of this stub (a real LLM call would do all of
this far better): only detects skills that are literal substrings of the
input text; role extraction is a handful of regex patterns, not open-ended
understanding; skill-level detection is a small keyword window, easily
fooled by negation ("I don't know much SQL" would still register SQL).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

STUB_LLM_EXTRACTION = True

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_ROLE_PATTERNS = [
    r"(?:become|be|work as|targeting|aiming (?:for|to be)) (?:an?|the)? ?([a-zA-Z][a-zA-Z\s]{2,40}?)(?:[.,]| role| position| job|$)",
    r"(?:break into|breaking into|get into|getting into) ([a-zA-Z][a-zA-Z\s]{2,40}?)(?:[.,]|$)",
]

_LEVEL_MARKERS = {
    "advanced": ["expert", "experienced", "advanced", "strong", "proficient", "senior"],
    "beginner": ["some", "basic", "a bit", "a little", "beginner", "new to", "just started", "little"],
    "intermediate": ["intermediate", "comfortable", "decent", "solid", "good"],
}

_TIME_BUDGET_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:a|per|/)\s*week", re.IGNORECASE)

_FORMAT_KEYWORDS = {
    "video": ["video", "watch", "youtube"],
    "self-paced": ["self-paced", "self paced", "my own pace", "own schedule"],
    "cohort": ["cohort", "live class", "instructor-led", "instructor led", "bootcamp"],
    "reading": ["reading", "text-based", "articles", "docs"],
}


def _extract_target_role(text: str) -> str | None:
    for pattern in _ROLE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            role = re.sub(r"\s+", " ", m.group(1).strip())
            return role.title()
    return None


def _extract_skill_level(text: str, skill: str) -> str:
    idx = text.lower().find(skill.lower())
    if idx == -1:
        return "unspecified"
    window = text[max(0, idx - 40) : idx + len(skill) + 10].lower()
    for level, markers in _LEVEL_MARKERS.items():
        if any(marker in window for marker in markers):
            return level
    return "unspecified"


def _extract_skills(text: str, known_skills: list[str]) -> list[dict[str, str]]:
    lowered = text.lower()
    return [
        {"skill": skill, "level": _extract_skill_level(text, skill)}
        for skill in known_skills
        if skill.lower() in lowered
    ]


def _extract_time_budget(text: str) -> float | None:
    m = _TIME_BUDGET_RE.search(text)
    return float(m.group(1)) if m else None


def _extract_format_preference(text: str) -> str | None:
    lowered = text.lower()
    for fmt, keywords in _FORMAT_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return fmt
    return None


def extract(raw_text: str, known_skills: list[str]) -> dict[str, Any]:
    """Rule-based stand-in for profile_schema_extract. Returns a dict
    matching the LearnerProfile field shape (see schema.py), minus
    learner_id/missing_fields/follow_up_questions, which agent.py fills in."""
    return {
        "target_role": _extract_target_role(raw_text),
        "current_skills": _extract_skills(raw_text, known_skills),
        "time_budget_hours_per_week": _extract_time_budget(raw_text),
        "format_preference": _extract_format_preference(raw_text),
        "completed_courses": [],  # stub never infers this from free text
        "extraction_method": "rule-based-stub",
    }


_SYSTEM_PROMPT = (
    "You are an intake-profiling assistant for a personalized learning path system. "
    "Extract a structured learner profile from the learner's free-form message.\n\n"
    "Only report skills from this exact allowed list (case-sensitive, use these exact "
    "strings, never invent or paraphrase a skill name): {known_skills}\n\n"
    "Return a JSON object with these exact keys:\n"
    '- target_role: string or null — the job/role the learner is aiming for, in their own words\n'
    '- current_skills: array of {{"skill": <exact string from the allowed list>, '
    '"level": "beginner"|"intermediate"|"advanced"}} — only skills from the allowed list the '
    "learner actually indicates some experience with\n"
    "- time_budget_hours_per_week: number or null\n"
    '- format_preference: string or null (e.g. "video", "self-paced", "cohort", "reading")\n\n'
    "Only extract what's actually stated or clearly implied. Do not guess or invent details."
)


def extract_llm(raw_text: str, known_skills: list[str]) -> dict[str, Any]:
    """Real implementation of profile_schema_extract, via Groq (see
    common/llm.py). Same return shape as extract() above; current_skills
    is filtered to the allowed vocabulary in case the model hallucinates
    a skill name outside it, since downstream taxonomy matching is
    exact-string."""
    from common.llm import chat_json

    result = chat_json(_SYSTEM_PROMPT.format(known_skills=known_skills), raw_text)
    return {
        "target_role": result.get("target_role"),
        "current_skills": [
            s for s in (result.get("current_skills") or [])
            if isinstance(s, dict) and s.get("skill") in known_skills and s.get("level") in
            ("beginner", "intermediate", "advanced")
        ],
        "time_budget_hours_per_week": result.get("time_budget_hours_per_week"),
        "format_preference": result.get("format_preference"),
        "completed_courses": [],
        "extraction_method": "groq-llm",
    }
