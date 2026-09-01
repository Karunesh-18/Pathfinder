import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { AuthForm } from '../components/auth/AuthForm'
import { errorMessage } from '../components/common/ErrorBanner'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(email: string, password: string) {
    setError(null)
    setIsPending(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setIsPending(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-8">
      <h1 className="mb-1 text-2xl font-semibold">Welcome back</h1>
      <p className="mb-6 text-sm text-fg-muted">Log in to pick up your learning path.</p>
      <AuthForm mode="login" onSubmit={handleSubmit} isPending={isPending} error={error} />
      <p className="mt-5 text-center text-sm text-fg-muted">
        New here?{' '}
        <Link to="/signup" className="font-medium text-navy hover:underline dark:text-navy-light">
          Create an account
        </Link>
      </p>
    </div>
  )
}
