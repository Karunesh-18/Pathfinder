# Contributing to AI Learning Path Generator

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Node.js 18+
- A [Supabase](https://supabase.com) project (free tier works)
- An [OpenAI API key](https://platform.openai.com/api-keys)
- Optional: [OpenRouter](https://openrouter.ai/) key for primary model routing
- Optional: [Replicate](https://replicate.com/) token for mental-model image generation

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-learning-path-generator.git
cd ai-learning-path-generator

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Link Supabase project
npx supabase link --project-ref YOUR_PROJECT_REF

# Push database schema
npx supabase db push

# Deploy edge functions
npx supabase functions deploy

# Set the edge function secrets
npx supabase secrets set OPENAI_API_KEY=sk-your-openai-key
npx supabase secrets set OPENROUTER_API_KEY=sk-or-your-openrouter-key   # optional
npx supabase secrets set REPLICATE_API_TOKEN=r8_your-replicate-token    # optional

# Start dev server
npm run dev
```

The dev server runs at [http://localhost:3333](http://localhost:3333) (see `vite.config.ts`).

## Project Structure

```
src/
  components/      React components (landing, auth, learning, UI primitives)
  contexts/        React contexts (personalization discovery)
  hooks/           Custom React hooks grouped by domain
  integrations/    Supabase client + generated types
  pages/           Top-level routes
  store/           Zustand stores
  lib/             Utilities
  utils/           Helper functions
supabase/
  migrations/      SQL migrations
  functions/       21 Deno edge functions for AI generation
AGENTS.md          Agent architecture definitions
CLAUDE.md          AI-tool-friendly project guide
```

See `CLAUDE.md` and `AGENTS.md` for detailed architecture documentation.

## Making Changes

### Before You Start

1. Check existing [issues](https://github.com/Enterprise-DNA-OS/ai-learning-path-generator/issues) for the feature/bug
2. Open an issue to discuss significant changes before implementing
3. Read `CLAUDE.md` for coding conventions and patterns

### Coding Standards

- **TypeScript strict mode** -- no `any` types where avoidable
- **Tailwind CSS only** -- no inline styles, no CSS modules
- **Lucide React** -- the only icon library
- **`@/` imports** -- always use the path alias, never relative `../../../`
- **Mobile-first** -- base styles are for mobile, add `sm:`, `md:`, `lg:` for larger screens

### Key Patterns to Follow

**Supabase client** -- import the singleton from `@/integrations/supabase/client`:

```typescript
import { supabase } from "@/integrations/supabase/client";
```

**Edge function invocation** -- always use `supabase.functions.invoke`:

```typescript
const { data, error } = await supabase.functions.invoke("generate-learning-content", {
  body: { pathId, stepIndex, topic },
});
```

**Protected routes** -- gate user-specific pages inside their own components by reading from `useAuth()` and navigating away if there's no user. The top-level `App.tsx` keeps routing flat.

**Auth state** -- use `useAuth()` from `@/hooks/auth` for user/session/loading state. The provider caches the session in `localStorage` for instant paint.

**UI components** -- use the shadcn/ui primitives in `src/components/ui/`. If a primitive doesn't exist, add one using the shadcn CLI.

**Forms** -- use React Hook Form + Zod for validation.

### Adding a New Edge Function

1. Create a new folder under `supabase/functions/<your-function>/`
2. Add `index.ts` following the pattern of existing functions (e.g. `generate-learning-content/index.ts`)
3. If the function needs text generation, use the shared `createAIClient()` from `../_shared/ai-provider/index.ts`
4. If the function needs user context, use `getAuthContext(req)` from `../_shared/auth.ts`
5. Deploy with `npx supabase functions deploy <your-function>`
6. Invoke from the frontend via `supabase.functions.invoke("<your-function>", { body: {...} })`

### Adding a New Page / Route

1. Create the page file under `src/pages/`
2. Register the route in `src/App.tsx` inside the `<Routes>` block
3. Use `useAuth()` to gate user-only content
4. If the page needs new UI primitives, coordinate with the `ui-primitives` agent

### Verification

Before submitting a PR, run:

```bash
# Type check
npx tsc --noEmit

# Build
npm run build
```

Both must pass with zero errors.

## Pull Request Process

1. **Fork** the repo and create a feature branch
2. **Make your changes** following the coding standards above
3. **Verify** with `npx tsc --noEmit && npm run build`
4. **Write a clear PR description** explaining what and why
5. **Submit** -- maintainers will review within a few days

### PR Title Convention

- `Add: podcast-mode playback controls`
- `Fix: deep-dive crash on empty related topics`
- `Improve: loading states on generate buttons`

### What Makes a Good PR

- Focused on one thing (don't mix features with refactors)
- Includes context on why, not just what
- Doesn't break existing features
- Follows the existing code patterns
- Works on mobile

## Reporting Bugs

Open an issue with:

1. What you expected to happen
2. What actually happened
3. Steps to reproduce
4. Browser/device info
5. Screenshots if applicable

## Feature Requests

Open an issue describing:

1. The problem you're trying to solve
2. Your proposed solution
3. Alternatives you've considered

## AI-Assisted Development

AI-assisted development is welcome and encouraged. Many contributors use tools like:

- **Claude Code** -- the project includes agent definitions in `AGENTS.md` for specialized development
- **Cursor** / **Copilot** -- great for working within established patterns
- Any other AI coding tool

When submitting AI-assisted PRs, please review the generated code for correctness and ensure it follows the project's conventions.

## Code of Conduct

Be respectful. We're all here to build something great. Harassment, discrimination, and toxic behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
