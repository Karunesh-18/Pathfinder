"""Shared environment/config loading, used by each store's db.py.

Kept intentionally tiny: reads SUPABASE_DB_URL / DATABASE_URL from the
environment or a project-root .env file (gitignored), with no external
dependency. Real environment variables always win over the file.

Extracted from stores/course-knowledge-base/db.py so a second store
(stores/learner-profile-store) doesn't duplicate the same loader. Left
course-knowledge-base/db.py's own copy alone rather than risk touching an
already-verified module — see its docstring.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_database_url() -> str | None:
    load_env_file()
    return os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
