"""auth_routes.py — signup, login, and "who am I" endpoints."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, Depends, HTTPException  # noqa: E402

from api_schemas import AuthOut, LoginRequest, SignupRequest, UserOut  # noqa: E402
from current_user import get_current_user_id  # noqa: E402
from service_bridge import authenticate_user, create_user, get_user  # noqa: E402

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=AuthOut)
def signup(body: SignupRequest) -> AuthOut:
    try:
        token, user = create_user(body.email, body.password, body.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "email_taken", "message": str(exc)}) from exc
    return AuthOut(access_token=token, user=UserOut(**user))


@router.post("/login", response_model=AuthOut)
def login(body: LoginRequest) -> AuthOut:
    result = authenticate_user(body.email, body.password)
    if result is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "invalid_credentials", "message": "Incorrect email or password"},
        )
    token, user = result
    return AuthOut(access_token=token, user=UserOut(**user))


@router.get("/me", response_model=UserOut)
def me(current_user_id: str = Depends(get_current_user_id)) -> UserOut:
    user = get_user(current_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "User not found"})
    return UserOut(**user)
