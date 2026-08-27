# Frontend Doc — Adaptive Learning Agent

Read `00_MASTER.md` first. This is the frontend dev's detailed spec.

## Responsibilities

Seven screens, all calling the backend API only (never the AI service directly).

## Screens

1. **AI Onboarding** — conversational goal capture. Calls `POST /api/chat` per turn. If a clarifying question comes back (`asked_clarifying_question: true`), render it as part of the chat, not a separate modal — it should feel like conversation, not a form.
2. **Home Dashboard** — goal, skill-overlap-with-target-role %, current focus, next action, upcoming milestone. Calls `GET /api/dashboard/{user_id}` once on load.
3. **Learning Roadmap** — interactive timeline/DAG of milestones (completed/current/future). Calls `GET /api/path/{user_id}`. Shows the latest `change_summary` as a small banner when the path was just regenerated ("Path updated: you're ahead of pace, so we moved SQL earlier"). Drag-to-reorder posts back to `POST /api/path/{user_id}` and should surface the AI's trade-off explanation for the manual reorder if you build that stretch feature.
4. **Resource Discovery** — resource cards (title, provider, difficulty, est. time, skill match %) with a "Why this?" button calling `GET /api/explain/{user_id}/{resource_id}` on demand — don't prefetch all explanations.
5. **Learning Session** — external resource link + a "mark progress" action (`POST /api/progress/{user_id}`) + an inline feedback box (`POST /api/feedback/{user_id}`) after marking complete.
6. **Progress & Skill Dashboard** — skill growth chart. **Show mastery and completion as two separate bars/numbers per skill** — this is one of the standout ideas from the concept doc, don't collapse it into one "progress %."
7. **AI Mentor** — persistent chat for explanations, comparisons, and "why not X" questions. Same `POST /api/chat` endpoint, different context/mode.

## Component list

- `ChatWindow`, `ChatBubble`, `ClarifyingQuestionBubble`
- `DashboardSummaryCard`, `SkillOverlapBadge`
- `RoadmapTimeline`, `MilestoneCard`, `ChangeSummaryBanner`
- `ResourceCard`, `ExplanationPopover`
- `FeedbackBox`
- `SkillMasteryChart` (dual bar: completion vs mastery, per skill)
- `AppShell`

## State management

One `LearnerContext` holding `profile`, `path`, `dashboard`, refetched after any mutating call. No Redux needed at this scale.

## API calls by screen

| Screen | Calls |
|---|---|
| Onboarding | `POST /api/chat` |
| Home Dashboard | `GET /api/dashboard/{user_id}` |
| Roadmap | `GET/POST /api/path/{user_id}`, `GET /api/explain/{user_id}/{resource_id}` |
| Resource Discovery | `GET /api/recommend/{user_id}`, `GET /api/explain/{user_id}/{resource_id}` |
| Learning Session | `POST /api/progress/{user_id}`, `POST /api/feedback/{user_id}` |
| Progress Dashboard | `GET /api/dashboard/{user_id}` |
| AI Mentor | `POST /api/chat` |

## UX priorities

- The roadmap and skill-mastery chart are what the demo video lingers on — prioritize polish there.
- Never present an estimated state (pace/emotion/difficulty) as fact in the UI — label it ("estimated pace: moderate") since the backend itself treats these as confidence-weighted estimates, not ground truth.
- Loading states for anything that hits the AI service (chat reply, explanations, path regeneration) — skeletons, not blank screens.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL
npm run dev
```
