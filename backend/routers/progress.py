from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile, AssessmentResult
from backend.schemas import ProgressRequest
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/{user_id}")
def report_progress(user_id: str, body: ProgressRequest, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    # Record assessment result
    res_entry = AssessmentResult(
        user_id=user_id,
        resource_id=body.resource_id,
        status=body.status,
        quiz_score=body.quiz_score if body.quiz_score is not None else 0.85,
        time_spent_min=body.time_spent_min if body.time_spent_min is not None else 25,
        est_time_min=30
    )
    db.add(res_entry)
    db.commit()

    # Call AI service to analyze evidence & update digital twin
    prof_dict = {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "digital_twin": profile.digital_twin or {}
    }

    assessment_data = {
        "resource_id": body.resource_id,
        "status": body.status,
        "quiz_score": body.quiz_score if body.quiz_score is not None else 0.85,
        "time_spent_min": body.time_spent_min if body.time_spent_min is not None else 25,
        "est_time_min": 30
    }

    updated_prof_dict = AIInterface.analyze_evidence(prof_dict, assessment_data)
    profile.digital_twin = updated_prof_dict.get("digital_twin", {})
    db.commit()

    # Internal trigger to regenerate/replan roadmap
    from backend.routers.path import generate_or_regenerate_path
    new_path = generate_or_regenerate_path(user_id, db)

    return {
        "status": "success",
        "message": "Progress recorded, evidence analyzed, and digital twin updated.",
        "updated_twin": profile.digital_twin,
        "path_version": new_path.path_version,
        "change_summary": new_path.change_summary
    }
