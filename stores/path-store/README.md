# Path Store

## Role

The generated LearningPath per learner: ordered steps, milestone flags, completion state.

## Read / written by

Agents 05 (Path Construction), 06 (Explainability & Q&A), 08 (Dashboard).

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 04.

## Status: prototype implemented (Phase 03)

`schema.sql` + `path_store.py` (dual backend, same pattern as the other three stores). One row per `(learner_id, step_index)`; `save_path` replaces a learner's entire stored path (simplest correct semantics for a re-plan, ahead of the real re-plan trigger in Phase 05). Written to by `services/path-construction/test_harness.py`.
