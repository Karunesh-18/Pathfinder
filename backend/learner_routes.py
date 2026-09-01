"""learner_routes.py — intake/profile and skill-gap endpoints."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, Depends, HTTPException  # noqa: E402

from api_schemas import (  # noqa: E402
    CreateLearnerRequest,
    GapsOut,
    ProfileOut,
    SkillGapOut,
    UpdateProfileRequest,
)
from current_user import get_current_user_id, require_owner  # noqa: E402
from service_bridge import (  # noqa: E402
    DEFAULT_TARGET_ROLE,
    compute_gaps,
    create_or_update_profile,
    get_profile,
    update_profile_fields,
)

router = APIRouter(prefix="/api", tags=["learners"])


@router.post("/learners", response_model=ProfileOut)
def create_or_update_learner(
    body: CreateLearnerRequest, current_user_id: str = Depends(get_current_user_id)
) -> ProfileOut:
    profile = create_or_update_profile(body.raw_text, current_user_id)
    return ProfileOut(**profile)


@router.get("/learners/{learner_id}", response_model=ProfileOut)
def get_learner(learner_id: str, current_user_id: str = Depends(get_current_user_id)) -> ProfileOut:
    require_owner(learner_id, current_user_id)
    profile = get_profile(learner_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"No profile found for learner_id={learner_id}"})
    return ProfileOut(**profile)


@router.patch("/learners/{learner_id}", response_model=ProfileOut)
def update_learner(
    learner_id: str, body: UpdateProfileRequest, current_user_id: str = Depends(get_current_user_id)
) -> ProfileOut:
    require_owner(learner_id, current_user_id)
    updates = body.model_dump(exclude_unset=True)
    if "current_skills" in updates and updates["current_skills"] is not None:
        updates["current_skills"] = [s if isinstance(s, dict) else s.model_dump() for s in body.current_skills]
    try:
        profile = update_profile_fields(learner_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return ProfileOut(**profile)


@router.get("/learners/{learner_id}/gaps", response_model=GapsOut)
def get_learner_gaps(
    learner_id: str, target_role: str = DEFAULT_TARGET_ROLE, current_user_id: str = Depends(get_current_user_id)
) -> GapsOut:
    require_owner(learner_id, current_user_id)
    profile = get_profile(learner_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"No profile found for learner_id={learner_id}"})
    gaps = compute_gaps(profile, target_role)
    return GapsOut(gaps=[SkillGapOut(**g) for g in gaps])
