import { Link } from 'react-router-dom'

import { FeatureCard } from '../components/landing/FeatureCard'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 0 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15Z" />
      </svg>
    ),
    title: 'A plan built for you',
    description: 'Tell us your goal in your own words — we turn it into a structured, ordered course roadmap.',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 3v18h18M7 15l4-4 3 3 5-6" />
      </svg>
    ),
    title: 'Track real progress',
    description: 'Report what you finish and watch your skill gaps close, with an adaptive plan that replans as you grow.',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 8V4H8M12 4l8 8-8 8-8-8 4-4" />
      </svg>
    ),
    title: 'See the whole skill tree',
    description: 'Visualize how skills build on each other for your target role, and which courses teach each one.',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    ),
    title: 'Ask anything, anytime',
    description: 'A built-in assistant explains why each course is in your plan and answers questions about your path.',
  },
]

export function LandingPage() {
  const { user } = useAuth()

  return (
    <div className="mx-auto max-w-4xl py-8 sm:py-12">
      <div className="text-center">
        <h1 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl">
          Find your path into a tech career, one course at a time
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-base text-fg-muted">
          PathFinder builds a personalized, ordered learning roadmap toward a target role, explains its reasoning, and
          adapts as you make progress.
        </p>
        <div className="mt-7 flex items-center justify-center gap-3">
          {user ? (
            <Link
              to="/dashboard"
              className="rounded-full bg-coral px-6 py-3 text-sm font-semibold text-white transition hover:bg-coral-dark"
            >
              Go to your dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/signup"
                className="rounded-full bg-coral px-6 py-3 text-sm font-semibold text-white transition hover:bg-coral-dark"
              >
                Get started free
              </Link>
              <Link
                to="/login"
                className="rounded-full border border-border px-6 py-3 text-sm font-semibold text-fg transition hover:bg-bg-raised"
              >
                Log in
              </Link>
            </>
          )}
        </div>
      </div>

      <div className="mt-12 grid grid-cols-1 gap-4 sm:mt-16 sm:grid-cols-2">
        {FEATURES.map((f) => (
          <FeatureCard key={f.title} {...f} />
        ))}
      </div>
    </div>
  )
}
