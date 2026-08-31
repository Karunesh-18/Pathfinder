# Intake & Profiling Agent

**Type:** Reasoning agent

## Role

Turns free-form goals into a structured profile — target role, current skills and levels, completed courses, time budget, format preference — and asks follow-ups when it's underspecified.

## Inputs (reads)

- Learner free text
- Existing profile

## Outputs (writes)

- Structured LearnerProfile

## Tools

- `profile_schema_extract`
- `learner_profile_store`
- `skills_taxonomy_lookup`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 02.

## Status: prototype implemented (Phase 01)

- `schema.py` — the `LearnerProfile` / `SkillEntry` pydantic models.
- `extract.py` — **now backed by a real LLM call**, via Groq (`common/llm.py`), not Anthropic — the plan's stack section names the Claude Agent SDK, but explicitly allows swapping the stack, and Groq doesn't host Claude. `extract_llm()` does the real extraction; the original rule-based/keyword `extract()` stays as an automatic fallback if `GROQ_API_KEY` isn't set or the call fails (network error, rate limit, bad JSON) — `intake_agent.py` dispatches between them and prints a warning on fallback rather than crashing. Real output is stamped `extraction_method="groq-llm"`; stub output stays `"rule-based-stub"`, so it's always possible to tell which one produced a given profile.
- `taxonomy_lookup.py` — **`skills_taxonomy_lookup` is an interim implementation**, not the full Skills Taxonomy Graph. It derives a flat skill vocabulary for a role from the Course & Skills Knowledge Base's real seed data, with no dependency/prerequisite edges — that gap is the actual taxonomy graph's job (see `stores/skills-taxonomy-graph/README.md`).
- `agent.py` — orchestrates the above, flags missing required fields with follow-up questions, and persists to the Learner Profile Store.
- `test_harness.py` — runs 3 sample learner goal statements end to end (validated against sample goals, per the Phase 01 deliverable).

Run it:

```bash
python services/intake-profiling/test_harness.py
```
