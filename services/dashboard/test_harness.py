"""Test harness for the Dashboard / Reporting Service prototype.

Runs the full pipeline built so far — Intake -> Skill-Gap -> Path
Construction -> one Progress event (which fully closes the SQL gap, same
as Phase 05's demo) -> Dashboard — and prints the rendered view. This
shows the dashboard correctly reflecting real progress (SQL in
COMPLETED, dropped out of the remaining timeline) rather than the
misleading "0 complete" a naive single-list model would produce.

Usage:
    python services/dashboard/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate import build_dashboard  # noqa: E402
from render import render_text  # noqa: E402

_FEEDBACK_PATH = Path(__file__).resolve().parents[2] / "services" / "progress-feedback"
sys.path.insert(0, str(_FEEDBACK_PATH))
from feedback_agent import apply_progress_event  # noqa: E402

_PATHCONSTRUCTION_PATH = Path(__file__).resolve().parents[2] / "services" / "path-construction"
sys.path.insert(0, str(_PATHCONSTRUCTION_PATH))
from build_path import build_path  # noqa: E402

_SKILLGAP_PATH = Path(__file__).resolve().parents[2] / "services" / "skill-gap"
sys.path.insert(0, str(_SKILLGAP_PATH))
from gap import compute_skill_gaps  # noqa: E402

_INTAKE_PATH = Path(__file__).resolve().parents[2] / "services" / "intake-profiling"
sys.path.insert(0, str(_INTAKE_PATH))
from intake_agent import DEFAULT_ROLE_FOR_TAXONOMY, profile_from_text  # noqa: E402

_PATHSTORE_PATH = Path(__file__).resolve().parents[2] / "stores" / "path-store"
sys.path.insert(0, str(_PATHSTORE_PATH))
import path_store  # noqa: E402

SAMPLE_GOAL = (
    "I want to become a data engineer. I already know Python and some SQL, "
    "and I can spend about 5 hours a week learning. I prefer video courses."
)
PROGRESS_EVENT_TEXT = (
    "I finished The Complete SQL Bootcamp and now feel very comfortable with SQL. "
    "I also feel more comfortable with Python these days."
)


def main() -> None:
    profile = profile_from_text(SAMPLE_GOAL)
    gaps = compute_skill_gaps(profile.model_dump(), DEFAULT_ROLE_FOR_TAXONOMY)
    steps = build_path([g.model_dump() for g in gaps], DEFAULT_ROLE_FOR_TAXONOMY, profile.time_budget_hours_per_week)
    path_store.save_path(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, [s.model_dump() for s in steps])

    apply_progress_event(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, PROGRESS_EVENT_TEXT)

    dashboard = build_dashboard(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY)
    print(render_text(dashboard))


if __name__ == "__main__":
    main()
