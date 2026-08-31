"""compute_skill_gaps — deterministic gap math.

Per ARCHITECTURE.md Section 03, card 03: "LLM judgment only interprets
vague self-ratings; the gap math is deterministic." There's no separate
LLM-judgment step here — the Intake & Profiling Agent's stub (see
services/intake-profiling/extract.py) already canonicalizes current_skills
against the same taxonomy vocabulary before this ever runs, so this module
is purely the deterministic comparison the plan describes: for each
required skill, how far below the required level is the learner (0 if
they meet or exceed it), weighted by that skill's priority for the role.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skillgap_schema import SkillGap  # noqa: E402

_TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "stores" / "skills-taxonomy-graph"
if str(_TAXONOMY_PATH) not in sys.path:
    sys.path.insert(0, str(_TAXONOMY_PATH))
import taxonomy_store  # noqa: E402

LEVEL_ORDER = {"none": 0, "unspecified": 0, "beginner": 1, "intermediate": 2, "advanced": 3}


def compute_skill_gaps(profile: dict[str, Any], target_role: str) -> list[SkillGap]:
    """profile: a LearnerProfile-shaped dict (e.g. from
    services/intake-profiling's LearnerProfile.model_dump()). Returns gaps
    ranked by gap_score descending, skills already met are omitted."""
    requirements = taxonomy_store.get_role_requirements(target_role)
    current_by_skill = {s["skill"]: s["level"] for s in profile.get("current_skills", [])}

    gaps: list[SkillGap] = []
    for req in requirements:
        current_level = current_by_skill.get(req["skill"], "none")
        current_value = LEVEL_ORDER.get(current_level, 0)
        required_value = LEVEL_ORDER[req["required_level"]]
        level_gap = max(0, required_value - current_value)
        if level_gap == 0:
            continue  # learner already meets or exceeds the requirement
        gaps.append(
            SkillGap(
                skill=req["skill"],
                required_level=req["required_level"],
                current_level=current_level,
                weight=req["weight"],
                gap_score=req["weight"] * level_gap,
                priority_rank=0,  # filled in below, after sorting
            )
        )

    gaps.sort(key=lambda g: g.gap_score, reverse=True)
    for i, g in enumerate(gaps, start=1):
        g.priority_rank = i
    return gaps
