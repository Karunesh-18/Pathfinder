from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile, LearningPath, AssessmentResult
from backend.schemas import DashboardResponse
from ai_service import calculate_career_readiness

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/{user_id}", response_model=DashboardResponse)
def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    twin = profile.digital_twin or {}
    skill_vector = twin.get("skill_vector", {})
    behavior = twin.get("behavior", {})

    prof_dict = {
        "target_role": profile.target_role or "Data Scientist",
        "digital_twin": twin
    }
    readiness_pct = calculate_career_readiness(prof_dict)

    # Fetch latest learning path
    latest_path = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == user_id)
        .order_by(LearningPath.path_version.desc())
        .first()
    )

    milestones = latest_path.milestones if latest_path else []
    latest_change = latest_path.change_summary if latest_path else "Initial roadmap generated."

    # Compute skill growth showing mastery vs completion as separate numbers
    assessments = db.query(AssessmentResult).filter(AssessmentResult.user_id == user_id).all()
    completed_res_count = len([a for a in assessments if a.status == "done"])

    skill_growth = {}
    all_skills = ["python_basics", "sql_basics", "data_analysis", "fastapi_backend", "machine_learning"]
    for s in all_skills:
        mastery_val = skill_vector.get(s, 0.2)
        # completion estimated based on resource completions
        comp_val = min(1.0, mastery_val * 0.85 + (0.1 if completed_res_count > 0 else 0.0))
        skill_growth[s] = {
            "completion": round(comp_val * 100, 1),
            "mastery": round(mastery_val * 100, 1)
        }

    # Next 3 actions
    next_actions = [
        {
            "action_id": "act_1",
            "title": "Complete Python Core Milestone Quiz",
            "due_in_days": 2,
            "type": "quiz"
        },
        {
            "action_id": "act_2",
            "title": "Review SQL JOINs & Window Functions",
            "due_in_days": 4,
            "type": "reading"
        },
        {
            "action_id": "act_3",
            "title": "Submit FastAPI Endpoint Exercise",
            "due_in_days": 6,
            "type": "project"
        }
    ]

    return DashboardResponse(
        user_id=user_id,
        goal=profile.goal or "Master Data Science & AI",
        target_role=profile.target_role or "Data Scientist",
        career_readiness_pct=readiness_pct,
        skill_growth=skill_growth,
        milestones=milestones,
        next_actions=next_actions,
        latest_change_summary=latest_change
    )
