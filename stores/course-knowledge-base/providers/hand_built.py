"""Hand-built sample provider — the interim stand-in for whichever
platform(s) don't have a live connector configured yet.

This is not a "platform" of its own; it's what ingest.py falls back to when
a real provider adapter (coursera.py, udemy.py, or a future one) raises
ProviderNotConfigured. It loads seed_data_engineer.json, which already
tags each course with its real provider name, and returns just the subset
matching whichever provider asked for a fallback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

name = "hand-built-sample"

_KB_DIR = Path(__file__).resolve().parent.parent

# One seed file per role. New roles added for the multi-role rework go
# here — see stores/course-knowledge-base/ingest.py's ROLE_SEEDS, which
# must list the same role names.
SEED_FILES = {
    "Data Engineer": _KB_DIR / "seed_data_engineer.json",
    "Data Scientist": _KB_DIR / "seed_data_scientist.json",
    "ML Engineer": _KB_DIR / "seed_ml_engineer.json",
    "Frontend Developer": _KB_DIR / "seed_frontend_developer.json",
}


def _load_seed(target_role: str) -> dict[str, Any] | None:
    seed_path = SEED_FILES.get(target_role)
    if seed_path is None or not seed_path.exists():
        return None
    return json.loads(seed_path.read_text(encoding="utf-8"))


def fetch_for_provider(target_role: str, provider_name: str) -> list[dict[str, Any]]:
    """Return the hand-built rows tagged as coming from `provider_name`."""
    seed = _load_seed(target_role)
    if seed is None or seed["target_role"] != target_role:
        return []
    return [c for c in seed["courses"] if c["provider"] == provider_name]
