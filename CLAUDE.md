# CLAUDE.md — Project Guide for AI Tools

This file is the source of truth for AI coding tools (Claude Code, Copilot, Cursor) working on this project. It captures current build status, conventions, and gotchas so AI tools produce code that fits — and don't reintroduce bugs already hit and fixed once.

`ARCHITECTURE.md` is the original plan (kept unmodified, treat as the design source of truth for *what* to build). This file tracks *what's actually built* and *how the codebase actually works*, which has diverged from and gone beyond the plan in places — read both.

## Project Overview

**Personalized Learning Path Recommender** — a multi-agent system that takes a learner's free-form goal, builds a structured profile, identifies skill gaps against a target role, constructs an ordered learning path from real course data, explains its reasoning, and adapts as the learner reports progress. Per `ARCHITECTURE.md`'s roster: 8 agents/services + 4 data stores.

Target role scope right now: **Data Engineer only** (the one role seeded into the Course & Skills Knowledge Base and Skills Taxonomy Graph).

## Status — build progress by phase

Per `ARCHITECTURE.md` Section 05's roadmap. All phases below are implemented and verified working end to end against live Supabase + Groq.

| Phase | What | Status |
|---|---|---|
| 00 · Foundations | Course & Skills Knowledge Base | ✅ Done — Supabase-backed, 12 hand-built sample courses (see Known Gaps) |
| 01 · Intake | Intake & Profiling Agent | ✅ Done — real Groq LLM extraction, rule-based stub as fallback |
| 02 · Recommendation core | Retrieval & Ranking Service | ✅ Done — TF-IDF cosine similarity, built fresh (no `v3.py` existed to adapt) |
| 03 · Gap & path | Skill-Gap Agent + Path Construction | ✅ Done — deterministic gap scoring + DAG-ordered path with milestones |
| 04 · Explainability | Explainability & Q&A Agent | ✅ Done — real Groq LLM rationale + Q&A, rule-based stub as fallback |
| 05 · Feedback loop | Progress & Feedback Agent | ✅ Done — one full replan cycle verified working |
| 06 · Dashboard | Dashboard / Reporting Service | ✅ Done — deterministic aggregation, text-rendered (no frontend exists) |
| 07 · Evaluation | Real pilot | ❌ Not started — needs real learners, not more code |

**Orchestrator Agent** (roster card 01) is **not built** — it's in the agent roster but was never assigned to a roadmap phase, and nothing in this project calls the 8 services through a single entry point yet. Each service is invoked directly via its own `test_harness.py`.

## Tech stack actually in use (deviates from `ARCHITECTURE.md` Section 06)

- **Language**: Python (plan left this open; confirmed with user — matches the Python reference repos under `reference/`)
- **Reasoning agents**: **Groq**, not the Claude Agent SDK the plan names. The plan explicitly allows swapping the stack (Section 06: "a starting point, not a commitment"); Groq doesn't host Claude, so this goes through `common/llm.py`'s own Groq client, not the Agent SDK. Default model: `openai/gpt-oss-120b` — verified live against `client.models.list()`, not assumed; Groq's lineup changes (`llama-3.3-70b-versatile`, an earlier guess, 404s on this account as of 2026-08-31).
- **Storage**: Supabase (Postgres + pgvector), exactly as the plan specifies. Every store also has a SQLite fallback (see Conventions).
- **Course data**: no Coursera/Udemy MCP connectors configured (see Known Gaps) — hand-built sample data instead, behind the same provider-adapter seam a real connector would use.

## Project Structure

```
ARCHITECTURE.md              # the original plan — unmodified, read-only
CLAUDE.md                    # this file
THIRD_PARTY_NOTICES.md       # license notices for everything under reference/ and data/
requirements.txt
.env.example                 # copy to .env and fill in — never paste secrets into chat
.gitignore

common/                      # shared infra, used by every service/store
  env.py                     #   .env loading + get_database_url()
  llm.py                     #   Groq client — chat_text() / chat_json() / is_llm_configured()
  console.py                 #   fix_windows_console_encoding() — call first in any script that prints

services/                    # the 8 agents/services from the roster
  orchestrator/               #   README only — not built
  intake-profiling/           #   intake_agent.py, extract.py (+_llm), profile_schema.py, taxonomy_lookup.py
  skill-gap/                  #   gap.py, skillgap_schema.py
  retrieval-ranking/          #   rank.py (tfidf_rank)
  path-construction/          #   build_path.py, dag.py, pathconstruction_schema.py
  explainability-qa/          #   explain_agent.py, rationale.py (+_llm), qa.py (+_llm), explain_schema.py
  progress-feedback/          #   feedback_agent.py, progress_ingest.py (+_llm), progress_schema.py
  dashboard/                  #   aggregate.py, render.py, dashboard_schema.py
  <each has a>                #   test_harness.py — run directly with `python services/<name>/test_harness.py`

stores/                      # the 4 data stores from the roster, all Supabase-backed w/ SQLite fallback
  course-knowledge-base/      #   db.py, schema.sql, seed_data_engineer.json, providers/{coursera,udemy,hand_built}.py
  learner-profile-store/      #   profile_store.py, schema.sql
  skills-taxonomy-graph/      #   taxonomy_store.py, schema.sql, seed_data_engineer_taxonomy.json
  path-store/                 #   path_store.py, schema.sql

data/taxonomy/educor/        # pulled EduCOR ontology (CC0-1.0) — not yet wired into skills-taxonomy-graph
reference/                   # 4 trimmed reference repos, pattern study only — see THIRD_PARTY_NOTICES.md
```

## Critical Conventions

### 1. Never name a module `schema.py`, `agent.py`, or `db.py`

**This bit the project three separate times.** Python caches imports by bare module name in `sys.modules`; when a test harness imports multiple services in one process (which every harness past Phase 02 does), two same-named modules from different directories silently collide — the second `import db` (or `schema`, or `agent`) returns the *first* one's module, not its own. It doesn't raise ImportError; it just quietly gives you the wrong module, which then fails in a confusing way somewhere else (`AttributeError: module 'db' has no attribute 'save_profile'` was the first symptom).

**Fixed convention, followed everywhere in this codebase:**
- Schema files: `<component>_schema.py` (`profile_schema.py`, `skillgap_schema.py`, `pathconstruction_schema.py`, `explain_schema.py`, `progress_schema.py`, `dashboard_schema.py`)
- Agent orchestration files: `<component>_agent.py` (`intake_agent.py`, `explain_agent.py`, `feedback_agent.py`)
- Store DB modules: `<component>_store.py` (`profile_store.py`, `taxonomy_store.py`, `path_store.py`) — **except** `stores/course-knowledge-base/db.py`, which kept its original name since it was already verified working before the collision pattern was noticed; every *other* store deliberately avoids `db.py`.

**When adding a new module: never use a bare generic name.** If you're tempted to write `schema.py`, `agent.py`, `db.py`, `utils.py`, `config.py` — don't. Name it after the component.

### 2. Every store has a dual backend: Postgres/Supabase, SQLite fallback

Pattern: `get_database_url()` (`common/env.py`) checks `SUPABASE_DB_URL` or `DATABASE_URL` in the environment or project-root `.env`. If set, the store talks to Postgres (applying its `schema.sql`, using native arrays/JSONB). If not, it transparently falls back to a local SQLite file with the same shape. `backend_name()` on every store module reports which one is active — always check it when debugging, don't assume.

**Postgres `NUMERIC` columns come back from `psycopg2` as `decimal.Decimal`, not `float`.** This caused a real crash (`Decimal * float` in path-construction's hour math) and was fixed by normalizing to `float` right after every Postgres read (`course-knowledge-base/db.py`, `path-store/path_store.py`, `learner-profile-store/profile_store.py` all do this). **Any new Postgres read of a `NUMERIC`/`DECIMAL` column needs the same normalization** — it won't crash immediately, it'll produce silently-wrong arithmetic or a `TypeError` two calls later.

**`CREATE TABLE IF NOT EXISTS` is a no-op against a table that already exists.** Adding a column to an existing store's schema needs an explicit `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` in `schema.sql`, or it'll silently not apply to a database from an earlier run (see `course-knowledge-base/schema.sql`'s `estimated_hours` column for the pattern).

### 3. Every reasoning agent has a real LLM call + a rule-based stub fallback

Pattern: `is_llm_configured()` (`common/llm.py`) checks `GROQ_API_KEY`. If set, the agent's orchestration file (`intake_agent.py`, `explain_agent.py`, `feedback_agent.py`) tries the real `*_llm` function first, inside a `try/except` that falls back to the original rule-based stub on *any* exception (network error, rate limit, malformed JSON) and prints a `[component] Groq call failed (...); falling back to rule-based stub.` warning — it never lets an LLM failure crash the pipeline. If `GROQ_API_KEY` isn't set at all, it goes straight to the stub, no warning needed.

Stub output is always stamped with a method marker (`extraction_method="rule-based-stub"` vs `"groq-llm"`) so it's possible to tell which one produced a given result after the fact.

**When adding a new reasoning-agent capability, follow this same shape**: a `*_llm` function using `common/llm.py`'s `chat_text`/`chat_json`, a stub fallback, and dispatch logic in the orchestrator — not a bare LLM call with no fallback.

### 4. Cross-service imports go through `sys.path` insertion, not real Python packages

Directory names are kebab-case (`intake-profiling`, `skill-gap`, ...) per explicit user request when the skeleton was built — Python can't `import` a hyphenated package name. So every file that needs a sibling service/store inserts that directory onto `sys.path` and does a bare `import <module>`, e.g.:
```python
_SKILLGAP_PATH = Path(__file__).resolve().parents[2] / "services" / "skill-gap"
if str(_SKILLGAP_PATH) not in sys.path:
    sys.path.insert(0, str(_SKILLGAP_PATH))
from gap import compute_skill_gaps
```
This is why Convention #1 (unique module names) matters so much — it's the only thing preventing collisions in this import style. Every orchestrator (`*_agent.py`) inserts the **project root** first, before anything else, so `common.env`/`common.llm`/`common.console` are always importable regardless of what else gets imported later in the file.

### 5. Console output must survive cp1252 (this machine is Windows)

Hand-written strings with em dashes or `★` broke `print()` on this console early on (fixed by using plain ASCII in those specific strings) — but **real LLM-generated text can contain any Unicode character** and isn't under this project's control. `common/console.py`'s `fix_windows_console_encoding()` reconfigures stdout/stderr to UTF-8 with `errors="replace"` and is called first-thing in every `test_harness.py`. **Any new entry-point script must call it too**, before any printing happens — otherwise a stray character in LLM output will crash the whole script.

## Environment Variables

Copy `.env.example` to `.env` at the project root (gitignored, never commit it, never paste its contents into chat):

- `SUPABASE_DB_URL` — direct Postgres connection string (port 5432, not the 6543 pooler — DDL needs a direct session). Without it, every store falls back to local SQLite.
- `GROQ_API_KEY` — without it, every reasoning agent falls back to its rule-based stub.

## Running Things

Every service is a standalone script — there's no single entry point (no orchestrator yet):

```bash
pip install -r requirements.txt

python stores/course-knowledge-base/ingest.py          # seed the course KB (run first)
python stores/skills-taxonomy-graph/taxonomy_store.py   # seed the taxonomy graph (run first)

python services/retrieval-ranking/test_harness.py
python services/intake-profiling/test_harness.py
python services/skill-gap/test_harness.py
python services/path-construction/test_harness.py
python services/explainability-qa/test_harness.py
python services/progress-feedback/test_harness.py
python services/dashboard/test_harness.py
```

Each later harness re-runs the earlier pipeline stages internally (Intake → Skill-Gap → Path Construction → ...) using the same sample learner goal, so they're independently runnable — no fixture setup needed beyond the two seed scripts above.

## Known Gaps / Deliberate Assumptions

- **Course data is a hand-built 12-course sample**, not real Coursera/Udemy data. No MCP connectors are configured for either platform. `stores/course-knowledge-base/providers/{coursera,udemy}.py` are ready-shaped adapters that currently raise `ProviderNotConfigured` and fall back to the hand-built rows — wiring a real connector means filling in `fetch()` in those two files; nothing else in the pipeline needs to change.
- **Skills Taxonomy Graph is hand-curated**, not seeded from O*NET/ESCO (or `data/taxonomy/educor/`, which was pulled but never wired in — see `stores/skills-taxonomy-graph/README.md`).
- **Target role is hardcoded to "Data Engineer"** in several places (`DEFAULT_ROLE_FOR_TAXONOMY` in `intake_agent.py`) — the system doesn't yet route a learner's own stated target role to a matching taxonomy/course-KB slice, because only one role is seeded.
- **`estimated_hours` per course is a rough hand estimate**, not scraped from a real source — used for path-fitting math, flagged as such in the seed data.
- **`DEFAULT_WEEKLY_HOURS = 5.0`** (`path-construction/build_path.py`) is the fallback when a learner's time budget is unspecified.
- **Replan threshold is `REPLAN_THRESHOLD_FRACTION = 0.05`** (`progress-feedback/feedback_agent.py`) — a concrete stand-in for the plan's qualitative "materially changed."
- **No Orchestrator Agent** — see Status table above.
- **No frontend** — `dashboard/render.py`'s `chart_render` is plain text, standing in for whatever a real chart library/frontend would consume the same `DashboardViewModel` to produce.

## Things Not To Do

- Don't add a module named `schema.py`, `agent.py`, `db.py`, or any other bare generic name — see Convention #1.
- Don't read a Postgres `NUMERIC`/`DECIMAL` column without normalizing to `float` — see Convention #2.
- Don't add a real LLM call without a stub fallback and dispatch logic — see Convention #3.
- Don't print anything in a new entry-point script before calling `fix_windows_console_encoding()` — see Convention #5.
- Don't edit `ARCHITECTURE.md` — it's the original plan, kept as-is on purpose. Document deviations here instead.
- Don't paste `.env` contents (Supabase connection string, Groq API key) into chat — edit the file directly.
