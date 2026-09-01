import { useState } from 'react'
import type { FormEvent } from 'react'

import { ErrorBanner } from '../common/ErrorBanner'

interface AuthFormProps {
  mode: 'login' | 'signup'
  onSubmit: (email: string, password: string, displayName?: string) => void
  isPending: boolean
  error: string | null
}

export function AuthForm({ mode, onSubmit, isPending, error }: AuthFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    onSubmit(email.trim(), password, mode === 'signup' ? displayName.trim() : undefined)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {mode === 'signup' && (
        <div>
          <label htmlFor="displayName" className="mb-1 block text-xs font-medium uppercase tracking-wide text-fg-muted">
            Name (optional)
          </label>
          <input
            id="displayName"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Ada Lovelace"
            className="w-full rounded-lg border border-border bg-bg px-3.5 py-2.5 text-sm outline-none focus:border-navy"
          />
        </div>
      )}

      <div>
        <label htmlFor="email" className="mb-1 block text-xs font-medium uppercase tracking-wide text-fg-muted">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-lg border border-border bg-bg px-3.5 py-2.5 text-sm outline-none focus:border-navy"
        />
      </div>

      <div>
        <label htmlFor="password" className="mb-1 block text-xs font-medium uppercase tracking-wide text-fg-muted">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          className="w-full rounded-lg border border-border bg-bg px-3.5 py-2.5 text-sm outline-none focus:border-navy"
        />
      </div>

      {error && <ErrorBanner message={error} />}

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-full bg-coral px-4 py-3 text-sm font-semibold text-white transition hover:bg-coral-dark disabled:opacity-50"
      >
        {isPending ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
      </button>
    </form>
  )
}
