"""main.py — FastAPI application entry point.

Wraps the six existing services (intake-profiling, skill-gap,
retrieval-ranking, path-construction, explainability-qa, progress-feedback)
plus the dashboard aggregator into a REST API for the React frontend. No
services/ or stores/ code is modified — everything here is additive,
calling into backend/service_bridge.py, which is the one place that
imports those directories (see its own docstring).

Convention #5 (CLAUDE.md): any new entry-point script must call
fix_windows_console_encoding() before any printing. Because
`uvicorn backend.main:app` imports this module rather than running it as
__main__, that call has to be unconditional top-level module code, not
guarded behind `if __name__ == "__main__":`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

_ROOT = _BACKEND_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import os  # noqa: E402

from common.console import fix_windows_console_encoding  # noqa: E402
from common.env import load_env_file  # noqa: E402

fix_windows_console_encoding()
load_env_file()

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

import auth_routes  # noqa: E402
import chat_routes  # noqa: E402
import courses_routes  # noqa: E402
import dashboard_routes  # noqa: E402
import explain_routes  # noqa: E402
import learner_routes  # noqa: E402
import path_routes  # noqa: E402
import progress_routes  # noqa: E402

app = FastAPI(
    title="PathFinder API",
    description="REST layer over the PathFinder personalized learning path recommender services.",
    version="0.1.0",
)

# ALLOWED_ORIGINS: comma-separated list of extra frontend origins to trust
# (e.g. the deployed Vercel URL). Local dev origins are always included so
# `npm run dev` keeps working without any env var set.
_default_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
_extra_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(learner_routes.router)
app.include_router(path_routes.router)
app.include_router(explain_routes.router)
app.include_router(progress_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(courses_routes.router)
app.include_router(chat_routes.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Never leak a raw traceback to the frontend; log it server-side
    # (stdout/stderr are already UTF-8-safe thanks to
    # fix_windows_console_encoding(), so a Unicode Groq-generated message
    # in the exception text won't crash this print either).
    print(f"[backend] Unhandled exception on {request.method} {request.url.path}: {exc!r}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "PathFinder API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
