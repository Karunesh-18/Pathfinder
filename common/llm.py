"""Groq-backed LLM helper — the real reasoning-agent backend, alongside
the rule-based stubs each reasoning-adjacent service (intake-profiling,
explainability-qa, progress-feedback) built while no LLM was configured.

ARCHITECTURE.md's stack section names the Claude Agent SDK, but explicitly
frames the stack as "a starting point, not a commitment — swap anything
the team already has strong opinions about" (Section 06). Groq doesn't
host Claude, so this goes through Groq's own (OpenAI-compatible) chat
completions API via the official `groq` package, not the Claude Agent SDK.

Reads GROQ_API_KEY the same way the stores read SUPABASE_DB_URL:
environment variable or project-root .env (common/env.py), never from
chat. is_llm_configured() lets each service's agent module choose between
its real LLM call and its rule-based stub at runtime — nothing breaks if
the key isn't set, and a failed call falls back to the stub rather than
crashing the pipeline (see each agent's dispatch logic).
"""

from __future__ import annotations

import json
import os
from typing import Any

from common.env import load_env_file

# A capable general-purpose model on Groq's currently supported lineup —
# verified live against client.models.list() rather than assumed, since
# Groq's lineup changes (llama-3.3-70b-versatile, once the default here,
# 404s on this account as of 2026-08-31). Override per-call if a task
# needs something else.
DEFAULT_MODEL = "openai/gpt-oss-120b"

_client = None


def is_llm_configured() -> bool:
    load_env_file()
    return bool(os.environ.get("GROQ_API_KEY"))


def _get_client():
    global _client
    if _client is not None:
        return _client
    load_env_file()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    from groq import Groq  # imported lazily so stub-only usage doesn't need the package

    _client = Groq(api_key=api_key)
    return _client


def chat_text(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.3) -> str:
    """Plain-text completion — for generation tasks (rationale, Q&A)."""
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def chat_json(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.1) -> dict[str, Any]:
    """JSON-mode completion — for structured extraction tasks (intake,
    progress interpretation). Raises if the model doesn't return valid
    JSON; callers should catch and fall back to their stub."""
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
                + "\n\nRespond with ONLY a single valid JSON object. No markdown code fences, no commentary before or after.",
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
