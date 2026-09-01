"""dashboard_routes.py — dashboard aggregation and course browsing."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, Depends, HTTPException  # noqa: E402

from api_schemas import CourseOut, CoursesOut, DashboardOut, SystemStatusOut  # noqa: E402
from current_user import get_current_user_id, require_owner  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, get_dashboard, list_courses, system_status  # noqa: E402

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard/{learner_id}", response_model=DashboardOut)
def get_learner_dashboard(
    learner_id: str, target_role: str = DEFAULT_TARGET_ROLE, current_user_id: str = Depends(get_current_user_id)
) -> DashboardOut:
    require_owner(learner_id, current_user_id)
    try:
        dashboard = get_dashboard(learner_id, target_role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return DashboardOut(**dashboard)


@router.get("/courses", response_model=CoursesOut)
def get_courses(target_role: str | None = None) -> CoursesOut:
    courses = list_courses(target_role)
    return CoursesOut(courses=[CourseOut(**c) for c in courses])


@router.get("/system/status", response_model=SystemStatusOut)
def get_system_status() -> SystemStatusOut:
    return SystemStatusOut(**system_status())
