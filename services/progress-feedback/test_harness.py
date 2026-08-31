"""End-to-end test harness for Phase 05: submit a progress event and show
a full replan cycle.

Builds an initial profile + path (same sample goal used throughout), then
submits a progress event describing finishing a course and feeling more
comfortable with two skills, and prints the before/after total gap score,
whether a replan was triggered, and the new path if so.

Usage:
    python services/progress-feedback/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
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

    print(f"learner_id: {profile.learner_id}")
    print(f"Initial skill gaps: {len(gaps)}  |  initial path steps: {len(steps)}\n")

    print("=" * 78)
    print(f"Progress event: {PROGRESS_EVENT_TEXT!r}")
    print("-" * 78)
    result = apply_progress_event(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, PROGRESS_EVENT_TEXT)

    print(f"completed_course_id: {result.completed_course_id}")
    print(f"skill_updates (from free-text interpretation): {result.skill_updates}")
    print(f"total_gap_score before: {result.total_gap_before:.1f}")
    print(f"total_gap_score after:  {result.total_gap_after:.1f}")
    drop_pct = (
        (result.total_gap_before - result.total_gap_after) / result.total_gap_before * 100
        if result.total_gap_before
        else 0
    )
    print(f"gap reduction: {drop_pct:.1f}%  (replan threshold: 5.0%)")
    print(f"replan_triggered: {result.replan_triggered}")

    if result.replan_triggered:
        new_path = path_store.get_path(profile.learner_id)
        print(f"\nNew path ({len(new_path)} steps):")
        for s in new_path:
            print(f"  step {s['step_index']}: {s['title']} ({s['provider']})  addresses: {s['skill_gap_addressed']}")
    else:
        print("\n(No replan — gap picture did not change enough to cross the threshold.)")


if __name__ == "__main__":
    main()
