from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile
from backend.schemas import ExplanationResponse
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/explain", tags=["Explain"])

@router.get("/{user_id}/{resource_id}", response_model=ExplanationResponse)
def get_explanation(user_id: str, resource_id: str, db: Session = Depends(get_db)):
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
    explanation = AIInterface.explain(prof_dict, resource_id, recs)

    return ExplanationResponse(
        resource_id=resource_id,
        explanation=explanation
    )
