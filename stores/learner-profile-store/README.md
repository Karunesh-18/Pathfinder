# Learner Profile Store

## Role

Per-learner record: goal role, skill vector with levels, completed courses, time budget, format preference, feedback history.

## Read / written by

Agents 01 (Orchestrator), 02 (Intake & Profiling), 03 (Skill-Gap Analysis), 07 (Progress & Feedback), 08 (Dashboard).

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 04.

## Status: prototype implemented (Phase 01)

`schema.sql` (Postgres/Supabase target) + `profile_store.py` (dual backend: Postgres/Supabase when `SUPABASE_DB_URL`/`DATABASE_URL` is set, local SQLite fallback otherwise — same pattern as `stores/course-knowledge-base/db.py`, sharing its env-loading logic via `common/env.py`). Currently written to by `services/intake-profiling/agent.py`.

Named `profile_store.py`, not `db.py` — a module named `db` already exists in `stores/course-knowledge-base`, and two same-named modules imported from different directories in one Python process collide in `sys.modules`. Hit this as a real bug while building Phase 01; renaming this file fixed it.
