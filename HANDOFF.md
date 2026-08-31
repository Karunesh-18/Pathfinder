# Handoff Notes

For whoever's picking this project up next. Written 31 Aug 2026, at the end of the first prototyping pass. Everything described here was verified working as of this date — a full regression sweep across all 7 test harnesses passed cleanly right before this was written.

Read this first, then `CLAUDE.md` (conventions and gotchas — read this before writing any code), then `ARCHITECTURE.md` (the original design plan, kept unmodified as the source of truth for *intent*).

## What this is, in one paragraph

A multi-agent system that takes a learner's plain-English goal ("I want to become a data engineer..."), turns it into a structured profile, figures out their skill gaps against a target role, builds them an ordered course sequence from real course metadata, explains why each step is there, and adapts the plan when they report progress. Right now it only knows one target role (Data Engineer) and its course data is a hand-built sample, not live Coursera/Udemy data — see "What's real vs. simulated" below before you assume otherwise.

## Where things stand

Phases 00 through 06 of the build plan (`ARCHITECTURE.md` Section 05) are built and working:

- Course & Skills Knowledge Base (Supabase-backed)
- Intake & Profiling Agent (real LLM extraction via Groq)
- Retrieval & Ranking (TF-IDF)
- Skill-Gap Agent + Path Construction (deterministic, dependency-graph-ordered)
- Explainability & Q&A Agent (real LLM, via Groq)
- Progress & Feedback Agent — a full "learner reports progress → plan re-adjusts" cycle works
- Dashboard (text-rendered, no frontend exists yet)

**Not built:** the Orchestrator Agent (nothing routes a single conversation across all 8 services yet — each is invoked directly via its own script), and Phase 07 (a real evaluation pilot, which needs actual learners, not code).

See `CLAUDE.md`'s status table for the exact same thing in a denser format, plus what's stubbed vs. real in each piece.

## Getting started

```bash
pip install -r requirements.txt
```

You'll need two things in a `.env` file at the project root (copy `.env.example`, fill in your own — **never commit this file or paste its contents anywhere**):

1. **`SUPABASE_DB_URL`** — a Postgres connection string. Ask whoever ran this before you for access to the existing Supabase project, or stand up your own (the schema will apply itself automatically the first time you run anything). Without this, every store quietly falls back to a local SQLite file instead — useful for offline work, but it's a separate, empty database from whatever's in Supabase now.
2. **`GROQ_API_KEY`** — get one free at console.groq.com. Without this, every reasoning agent falls back to a rule-based stub instead of a real LLM call — the system still runs, just with template-generated text instead of genuinely generated language.

Then seed the two stores that need seeding, and run any test harness:

```bash
python stores/course-knowledge-base/ingest.py
python stores/skills-taxonomy-graph/taxonomy_store.py

python services/path-construction/test_harness.py   # or any of the other 6
```

Each harness re-runs the earlier pipeline stages internally using the same sample learner goal, so they're independently runnable in any order after the two seed steps above.

## What's real vs. simulated — read this before demoing or extending anything

This is the single most important thing to internalize before you build on top of this:

| Piece | Status |
|---|---|
| Course data (12 courses) | **Hand-built sample**, not live Coursera/Udemy data. Real course titles/providers, descriptions written from general knowledge, not scraped. |
| `estimated_hours` per course | **Rough hand estimate**, not sourced from anywhere real. |
| Skills Taxonomy Graph (12 skills, 13 dependency edges) | **Hand-curated** from general domain knowledge, not O*NET/ESCO or any real taxonomy. |
| Intake extraction, rationale generation, Q&A, progress interpretation | **Real LLM calls** (Groq), assuming `GROQ_API_KEY` is set — otherwise silently falls back to a much simpler rule-based version. Check the printed backend/method info in each harness's output if you're not sure which one ran. |
| Skill-gap scoring, path ordering, dashboard aggregation | **Fully real**, deterministic, not simulated in any way — this part of the system is exactly as solid as it looks. |
| Postgres storage | **Real**, if `SUPABASE_DB_URL` is set. Falls back to local SQLite otherwise. |

None of the simulated pieces are hidden — every one is flagged in its own file's docstring and in the relevant `README.md`, and status fields in the data itself (`extraction_method`, `source`) tell you which path produced a given result. But it's easy to skim past those, so: **don't assume the course catalog or skills graph reflect anything beyond what's described above.**

## If you're continuing the build, roughly in priority order

1. **Wire in real Coursera/Udemy data.** `stores/course-knowledge-base/providers/{coursera,udemy}.py` are pre-shaped for this — they currently just raise `ProviderNotConfigured`. Filling in their `fetch()` functions with a real MCP connector or API call is the single highest-leverage next step; almost everything downstream (ranking, gap analysis, path construction) gets meaningfully more real the moment this does.
2. **Real taxonomy data** (O*NET, ESCO, or the already-pulled-but-unused `data/taxonomy/educor/` ontology) to replace the hand-curated skill graph.
3. **More target roles** — right now everything is hardcoded to "Data Engineer" in a few places (`DEFAULT_ROLE_FOR_TAXONOMY` in `services/intake-profiling/intake_agent.py` is the main one); the whole system needs a role-selection step before it can handle a second role.
4. **The Orchestrator Agent** — nothing currently strings the 8 services together into one conversational entry point.
5. **A real pilot** (Phase 07) — proxy metrics only mean something once real learners are using this.

## Gotchas that will cost you time if you don't know them going in

Full detail in `CLAUDE.md`, but the two that will bite fastest:

- **Never name a new file `schema.py`, `agent.py`, or `db.py`.** Every service imports its neighbors via `sys.path` tricks (the directories are kebab-case, which Python can't import as real packages), and two same-named modules from different folders silently shadow each other in the same process — no error, just the wrong module quietly being used. This happened three times already; the fix each time was renaming the file. Follow the existing `<component>_schema.py` / `<component>_agent.py` / `<component>_store.py` pattern.
- **Postgres `NUMERIC` columns come back as `Decimal`, not `float`**, via `psycopg2`. Every existing store normalizes this after reading; a new one that doesn't will produce silently wrong arithmetic, not a crash you'd catch immediately.

## Where everything lives

- `ARCHITECTURE.md` — the original design plan. Don't edit it; it's the record of intent.
- `CLAUDE.md` — conventions, gotchas, and current build status, for both AI tools and humans. Keep this updated as the source of truth for "what's actually built" as you go — it's meant to be a living document, unlike `ARCHITECTURE.md`.
- `HANDOFF.md` — this file. A one-time snapshot for onboarding, not meant to be kept in sync forever the way `CLAUDE.md` is — if it goes stale, trust `CLAUDE.md` over this.
- `THIRD_PARTY_NOTICES.md` — license notices for the trimmed reference repos under `reference/` and the ontology data under `data/taxonomy/educor/`.
- Every `services/<name>/README.md` and `stores/<name>/README.md` — role, inputs/outputs, and implementation status for that specific piece, straight from its card in `ARCHITECTURE.md`.

## One housekeeping note

There's no git repository initialized in this project yet. `.gitignore` is already in place (covers `.env`, `__pycache__`, the SQLite fallback files, `node_modules` under the reference repos). Worth doing before this grows much further.
