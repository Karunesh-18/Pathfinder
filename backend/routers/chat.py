from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, LearnerProfile
from backend.schemas import ChatRequest, ChatResponse
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def handle_chat(req: ChatRequest, db: Session = Depends(get_db)):
    # Fetch or create user
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        user = User(id=req.user_id)
        db.add(user)
        db.commit()

    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == req.user_id).first()
    if not profile:
        default_twin = {
            "skill_vector": {"python_basics": 0.2, "sql_basics": 0.1},
            "skill_confidence": {"python_basics": 0.5, "sql_basics": 0.3},
            "experience_vector": {"video": 0.8},
            "behavior": {"completion_rate": 0.8},
            "state": {
                "pace": {"value": "moderate", "confidence": 0.6},
                "difficulty_fit": {"value": "good", "confidence": 0.4},
                "emotion": {"value": "neutral", "confidence": 0.5}
            }
        }
        profile = LearnerProfile(
            user_id=req.user_id,
            goal=req.message,
            target_role="Data Scientist",
            timeframe_weeks=8,
            hours_per_week=10,
            digital_twin=default_twin,
            questions_asked_session=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    prof_dict = {
        "user_id": profile.user_id,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "timeframe_weeks": profile.timeframe_weeks,
        "hours_per_week": profile.hours_per_week,
        "digital_twin": profile.digital_twin or {},
        "questions_asked_session": profile.questions_asked_session or 0
    }

    ai_res = AIInterface.process_chat(req.message, prof_dict)

    # Merge extracted fields into profile
    ext = ai_res.get("extracted_fields", {})
    if ext.get("goal"):
        profile.goal = ext["goal"]
    if ext.get("target_role"):
        profile.target_role = ext["target_role"]
    if ext.get("timeframe_weeks"):
        profile.timeframe_weeks = ext["timeframe_weeks"]
    if ext.get("hours_per_week"):
        profile.hours_per_week = ext["hours_per_week"]

    profile.questions_asked_session = prof_dict.get("questions_asked_session", 0)
    db.commit()

    return ChatResponse(
        reply=ai_res["reply"],
        extracted_fields=ext,
        asked_clarifying_question=ai_res["asked_clarifying_question"]
    )
