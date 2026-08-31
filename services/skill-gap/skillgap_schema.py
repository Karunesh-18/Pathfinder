"""SkillGap schema — the structured output of the Skill-Gap Analysis
Agent. See ARCHITECTURE.md Section 03, card 03.

Named skillgap_schema.py, not schema.py — see profile_schema.py's
docstring in services/intake-profiling for why a bare "schema" module name
is unsafe once more than one service is imported in the same process."""

from __future__ import annotations

from pydantic import BaseModel


class SkillGap(BaseModel):
    skill: str
    required_level: str
    current_level: str
    weight: float
    gap_score: float
    priority_rank: int
