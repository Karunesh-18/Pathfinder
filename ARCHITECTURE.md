# Personalized Learning Path Recommender

System architecture & build plan · draft v1

How the six required components become a working multi-agent system: what each agent does, what it's built from, what it reads and writes, and the order to build it in.

Prepared for **Haris** · **31 Aug 2026** · Status: **Ready to prototype**

## Index

1. [Where we actually stand](#01-where-we-actually-stand)
2. [Architecture overview](#02-architecture-overview)
3. [Agent & service roster](#03-agent--service-roster)
4. [Data & memory layer](#04-data--memory-layer)
5. [Build plan](#05-build-plan)
6. [Suggested tech stack](#06-suggested-tech-stack)
7. [Risks & open questions](#07-risks--open-questions)
8. [Recommended first prototype](#08-recommended-first-prototype)

---

## 01 · Where we actually stand

A quick reset before the plan, because it changes what "reuse the existing algorithm" means.

`v3.py` solves a narrower problem than this brief: given a synthetic dataset of templated course reviews, it exactly identifies the course by dictionary lookup on a fixed topic sentence, then ranks 10 similar reviews by TF-IDF cosine similarity, tuned until it matched a leaderboard score. It has no concept of learner goals, skill levels, or prerequisites, and it won't generalize to real Coursera or Udemy content, which isn't built from templates.

> **What's actually reusable**
>
> The similarity-ranking technique itself — TF-IDF / embedding cosine similarity over course text — is a legitimate building block for content-based retrieval. It just needs to be repointed at real course descriptions instead of templated reviews. That's the one piece of `v3.py` that carries forward into the plan below (Agent 04).

## 02 · Architecture overview

A request moves through five agents/services in sequence, reading and writing three shared stores. A sixth agent closes the loop when the learner reports progress.

**Diagram description (as authored in the source artifact):** A learner's goal flows left to right through the Intake and Profiling Agent, Skill-Gap Analysis Agent, Course Retrieval and Ranking Service, Path Construction Service, and Explainability and Q&A Agent, producing a roadmap and rationale. Along the way these components read and write three shared stores: the Learner Profile Store, the Course and Skills Knowledge Base, and the Path Store. A dashed line shows the Progress and Feedback Agent capturing learner progress, writing it back to the Profile Store, and re-triggering the Skill-Gap Agent to replan.

Main thread: `Learner → Intake & Profiling Agent → Skill-Gap Analysis Agent → Retrieval & Ranking Service → Path Construction Service → Explainability Agent → roadmap + rationale returned to learner`

Reads/writes against the data layer:
- Intake & Profiling Agent writes profile → Learner Profile Store
- Skill-Gap Analysis Agent reads profile ← Learner Profile Store
- Skill-Gap Analysis Agent reads taxonomy / MCP catalog search ← Course & Skills Knowledge Base
- Retrieval & Ranking Service reads taxonomy / MCP catalog search ← Course & Skills Knowledge Base
- Path Construction Service writes roadmap → Path Store
- Explainability Agent reads roadmap ← Path Store

Feedback loop (dashed): Progress & Feedback Agent captures learner progress → writes back into Learner Profile Store → re-triggers the Skill-Gap Analysis Agent to replan.

> Figure caption: The main request thread (amber) runs left to right through five components and back to the learner. Structural reads/writes against the three stores are thin grey lines. The dashed loop shows how a learner's later progress re-enters the pipeline at the Skill-Gap Agent instead of starting over.

Not every box needs to reason with an LLM. Four of the nine components above are deterministic code wrapped in a tool interface — ranking math and graph algorithms, not language understanding. Section 03 marks which is which; treating everything as an "agent" is the most common way these systems get slower and harder to debug than they need to be.

## 03 · Agent & service roster

Eight components cover the six requirements in the brief. Each card states its type, its one job, what it reads and writes, and the tools it's built from.

### 01 — Orchestrator Agent
**Type:** Reasoning agent
**Mission:** Owns the conversation session; decides which specialist to call next from learner intent and session state; merges results into one reply.
- **Reads:** Raw learner message, session state
- **Writes:** Routed sub-agent call, composed reply
- **Tools:** `session_store`, `subagent_invoke`, `dialogue_memory`

### 02 — Intake & Profiling Agent
**Type:** Reasoning agent
**Mission:** Turns free-form goals into a structured profile — target role, current skills and levels, completed courses, time budget, format preference — and asks follow-ups when it's underspecified.
- **Reads:** Learner free text, existing profile
- **Writes:** Structured LearnerProfile
- **Tools:** `profile_schema_extract`, `learner_profile_store`, `skills_taxonomy_lookup`

### 03 — Skill-Gap Analysis Agent
**Type:** Hybrid
**Mission:** Ranks the missing or weak skills between the learner's current profile and the target role. LLM judgment only interprets vague self-ratings; the gap math is deterministic.
- **Reads:** LearnerProfile, role skill requirements
- **Writes:** Ranked SkillGap list
- **Tools:** `skills_taxonomy_graph`, `role_requirements_table`, `embedding_similarity`

### 04 — Retrieval & Ranking Service
**Type:** Deterministic service
**Mission:** For each skill gap, retrieves and ranks real candidate courses, projects and assessments by relevance, level-fit and format-fit. Where the v3.py similarity technique legitimately carries forward — repointed at real course text.
- **Reads:** SkillGap list, LearnerProfile
- **Writes:** Ranked candidates per gap
- **Tools:** `coursera.search_courses`, `coursera.search_hands_on_learning`, `udemy.search_courses`, `udemy.get_course_curriculum`, `tfidf_rank`

### 05 — Path Construction Service
**Type:** Deterministic service
**Mission:** Builds the prerequisite graph across chosen candidates, topologically sorts it, inserts milestone checkpoints, and fits the sequence to the learner's time budget. No language reasoning needed.
- **Reads:** Ranked candidates, prerequisite metadata, time budget
- **Writes:** Ordered LearningPath with milestones
- **Tools:** `dag_builder`, `topo_sort`, `path_store`

### 06 — Explainability & Q&A Agent
**Type:** Reasoning agent
**Mission:** Generates a plain-language rationale per step, naming the skill gap it closes and the profile signal that triggered it. Answers free-form learner questions about the plan.
- **Reads:** LearningPath, LearnerProfile, SkillGap list, course metadata
- **Writes:** Per-step rationale, conversational answers
- **Tools:** `path_store`, `course_kb_retrieve`, `rag_generate`

### 07 — Progress & Feedback Agent
**Type:** Hybrid
**Mission:** Ingests completions, scores and explicit feedback; updates the skill vector and preference weights; triggers a re-plan when the gap picture has materially changed.
- **Reads:** Progress events, current LearnerProfile
- **Writes:** Updated LearnerProfile, re-plan trigger
- **Tools:** `progress_ingest`, `learner_profile_store`, `replan_trigger`

### 08 — Dashboard / Reporting Service
**Type:** Deterministic service
**Mission:** Aggregates profile, path and progress into the visuals the brief asks for — skill radar, milestone timeline, next recommended action. Pure aggregation, no reasoning.
- **Reads:** LearnerProfile, LearningPath, progress log
- **Writes:** Dashboard view model
- **Tools:** `store_read (x3)`, `chart_render`

## 04 · Data & memory layer

Four stores everything above reads and writes against. None of this exists in v3.py's world — it was one CSV.

**Learner Profile Store** — Per-learner record: goal role, skill vector with levels, completed courses, time budget, format preference, feedback history. Read/written by agents 01, 02, 03, 07, 08.

**Skills Taxonomy Graph** — Skill nodes with dependency edges, seeded from a reference source (O*NET / ESCO) and curated per target role in scope. Read by agents 02, 03.

**Course & Skills Knowledge Base** — Vector index of course metadata pulled from the Coursera and Udemy Business connectors: title, description, skills taught, level, prerequisites. Read/written by agents 03, 04, 06.

**Path Store** — The generated LearningPath per learner: ordered steps, milestone flags, completion state. Read/written by agents 05, 06, 08.

## 05 · Build plan

Eight phases, each unlocked by the one before it. Nothing downstream of Phase 0 can be honestly tested without real course data in the loop.

| Phase | Goal | Deliverable | Est. |
|---|---|---|---|
| 00 · Foundations | Stand up the data layer before any agent runs | Profile schema live; Coursera + Udemy MCP connected and indexed into the Course KB; a starter taxonomy for 10–15 target roles | 1–2 wk |
| 01 · Intake | Turn a real learner statement into a structured profile | Intake & Profiling Agent (02) validated against sample goals | 1 wk |
| 02 · Recommendation core | Prove content-based ranking works on real courses | Retrieval & Ranking Service (04), reusing the TF-IDF technique on real text | 1–2 wk |
| 03 · Gap & path | Turn ranked candidates into a sequenced roadmap | Skill-Gap Agent (03) + Path Construction Service (05), DAG and milestones | 1–2 wk |
| 04 · Explainability | Make every recommendation defensible in plain language | Explainability & Q&A Agent (06) wired to the completed path | 1 wk |
| 05 · Feedback loop | Close the adaptive loop end to end | Progress & Feedback Agent (07); one full replan cycle working | 1 wk |
| 06 · Dashboard | Visualize the now-complete data model | Dashboard / Reporting Service (08): skill radar, timeline, next action | 1 wk |
| 07 · Evaluation | Measure it honestly — there's no leaderboard this time | Pilot with real learner goals; track gap-closure rate, path completion, rationale ratings | ongoing |

## 06 · Suggested tech stack

A starting point, not a commitment — swap anything the team already has strong opinions about.

**Orchestration** — Claude Agent SDK for the reasoning agents; plain function calls for the deterministic services underneath them.

**Storage** — Postgres with pgvector — keeps the profile, taxonomy, course index and path store in one database instead of four.

**Course data** — Coursera and Udemy Business MCP connectors as primary sources; Coursera's Catalog API and Udemy's Affiliate API as non-MCP fallbacks.

**Taxonomy seed** — O*NET or ESCO as a reference to seed the skills graph, then hand-curate the roles actually in scope.

**Dashboard** — A lightweight frontend reading straight from the same Postgres store — no separate analytics pipeline needed at this scale.

## 07 · Risks & open questions

**Connector scope** — The Udemy Business connector likely reflects only your org's licensed catalog, not the full public marketplace — confirm this before the retrieval layer depends on it.

**Cold start** — A brand-new learner has no history. Intake needs to work well from a single conversation, not accumulate accuracy over time the way the ranking script did.

**Prerequisite data quality** — Real catalogs don't expose clean prerequisite graphs the way the synthetic dataset implied structure existed. Prerequisites will likely need hand-curation for whichever roles ship first.

**No ground truth** — There's no leaderboard here. Success has to come from proxy metrics — gap-closure rate, completion rate, rationale ratings — and a small pilot, not a single score.

## 08 · Recommended first prototype

Start at Phase 00 + 02 combined: connect the Coursera and Udemy MCP tools, pull real metadata for one target role, and repoint the existing TF-IDF similarity code at it. That's the one piece of `v3.py` that's genuinely salvageable, and it gives an early, honest read on whether content-based ranking is good enough before the rest of the pipeline gets built on top of it.

---

Learning Path Recommender · Architecture & Build Plan · v1

---

*Note: this document is a faithful text transcription of the architecture artifact at https://claude.ai/code/artifact/de61f24d-4504-431b-bffe-ef9c3981ab28 (rendered HTML → Markdown), preserving its section structure and content unmodified. The original diagram (an inline SVG) is represented above as the text description and reads/writes list that were already part of the artifact's accessible description and figure caption, not new analysis.*
