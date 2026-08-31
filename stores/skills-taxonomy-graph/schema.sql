-- Skills Taxonomy Graph — target schema (Postgres/Supabase)
--
-- Per ARCHITECTURE.md Section 04 / Section 03 card 03. This is a
-- deliberately minimal shape: skill nodes are implicit (just skill-name
-- strings, matching the vocabulary already used in the Course & Skills
-- Knowledge Base), a per-role weighted requirement list, and a
-- prerequisite edge list. A real graph seeded from O*NET/ESCO would add
-- proper node metadata (categories, external IDs); this doesn't attempt
-- that yet — see the store's README for what's hand-curated vs. real.

CREATE TABLE IF NOT EXISTS skill_requirements (
    role            TEXT NOT NULL,
    skill           TEXT NOT NULL,
    required_level  TEXT NOT NULL,           -- 'beginner' | 'intermediate' | 'advanced'
    weight          NUMERIC NOT NULL DEFAULT 1,  -- relative priority within the role
    PRIMARY KEY (role, skill)
);

CREATE TABLE IF NOT EXISTS skill_dependencies (
    role          TEXT NOT NULL,
    skill         TEXT NOT NULL,
    prerequisite  TEXT NOT NULL,
    PRIMARY KEY (role, skill, prerequisite)
);
