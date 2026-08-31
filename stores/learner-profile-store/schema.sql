-- Learner Profile Store — target schema (Postgres/Supabase)
--
-- Per ARCHITECTURE.md Section 04 / Section 03 card 02. Applied
-- automatically by db.py the first time save_profile() runs against a
-- configured Postgres/Supabase connection.

CREATE TABLE IF NOT EXISTS learner_profiles (
    learner_id                 TEXT PRIMARY KEY,
    target_role                TEXT,
    current_skills              JSONB NOT NULL DEFAULT '[]',  -- [{"skill": "...", "level": "..."}]
    completed_courses           TEXT[] NOT NULL DEFAULT '{}',
    time_budget_hours_per_week  NUMERIC,
    format_preference           TEXT,
    missing_fields               TEXT[] NOT NULL DEFAULT '{}',
    follow_up_questions          TEXT[] NOT NULL DEFAULT '{}',
    raw_text                    TEXT,
    extraction_method            TEXT NOT NULL DEFAULT 'rule-based-stub',
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);
