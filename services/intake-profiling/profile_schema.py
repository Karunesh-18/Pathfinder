"""LearnerProfile schema — the structured output of the Intake & Profiling
Agent. See ARCHITECTURE.md Section 03, card 02.

Named profile_schema.py, not schema.py — a bare "schema" module name
collides with other services' own schema.py in sys.modules the moment
both get imported in the same Python process (hit this as a real bug
building Phase 03: services/skill-gap/schema.py shadowed this file). Every
service's schema module should have a component-specific name, not the
generic "schema"."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SkillLevel = Literal["beginner", "intermediate", "advanced", "unspecified"]


class SkillEntry(BaseModel):
    skill: str
    level: SkillLevel = "unspecified"


class LearnerProfile(BaseModel):
    learner_id: str
    target_role: str | None = None
    current_skills: list[SkillEntry] = Field(default_factory=list)
    completed_courses: list[str] = Field(default_factory=list)
    time_budget_hours_per_week: float | None = None
    format_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    raw_text: str = ""
    extraction_method: str = "rule-based-stub"
