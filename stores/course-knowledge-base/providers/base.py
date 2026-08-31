"""Provider adapter contract for the Course & Skills Knowledge Base.

Every course source — a live MCP connector, a REST API fallback, or the
hand-built sample set standing in for either right now — implements this
same interface. ingest.py loops over a list of registered providers and
doesn't care which kind it's talking to. Adding a new platform (edX,
LinkedIn Learning, Pluralsight, whatever comes up) means writing one new
adapter module in this package and registering it in ingest.py — nothing
else in the pipeline (ingest.py's SQLite write, rank.py, test_harness.py)
needs to change, since they all consume the same normalized row shape
regardless of source.
"""

from __future__ import annotations

from typing import Any, Protocol


class ProviderNotConfigured(Exception):
    """Raised by a provider adapter when it has no working live connection
    right now (no MCP tool registered, no API credentials, etc.).

    This is a deliberate signal, not a failure: ingest.py catches it and
    falls back to the hand-built provider's rows tagged with that platform's
    name, so one unconfigured platform doesn't take down the whole run, and
    "not configured yet" stays visibly distinct from "configured but found
    nothing for this role".
    """


class CourseProvider(Protocol):
    """The interface every providers/<name>.py module must satisfy.

    A module, not a class, is the actual unit here — see providers/coursera.py
    and providers/udemy.py for the concrete shape: a module-level `name` and
    a module-level `fetch(target_role)` function are enough. This Protocol
    documents the contract; nothing enforces it structurally beyond that.
    """

    name: str  # must match the `provider` column, e.g. "Coursera", "Udemy"

    def fetch(self, target_role: str) -> list[dict[str, Any]]:
        """Return normalized course dicts for `target_role`.

        Each dict must carry: id, title, provider, url, description,
        skills_taught (list[str]), level, format, prerequisites (list[str])
        — the same shape schema.sql defines and seed_data_engineer.json
        already uses. Raise ProviderNotConfigured instead of returning []
        when this platform simply isn't wired up yet.
        """
        ...
