# Retrieval & Ranking Service

**Type:** Deterministic service

## Role

For each skill gap, retrieves and ranks real candidate courses, projects and assessments by relevance, level-fit and format-fit. This is where the plan's `v3.py` similarity technique was meant to legitimately carry forward — repointed at real course text.

## Inputs (reads)

- SkillGap list
- LearnerProfile

## Outputs (writes)

- Ranked candidates per gap

## Tools (per plan)

- `coursera.search_courses`
- `coursera.search_hands_on_learning`
- `udemy.search_courses`
- `udemy.get_course_curriculum`
- `tfidf_rank`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 04.

## Status: prototype implemented (Phase 00 + 02 slice)

The Coursera/Udemy MCP tools named above are **not configured in this environment** — no such connector tools are available, matching the plan's own Section 07 risk note. `coursera.*` / `udemy.*` are aspirational tool names carried over from the plan; nothing in this code calls them.

`rank.py` implements `tfidf_rank` from scratch: TF-IDF vectorization + cosine similarity over course text, general-purpose (any learner query against any course corpus). No dataset-specific masking/reconstruction logic was carried forward, per instruction — there was nothing to carry forward anyway, since `v3.py` does not exist anywhere in this project (checked; not found under any path). This is a fresh implementation of the *technique* the plan describes, not an adaptation of prior code.

Run the test harness:

```bash
python services/retrieval-ranking/test_harness.py
```
