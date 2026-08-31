# Dashboard / Reporting Service

**Type:** Deterministic service

## Role

Aggregates profile, path and progress into the visuals the brief asks for — skill radar, milestone timeline, next recommended action. Pure aggregation, no reasoning.

## Inputs (reads)

- LearnerProfile
- LearningPath
- Progress log

## Outputs (writes)

- Dashboard view model

## Tools

- `store_read (x3)`
- `chart_render`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 08.

## Status: prototype implemented (Phase 06) — deterministic, no LLM stub needed

Unlike every reasoning/hybrid agent built in earlier phases, this one needed no `ANTHROPIC_API_KEY` workaround — "pure aggregation, no reasoning," per the plan's own card.

- `dashboard_schema.py` — `DashboardViewModel`, deliberately split into `completed_history` and `remaining_timeline` as two separate lists rather than one step-indexed timeline with a `completed` flag.
- `aggregate.py` — **design note worth reading**: the Path Store only ever holds the *remaining* plan (Path Construction and the replan cycle both rebuild it from unmet gaps), so a course whose gap gets fully closed drops out of the path rather than being marked done in place. Cross-referencing `completed_courses` against the current path would show a misleading "0 of N complete" right after real progress happens. Solved by keeping completed work (from the profile, looked up in the Course KB) and remaining work (the current path, verbatim) as two lists, normalizing overall progress against their combined hours.
- `render.py` — **`chart_render` is a plain-text rendering**, not a real chart: this project has no frontend built anywhere to hand a chart library to. Same `DashboardViewModel` a real chart_render would consume.
- `test_harness.py` — runs the full pipeline (Intake → Skill-Gap → Path Construction → one Progress event that fully closes the SQL gap) and prints the rendered dashboard, demonstrating the completed/remaining split actually working: SQL shows in COMPLETED at "advanced," dropped from the remaining timeline.

Run it:

```bash
python services/dashboard/test_harness.py
```
