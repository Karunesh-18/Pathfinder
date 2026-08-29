from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import LearnerProfile, Feedback
from backend.schemas import FeedbackRequest, FeedbackResponse
from backend.ai_interface import AIInterface

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/{user_id}", response_model=FeedbackResponse)
def submit_feedback(user_id: str, body: FeedbackRequest, db: Session = Depends(get_db)):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    extracted_signals = AIInterface.analyze_feedback(body.text)

    # Save to feedback table
    fb_record = Feedback(
        user_id=user_id,
        resource_id=body.resource_id,
        raw_text=body.text,
        extracted=extracted_signals
    )
    db.add(fb_record)

    # Update digital twin state
    twin = profile.digital_twin or {}
    state = twin.get("state", {})
    confs = extracted_signals.get("confidence_per_field", {})

    state["emotion"] = {"value": extracted_signals.get("emotion", "neutral"), "confidence": confs.get("emotion", 0.5)}
    state["pace"] = {"value": extracted_signals.get("pace_signal", "good"), "confidence": confs.get("pace", 0.5)}
    state["difficulty_fit"] = {"value": extracted_signals.get("difficulty_signal", "good"), "confidence": confs.get("difficulty_fit", 0.5)}

    twin["state"] = state
    profile.digital_twin = twin
    db.commit()

    followup = None
    min_conf = min(confs.values()) if confs else 1.0
    if min_conf < 0.5 and (profile.questions_asked_session or 0) < 2:
        followup = "You mentioned feeling stuck — would an interactive code practice task help clear things up?"
        profile.questions_asked_session = (profile.questions_asked_session or 0) + 1
        db.commit()

    return FeedbackResponse(
        message="Feedback analyzed successfully",
        extracted=extracted_signals,
        followup_question=followup
    )
