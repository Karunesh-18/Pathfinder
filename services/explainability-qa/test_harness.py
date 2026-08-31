"""Test harness for the Explainability & Q&A Agent prototype.

Runs one sample learner goal through Intake -> Skill-Gap -> Path
Construction (same as services/path-construction/test_harness.py), then:
  - prints a plain-language rationale for every step in the path
  - asks a handful of sample questions and prints the (stubbed) answers

Usage:
    python services/explainability-qa/test_harness.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.console import fix_windows_console_encoding  # noqa: E402

fix_windows_console_encoding()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explain_agent import ask, explain_path  # noqa: E402

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

SAMPLE_QUESTIONS = [
    "How long will this whole plan take?",
    "Why is SQL in my plan?",
    "What should I start with?",
    "What are the milestones?",
    "What's the weather like today?",  # deliberately unrecognized, to show the honest fallback
]


def main() -> None:
    profile = profile_from_text(SAMPLE_GOAL)
    gaps = compute_skill_gaps(profile.model_dump(), DEFAULT_ROLE_FOR_TAXONOMY)
    steps = build_path([g.model_dump() for g in gaps], DEFAULT_ROLE_FOR_TAXONOMY, profile.time_budget_hours_per_week)
    path_store.save_path(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, [s.model_dump() for s in steps])

    print(f"learner_id: {profile.learner_id}")
    print(f"Sample goal: {SAMPLE_GOAL!r}\n")

    print("=" * 78)
    print("PER-STEP RATIONALE")
    print("-" * 78)
    for item in explain_path(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY):
        step = item["step"]
        print(f"Step {step['step_index']}: {step['title']} ({step['provider']})")
        print(f"  {item['rationale']}")
        print()

    print("=" * 78)
    print("Q&A")
    print("-" * 78)
    for q in SAMPLE_QUESTIONS:
        answer = ask(profile.learner_id, DEFAULT_ROLE_FOR_TAXONOMY, q)
        print(f"Q: {q}")
        print(f"A: {answer}")
        print()


if __name__ == "__main__":
    main()
