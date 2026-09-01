"""courses_routes.py — course detail, course tree, and roles list.

Public/unauthenticated (not learner-scoped) — matches GET /api/courses and
GET /api/system/status, which stay in dashboard_routes.py per the
implementation plan to minimize churn on an already-working file.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, HTTPException  # noqa: E402

from api_schemas import CourseOut, CourseTreeOut, RoleOut, RolesOut, SkillTreeNodeOut  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, get_course, get_course_tree, list_roles  # noqa: E402

router = APIRouter(prefix="/api", tags=["courses"])


@router.get("/courses/tree", response_model=CourseTreeOut)
def get_course_tree_for_role(target_role: str = DEFAULT_TARGET_ROLE) -> CourseTreeOut:
    # Registered before /courses/{course_id} — FastAPI matches routes in
    # registration order, and a path-param route would otherwise swallow
    # "tree" as a literal course_id.
    tree = get_course_tree(target_role)
    return CourseTreeOut(
        target_role=tree["target_role"],
        skills=[SkillTreeNodeOut(**s) for s in tree["skills"]],
    )


@router.get("/courses/{course_id}", response_model=CourseOut)
def get_course_detail(course_id: str) -> CourseOut:
    course = get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"No course found for id={course_id}"})
    return CourseOut(**course)


@router.get("/roles", response_model=RolesOut)
def get_roles() -> RolesOut:
    return RolesOut(roles=[RoleOut(**r) for r in list_roles()])
