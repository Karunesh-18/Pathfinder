# Course & Skills Knowledge Base

## Role (per plan)

Vector index of course metadata pulled from the Coursera and Udemy Business connectors: title, description, skills taught, level, prerequisites.

## Read / written by

Agents 03 (Skill-Gap Analysis), 04 (Retrieval & Ranking), 06 (Explainability & Q&A).

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 04.

## Status: prototype implemented (Phase 00 + 02 slice) — with two fallbacks, both flagged to the user

**Fallback 1 — data source.** No Coursera/Udemy MCP connectors are configured in this environment, and neither service has a public catalog API usable without partner credentials this project doesn't have. Per the user's own fallback instruction, `seed_data_engineer.json` is a small **hand-built sample set**: 12 real, currently-existing courses for the target role **Data Engineer** (chosen as a reasonable default — real providers and real course titles, e.g. "IBM Data Engineering Professional Certificate" on Coursera, "The Complete SQL Bootcamp" on Udemy). Descriptions are written from general knowledge of these courses, not scraped or fetched live — they are representative, not verbatim listings. Treat this as a stand-in for the real connector output, not production data.

**Fallback 2 — storage engine.** The plan specifies Postgres + pgvector. This machine has no Postgres server and no `psycopg2`/`pgvector` packages installed (checked before building). `schema.sql` is the actual target Postgres+pgvector schema. `db.py` auto-detects a Postgres/Supabase connection (`SUPABASE_DB_URL` or `DATABASE_URL`, read from the environment or a project-root `.env`) and uses it — applying `schema.sql` and writing native Postgres arrays — when one is configured; otherwise it transparently falls back to a local SQLite file (`course_kb.db`) with the same shape. `ingest.py` and `test_harness.py` both go through `db.py`, so neither needs to change when a real database shows up.

## Connecting a real database (Supabase or otherwise)

1. Copy `.env.example` (project root) to `.env` and fill in `SUPABASE_DB_URL` with your Supabase project's **direct** Postgres connection string (Project Settings → Database → Connection string → URI; port 5432, not the 6543 pooler — DDL needs a direct session).
2. `pip install -r requirements.txt` (adds `psycopg2-binary`).
3. Run `python stores/course-knowledge-base/ingest.py` — it will print `Storage backend: Postgres/Supabase` and apply `schema.sql` automatically (idempotent — safe to re-run).
4. `.env` is gitignored; the connection string never needs to be pasted into chat.

Without step 1, everything still works exactly as before, on SQLite.

Run ingestion:

```bash
python stores/course-knowledge-base/ingest.py
```

## Provider adapter pattern (room for more platforms)

Only Coursera and Udemy are in scope right now, per the plan and per instruction — but the ingestion pipeline doesn't hardcode that. `providers/` holds one adapter module per platform, each implementing the same contract (`providers/base.py`: a `name` and a `fetch(target_role)` that returns normalized course rows, or raises `ProviderNotConfigured` if it isn't wired up yet). `ingest.py` just loops over a `PROVIDERS` list and falls back to the hand-built sample rows tagged with that platform's name when a provider isn't configured — which is the case for both Coursera and Udemy today.

Adding a third platform later (edX, LinkedIn Learning, Pluralsight, whatever comes up) means writing one new `providers/<name>.py` file and adding it to `PROVIDERS` in `ingest.py`. `schema.sql`, `rank.py`, and `test_harness.py` don't change — they already consume rows by shape, not by source.
