import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { AuthForm } from '../components/auth/AuthForm'
import { errorMessage } from '../components/common/ErrorBanner'
import { useAuth } from '../context/AuthContext'

export function SignupPage() {
  const { user, signup } = useAuth()
  const navigate = useNavigate()
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(email: string, password: string, displayName?: string) {
    setError(null)
    setIsPending(true)
    try {
      await signup(email, password, displayName)
      navigate('/onboarding')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setIsPending(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-8">
      <h1 className="mb-1 text-2xl font-semibold">Create your account</h1>
      <p className="mb-6 text-sm text-fg-muted">A few seconds, then we'll build your first learning path.</p>
      <AuthForm mode="signup" onSubmit={handleSubmit} isPending={isPending} error={error} />
      <p className="mt-5 text-center text-sm text-fg-muted">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-navy hover:underline dark:text-navy-light">
          Log in
        </Link>
      </p>
    </div>
  )
}
