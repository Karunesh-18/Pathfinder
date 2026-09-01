"""current_user.py — FastAPI dependency that resolves the authenticated
user id from the Authorization header.

New in the login/multi-role rework. Uses fastapi.security.HTTPBearer
(rather than a bare Header(...) parameter) specifically because it makes
Swagger UI (/docs) render an "Authorize" button, which is how this whole
auth layer gets manually verified per the implementation plan.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import Depends, HTTPException  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # noqa: E402

from auth_token import decode_access_token  # noqa: E402

_bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=401,
    detail={"code": "unauthorized", "message": "Missing or invalid bearer token"},
)


def get_current_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    if creds is None:
        raise _UNAUTHORIZED
    try:
        payload = decode_access_token(creds.credentials)
    except Exception as exc:
        raise _UNAUTHORIZED from exc
    user_id = payload.get("sub")
    if not user_id:
        raise _UNAUTHORIZED
    return user_id


def require_owner(learner_id: str, current_user_id: str) -> None:
    """Raise 403 if the authenticated user doesn't own this learner_id.
    learner_id IS the owning user's id in this system (see
    stores/account-store's docstring) — no lookup needed, just a string
    comparison."""
    if current_user_id != learner_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "forbidden", "message": "Not your learner profile"},
        )
