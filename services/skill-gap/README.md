# Skill-Gap Analysis Agent

**Type:** Hybrid (LLM judgment + deterministic math)

## Role

Ranks the missing or weak skills between the learner's current profile and the target role. LLM judgment only interprets vague self-ratings; the gap math is deterministic.

## Inputs (reads)

- LearnerProfile
- Role skill requirements

## Outputs (writes)

- Ranked SkillGap list

## Tools

- `skills_taxonomy_graph`
- `role_requirements_table`
- `embedding_similarity`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 03.

## Status: prototype implemented (Phase 03)

- `skillgap_schema.py` — the `SkillGap` pydantic model.
- `gap.py` — `compute_skill_gaps`, fully deterministic: compares a `LearnerProfile`'s `current_skills` against `stores/skills-taxonomy-graph`'s weighted role requirements, scores each unmet requirement `weight × level_gap`, ranks descending. No LLM-judgment step exists (same missing-`ANTHROPIC_API_KEY` situation as `services/intake-profiling`) — but since Intake already canonicalizes skill names against the same taxonomy vocabulary, there was no vague self-rating left to interpret here anyway.
- `test_harness.py` — runs the same 3 sample goals from Phase 01 through gap computation and prints the ranked list per profile.

Run it:

```bash
python services/skill-gap/test_harness.py
```
