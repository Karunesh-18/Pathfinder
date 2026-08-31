"""api_schemas.py — request/response Pydantic models for the backend REST
API.

Deliberately its own set of models, not re-exports of the service
schemas (profile_schema.LearnerProfile, dashboard_schema.DashboardViewModel,
...) — this keeps the file free of any sys.path import-hacking (it's a
plain, portable Pydantic module) and keeps the public API contract
independent of internal service refactors. Constructed via
`Model(**dict)` from whatever backend.service_bridge returns; Pydantic
v2's default extra="ignore" behavior means extra DB columns (e.g. a
Postgres row's updated_at) are silently dropped rather than erroring.

Named api_schemas.py, not schemas.py — see
services/intake-profiling/profile_schema.py's docstring for why bare
generic module names are unsafe in this codebase.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Learner profile (intake)
# ---------------------------------------------------------------------------

class SkillEntryOut(BaseModel):
    skill: str
    level: str = "unspecified"


class ProfileOut(BaseModel):
    learner_id: str
    target_role: str | None = None
    current_skills: list[SkillEntryOut] = Field(default_factory=list)
    completed_courses: list[str] = Field(default_factory=list)
    time_budget_hours_per_week: float | None = None
    format_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    raw_text: str = ""
    extraction_method: str = "rule-based-stub"


class CreateLearnerRequest(BaseModel):
    raw_text: str
    learner_id: str | None = None


# ---------------------------------------------------------------------------
# Skill gaps
# ---------------------------------------------------------------------------

class SkillGapOut(BaseModel):
    skill: str
    required_level: str
    current_level: str
    weight: float
    gap_score: float
    priority_rank: int


class GapsOut(BaseModel):
    gaps: list[SkillGapOut]


# ---------------------------------------------------------------------------
# Learning path
# ---------------------------------------------------------------------------

class PathStepOut(BaseModel):
    step_index: int
    course_id: str
    title: str
    provider: str
    skill_gap_addressed: str
    milestone: bool = False
    estimated_hours: float = 0
    cumulative_hours: float = 0
    estimated_completion_week: int | None = None


class PathOut(BaseModel):
    steps: list[PathStepOut]


# ---------------------------------------------------------------------------
# Explainability & Q&A
# ---------------------------------------------------------------------------

class ExplainedStepOut(BaseModel):
    step: PathStepOut
    rationale: str


class ExplainOut(BaseModel):
    explained_steps: list[ExplainedStepOut]


class AskRequest(BaseModel):
    question: str


class AskOut(BaseModel):
    answer: str


# ---------------------------------------------------------------------------
# Progress & feedback
# ---------------------------------------------------------------------------

class ProgressRequest(BaseModel):
    raw_text: str


class ReplanResultOut(BaseModel):
    learner_id: str
    completed_course_id: str | None = None
    skill_updates: list[dict[str, str]] = Field(default_factory=list)
    total_gap_before: float
    total_gap_after: float
    replan_triggered: bool
    new_path_step_count: int = 0


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class SkillRadarPointOut(BaseModel):
    skill: str
    required_level: str
    current_level: str
    required_value: int
    current_value: int


class HistoryItemOut(BaseModel):
    course_id: str
    title: str
    provider: str
    estimated_hours: float


class TimelineStepOut(BaseModel):
    step_index: int
    title: str
    provider: str
    milestone: bool
    cumulative_hours: float
    estimated_completion_week: int | None = None


class NextActionOut(BaseModel):
    step_index: int
    title: str
    provider: str
    skill_gap_addressed: str


class SummaryStatsOut(BaseModel):
    completed_courses: int
    remaining_steps: int
    completed_hours: float
    remaining_hours: float
    overall_progress_pct: float
    weeks_remaining: int | None = None


class DashboardOut(BaseModel):
    learner_id: str
    target_role: str
    skill_radar: list[SkillRadarPointOut] = Field(default_factory=list)
    completed_history: list[HistoryItemOut] = Field(default_factory=list)
    remaining_timeline: list[TimelineStepOut] = Field(default_factory=list)
    next_action: NextActionOut | None = None
    summary: SummaryStatsOut


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

class CourseOut(BaseModel):
    id: str
    title: str
    provider: str
    url: str | None = None
    description: str
    skills_taught: list[str] = Field(default_factory=list)
    level: str | None = None
    format: str | None = None
    target_roles: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    estimated_hours: float | None = None
    source: str = "hand-built-sample"


class CoursesOut(BaseModel):
    courses: list[CourseOut]


# ---------------------------------------------------------------------------
# System / diagnostics
# ---------------------------------------------------------------------------

class SystemStatusOut(BaseModel):
    profile_store_backend: str
    path_store_backend: str
    course_kb_backend: str
    taxonomy_store_backend: str
    llm_configured: bool


# ---------------------------------------------------------------------------
# Error envelope
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
