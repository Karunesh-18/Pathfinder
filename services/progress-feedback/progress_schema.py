"""ReplanResult schema — the structured output of the Progress & Feedback
Agent. See ARCHITECTURE.md Section 03, card 07.

Named progress_schema.py, not schema.py — see
services/intake-profiling/profile_schema.py's docstring for why.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReplanResult(BaseModel):
    learner_id: str
    completed_course_id: str | None = None
    skill_updates: list[dict[str, str]] = Field(default_factory=list)
    total_gap_before: float
    total_gap_after: float
    replan_triggered: bool
    new_path_step_count: int = 0
