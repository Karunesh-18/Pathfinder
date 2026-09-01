# CLAUDE.md — Project Guide for AI Tools

This file is the source of truth for AI coding tools (Claude Code, Copilot, Cursor) working on this project. It captures current build status, conventions, and gotchas so AI tools produce code that fits — and don't reintroduce bugs already hit and fixed once.

`ARCHITECTURE.md` is the original plan (kept unmodified, treat as the design source of truth for *what* to build). This file tracks *what's actually built* and *how the codebase actually works*, which has diverged from and gone beyond the plan in places — read both.

## Project Overview

**Personalized Learning Path Recommender** — a multi-agent system that takes a learner's free-form goal, builds a structured profile, identifies skill gaps against a target role, constructs an ordered learning path from real course data, explains its reasoning, and adapts as the learner reports progress. Per `ARCHITECTURE.md`'s roster: 8 agents/services + 4 data stores.

Target role scope: **four roles seeded** into the Course & Skills Knowledge Base and Skills Taxonomy Graph — Data Engineer, Data Scientist, ML Engineer, Frontend Developer (added in the login/multi-role frontend rework; see `stores/course-knowledge-base/ingest.py`'s `ROLE_SEEDS` and `stores/skills-taxonomy-graph/taxonomy_store.py`'s `SEED_FILES` to add more). `services/intake-profiling/intake_agent.py`'s `DEFAULT_ROLE_FOR_TAXONOMY` ("Data Engineer") is now genuinely a fallback, not the only option — a learner's actual target role is set authoritatively via the frontend's Explore Roles / Settings pages (`PATCH /api/learners/{id}`), since free-text chat extraction only trusts an exact match against a seeded role name.

A lightweight real-accounts auth layer and a React frontend (login/signup, chat-based onboarding, course browsing with filters, a course-detail page, a skill-tree visualization, a general-purpose chatbot, a roadmap/dashboard split, and role/settings management) sit in front of the pipeline — see `backend/` and `frontend/` below. There is still no Orchestrator Agent; `backend/service_bridge.py` is the closest thing to one, but it's a REST-API bridge, not the roster's agent.

## Status — build progress by phase

Per `ARCHITECTURE.md` Section 05's roadmap. All phases below are implemented and verified working end to end against live Supabase + Groq.

| Phase | What | Status |
|---|---|---|
| 00 · Foundations | Course & Skills Knowledge Base | ✅ Done — Supabase-backed, 42 hand-built sample courses across 4 roles (see Known Gaps) |
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

stores/                      # the 4 data stores from the roster, all Supabase-backed w/ SQLite fallback,
                              #   plus a 5th (account-store) added for login — not part of ARCHITECTURE.md's roster
  course-knowledge-base/      #   db.py, schema.sql, seed_<role>.json (x4), providers/{coursera,udemy,hand_built}.py
  learner-profile-store/      #   profile_store.py, schema.sql
  skills-taxonomy-graph/      #   taxonomy_store.py, schema.sql, seed_<role>_taxonomy.json (x4)
  path-store/                 #   path_store.py, schema.sql
  account-store/               #   account_store.py, schema.sql — users table (bcrypt password hash), keyed by uuid

backend/                     # FastAPI REST layer wrapping the services/stores for the React frontend
  main.py                     #   app entry, CORS, router registration — call chain: CLAUDE.md Convention #4
  service_bridge.py           #   the ONLY file that imports services/ or stores/ — every route module goes through it
  api_schemas.py               #   all request/response Pydantic models
  auth_token.py, current_user.py, auth_routes.py  # JWT (PyJWT) issue/verify + signup/login/me
  learner_routes.py, path_routes.py, explain_routes.py, progress_routes.py, dashboard_routes.py, courses_routes.py
                              #   every {learner_id}-scoped route requires Depends(get_current_user_id) + a
                              #   403 ownership check; /api/courses, /api/courses/{id}, /api/courses/tree,
                              #   /api/roles, /api/system/status stay public (not learner-scoped)
  chat_assistant.py, chat_routes.py  # general-purpose chatbot — Convention #3 shape, lives in backend/ not services/
                              #   (not a pipeline stage, doesn't belong in the 8-agent roster)

frontend/                    # React 19 + Vite + TS + Tailwind v4 + react-query + react-router v7
  src/context/AuthContext.tsx  #   JWT in localStorage, GET /api/auth/me revalidation — see src/api/client.ts
                              #   for the Authorization header attach + 401-redirect-to-/login logic
  src/pages/                  #   Landing, Login, Signup, Onboarding, Roles, Courses (+ filters), CourseDetail,
                              #   CourseTree (@xyflow/react — skill DAG, not a course DAG, see below), Chatbot,
                              #   Roadmap (sequence + progress strip), Dashboard (skill analytics + reporting),
                              #   Settings (edit profile)

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
- `GROQ_API_KEY` — without it, every reasoning agent (and `backend/chat_assistant.py`) falls back to its rule-based stub.
- `JWT_SECRET` — signs login tokens (`backend/auth_token.py`). Without it, the backend falls back to a fixed, insecure development-only secret and prints a warning — fine for local dev, never for a real deployment.
- `ALLOWED_ORIGINS` — comma-separated extra CORS origins for the deployed frontend (`backend/main.py` always allows `http://localhost:5173` regardless).

## Running Things

Each service is still independently runnable via its own `test_harness.py` (no orchestrator agent), but there is now a real entry point for actually using the app — `backend/` + `frontend/`:

```bash
pip install -r requirements.txt

python stores/course-knowledge-base/ingest.py          # seed the course KB for all 4 roles (run first)
python stores/skills-taxonomy-graph/taxonomy_store.py   # seed the taxonomy graph for all 4 roles (run first)

python services/retrieval-ranking/test_harness.py
python services/intake-profiling/test_harness.py
python services/skill-gap/test_harness.py
python services/path-construction/test_harness.py
python services/explainability-qa/test_harness.py
python services/progress-feedback/test_harness.py
python services/dashboard/test_harness.py

uvicorn backend.main:app --reload   # API on http://127.0.0.1:8000, docs at /docs
cd frontend && npm install && npm run dev   # app on http://localhost:5173
```

Each later test-harness re-runs the earlier pipeline stages internally (Intake → Skill-Gap → Path Construction → ...) using the same sample learner goal (always the Data Engineer role — the harnesses were never updated to exercise other roles), so they're independently runnable — no fixture setup needed beyond the two seed scripts above. The frontend/backend path is the multi-role-aware one; a harness run only ever proves the Data Engineer regression case still works.

## Known Gaps / Deliberate Assumptions

- **Course data is a hand-built sample** (42 courses across 4 roles), not real Coursera/Udemy data. No MCP connectors are configured for either platform. `stores/course-knowledge-base/providers/{coursera,udemy}.py` are ready-shaped adapters that currently raise `ProviderNotConfigured` and fall back to the hand-built rows (now one seed JSON per role, selected via `providers/hand_built.py`'s `SEED_FILES` map) — wiring a real connector means filling in `fetch()` in those two files; nothing else in the pipeline needs to change.
- **Skills Taxonomy Graph is hand-curated**, not seeded from O*NET/ESCO (or `data/taxonomy/educor/`, which was pulled but never wired in — see `stores/skills-taxonomy-graph/README.md`). Same caveat now applies across all 4 seeded roles, not just Data Engineer.
- **`course.prerequisites` is display-only free text, never consumed by pipeline logic** — it doesn't reliably match the taxonomy's exact-string skill vocabulary (e.g. a course lists `"ETL basics"` while the taxonomy's skill is `"ETL"`). The only structurally reliable dependency graph is the skill-level one in `skill_dependencies` (`taxonomy_store.get_dependencies`); the frontend's Course Tree page is built from that, not from `prerequisites`.
- **Free-text target-role extraction is a deliberately weak link.** `intake_agent.py` normalizes an extracted `target_role` against `taxonomy_lookup.known_roles()` (case-insensitive exact match) and drops it to `missing_fields` on no match, rather than trusting a fuzzy guess like "data science professional" ≈ "Data Scientist". The frontend's Explore Roles page and Settings page (`PATCH /api/learners/{id}`) are the authoritative way a learner sets/corrects their target role.
- **No auth hardening beyond the basics**: JWT has no refresh-token rotation, expires after 7 days with no renewal flow, and there's no email verification or password-reset flow — matches the user's explicit "lightweight real accounts" scope, not an oversight.
- **`estimated_hours` per course is a rough hand estimate**, not scraped from a real source — used for path-fitting math, flagged as such in the seed data.
- **`DEFAULT_WEEKLY_HOURS = 5.0`** (`path-construction/build_path.py`) is the fallback when a learner's time budget is unspecified.
- **Replan threshold is `REPLAN_THRESHOLD_FRACTION = 0.05`** (`progress-feedback/feedback_agent.py`) — a concrete stand-in for the plan's qualitative "materially changed."
- **No Orchestrator Agent** — see Status table above; `backend/service_bridge.py` is a REST-API bridge, not the roster's agent.
- **A real frontend exists** (`frontend/`, React) as of the login/multi-role rework, but `services/dashboard/render.py`'s `chart_render` (plain-text rendering, used only by `dashboard`'s own `test_harness.py`) was left as-is — the frontend's `DashboardPage`/`SkillRadarChart` consume the same `DashboardViewModel` independently via `backend/dashboard_routes.py`, not through `render.py`.

## Things Not To Do

- Don't add a module named `schema.py`, `agent.py`, `db.py`, or any other bare generic name — see Convention #1.
- Don't read a Postgres `NUMERIC`/`DECIMAL` column without normalizing to `float` — see Convention #2.
- Don't add a real LLM call without a stub fallback and dispatch logic — see Convention #3.
- Don't print anything in a new entry-point script before calling `fix_windows_console_encoding()` — see Convention #5.
- Don't edit `ARCHITECTURE.md` — it's the original plan, kept as-is on purpose. Document deviations here instead.
- Don't paste `.env` contents (Supabase connection string, Groq API key) into chat — edit the file directly.
- Don't call `course_kb_db.list_courses()` without filtering by `target_role` when the result feeds course *selection* (as opposed to a lookup by already-known id). With 4 roles now sharing one `courses` table, an unfiltered list lets a same-named skill (e.g. "Python") pull in a course tagged for a different role entirely — this was a real regression caught during the multi-role rework's regression testing, fixed in both `services/path-construction/build_path.py` (candidate course selection) and `services/progress-feedback/feedback_agent.py` (progress-text course-completion matching, since some course titles are intentionally reused across role seed files with different ids).
