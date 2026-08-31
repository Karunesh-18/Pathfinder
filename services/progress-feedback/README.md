# Progress & Feedback Agent

**Type:** Hybrid (LLM judgment + deterministic math)

## Role

Ingests completions, scores and explicit feedback; updates the skill vector and preference weights; triggers a re-plan when the gap picture has materially changed.

## Inputs (reads)

- Progress events
- Current LearnerProfile

## Outputs (writes)

- Updated LearnerProfile
- Re-plan trigger

## Tools

- `progress_ingest`
- `learner_profile_store`
- `replan_trigger`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 07.

## Status: prototype implemented (Phase 05) — one full replan cycle working

- `progress_schema.py` — the `ReplanResult` model.
- `progress_ingest.py` — **`progress_ingest`'s "vague self-rating" half now backed by a real LLM call**, via Groq (`common/llm.py`): `interpret_progress_event_llm()` identifies the completed course and skill self-ratings directly, without the substring-window heuristics the rule-based `interpret_progress_event()` needed (and had a real bug in — it originally anchored the level-marker search on only the *first* occurrence of a skill name, so "I finished the SQL Bootcamp... now feel very comfortable with SQL" missed the SQL self-rating entirely; fixed to scan every occurrence before the LLM path existed, and both are still verified correct). The rule-based version stays as the automatic fallback.
- `feedback_agent.py` — deterministic from there: bumps skill levels (never downward), marks the course completed, recomputes total gap score before/after, and triggers a replan (rebuilds and re-persists the path) when the gap score drops by ≥5% — a concrete stand-in for the plan's "materially changed."
- `test_harness.py` — builds an initial profile+path, submits one progress event, shows the before/after gap score and the replanned (now shorter) path.

Run it:

```bash
python services/progress-feedback/test_harness.py
```
