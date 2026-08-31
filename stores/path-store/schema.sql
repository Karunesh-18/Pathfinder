-- Path Store — target schema (Postgres/Supabase)
--
-- Per ARCHITECTURE.md Section 04 / Section 03 card 05. One row per
-- (learner, step) — the ordered LearningPath is the set of rows for a
-- learner_id, read back sorted by step_index.

CREATE TABLE IF NOT EXISTS learning_path_steps (
    learner_id                 TEXT NOT NULL,
    step_index                 INTEGER NOT NULL,
    course_id                  TEXT NOT NULL,
    title                      TEXT NOT NULL,
    provider                   TEXT NOT NULL,
    skill_gap_addressed        TEXT NOT NULL,
    milestone                  BOOLEAN NOT NULL DEFAULT false,
    estimated_hours            NUMERIC NOT NULL DEFAULT 0,
    cumulative_hours           NUMERIC NOT NULL DEFAULT 0,
    estimated_completion_week  INTEGER,
    target_role                TEXT,
    generated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (learner_id, step_index)
);
