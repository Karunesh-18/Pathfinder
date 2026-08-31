"""explain_routes.py — per-step rationale and free-form Q&A."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, HTTPException  # noqa: E402

from api_schemas import AskOut, AskRequest, ExplainedStepOut, ExplainOut, PathStepOut  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, ask_question, explain_path  # noqa: E402

router = APIRouter(prefix="/api", tags=["explain"])


@router.get("/explain/{learner_id}", response_model=ExplainOut)
def get_explanations(learner_id: str, target_role: str = DEFAULT_TARGET_ROLE) -> ExplainOut:
    try:
        explained = explain_path(learner_id, target_role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return ExplainOut(
        explained_steps=[
            ExplainedStepOut(step=PathStepOut(**item["step"]), rationale=item["rationale"])
            for item in explained
        ]
    )


@router.post("/explain/{learner_id}/ask", response_model=AskOut)
def ask(learner_id: str, body: AskRequest, target_role: str = DEFAULT_TARGET_ROLE) -> AskOut:
    try:
        answer = ask_question(learner_id, target_role, body.question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return AskOut(answer=answer)
