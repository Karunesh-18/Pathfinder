"""End-to-end test harness for Phase 03: Intake -> Skill-Gap -> Path
Construction.

Runs the same sample learner goals from Phase 01/02 all the way through:
free text -> LearnerProfile -> ranked SkillGap list -> ordered
LearningPath with milestones and a projected weekly schedule -> persisted
to the Path Store. Prints each stage for a by-eye sanity check.

Usage:
    python services/path-construction/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
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

SAMPLE_GOALS = [
    "I want to become a data engineer. I already know Python and some SQL, "
    "and I can spend about 5 hours a week learning. I prefer video courses.",
    "I'm trying to break into data engineering. I've done a bit of SQL work "
    "before but nothing with pipelines or cloud tools.",
]


def main() -> None:
    print(f"Path Store backend: {path_store.backend_name()}\n")

    for i, text in enumerate(SAMPLE_GOALS, start=1):
        profile = profile_from_text(text)
        gaps = compute_skill_gaps(profile.model_dump(), DEFAULT_ROLE_FOR_TAXONOMY)
        steps = build_path(
            [g.model_dump() for g in gaps],
            DEFAULT_ROLE_FOR_TAXONOMY,
            profile.time_budget_hours_per_week,
        )
        path_store.save_path(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, [s.model_dump() for s in steps])

        print("=" * 78)
        print(f"Sample goal {i}: {text!r}")
        print(f"learner_id: {profile.learner_id}")
        weekly = profile.time_budget_hours_per_week or "unspecified (defaulted to 5.0)"
        print(f"time_budget_hours_per_week: {weekly}")
        print(f"skill gaps identified: {len(gaps)}  |  path steps built: {len(steps)}")
        print("-" * 78)
        if not steps:
            print("  (no path — no course in the KB covers any identified gap)")
        for s in steps:
            marker = "[MILESTONE]" if s.milestone else ""
            print(
                f"  step {s.step_index}: {s.title} ({s.provider})  "
                f"[{s.estimated_hours:.0f}h, cumulative {s.cumulative_hours:.0f}h, "
                f"~week {s.estimated_completion_week}]  "
                f"addresses: {s.skill_gap_addressed}  {marker}"
            )
        if steps:
            print(f"\n  Projected total: {steps[-1].cumulative_hours:.0f}h over ~{steps[-1].estimated_completion_week} weeks")
        print()


if __name__ == "__main__":
    main()
