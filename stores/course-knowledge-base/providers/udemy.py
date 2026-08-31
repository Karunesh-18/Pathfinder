"""Udemy provider adapter.

Per ARCHITECTURE.md Section 03 (card 04) and Section 06, the intended live
sources are the `udemy.search_courses` / `udemy.get_course_curriculum` MCP
tools (Udemy Business), with Udemy's Affiliate API as the documented
non-MCP fallback. Section 07 also flags that the Business connector likely
only reflects an org's licensed catalog, not the full public marketplace —
worth re-checking once this is actually implemented.

Neither is available in this environment: no udemy.* MCP tools are
registered (checked via tool search), and no Affiliate API credentials
exist in this project. fetch() raises ProviderNotConfigured until one of
those is wired up — ingest.py then falls back to the hand-built rows tagged
provider="Udemy" in the interim.
"""

from __future__ import annotations

from typing import Any

from .base import ProviderNotConfigured

name = "Udemy"


def fetch(target_role: str) -> list[dict[str, Any]]:
    # TODO: once a udemy.* MCP tool (or Affiliate API key) is available,
    # call it here and normalize each result into the shape documented in
    # base.CourseProvider.fetch — id, title, provider="Udemy", url,
    # description, skills_taught, level, format, prerequisites.
    raise ProviderNotConfigured(
        "No Udemy MCP connector or Affiliate API credentials configured."
    )
