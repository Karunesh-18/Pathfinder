# Coding Standards & Workflow — Whole Team

Applies to backend, frontend, and AI code alike. Keep this short enough that everyone actually follows it.

## 1. Repo & branching

- `main` is always demo-able — never commit straight to it.
- Branch naming: `feature/<area>-<short-desc>` e.g. `feature/ai-path-generator`, `feature/frontend-roadmap-view`, `fix/backend-progress-endpoint`.
- One PR per feature, even solo — keeps a real commit history for the "GitHub repo" submission requirement.
- Commit messages: `<area>: <what changed>` e.g. `ai: add decide_replan_action per replanning table`. Small, frequent commits beat one giant "final version" commit.

## 2. Clean code guidelines

- **Functions do one thing.** If you're writing "and" in a function's docstring, split it.
- **Names say what, not how.** `get_prioritized_gaps`, not `process_data`.
- **No magic numbers without a name.** The `0.5` confidence threshold, the `2` question cap, the `0.6/0.4` update weights — all named constants at the top of the file, not inline.
- **Keep the AI service's core functions pure** (data in, result out — see `03_AI.md` §Internal interface). Side effects (DB writes, logging) belong in the backend layer that calls them, not inside the AI logic itself. This makes the AI functions testable without spinning up Postgres.
- **Explicit over clever.** The skill-gap engine and replanning table are supposed to be simple, inspectable code (see `03_AI.md` §2 and §8) — resist the urge to fold them into one LLM prompt just because it's shorter to write. Judges (and your future selves debugging at 2am) need to see the logic.
- **Every estimated/uncertain value carries its confidence next to it in code**, not just in the docs — if you find yourself passing `pace: "moderate"` without a confidence value alongside it, something upstream dropped it.

## 3. Testing (lightweight, not academic)

Given the timeline, don't aim for full coverage — aim for tests on the parts that are your actual "AI/ML implementation" claims, since those are gradeable and demoable:

- `decide_replan_action()` — unit test against every row of the replanning table in `03_AI.md` §8
- Path generator — assert topological validity (no milestone needs a skill not yet unlocked)
- Skill gap engine — a couple of fixed persona inputs with known expected gaps
- API endpoints — smoke test each one returns 200 with a valid payload; don't chase edge cases you won't hit in the demo

## 4. Environment & secrets

- Never commit `.env` — commit `.env.example` with placeholder keys only.
- LLM API keys, DB URL, and any embeddings API key live in `.env` per service (`backend/.env`, `ai_service/.env`, `frontend/.env`).
- Shared fixture data (`skill_graph.json`, `resource_catalog.json`) lives once in `/data`, referenced by path — don't let AI and backend each keep their own copy that drifts.

## 5. Code review checklist (quick, before merging)

- [ ] Does this match the API contract in `00_MASTER.md` §7 exactly (field names, types)?
- [ ] Any new estimated field — does it have a confidence value next to it?
- [ ] Any new magic number — is it named?
- [ ] Does it still run locally per the setup instructions in the relevant doc?

## 6. Documentation habit

If you change an endpoint's request/response shape or a data model field, update `00_MASTER.md` and the relevant role doc in the same PR — not after. Docs drifting from code is the most common reason integration breaks the day before a demo.
