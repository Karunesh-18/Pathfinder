"""auth_token.py — signs/verifies the JWT bearer tokens issued at login.

New in the login/multi-role rework. Uses PyJWT (HS256, symmetric secret)
rather than a session store — no refresh-token rotation, matching the
"lightweight real accounts" scope the user chose. If JWT_SECRET isn't set
in the environment/.env, falls back to a fixed, clearly-insecure
development default and prints a one-time warning, mirroring the existing
"missing env var -> fall back, never crash" convention already used for
GROQ_API_KEY/SUPABASE_DB_URL (see CLAUDE.md).
"""

from __future__ import annotations

import datetime
import os
from typing import Any

import jwt

_INSECURE_DEV_SECRET = "pathfinder-insecure-dev-secret-do-not-use-in-production"
_ALGORITHM = "HS256"
_EXPIRY_DAYS = 7

_warned_insecure_secret = False


def _get_secret() -> str:
    global _warned_insecure_secret
    secret = os.environ.get("JWT_SECRET")
    if secret:
        return secret
    if not _warned_insecure_secret:
        print(
            "[auth_token] JWT_SECRET not set — using an insecure development "
            "default. Set JWT_SECRET in .env before deploying this anywhere real."
        )
        _warned_insecure_secret = True
    return _INSECURE_DEV_SECRET


def create_access_token(user_id: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(days=_EXPIRY_DAYS),
    }
    return jwt.encode(payload, _get_secret(), algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Raises jwt.PyJWTError (or a subclass) on an invalid/expired token —
    callers (backend/current_user.py) are expected to catch broadly."""
    return jwt.decode(token, _get_secret(), algorithms=[_ALGORITHM])
