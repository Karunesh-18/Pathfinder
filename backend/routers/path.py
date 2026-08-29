from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile, LearningPath, AssessmentResult
from backend.schemas import PathResponse
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/path", tags=["Path"])

@router.post("/{user_id}", response_model=PathResponse)
def generate_or_regenerate_path(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    prof_dict = {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "digital_twin": profile.digital_twin or {}
    }

    # Fetch latest existing path for version incrementing and diff comparison
    latest_path = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == user_id)
        .order_by(LearningPath.path_version.desc())
        .first()
    )

    prev_path_dict = None
    new_version = 1
    if latest_path:
        new_version = latest_path.path_version + 1
        prev_path_dict = {
            "milestones": latest_path.milestones,
            "change_summary": latest_path.change_summary
        }

    recs = AIInterface.get_recommendations(prof_dict, top_k=10)
    generated = AIInterface.generate_path(prof_dict, recs, prev_path_dict)

    new_path = LearningPath(
        user_id=user_id,
        path_version=new_version,
        milestones=generated["milestones"],
        change_summary=generated.get("change_summary", "")
    )
    db.add(new_path)
    db.commit()
    db.refresh(new_path)

    return PathResponse(
        user_id=user_id,
        path_version=new_path.path_version,
        milestones=new_path.milestones,
        change_summary=new_path.change_summary
    )

@router.get("/{user_id}", response_model=PathResponse)
def get_current_path(user_id: str, db: Session = Depends(get_db)):
    latest_path = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == user_id)
        .order_by(LearningPath.path_version.desc())
        .first()
    )
    if not latest_path:
        # Auto-trigger generation if no path exists yet
        return generate_or_regenerate_path(user_id, db)

    # Compute live status per milestone from assessment results
    assessments = db.query(AssessmentResult).filter(AssessmentResult.user_id == user_id).all()
    completed_res_ids = {a.resource_id for a in assessments if a.status == "done"}

    updated_milestones = []
    for ms in latest_path.milestones:
        ms_res = ms.get("resources", [])
        if any(r in completed_res_ids for r in ms_res):
            ms["status"] = "done"
        updated_milestones.append(ms)

    return PathResponse(
        user_id=user_id,
        path_version=latest_path.path_version,
        milestones=updated_milestones,
        change_summary=latest_path.change_summary
    )
