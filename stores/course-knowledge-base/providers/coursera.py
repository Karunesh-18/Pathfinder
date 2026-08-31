"""Coursera provider adapter.

Per ARCHITECTURE.md Section 03 (card 04) and Section 06, the intended live
sources are the `coursera.search_courses` / `coursera.search_hands_on_learning`
MCP tools, with Coursera's Catalog API as the documented non-MCP fallback.

Neither is available in this environment: no coursera.* MCP tools are
registered (checked via tool search), and no Catalog API credentials exist
in this project. fetch() raises ProviderNotConfigured until one of those is
actually wired up — ingest.py then falls back to the hand-built rows tagged
provider="Coursera" in the interim. Nothing else in the pipeline changes
when this is filled in for real.
"""

from __future__ import annotations

from typing import Any

from .base import ProviderNotConfigured

name = "Coursera"


def fetch(target_role: str) -> list[dict[str, Any]]:
    # TODO: once a coursera.* MCP tool (or Catalog API key) is available,
    # call it here and normalize each result into the shape documented in
    # base.CourseProvider.fetch — id, title, provider="Coursera", url,
    # description, skills_taught, level, format, prerequisites.
    raise ProviderNotConfigured(
        "No Coursera MCP connector or Catalog API credentials configured."
    )
