import { useState } from 'react'
import type { FormEvent } from 'react'

import { useSubmitProgress } from '../../api/progressApi'
import type { ReplanResult } from '../../api/types'
import { errorMessage } from '../common/ErrorBanner'
import { useAuth } from '../../context/AuthContext'

export function ProgressUpdateForm({
  onResult,
  targetRole,
}: {
  onResult: (result: ReplanResult) => void
  targetRole?: string
}) {
  const { learnerId } = useAuth()
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const submitProgress = useSubmitProgress(learnerId, targetRole)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const value = text.trim()
    if (!value) return
    setError(null)
    submitProgress.mutate(value, {
      onSuccess: (result) => {
        onResult(result)
        setText('')
      },
      onError: (err) => setError(errorMessage(err)),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-border bg-bg-raised p-4">
      <label htmlFor="progress-text" className="mb-2 block text-sm font-semibold">
        Log your progress
      </label>
      <textarea
        id="progress-text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        placeholder="e.g. I finished The Complete SQL Bootcamp and feel comfortable with SQL now."
        className="w-full resize-none rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus:border-navy"
      />
      {error && <p className="mt-2 text-xs text-danger">{error}</p>}
      <button
        type="submit"
        disabled={submitProgress.isPending || !text.trim()}
        className="mt-3 rounded-full bg-navy px-4 py-2 text-sm font-semibold text-white transition disabled:opacity-40"
      >
        {submitProgress.isPending ? 'Submitting…' : 'Submit update'}
      </button>
    </form>
  )
}
