from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, LearnerProfile
from backend.schemas import ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("")
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == body.user_id).first()
    if not profile:
        user = db.query(User).filter(User.id == body.user_id).first()
        if not user:
            user = User(id=body.user_id)
            db.add(user)
            db.commit()
        profile = LearnerProfile(user_id=body.user_id, digital_twin={})
        db.add(profile)

    if body.goal is not None:
        profile.goal = body.goal
    if body.target_role is not None:
        profile.target_role = body.target_role
    if body.timeframe_weeks is not None:
        profile.timeframe_weeks = body.timeframe_weeks
    if body.hours_per_week is not None:
        profile.hours_per_week = body.hours_per_week

    # Merge digital twin JSON safely
    if body.digital_twin is not None:
        existing_twin = profile.digital_twin or {}
        existing_twin.update(body.digital_twin)
        profile.digital_twin = existing_twin

    db.commit()
    db.refresh(profile)

    return {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "timeframe_weeks": profile.timeframe_weeks,
        "hours_per_week": profile.hours_per_week,
        "digital_twin": profile.digital_twin,
        "questions_asked_session": profile.questions_asked_session
    }

@router.get("/{user_id}")
def get_profile(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    return {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "timeframe_weeks": profile.timeframe_weeks,
        "hours_per_week": profile.hours_per_week,
        "digital_twin": profile.digital_twin,
        "questions_asked_session": profile.questions_asked_session
    }
