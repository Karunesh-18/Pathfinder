"""Test harness for the Skill-Gap Analysis Agent prototype.

Runs the same sample learner goals used in Phase 01 through
compute_skill_gaps and prints the ranked SkillGap list per profile, for a
by-eye sanity check.

Usage:
    python services/skill-gap/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gap import compute_skill_gaps  # noqa: E402

_INTAKE_PATH = Path(__file__).resolve().parents[2] / "services" / "intake-profiling"
sys.path.insert(0, str(_INTAKE_PATH))
from intake_agent import DEFAULT_ROLE_FOR_TAXONOMY, profile_from_text  # noqa: E402

SAMPLE_GOALS = [
    "I want to become a data engineer. I already know Python and some SQL, "
    "and I can spend about 5 hours a week learning. I prefer video courses.",
    "I'm trying to break into data engineering. I've done a bit of SQL work "
    "before but nothing with pipelines or cloud tools.",
    "Help me learn data engineering skills.",
]


def main() -> None:
    for i, text in enumerate(SAMPLE_GOALS, start=1):
        profile = profile_from_text(text)
        gaps = compute_skill_gaps(profile.model_dump(), DEFAULT_ROLE_FOR_TAXONOMY)

        print("=" * 78)
        print(f"Sample goal {i}: {text!r}")
        print(f"target_role (extracted): {profile.target_role}  |  gaps computed against: {DEFAULT_ROLE_FOR_TAXONOMY}")
        print("-" * 78)
        if not gaps:
            print("  (no gaps — profile already meets every tracked requirement)")
        for g in gaps:
            print(
                f"  #{g.priority_rank:>2} [score {g.gap_score:>4.1f}] {g.skill:<24s} "
                f"need {g.required_level:<12s} have {g.current_level}"
            )
        print()


if __name__ == "__main__":
    main()
