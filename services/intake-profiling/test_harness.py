"""Test harness for the Intake & Profiling Agent prototype.

Runs profile_from_text against sample learner goal statements and prints
the structured profile plus any follow-up questions, for a by-eye sanity
check. This is Phase 01's stated deliverable: "Intake & Profiling Agent
(02) validated against sample goals."

Usage:
    python services/intake-profiling/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intake_agent import profile_from_text  # noqa: E402

SAMPLE_GOALS = [
    "I want to become a data engineer. I already know Python and some SQL, "
    "and I can spend about 5 hours a week learning. I prefer video courses.",
    "I'm trying to break into data engineering. I've done a bit of SQL work "
    "before but nothing with pipelines or cloud tools.",
    "Help me learn data engineering skills.",
]


def main() -> None:
    import profile_store as profile_db  # noqa: E402  (path already set up by agent import)

    print(f"Learner Profile Store backend: {profile_db.backend_name()}\n")

    for i, text in enumerate(SAMPLE_GOALS, start=1):
        print("=" * 78)
        print(f"Sample goal {i}: {text!r}")
        print("-" * 78)
        profile = profile_from_text(text)
        print(f"learner_id: {profile.learner_id}")
        print(f"target_role: {profile.target_role}")
        print(f"current_skills: {[(s.skill, s.level) for s in profile.current_skills]}")
        print(f"time_budget_hours_per_week: {profile.time_budget_hours_per_week}")
        print(f"format_preference: {profile.format_preference}")
        print(f"missing_fields: {profile.missing_fields}")
        if profile.follow_up_questions:
            print("follow_up_questions:")
            for q in profile.follow_up_questions:
                print(f"  - {q}")
        print()


if __name__ == "__main__":
    main()
