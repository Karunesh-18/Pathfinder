"""learner_routes.py — intake/profile and skill-gap endpoints."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, HTTPException  # noqa: E402

from api_schemas import CreateLearnerRequest, GapsOut, ProfileOut, SkillGapOut  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, compute_gaps, create_or_update_profile, get_profile  # noqa: E402

router = APIRouter(prefix="/api", tags=["learners"])


@router.post("/learners", response_model=ProfileOut)
def create_or_update_learner(body: CreateLearnerRequest) -> ProfileOut:
    profile = create_or_update_profile(body.raw_text, body.learner_id)
    return ProfileOut(**profile)


@router.get("/learners/{learner_id}", response_model=ProfileOut)
def get_learner(learner_id: str) -> ProfileOut:
    profile = get_profile(learner_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"No profile found for learner_id={learner_id}"})
    return ProfileOut(**profile)


@router.get("/learners/{learner_id}/gaps", response_model=GapsOut)
def get_learner_gaps(learner_id: str, target_role: str = DEFAULT_TARGET_ROLE) -> GapsOut:
    profile = get_profile(learner_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"No profile found for learner_id={learner_id}"})
    gaps = compute_gaps(profile, target_role)
    return GapsOut(gaps=[SkillGapOut(**g) for g in gaps])
