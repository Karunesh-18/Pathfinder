"""StepRationale schema — the structured per-step output of the
Explainability & Q&A Agent. See ARCHITECTURE.md Section 03, card 06.

Named explain_schema.py, not schema.py — see
services/intake-profiling/profile_schema.py's docstring for why.
"""

from __future__ import annotations

from pydantic import BaseModel


class StepRationale(BaseModel):
    step_index: int
    course_id: str
    skill: str
    rationale_text: str
