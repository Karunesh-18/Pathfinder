-- Account Store — target schema (Postgres/Supabase)
--
-- New in the login/multi-role rework. Holds one row per registered user.
-- A user's id is reused verbatim as learner_profiles.learner_id elsewhere
-- in the system (no foreign key, no cross-store join — see CLAUDE.md's
-- "no cross-store joins by design" convention). Applied automatically by
-- account_store.py the first time create_user()/get_user_by_email() runs
-- against a configured Postgres/Supabase connection.

CREATE TABLE IF NOT EXISTS users (
    id             TEXT PRIMARY KEY,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    display_name   TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
