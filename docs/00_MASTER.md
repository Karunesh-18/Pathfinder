# Adaptive Learning Agent — Master Doc

Round 2 Hackathon — Personalized Learning Path Recommender

This is the single source of truth. Read this first, then your role doc:

- `01_BACKEND.md`
- `02_FRONTEND.md`
- `03_AI.md`
- `04_CODING_STANDARDS.md` — everyone
- `05_MCP_GUIDE.md` — mainly AI dev, relevant if backend/frontend add tool-calling later
- `06_DEPLOYMENT.md` — everyone, own your service's section

---

## 1. Product positioning

Not a course recommender. An **adaptive learning agent**: it models the learner continuously, discovers resources, measures actual learning evidence (not just completion), asks targeted questions when it lacks information, and rebuilds the path as evidence comes in.

Core loop:
```
Goal → Learner Model (Digital Twin) → Skill Gap → Resource Discovery
→ Personalized Path → Learning → Evidence → Mastery/Experience Analysis
→ (ask targeted question if low-confidence) → Digital Twin Update
→ Dynamic Replanning → back to Path
```

## 2. MVP scope decisions (read this before building anything)

We are building the full architecture in code (generic, not hardcoded) but only fully populating **one domain** for the demo, and cutting anything that's a project of its own. This table is the actual build contract — the full concept doc is what goes in the solution writeup.

| Area | Full concept | What we build |
|---|---|---|
| Domains | Coding, photography, music, etc. | One domain fully populated (coding/data). Engine stays domain-agnostic in code — no hardcoded skill names in logic. |
| Platform integration | Official APIs/xAPI/LMS integration | User self-reports completion only. No live platform integrations. |
| Resource discovery | Curated + scheduled refresh + live web discovery | Curated catalog only, refreshed on a schedule (or manually). Live discovery described as future work, not built. |
| Assessment | Quiz, coding task, project, photo, audio, written explanation | One type: short auto-graded quiz. |
| Career alignment | Full readiness scoring module + screen | One number on the dashboard: skill overlap % vs target role. No separate screen. |
| Browser extension | Companion evidence collector | Not built. Future work slide only. |
| Questioning | Unlimited targeted questions | Max 2 clarifying questions per session before falling back to a default assumption. |
| Emotion/state detection | Estimated from feedback + behavior | Same — but explicitly labeled "estimate with confidence" everywhere in the UI. Never claim certainty, never use webcam/biometric input. |

## 3. Team & ownership

| Area | Owner | Owns |
|---|---|---|
| Backend | Backend dev | API, DB schema, auth, orchestration into AI service, deployment |
| Frontend | Frontend dev | Onboarding chat, dashboard, roadmap, resource cards, mentor chat |
| AI/ML | AI dev | Digital Twin logic, skill gap engine, hybrid recommender, path generator, evidence/mastery analysis, active questioning, replanning rules, explanation generation |

## 4. Tech stack

- Frontend: React (Vite) or Next.js, Recharts for skill/mastery visuals
- Backend: FastAPI, PostgreSQL, SQLAlchemy
- Vector search: FAISS or pgvector (pgvector avoids running a second service — prefer it if Postgres is already there)
- AI: sentence-transformers or an LLM embeddings API for semantic matching; an LLM API for extraction, chat, explanation, feedback analysis, question generation, quiz generation
- Deployment: Render/Railway (backend + AI), Vercel (frontend)

## 5. Learner Digital Twin (data shape, scoped)

```json
{
  "user_id": "uuid",
  "goal": "string",
  "target_role": "string",
  "timeframe_weeks": "int",
  "hours_per_week": "int",
  "skill_vector": { "python": 0.82, "sql": 0.35 },
  "skill_confidence": { "python": 0.9, "sql": 0.4 },
  "experience_vector": { "video": 0.75, "projects": 0.9 },
  "behavior": { "avg_session_min": 42, "completion_rate": 0.81, "quiz_accuracy": 0.74 },
  "state": {
    "pace": { "value": "moderate", "confidence": 0.6 },
    "difficulty_fit": { "value": "good", "confidence": 0.7 },
    "emotion": { "value": "neutral", "confidence": 0.5 }
  },
  "questions_asked_this_session": 0
}
```
Confidence sits next to every estimated field — this is what "ask only when uncertain" thresholds against. Store this whole object as one JSONB column on `learner_profiles` for the MVP rather than splitting into more tables (see data model below).

## 6. Data model (scoped — merged from the full concept's 15+ entities)

| Entity | Purpose |
|---|---|
| `users` | Account/identity |
| `learner_profiles` | Goal, constraints, and the full Digital Twin JSON (skills, experience, behavior, state — see above) |
| `skills` | Skill nodes for the active domain |
| `skill_prerequisites` | Directed prerequisite edges |
| `resources` | Curated catalog entries (course/video/article/project) |
| `resource_skills` | Skills each resource addresses |
| `learning_paths` | Roadmap versions — include `path_version` int so replanning is auditable, not a silent overwrite |
| `path_items` | Individual milestones/activities in a path version |
| `assessment_results` | Quiz scores + self-reported completion + time spent (merged — don't split "progress_events" out separately for MVP) |
| `feedback` | Free-text feedback + extracted structured signals (emotion/pace/difficulty + confidence) |
| `recommendations` | Ranked resources + reason, per generation |

## 7. API contract (backend, consumed by frontend) — see `01_BACKEND.md` for full schemas

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | Goal capture, mentor chat, targeted follow-up questions |
| POST | `/api/profile` | Create/update learner profile |
| GET | `/api/profile/{user_id}` | Fetch Digital Twin |
| GET | `/api/recommend/{user_id}` | Ranked resources for current gaps |
| POST | `/api/path/{user_id}` | Generate/regenerate roadmap |
| GET | `/api/path/{user_id}` | Fetch current roadmap version |
| POST | `/api/progress/{user_id}` | Report completion/quiz result, triggers evidence analysis |
| POST | `/api/feedback/{user_id}` | Free-text/structured feedback on a resource |
| GET | `/api/explain/{user_id}/{resource_id}` | Grounded "why this" explanation |
| GET | `/api/dashboard/{user_id}` | Skill growth, mastery, milestones, next actions |

## 8. Repo structure

```
/backend        - FastAPI app, DB models, endpoints
/ai_service     - digital twin, skill gap, recommender, path generator, evidence engine
/frontend       - React app
/data           - skill_graph.json, resource_catalog.json (one domain for MVP)
/docs           - all docs in this set
README.md       - setup + run instructions
```

## 9. Standout features to lead with in the demo/write-up

Digital Twin (evolving, not static) · self-rebuilding roadmap from real evidence · targeted questions instead of guessing · completion ≠ mastery · editable roadmap with trade-off explanations · domain-agnostic engine (shown via one populated domain).

## 10. Demo story (~4:30)

0:00–0:30 goal + constraints in chat → 0:30–1:00 one or two targeted questions build the Digital Twin → 1:00–1:30 skill gaps + roadmap appear → 1:30–2:15 resource cards with "why this/why now/why not X" → 2:15–3:00 feed in a pre-seeded "fast learner" result (high quiz score, "too easy" feedback) and show the roadmap compress/advance → 3:00–3:30 feed in a pre-seeded "struggling" result and show remedial insertion → 3:30–4:00 dashboard: skill growth + mastery vs completion → 4:00–4:30 close.

Use pre-seeded feedback text for the two adaptation demos — don't rely on a live LLM call producing exactly the right signal on stage.

## 11. Submission checklist

- [ ] Source ZIP (exclude venv/node_modules/build)
- [ ] GitHub repo, accessible, real commit history
- [ ] Solution doc (PDF/PPT): problem understanding, architecture, AI/ML techniques, MVP scope decisions, challenges
- [ ] 3–5 min demo video
- [ ] Deployed URL or local setup instructions

## 12. Suggested timeline

| Phase | Backend | Frontend | AI |
|---|---|---|---|
| Day 1 | DB schema + skeleton endpoints (mocked) | Chat UI + onboarding | Skill graph + resource catalog (one domain) + embeddings |
| Day 2 | Wire real endpoints to AI service | Roadmap + resource cards | Skill gap engine + hybrid recommender + path generator |
| Day 3 | Feedback/progress endpoints + replanning trigger | Dashboard + mentor chat + explanations | Evidence engine + active questioning + replanning rules |
| Day 4 | Deploy, integration testing | Deploy, integration testing | Tune ranking + quiz generation, write AI/ML section |
| Day 5 | Buffer, demo video, docs | Buffer, demo video, docs | Buffer, demo video, docs |
