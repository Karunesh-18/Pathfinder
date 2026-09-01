"""path_routes.py — build/get the learner's learning path."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, Depends, HTTPException  # noqa: E402

from api_schemas import PathOut, PathStepOut  # noqa: E402
from current_user import get_current_user_id, require_owner  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, build_and_save_path, get_path  # noqa: E402

router = APIRouter(prefix="/api", tags=["path"])


@router.post("/path/{learner_id}", response_model=PathOut)
def build_path_for_learner(
    learner_id: str, target_role: str = DEFAULT_TARGET_ROLE, current_user_id: str = Depends(get_current_user_id)
) -> PathOut:
    require_owner(learner_id, current_user_id)
    try:
        steps = build_and_save_path(learner_id, target_role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return PathOut(steps=[PathStepOut(**s) for s in steps])


@router.get("/path/{learner_id}", response_model=PathOut)
def get_path_for_learner(learner_id: str, current_user_id: str = Depends(get_current_user_id)) -> PathOut:
    require_owner(learner_id, current_user_id)
    # An empty path is a normal pre-build state, not an error — no 404 here.
    steps = get_path(learner_id)
    return PathOut(steps=[PathStepOut(**s) for s in steps])
