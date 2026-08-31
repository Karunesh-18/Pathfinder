# Skills Taxonomy Graph

## Role

Skill nodes with dependency edges, seeded from a reference source (O*NET / ESCO) and curated per target role in scope.

## Read by

Agents 02 (Intake & Profiling), 03 (Skill-Gap Analysis).

## Note

`./data/taxonomy/educor/` (EduCOR, CC0-1.0) already holds a pulled educational/career-recommendation ontology that could seed or complement this graph alongside O*NET/ESCO — worth evaluating when this store is actually built, not assumed here.

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 04.

## Status: prototype implemented (Phase 03) — hand-curated, not O*NET/ESCO-seeded

`schema.sql` + `taxonomy_store.py` (dual backend, same pattern as the other stores) hold two tables: `skill_requirements` (per-role weighted skill list) and `skill_dependencies` (prerequisite edges between skills). `seed_data_engineer_taxonomy.json` is **hand-curated from general domain knowledge** — 12 requirements and 13 dependency edges for "Data Engineer" — not sourced from O*NET, ESCO, or `data/taxonomy/educor`. Skill names match the vocabulary already used in the Course & Skills Knowledge Base so gap matching in `services/skill-gap` is exact-string, not fuzzy.

This closes the gap the earlier `services/intake-profiling/taxonomy_lookup.py` stub flagged: that module only ever derived a flat, edge-less skill list from the course KB; this store is the actual graph with dependency edges, which `services/path-construction` uses for ordering.

Run ingestion:

```bash
python stores/skills-taxonomy-graph/taxonomy_store.py
```
