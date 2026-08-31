"""DashboardViewModel schema — the structured output of the Dashboard /
Reporting Service. See ARCHITECTURE.md Section 03, card 08.

Named dashboard_schema.py, not schema.py — see
services/intake-profiling/profile_schema.py's docstring for why.

completed_history and remaining_timeline are deliberately two separate
lists rather than one step-indexed timeline with a `completed` flag — see
aggregate.py's module docstring for why forcing them together produces a
misleading "0 complete" the moment a replan prunes a finished course out
of the active path.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SkillRadarPoint(BaseModel):
    skill: str
    required_level: str
    current_level: str
    required_value: int  # 0-3
    current_value: int  # 0-3


class HistoryItem(BaseModel):
    course_id: str
    title: str
    provider: str
    estimated_hours: float


class TimelineStep(BaseModel):
    step_index: int
    title: str
    provider: str
    milestone: bool
    cumulative_hours: float
    estimated_completion_week: int | None


class NextAction(BaseModel):
    step_index: int
    title: str
    provider: str
    skill_gap_addressed: str


class SummaryStats(BaseModel):
    completed_courses: int
    remaining_steps: int
    completed_hours: float
    remaining_hours: float
    overall_progress_pct: float
    weeks_remaining: int | None


class DashboardViewModel(BaseModel):
    learner_id: str
    target_role: str
    skill_radar: list[SkillRadarPoint] = Field(default_factory=list)
    completed_history: list[HistoryItem] = Field(default_factory=list)
    remaining_timeline: list[TimelineStep] = Field(default_factory=list)
    next_action: NextAction | None = None
    summary: SummaryStats
