from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/recommend", tags=["Recommend"])

@router.get("/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    prof_dict = {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "digital_twin": profile.digital_twin or {}
    }

    recs = AIInterface.get_recommendations(prof_dict, top_k=10)
    return {
        "user_id": user_id,
        "recommendations": recs
    }
