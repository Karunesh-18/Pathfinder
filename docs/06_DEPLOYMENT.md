# Deployment Doc — Whole Team

One reliable deployment path beats three fragile ones (per the MVP scope in `00_MASTER.md`). Pick this stack unless someone has a strong reason otherwise.

## Recommended setup

- **Frontend** → Vercel (connects straight to a GitHub repo, auto-deploys on push to `main`)
- **Backend + AI service** → Render or Railway, either as two services or one if you kept the AI service as an in-process module (recommended — see `03_AI.md`)
- **Database** → managed Postgres on the same platform as the backend (Render/Railway both offer this) — avoid a separate DB host to cut down on env-var juggling

## Environment variables checklist

| Service | Vars |
|---|---|
| Backend | `DATABASE_URL`, `AI_SERVICE_URL` (if separate service), `CORS_ORIGINS` |
| AI service | `LLM_API_KEY`, `EMBEDDING_MODEL`, `VECTOR_STORE_PATH` |
| Frontend | `VITE_API_BASE_URL` |

Commit `.env.example` for each with placeholder values; never commit real `.env` files (see `04_CODING_STANDARDS.md` §4).

## Pre-demo checklist

- [ ] Deployed URL loads the onboarding chat without errors
- [ ] Full loop works end-to-end at least once on the deployed version, not just localhost (chat → profile → roadmap → resource → feedback → dashboard)
- [ ] Pre-seeded feedback text for the two adaptation demo beats (fast learner / struggling learner) is loaded into the deployed DB, not just your local one
- [ ] Fallback plan if the deployed LLM call is slow/down during judging: have a local/offline run ready as backup, and know the exact steps to run it (README should make this a copy-paste job, not a debugging session)

## README template (goes at repo root — required submission item)

```markdown
# Adaptive Learning Agent

## What this is
[1-2 sentence pitch]

## Live demo
[deployed URL]

## Local setup
### Backend
cd backend && ... (see 01_BACKEND.md)
### AI service
cd ai_service && ... (see 03_AI.md)
### Frontend
cd frontend && ... (see 02_FRONTEND.md)

## Architecture
[link to 00_MASTER.md or embed the diagram]

## Team
[names + roles]
```
