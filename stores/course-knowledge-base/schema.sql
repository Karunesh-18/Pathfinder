-- Course & Skills Knowledge Base — target schema (Postgres + pgvector)
--
-- Per ARCHITECTURE.md Section 04 / Section 06. Not yet run anywhere: this
-- machine has no Postgres server available. The prototype's actual runnable
-- store is stores/course-knowledge-base/ingest.py, which loads the same
-- shape into SQLite. Run this file against a real Postgres instance when one
-- is available, then point ingest.py at it instead.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS courses (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    provider        TEXT NOT NULL,          -- e.g. 'Coursera', 'Udemy'
    url             TEXT,
    description     TEXT NOT NULL,
    skills_taught   TEXT[] NOT NULL DEFAULT '{}',
    level           TEXT,                   -- 'beginner' | 'intermediate' | 'advanced'
    format          TEXT,                   -- 'self-paced' | 'cohort' | 'video' | ...
    target_roles    TEXT[] NOT NULL DEFAULT '{}',
    prerequisites   TEXT[] NOT NULL DEFAULT '{}',
    estimated_hours NUMERIC,                -- rough hand estimate, not scraped — see seed_data_engineer.json
    embedding       VECTOR(384),            -- populated once an embedding model is chosen
    source          TEXT NOT NULL DEFAULT 'hand-built-sample',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Added after the table's first deployment — CREATE TABLE IF NOT EXISTS
-- above is a no-op against an already-existing table, so new columns need
-- an explicit ALTER TABLE to reach a database from an earlier run of this
-- schema. Both statements are idempotent (safe to re-run).
ALTER TABLE courses ADD COLUMN IF NOT EXISTS estimated_hours NUMERIC;

CREATE INDEX IF NOT EXISTS courses_embedding_idx
    ON courses USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS courses_target_roles_idx
    ON courses USING gin (target_roles);
