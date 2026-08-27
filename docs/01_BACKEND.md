# Backend Doc — Adaptive Learning Agent

Read `00_MASTER.md` first. This is the backend dev's detailed spec.

## Responsibilities

- REST API consumed by the frontend
- Postgres schema and migrations
- Orchestrate calls into the AI service
- Enforce the "max 2 clarifying questions per session" rule server-side (don't trust the frontend to enforce it)
- Deployment

## Tech stack

FastAPI, SQLAlchemy, PostgreSQL (+ pgvector extension if the AI dev wants vector search inside Postgres instead of a separate FAISS index), Pydantic, Uvicorn.

## Database schema

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE learner_profiles (
  user_id UUID REFERENCES users(id) PRIMARY KEY,
  goal TEXT,
  target_role TEXT,
  timeframe_weeks INT,
  hours_per_week INT,
  digital_twin JSONB,          -- skill_vector, skill_confidence, experience_vector,
                                -- behavior, state (pace/difficulty_fit/emotion + confidence)
  questions_asked_session INT DEFAULT 0,
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE skills (
  id TEXT PRIMARY KEY,
  domain TEXT,
  name TEXT
);

CREATE TABLE skill_prerequisites (
  skill_id TEXT REFERENCES skills(id),
  prerequisite_id TEXT REFERENCES skills(id),
  PRIMARY KEY (skill_id, prerequisite_id)
);

CREATE TABLE resources (
  id TEXT PRIMARY KEY,
  domain TEXT,
  title TEXT,
  provider TEXT,
  url TEXT,
  description TEXT,
  difficulty TEXT,
  est_hours INT,
  format TEXT,                 -- video | reading | project | quiz
  last_verified DATE
);

CREATE TABLE resource_skills (
  resource_id TEXT REFERENCES resources(id),
  skill_id TEXT REFERENCES skills(id),
  PRIMARY KEY (resource_id, skill_id)
);

CREATE TABLE learning_paths (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  path_version INT,
  milestones JSONB,            -- [{milestone_id, title, resources, status, explanation}]
  change_summary TEXT,         -- what changed vs previous version and why (for the dashboard)
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE assessment_results (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  resource_id TEXT REFERENCES resources(id),
  status TEXT,                 -- not_started | in_progress | done
  quiz_score FLOAT,
  time_spent_min INT,
  est_time_min INT,
  completed_at TIMESTAMP
);

CREATE TABLE feedback (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  resource_id TEXT REFERENCES resources(id),
  raw_text TEXT,
  extracted JSONB,             -- {emotion, pace_signal, difficulty_signal, confidence}
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE recommendations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  resource_id TEXT REFERENCES resources(id),
  score FLOAT,
  reason TEXT,
  generated_at TIMESTAMP DEFAULT now()
);
```

## Endpoints

### `POST /api/chat`
Request: `{ "user_id": "uuid", "message": "string" }`
Response: `{ "reply": "string", "extracted_fields": {...}, "asked_clarifying_question": bool }`

Flow: append to history → call AI service `extract_goal()` (early turns) or `chat_reply()` (mentor mode) → if the AI service wants to ask a clarifying question, check `questions_asked_session < 2` before allowing it through; otherwise instruct the AI service to fall back to a default assumption and say so in the reply.

### `POST /api/profile`
Body: partial/full profile fields + `user_id`. Merges into `digital_twin` JSON rather than overwriting it wholesale.

### `GET /api/profile/{user_id}`
Returns the full Digital Twin.

### `GET /api/recommend/{user_id}`
Calls AI service `recommend(profile)`. Response: `{ "recommendations": [{resource_id, score, reason_short}] }`.

### `POST /api/path/{user_id}`
Calls AI service `generate_path()`. Increments `path_version`, stores `change_summary` from the AI service's diff of what changed vs the previous version.

### `GET /api/path/{user_id}`
Latest `learning_paths` row, with live `status` per milestone computed from `assessment_results`.

### `POST /api/progress/{user_id}`
Body: `{ "resource_id", "status", "quiz_score"?, "time_spent_min"? }`. Writes `assessment_results`, calls AI service `analyze_evidence()`, and if it returns an updated Digital Twin state, triggers `POST /api/path/{user_id}` internally to replan.

### `POST /api/feedback/{user_id}`
Body: `{ "resource_id", "text" }`. Calls AI service `analyze_feedback()`. If confidence on an important field is low, the response includes a `followup_question` (subject to the 2-question cap) instead of silently guessing.

### `GET /api/explain/{user_id}/{resource_id}`
Calls AI service `explain()`. Response: `{ "explanation": "string" }`, grounded in the actual profile fields that drove the recommendation.

### `GET /api/dashboard/{user_id}`
Aggregates skill growth (mastery vs completion, explicitly shown as two different numbers), milestone timeline, next 3 actions, and the latest `change_summary` so the UI can say "here's what changed and why."

## Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

## Integration notes

- Keep the AI service behind one interface module (`ai_service.py`) — see `03_AI.md` for the exact function signatures.
- Enforce the clarifying-question cap here, not in the AI service — it's a product/UX rule, keep it visible in the code that owns the session.
- Log every AI-service call's latency; useful for debugging and for the performance section of the solution doc.
