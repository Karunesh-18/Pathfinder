# Agent Coordination Protocol

This file defines the specialist agent architecture for AI Learning Path Generator. Each agent owns a specific domain of the codebase. When using AI tools like Claude Code, invoke the right agent for the task at hand.

## Agent Roster

| Agent | Domain | Key Files |
|---|---|---|
| `database-schema` | Supabase schema, RLS, migrations, generated types | `supabase/config.toml`, `supabase/migrations/`, `src/integrations/supabase/types.ts` |
| `auth-ui` | Auth pages, session context, auth forms | `src/pages/AuthPage.tsx`, `src/pages/SignIn.tsx`, `src/pages/SignUp.tsx`, `src/pages/SignUpSuccess.tsx`, `src/pages/ForgotPassword.tsx`, `src/components/auth/`, `src/hooks/auth/` |
| `ai-generation` | Supabase Edge Functions, AI provider wrapper, prompts | `supabase/functions/generate-*/`, `supabase/functions/chat-tutor/`, `supabase/functions/_shared/ai-provider/` |
| `media-generation` | Image + audio + realtime voice edge functions | `supabase/functions/generate-*-image/`, `supabase/functions/openai-tts/`, `supabase/functions/text-to-speech/`, `supabase/functions/realtime-speech/`, `supabase/functions/learning-modes-transform/` |
| `api-client` | Supabase client, generated types, invocation helpers | `src/integrations/supabase/`, `src/lib/` |
| `frontend-pages` | Top-level routes and page logic (except auth) | `src/pages/HomePage.tsx`, `src/pages/ProjectsPage.tsx`, `src/pages/Community.tsx`, `src/pages/PlanPage.tsx`, `src/pages/ContentPage.tsx`, `src/pages/AudioPage.tsx`, `src/pages/PodcastPage.tsx`, `src/pages/SettingsPage.tsx`, `src/pages/ProfilePage.tsx`, `src/pages/AdminGenerateTopics.tsx`, `src/pages/NotFound.tsx` |
| `learning-domain` | Learning path / step / content generation UI + hooks | `src/components/learning/`, `src/components/content/`, `src/components/journey/`, `src/components/plan/`, `src/hooks/content/`, `src/hooks/journey/`, `src/hooks/learning-steps/`, `src/hooks/projects/`, `src/store/learningCommandStore.ts` |
| `personalization` | Learning DNA, skill gaps, recommendations, insights | `src/components/personalization/`, `src/components/home/personalization/`, `src/contexts/PersonalizationDiscoveryContext.tsx`, `src/hooks/personalization/`, `src/hooks/recommendations/`, `src/hooks/analytics/` |
| `media-ui` | Audio / podcast / presentation / realtime voice UI | `src/components/audio/`, `src/components/audio-page/`, `src/components/podcast/`, `src/components/presentation/`, `src/hooks/audio/`, `src/hooks/podcast/`, `src/hooks/realtime-speech/` |
| `landing-ui` | Landing page sections and marketing components | `src/components/home/`, `src/components/navigation/`, `src/components/common/VideoBackground.tsx` |
| `ui-primitives` | shadcn/ui primitives and design system | `src/components/ui/`, `tailwind.config.ts`, `src/index.css`, `src/App.css`, `components.json` |

## Ownership Boundaries

Each agent **owns** a set of files (exclusive write) and **reads** other files for context. When crossing boundaries, coordinate through the shared contract points below.

### Shared Contract Points

Changes to these files require coordination across multiple agents:

- **`src/integrations/supabase/types.ts`** -- generated types, regenerated from the database schema. `database-schema` owns, all other agents read.
- **`src/integrations/supabase/client.ts`** -- the singleton Supabase client. Reads env vars, no mutation from feature agents.
- **`package.json`** -- dependencies shared across everything. Requires justification in PR.
- **`src/App.tsx`** -- routing and top-level providers. Any new page must be registered here.
- **`supabase/config.toml`** -- edge function registration and Supabase project config.
- **`supabase/functions/_shared/`** -- shared Deno utilities (CORS, auth, AI provider, config). Shared by all edge function agents.

## Feature Implementation Checklist

When adding a new feature, work through these domains in order:

1. **`database-schema`** -- If the feature needs a new table or column, add a migration first and regenerate types.
2. **`ai-generation`** / **`media-generation`** -- If the feature calls an AI model, write the edge function and deploy it.
3. **`api-client`** -- Add any shared frontend helper functions for the new endpoint.
4. **`learning-domain`** / **`personalization`** / **`media-ui`** -- Add the UI components and hooks that invoke the endpoint.
5. **`frontend-pages`** -- Register or update the page that hosts the feature.
6. **`landing-ui`** / **`ui-primitives`** -- Update shared components if the feature needs new UI primitives or landing-page sections.
7. **`auth-ui`** -- Only touch auth if the feature changes authentication behavior.

## Coordination Patterns

### Adding a New Generation Endpoint

1. `ai-generation` creates `supabase/functions/generate-<feature>/index.ts`
2. `ai-generation` uses the shared AI provider: `import { createAIClient } from "../_shared/ai-provider/index.ts"`
3. `ai-generation` registers the function in `supabase/config.toml` if it needs non-default settings
4. `ai-generation` deploys with `npx supabase functions deploy generate-<feature>`
5. `learning-domain` or `personalization` calls `supabase.functions.invoke("generate-<feature>", { body })` from the UI

### Adding a New Protected Page

1. `frontend-pages` creates the page file under `src/pages/`
2. `frontend-pages` adds a route in `src/App.tsx`
3. `frontend-pages` uses `useAuth()` to gate user-only content and redirect to `/sign-in` when there is no session
4. If the page needs new UI primitives, coordinate with `ui-primitives`

### Modifying the Landing Page

1. `landing-ui` updates the section component in `src/components/home/`
2. `landing-ui` updates `src/pages/HomePage.tsx` if a new section is added or removed
3. Images/videos live in `public/images/` and `public/videos/` -- keep generic filenames (no personal names)

## Communication Pattern

Agents don't talk directly. They communicate through:

- **Database schema** -- the shared contract in `src/integrations/supabase/types.ts`
- **Routes** -- the shared contract in `src/App.tsx`
- **Component APIs** -- TypeScript types at component boundaries
- **Edge function contracts** -- typed request/response shapes in `supabase/functions/<name>/index.ts`
- **This file** -- when changing ownership or adding new agents

## New Agent Definition Process

If you need a new agent domain, open an issue describing:

1. What files would the agent own?
2. What files would it read?
3. What contract points does it touch?
4. How does it coordinate with existing agents?
