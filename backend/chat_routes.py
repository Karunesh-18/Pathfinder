"""chat_routes.py — the general-purpose chatbot endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fastapi import APIRouter, Depends  # noqa: E402

from api_schemas import ChatOut, ChatRequest  # noqa: E402
from current_user import get_current_user_id  # noqa: E402
from service_bridge import chat_reply as _chat_reply  # noqa: E402

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatOut)
def chat(body: ChatRequest, current_user_id: str = Depends(get_current_user_id)) -> ChatOut:
    history = [{"role": turn.role, "text": turn.text} for turn in body.history]
    reply = _chat_reply(current_user_id, body.message, history)
    return ChatOut(reply=reply)
