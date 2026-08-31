"""LearningPathStep schema — the structured output of the Path
Construction Service. See ARCHITECTURE.md Section 03, card 05.

Named pathconstruction_schema.py, not schema.py — see
services/intake-profiling/profile_schema.py's docstring for why.
"""

from __future__ import annotations

from pydantic import BaseModel


class LearningPathStep(BaseModel):
    step_index: int
    course_id: str
    title: str
    provider: str
    skill_gap_addressed: str
    milestone: bool = False
    estimated_hours: float = 0
    cumulative_hours: float = 0
    estimated_completion_week: int | None = None
