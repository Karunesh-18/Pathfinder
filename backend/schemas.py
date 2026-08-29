from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Chat API
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    extracted_fields: Dict[str, Any]
    asked_clarifying_question: bool

# Profile API
class ProfileUpdate(BaseModel):
    user_id: str
    goal: Optional[str] = None
    target_role: Optional[str] = None
    timeframe_weeks: Optional[int] = None
    hours_per_week: Optional[int] = None
    digital_twin: Optional[Dict[str, Any]] = None

# Progress API
class ProgressRequest(BaseModel):
    resource_id: str
    status: str = "done"  # not_started | in_progress | done
    quiz_score: Optional[float] = None
    time_spent_min: Optional[int] = None

# Feedback API
class FeedbackRequest(BaseModel):
    resource_id: str
    text: str

class FeedbackResponse(BaseModel):
    message: str
    extracted: Dict[str, Any]
    followup_question: Optional[str] = None

# Path API
class PathResponse(BaseModel):
    user_id: str
    path_version: int
    milestones: List[Dict[str, Any]]
    change_summary: Optional[str] = None

# Explain API
class ExplanationResponse(BaseModel):
    resource_id: str
    explanation: str

# Dashboard API
class DashboardResponse(BaseModel):
    user_id: str
    goal: str
    target_role: str
    career_readiness_pct: float
    skill_growth: Dict[str, Any]  # {skill_id: {completion: float, mastery: float}}
    milestones: List[Dict[str, Any]]
    next_actions: List[Dict[str, Any]]
    latest_change_summary: Optional[str] = None
