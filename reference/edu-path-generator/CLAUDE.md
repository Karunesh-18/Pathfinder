# CLAUDE.md -- Project Guide for AI Tools

This file is the source of truth for AI coding tools (Claude Code, Cursor, GitHub Copilot) working on AI Learning Path Generator. It captures project conventions, architecture decisions, and common patterns so AI tools can produce code that fits.

## Project Overview

**AI Learning Path Generator** is a React + Supabase web app that turns any topic into a personalized, project-based learning path. Users describe what they want to learn, pick pace and depth, and the app generates a full multi-step path with on-demand lesson content, mental-model images, audio narration, and an AI tutor. Generation is powered by OpenAI / OpenRouter (text) and Replicate (images), all routed through Supabase Edge Functions.

### Tech Stack

- **Frontend**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS 3 + shadcn/ui (Radix primitives) + `tailwindcss-animate`
- **Animation**: Framer Motion
- **State**: Zustand + TanStack Query
- **Routing**: React Router DOM v6
- **Forms**: React Hook Form + Zod
- **Markdown**: `react-markdown` + `react-syntax-highlighter` + `remark-gfm` + `rehype-raw`
- **Backend**: Supabase (PostgreSQL, Auth, Edge Functions)
- **Text AI**: OpenRouter primary + OpenAI fallback via `_shared/ai-provider`
- **Image AI**: Replicate (mental model and presentation images)
- **Voice AI**: OpenAI TTS + Realtime Speech
- **Deployment**: Static hosting (Netlify / Vercel) + Supabase backend

## Agent Team Quick Reference

See [AGENTS.md](AGENTS.md) for the full agent specification. TL;DR:

| Task type | Agent |
|---|---|
| Database schema changes | `database-schema` |
| New login / signup flow | `auth-ui` |
| New text generation endpoint | `ai-generation` |
| New image / audio / voice endpoint | `media-generation` |
| Supabase client helpers | `api-client` |
| New top-level page / route | `frontend-pages` |
| Learning path / step / content UI | `learning-domain` |
| Personalization / recommendations | `personalization` |
| Audio / podcast / presentation UI | `media-ui` |
| Landing page section | `landing-ui` |
| shadcn/ui primitives | `ui-primitives` |

## When Tasks Span Multiple Agents

Order of operations: **Database -> Edge Function -> API client -> Domain hooks -> Page -> Landing UI**.

Example: adding a new "Generate quiz" feature.

1. `database-schema` adds a `quizzes` table tied to `learning_steps`
2. `ai-generation` creates `supabase/functions/generate-quiz/index.ts`
3. `api-client` (optional) adds a typed helper around `supabase.functions.invoke("generate-quiz", ...)`
4. `learning-domain` adds a `useQuiz` hook and a `<QuizPanel>` component in `src/components/content/`
5. `frontend-pages` wires the panel into `src/pages/ContentPage.tsx`

## Shared Conventions

### Import Aliases

Always use `@/` which maps to `src/`:

```typescript
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/auth";
```

Never use relative `../../../` imports.

### Supabase Client Usage

There is exactly **one** Supabase client for the frontend, exported from `@/integrations/supabase/client`:

```typescript
import { supabase } from "@/integrations/supabase/client";

// Read
const { data, error } = await supabase
  .from("learning_paths")
  .select("*")
  .eq("user_id", userId);

// Invoke edge function
const { data, error } = await supabase.functions.invoke("generate-learning-content", {
  body: { pathId, stepIndex, topic },
});

// Auth
const { data: { user } } = await supabase.auth.getUser();
```

The client uses the anon key from `import.meta.env.VITE_SUPABASE_ANON_KEY`. Row Level Security enforces per-user data isolation.

### Auth Pattern

Every page that needs the user reads it from `useAuth`:

```typescript
import { useAuth } from "@/hooks/auth";

function MyPage() {
  const { user, loading, session } = useAuth();
  if (loading) return <Loader />;
  if (!user) {
    // Either render a marketing view or navigate to /sign-in
    return <SignedOutView />;
  }
  // ...
}
```

The `AuthProvider` caches the session in `localStorage` (`learnflow_auth_session`) so the app hydrates instantly on the second visit. Cached sessions are verified in the background.

### Edge Function Pattern

Edge functions live in `supabase/functions/<name>/index.ts` and follow this template:

```typescript
// @ts-nocheck
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createAIClient } from "../_shared/ai-provider/index.ts";
import { corsHeaders } from "../_shared/utils.ts";
import { getAuthContext } from "../_shared/auth.ts";

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const auth = await getAuthContext(req);
    if ("errorResponse" in auth) return auth.errorResponse;

    const body = await req.json();

    const aiClient = createAIClient();
    const response = await aiClient.chat({
      functionType: "my-function",
      messages: [
        { role: "system", content: "You are ..." },
        { role: "user", content: JSON.stringify(body) },
      ],
      responseFormat: { type: "json_object" },
    });

    return new Response(JSON.stringify({ result: response.content }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error(`Error in ${req.url}:`, error);
    return new Response(
      JSON.stringify({ error: (error as Error).message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
```

- `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, and `REPLICATE_API_TOKEN` are Supabase secrets, never in `.env`
- Text generation goes through `createAIClient()` so model routing and fallbacks are centralized
- Use `getAuthContext(req)` when the endpoint needs a logged-in user
- Register a function in `supabase/config.toml` only if it needs non-default settings (e.g. disabling JWT verification)

### TypeScript Rules

- Use `strict` mode (enabled in `tsconfig.json`)
- Avoid `any` -- use `unknown` and narrow when you don't know the type
- Type component props explicitly
- Use the auto-generated types from `@/integrations/supabase/types` when reading from Supabase:
  ```typescript
  import { Database } from "@/integrations/supabase/types";
  type LearningPath = Database["public"]["Tables"]["learning_paths"]["Row"];
  ```
- Edge functions often include `// @ts-nocheck` because they target Deno. Frontend code must not use this.

### File Naming

- React components: `PascalCase.tsx` (e.g. `LearningStep.tsx`)
- Hooks: `useCamelCase.ts` or `useCamelCase.tsx` (e.g. `useLearningPath.ts`)
- Page components: `PascalCase.tsx` under `src/pages/`
- Utility modules: `camelCase.ts` under `src/lib/` or `src/utils/`
- Edge functions: `kebab-case/index.ts` under `supabase/functions/`

### Styling Conventions

- **Tailwind classes only**. No inline styles. No CSS-in-JS. No CSS modules.
- **Responsive**: mobile-first. Base classes are for mobile, add `sm:`, `md:`, `lg:` for larger screens.
- **Dark mode**: ready via `next-themes`. Use Tailwind's `dark:` prefix when relevant.
- **Icons**: Lucide React only. Import individual icons: `import { Loader2 } from "lucide-react";`
- **Brand gradient**: `bg-gradient-to-r from-[#6654f5] via-[#ca5a8b] to-[#f2b347]` -- the Enterprise DNA signature. Use for CTAs and headline accents. (Note: `ca5a8b` is the in-app stop; the static brand reference is `b84d8f`.)

### Form Pattern

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  topic: z.string().min(1, "Required"),
  level: z.enum(["beginner", "intermediate", "advanced"]),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const form = useForm<FormData>({ resolver: zodResolver(schema) });
  const onSubmit = (data: FormData) => { /* ... */ };
  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>;
}
```

## Environment Variables

Two separate environments:

### Frontend (`.env` / `.env.local`)

Only `VITE_`-prefixed variables are exposed to the browser:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Never put API keys that should be secret (OpenAI, OpenRouter, Replicate, service role) in `.env`. They'd leak to the client.

### Supabase Secrets (edge functions)

Set via `npx supabase secrets set KEY=value`:

```bash
npx supabase secrets set OPENAI_API_KEY=sk-...
npx supabase secrets set OPENROUTER_API_KEY=sk-or-...
npx supabase secrets set REPLICATE_API_TOKEN=r8_...
```

These are only accessible inside edge functions via `Deno.env.get("KEY")`.

## Project Structure Quick Reference

```
ai-learning-path-generator/
|-- AGENTS.md               # Agent specification
|-- CLAUDE.md               # This file
|-- CONTRIBUTING.md         # Contributor guide
|-- SECURITY.md             # Security policy
|-- LICENSE                 # MIT
|-- README.md               # Public project README
|-- index.html              # Vite entry point
|-- package.json
|-- tsconfig.json
|-- vite.config.ts
|-- tailwind.config.ts
|-- .env.example
|-- public/
|   |-- images/             # Landing page imagery (generic filenames only)
|   |-- videos/             # Landing page videos (generic filenames only)
|   |-- logo.svg            # Project logo
|-- src/
|   |-- App.tsx             # Routes + providers
|   |-- main.tsx            # Entry
|   |-- index.css           # Global Tailwind styles
|   |-- App.css             # App-scoped styles
|   |-- components/
|   |   |-- ai/             # AI tutor chat widgets
|   |   |-- audio/          # Audio playback + TTS
|   |   |-- audio-page/     # Full-path audio mode
|   |   |-- auth/           # AuthForm + ProtectedRoute
|   |   |-- common/         # VideoBackground, shared primitives
|   |   |-- community/      # Community feed UI
|   |   |-- content/        # Lesson renderer + deep-dive UI
|   |   |-- home/           # Landing page sections
|   |   |-- journey/        # Learning Journey Wizard
|   |   |-- learning/       # LearningStep view
|   |   |-- learning-command-center/
|   |   |-- navigation/     # MainNav, UserNav
|   |   |-- onboarding/     # Onboarding flows
|   |   |-- personalization/
|   |   |-- plan/           # Plan view
|   |   |-- podcast/        # Podcast mode
|   |   |-- presentation/   # Presentation mode
|   |   |-- profile/        # Profile editor
|   |   |-- projects/       # Project cards + list
|   |   |-- theme/          # Theme provider
|   |   |-- ui/             # shadcn/ui primitives
|   |-- contexts/
|   |   |-- PersonalizationDiscoveryContext.tsx
|   |-- hooks/              # Grouped by domain (auth, content, projects, ...)
|   |-- integrations/
|   |   |-- supabase/
|   |       |-- client.ts   # Singleton Supabase client
|   |       |-- types.ts    # Generated DB types
|   |-- lib/                # Helper modules
|   |-- pages/              # Route components
|   |-- store/              # Zustand stores
|   |-- styles/             # Shared CSS
|   |-- utils/              # Utility functions
|-- supabase/
    |-- config.toml         # Function + auth config
    |-- migrations/         # SQL migrations
    |-- functions/
        |-- _shared/        # CORS, auth, AI provider, utils
        |-- chat-tutor/
        |-- generate-*/     # 15+ generation functions
        |-- get-*/          # Personalization / recommendation functions
        |-- openai-tts/
        |-- text-to-speech/
        |-- realtime-speech/
        |-- learning-modes-transform/
```

## Common Tasks

### Running the App

```bash
npm install
cp .env.example .env         # Fill in Supabase credentials
npm run dev                  # Dev server at http://localhost:3333
npm run build                # Production build
npx tsc --noEmit             # Type check
```

### Adding a shadcn/ui Component

```bash
npx shadcn-ui@latest add <component-name>
```

Components land under `src/components/ui/` and are immediately importable via `@/components/ui/<component>`.

### Deploying Edge Functions

```bash
# Deploy all
npx supabase functions deploy

# Deploy one
npx supabase functions deploy generate-learning-content
```

### Regenerating Supabase Types

```bash
npx supabase gen types typescript --project-id your-project-id > src/integrations/supabase/types.ts
```

## Things Not To Do

- Do not put the OpenAI / OpenRouter / Replicate keys in `.env` (they would leak to the browser). Put them in Supabase secrets.
- Do not call OpenAI, OpenRouter, or Replicate directly from the frontend. Always go through an edge function.
- Do not add relative `../../../` imports. Use `@/` aliases.
- Do not use `any` without a comment explaining why (except edge functions that target Deno with `@ts-nocheck`).
- Do not add inline styles. Use Tailwind classes.
- Do not introduce new UI libraries (Ant Design, Chakra, MUI, etc.). Stick with shadcn/ui + Radix.
- Do not commit `.env`, generated `dist/`, `.claude/`, `.cursor/`, or `.mcp.json`. `.gitignore` should already block these.
- Do not add personal names to asset filenames. Use generic descriptive names.
- Do not re-introduce tracking widgets, SSO redirects to external services, or hardcoded commercial URLs.

## Branding

This project is an open-source release by **Enterprise DNA**. Keep the branding in:

- README header and footer
- `MainNav.tsx` ("AI Learning Path Generator" / "by Enterprise DNA" in the mobile menu header)
- The signature gradient `#6654f5 -> #b84d8f -> #f2b347`
- `package.json` author field
- `LICENSE` copyright line
- `SECURITY.md` contact address

The app is MIT-licensed. Forks and derivatives are welcome and don't need to keep the branding.
