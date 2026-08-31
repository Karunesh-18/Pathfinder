# Path Construction Service

**Type:** Deterministic service

## Role

Builds the prerequisite graph across chosen candidates, topologically sorts it, inserts milestone checkpoints, and fits the sequence to the learner's time budget. No language reasoning needed.

## Inputs (reads)

- Ranked candidates
- Prerequisite metadata
- Time budget

## Outputs (writes)

- Ordered LearningPath with milestones

## Tools

- `dag_builder`
- `topo_sort`
- `path_store`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 05.

## Status: prototype implemented (Phase 03)

- `pathconstruction_schema.py` — the `LearningPathStep` model.
- `dag.py` — `dag_builder` + `topo_sort`, stdlib-only Kahn's algorithm (no networkx added for a handful of nodes). Ties among independent courses break by skill-gap priority rank.
- `build_path.py` — for each ranked SkillGap, picks the best-fit unused course from the Course & Skills Knowledge Base via `tfidf_rank` (reusing Phase 02's ranker, not a copy of it), translates the Skills Taxonomy Graph's skill-level dependency edges into course-level edges, topologically sorts, flags milestones at each 25/50/75/100% cumulative-hours mark, and projects a completion week from the learner's weekly time budget (`DEFAULT_WEEKLY_HOURS = 5.0` when unspecified).
- `test_harness.py` — runs Intake → Skill-Gap → Path Construction end to end for 2 sample goals and persists the result to the Path Store.

Run it:

```bash
python services/path-construction/test_harness.py
```
