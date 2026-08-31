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

SEED_PATH = Path(__file__).resolve().parent.parent / "seed_data_engineer.json"


def _load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def fetch_for_provider(target_role: str, provider_name: str) -> list[dict[str, Any]]:
    """Return the hand-built rows tagged as coming from `provider_name`."""
    seed = _load_seed()
    if seed["target_role"] != target_role:
        return []
    return [c for c in seed["courses"] if c["provider"] == provider_name]
