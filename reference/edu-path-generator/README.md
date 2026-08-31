<p align="center">
  <img src="public/logo.svg" alt="AI Learning Path Generator" width="80" height="80" />
</p>

<h1 align="center">AI Learning Path Generator</h1>

<p align="center">
  <strong>The open-source AI learning platform that turns any topic into a project-based curriculum.</strong>
</p>

<p align="center">
  Created by <a href="https://www.enterprisedna.co"><strong>Enterprise DNA</strong></a> -- a leading data and AI education company.
</p>

<p align="center">
  <a href="#what-is-ai-learning-path-generator">What is it?</a> &bull;
  <a href="#built-with-ai">Built with AI</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#tech-stack">Tech Stack</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#self-hosting">Self-Hosting</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#developing-with-ai-tools">Dev with AI</a> &bull;
  <a href="#contributing">Contributing</a> &bull;
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18-61dafb?style=flat-square" alt="React 18" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178c6?style=flat-square" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Vite-5-646cff?style=flat-square" alt="Vite" />
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e?style=flat-square" alt="Supabase" />
  <img src="https://img.shields.io/badge/Tailwind-3-38bdf8?style=flat-square" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License" />
</p>

---

## What is AI Learning Path Generator?

AI Learning Path Generator is an open-source web app that turns a topic -- anything from "PyTorch fundamentals" to "Renaissance painting" -- into a full, personalized, project-based learning path. It's the fastest way to go from "I want to learn X" to "here are the 10 lessons, the deep-dives, the mental models, the audio walkthrough, and the practice projects."

Describe what you want to learn, pick your pace and depth, and the app generates:

- A complete learning path with ordered steps and milestones
- Lesson content for each step, generated on demand
- Visual **mental model** diagrams that capture the core concepts
- **Deep-dive** topics for anything you want to explore further
- An **AI tutor** chat that answers questions in the context of the current step
- **Audio narration** of each lesson (text-to-speech) plus a realtime voice mode
- **Presentation** and **podcast** modes for the same content, for different learning styles
- A **community** feed of auto-generated daily learning paths you can browse
- Personalized recommendations that adapt as you complete steps

All content is saved to your own Supabase project. You own every generated lesson, image, and audio file.

### Why another learning platform?

Most "AI learning" products give you a summary and walk away. AI Learning Path Generator is different:

- **Project-based by default** -- Every path is structured around things you actually build or analyse, not passive reading
- **Multi-modal content** -- Text lessons, visual mental models, audio narration, and a realtime voice tutor all generated from the same plan
- **Adaptive** -- Paths adapt to your pace, preferred format (text/audio/visual), and the prompts you've been asking
- **21 specialized AI edge functions** -- Each content type has its own Supabase Edge Function with a tuned prompt
- **Self-hostable** -- Bring your own OpenAI / OpenRouter / Replicate keys, run it on your own Supabase project, own every artifact
- **Open source** -- MIT licensed, built end-to-end with AI coding tools, easy to fork and adapt

---

## Built with AI

> **This entire application was built using AI-assisted development tools.** Enterprise DNA believes in the future of AI-augmented software development, and this project is a reference for what's possible. Every layer -- from the Supabase edge functions to the React UI -- was written collaboratively with AI coding agents.

### AI Development Tools Used

| Tool | Role |
|------|------|
| **[Claude Code](https://claude.ai/claude-code)** by Anthropic | Primary development tool. Claude Code acted as the AI coding agent, building features end-to-end across the full stack -- from edge functions to React components to page layouts. |
| **[Cursor](https://cursor.com)** | AI-powered IDE used throughout development for code navigation, inline edits, and rapid iteration. |
| **[GitHub Copilot](https://github.com/features/copilot)** | AI pair programming assistant for code completion and pattern matching. |

Enterprise DNA is committed to demonstrating that AI tools are not just productivity boosters -- they are a new way to build software. This project serves as a reference implementation for AI-assisted full-stack development.

---

## Features

### Learning Path Generation
- Free-form topic input -- describe what you want to learn
- Guided **Learning Journey Wizard** that walks you through topic, skill level, depth, and format
- Full learning plan generated with ordered steps, durations, and prerequisites
- Paths saved per user to your Projects page
- Public **Community** feed of auto-generated paths refreshed hourly

### On-Demand Content Generation
- Lesson content generated the moment you open a step (no pre-generation cost)
- **Deep-dive** topics: click any concept to expand it into a standalone mini-lesson
- **Related topics** suggestions at the bottom of each step
- Mental model **image generation** (via Replicate) for visual learners
- Presentation-mode slides with hero images per step

### AI Tutor
- Real-time chat-tutor edge function that answers questions in the context of the current step
- Streams responses into the lesson UI
- Prompt insights track what you're struggling with and feed the personalization engine

### Audio & Voice Modes
- **Text-to-speech** narration of every step (OpenAI TTS)
- **Realtime speech** mode for conversational learning via WebRTC
- **Audio page** that lets you listen to a full path end-to-end
- **Podcast** mode that turns a path into episodic audio content

### Personalization
- Learning DNA profile built from your interactions
- Skill gap analysis
- Adaptive difficulty that tracks your completion and accuracy
- Predictive recommendations for "what to learn next"
- Prompt insights that surface patterns in what you ask

### Projects & Progress Tracking
- Projects page lists every path you've started
- Per-step completion tracking
- Journey dashboard with overall progress
- Pick up where you left off across devices

### Authentication
- Email + password via Supabase Auth
- Password reset flow with email confirmation
- Protected routes for personalized views
- Profile page with account information and preferences

### UI / UX
- Brand gradient design system (#6654f5 / #b84d8f / #f2b347)
- Responsive mobile-first layouts
- Dark mode ready via `next-themes`
- Rich form controls via shadcn/ui + Radix
- Toast notifications via Sonner
- Smooth transitions via Framer Motion

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Vite](https://vitejs.dev/) + [React 18](https://react.dev/) |
| Language | [TypeScript 5](https://www.typescriptlang.org/) |
| UI Library | [shadcn/ui](https://ui.shadcn.com/) + [Radix UI](https://www.radix-ui.com/) |
| Styling | [Tailwind CSS 3](https://tailwindcss.com/) + `tailwindcss-animate` |
| Animation | [Framer Motion](https://www.framer.com/motion/) |
| Icons | [Lucide React](https://lucide.dev/) |
| Charts | [Recharts](https://recharts.org/) |
| Database | [Supabase](https://supabase.com/) (PostgreSQL + Row Level Security) |
| Auth | Supabase Auth (email/password) |
| AI Runtime | Supabase Edge Functions (Deno) |
| Text AI | [OpenRouter](https://openrouter.ai/) primary, [OpenAI](https://platform.openai.com/) fallback |
| Image AI | [Replicate](https://replicate.com/) for mental model and presentation images |
| Voice AI | OpenAI TTS + Realtime Speech |
| State | [Zustand](https://github.com/pmndrs/zustand) + [TanStack Query](https://tanstack.com/query) |
| Forms | [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/) |
| Routing | [React Router DOM v6](https://reactrouter.com/) |
| Markdown | `react-markdown` + `react-syntax-highlighter` + `remark-gfm` + `rehype-raw` |
| Deployment | Static hosting (Netlify / Vercel / Cloudflare Pages) + Supabase backend |

---

## Quick Start

### Prerequisites
- **Node.js 18+** and npm (or bun)
- A **[Supabase](https://supabase.com/)** account (free tier works)
- An **[OpenAI API key](https://platform.openai.com/api-keys)** (pay-as-you-go) -- and optionally an [OpenRouter](https://openrouter.ai/) key for primary model routing
- A **[Replicate API token](https://replicate.com/)** for mental model image generation (optional but recommended)

### Step 1: Clone and Install

```bash
git clone https://github.com/Enterprise-DNA-OS/ai-learning-path-generator.git
cd ai-learning-path-generator
npm install
```

### Step 2: Create Your Supabase Project

1. Sign in at [supabase.com](https://supabase.com/) and click **New Project**
2. Wait for the project to provision (~2 minutes)
3. From **Settings -> API**, copy:
   - **Project URL** -> `VITE_SUPABASE_URL`
   - **anon / public key** -> `VITE_SUPABASE_ANON_KEY`

### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```bash
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Step 4: Link and Deploy Edge Functions

Install the Supabase CLI and link your project:

```bash
npm install -g supabase
npx supabase login
npx supabase link --project-ref your-project-ref
```

Deploy all 21 edge functions:

```bash
npx supabase functions deploy
```

### Step 5: Set Supabase Secrets

AI API keys live in Supabase secrets (not in `.env`). Set your keys:

```bash
npx supabase secrets set OPENAI_API_KEY=sk-your-openai-key
npx supabase secrets set OPENROUTER_API_KEY=sk-or-your-openrouter-key   # optional, enables primary model routing
npx supabase secrets set REPLICATE_API_TOKEN=r8_your-replicate-token    # enables image generation
```

### Step 6: Apply Database Migrations

```bash
npx supabase db push
```

This runs the migrations in `supabase/migrations/` against your linked project.

### Step 7: Run Locally

```bash
npm run dev
```

Open [http://localhost:3333](http://localhost:3333), sign up, and start your first learning path.

---

## Self-Hosting

AI Learning Path Generator can be deployed anywhere that hosts a static Vite build.

### Netlify

1. Push your fork to GitHub
2. Connect the repo to Netlify
3. Set **Build command**: `npm run build`
4. Set **Publish directory**: `dist`
5. Add environment variables under **Site settings -> Environment variables**:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

### Vercel

```bash
npm run build
vercel deploy --prod
```

Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in the Vercel project settings.

### Static hosting

`npm run build` produces a `dist/` folder you can host anywhere:
- Cloudflare Pages
- GitHub Pages
- S3 + CloudFront
- Any static host

### Production Deployment Checklist

1. **Update environment variables** in your hosting platform
2. **Supabase Auth settings** -- add your production domain to the allowed redirect URLs under Authentication -> URL Configuration
3. **Enable HTTPS** -- required for Supabase Auth
4. **Set Supabase secrets** -- `OPENAI_API_KEY`, optional `OPENROUTER_API_KEY`, and `REPLICATE_API_TOKEN` for image generation
5. **Enable pg_cron and pg_net** extensions in Supabase if you want hourly community topic generation
6. **Monitor edge function logs** in your Supabase dashboard

---

## Architecture

### Project Structure

```
src/
  App.tsx                    Root routes + providers
  main.tsx                   Entry point
  components/
    ai/                      AI tutor widgets
    audio/                   Audio playback + TTS
    audio-page/              Full-path audio mode
    auth/                    AuthForm + ProtectedRoute
    common/                  VideoBackground, loaders, shared primitives
    community/               Community feed UI
    content/                 Lesson content renderer + deep-dive UI
    home/                    Landing page sections
    journey/                 Learning Journey Wizard
    learning/                LearningStep view
    learning-command-center/ Command palette + widgets
    navigation/              MainNav, UserNav
    onboarding/              Onboarding flows
    personalization/         Learning DNA, skill gaps
    plan/                    Plan view
    podcast/                 Podcast mode
    presentation/            Presentation mode
    profile/                 Profile editor
    projects/                Project cards + list
    theme/                   Theme provider
    ui/                      shadcn/ui primitives
  contexts/
    PersonalizationDiscoveryContext.tsx
  hooks/
    analytics/                Learning analytics
    audio/                    TTS + playback hooks
    auth/                     useAuth + AuthProvider
    capability/               Feature capability flags
    community/                Community feed hooks
    content/                  Content mode + generation hooks
    journey/                  Learning journey state
    learning-steps/           Step progression hooks
    navigation/               Route helpers
    personalization/          Learning DNA hooks
    podcast/                  Podcast mode hooks
    profile/                  User profile CRUD
    projects/                 Projects CRUD
    realtime-speech/          Realtime voice hooks
    recommendations/          Predictive recs
    ui/                       Toast, modal, dialog wrappers
  integrations/
    supabase/                 Supabase client + generated types
  lib/                        Helpers and utilities
  pages/
    HomePage.tsx              Landing page
    SignIn.tsx                Login
    SignUp.tsx                Signup
    SignUpSuccess.tsx         Post-signup verification screen
    ForgotPassword.tsx        Password reset
    AuthPage.tsx              Shared auth layout
    ProjectsPage.tsx          User learning paths
    Community.tsx             Public community paths
    PlanPage.tsx              Learning plan view
    ContentPage.tsx           Lesson content view
    AudioPage.tsx             Audio-mode view
    PodcastPage.tsx           Podcast-mode view
    SettingsPage.tsx          User settings
    ProfilePage.tsx           User profile
    AdminGenerateTopics.tsx   Admin utility
    NotFound.tsx              404
  store/
    learningCommandStore.ts   Zustand store for the learning command center
  styles/                      Shared CSS
  utils/                       Helper functions
supabase/
  config.toml                 Function + auth configuration
  migrations/                 SQL migrations
  functions/
    _shared/                  CORS, auth, AI provider, utils
    chat-tutor/               Realtime tutor chat
    generate-ai-insight/      Per-user AI insights
    generate-daily-community-topics/
    generate-deep-dive-content/
    generate-deep-dive-topics/
    generate-learning-content/
    generate-learning-journey/
    generate-mental-model-images/   Replicate image generation
    generate-path-mental-models/
    generate-presentation-image/    Replicate image generation
    generate-related-topics/
    get-predictive-recommendations/
    get-prompt-insights/
    get-recommended-topics/
    get-skill-gaps/
    get-user-learning-profile/
    learning-modes-transform/
    openai-tts/
    realtime-speech/
    text-to-speech/
```

### AI Flow

```
User opens a learning step
  -> React component calls supabase.functions.invoke("generate-learning-content", { body })
    -> Edge Function (Deno runtime) loads AI config
      -> Primary model via OpenRouter
      -> Fallback model via OpenRouter
      -> Final fallback: direct OpenAI
    <- Structured response
  <- Rendered in the UI and saved to Supabase
```

All AI calls flow through Supabase Edge Functions. API keys live in Supabase secrets -- they never touch the browser. The `_shared/ai-provider` module wraps model routing so any function can just call `createAIClient().chat(...)`.

### Database Schema (summary)

The app uses a set of Postgres tables in Supabase, protected by Row Level Security:

- **Learning paths** -- one row per generated path, with topic, level, and ownership
- **Learning steps** -- ordered steps belonging to a path
- **Generated content** -- lesson bodies, deep-dives, and related topics per step
- **Mental model images** -- Replicate-generated images tied to a step
- **User profiles** -- display name, preferences, timezone, learning DNA
- **Community topics** -- auto-generated public learning paths for the community feed
- **Personalization signals** -- prompt insights, skill gaps, predictive recommendations

Row Level Security is enforced on every user-facing table so users only see their own data.

---

## Developing with AI Tools

This project is designed to work well with AI development tools. Two files make this explicit:

- **`CLAUDE.md`** -- Project-wide instructions, conventions, and architecture overview. Claude Code reads this automatically.
- **`AGENTS.md`** -- Defines specialist agents with clear ownership boundaries.

### Using Claude Code

Open the project folder in Claude Code. The agent will pick up `CLAUDE.md` and `AGENTS.md` automatically and follow the conventions.

### Using Cursor

Open the project in Cursor. The `CLAUDE.md` file serves as context for Cursor's AI features. Use inline edit (Cmd+K) for quick changes and the chat panel for larger refactors.

### Using GitHub Copilot

Copilot picks up patterns from the existing codebase (Supabase client usage, auth checks, Tailwind conventions). The consistent conventions in `CLAUDE.md` make Copilot suggestions more accurate.

### Contributing with AI Tools

We encourage contributors to use AI tools. If you submit a PR:

1. Mention which AI tools you used -- we see it as a positive
2. Follow the conventions in `CLAUDE.md`
3. Use the specialist agent boundaries in `AGENTS.md`
4. Run `npx tsc --noEmit` and `npm run build` before submitting

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**TL;DR:**

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (AI tools welcome)
4. Run `npx tsc --noEmit` and `npm run build` to verify
5. Commit with a descriptive message
6. Push to your fork and open a PR

---

## License

[MIT](LICENSE) -- use it however you want.

---

## Acknowledgments

- Built with [Claude Code](https://claude.ai/claude-code) by Anthropic
- Developed in [Cursor](https://cursor.com) -- the AI-powered IDE
- AI pair programming by [GitHub Copilot](https://github.com/features/copilot)
- Text generation powered by [OpenAI](https://openai.com) and [OpenRouter](https://openrouter.ai/)
- Image generation powered by [Replicate](https://replicate.com/)
- Database, auth, and edge functions by [Supabase](https://supabase.com)
- UI components from [shadcn/ui](https://ui.shadcn.com/) and [Radix UI](https://www.radix-ui.com/)
- Originally released as **LearnFlow** by Enterprise DNA

---

<p align="center">
  Built with pride by <a href="https://www.enterprisedna.co"><strong>Enterprise DNA</strong></a>
  <br />
  Powered by AI-assisted development with Claude Code, Cursor, and GitHub Copilot
</p>
