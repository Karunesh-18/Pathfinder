"""progress_routes.py — submit a progress/feedback event, get the replan result."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, HTTPException  # noqa: E402

from api_schemas import ProgressRequest, ReplanResultOut  # noqa: E402
from service_bridge import DEFAULT_TARGET_ROLE, apply_progress  # noqa: E402

router = APIRouter(prefix="/api", tags=["progress"])


@router.post("/progress/{learner_id}", response_model=ReplanResultOut)
def submit_progress(learner_id: str, body: ProgressRequest, target_role: str = DEFAULT_TARGET_ROLE) -> ReplanResultOut:
    try:
        result = apply_progress(learner_id, target_role, body.raw_text)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)}) from exc
    return ReplanResultOut(**result)
