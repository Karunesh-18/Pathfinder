# Explainability & Q&A Agent

**Type:** Reasoning agent

## Role

Generates a plain-language rationale per step, naming the skill gap it closes and the profile signal that triggered it. Answers free-form learner questions about the plan.

## Inputs (reads)

- LearningPath
- LearnerProfile
- SkillGap list
- Course metadata

## Outputs (writes)

- Per-step rationale
- Conversational answers

## Tools

- `path_store`
- `course_kb_retrieve`
- `rag_generate`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 06.

## Status: prototype implemented (Phase 04)

- `explain_schema.py` — the `StepRationale` model.
- `rationale.py` — **`rag_generate` (per-step half) now backed by a real LLM call**, via Groq (`common/llm.py`). `generate_step_rationale_llm()` writes real, grounded, plain-language rationale from the step/gap context; the original fixed-template `generate_step_rationale()` stays as an automatic fallback if `GROQ_API_KEY` isn't set or the call fails.
- `qa.py` — **`rag_generate` (free-form Q&A half) now backed by a real LLM call**, via Groq: `answer_question_llm()` hands the model the full plan context (remaining path, profile, ranked gaps) as JSON and lets it answer directly, rather than keyword-routing to a handful of hardcoded intents. The original rule-based `answer_question()` stays as the fallback. Verified it correctly declines out-of-context questions ("what's the weather like today?") instead of hallucinating.
- `explain_agent.py` — assembles the real context (stored path, stored profile, freshly recomputed skill gaps) that both stubs run against.
- `test_harness.py` — runs one sample goal through the full pipeline, prints a rationale per step, then asks 5 sample questions (including one deliberately unrecognized one, to show the honest-fallback path).

Run it:

```bash
python services/explainability-qa/test_harness.py
```
