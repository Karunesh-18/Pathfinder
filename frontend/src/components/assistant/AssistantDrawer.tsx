import { useState } from 'react'
import type { FormEvent } from 'react'

import { useAskQuestion } from '../../api/explainApi'
import { errorMessage } from '../../components/common/ErrorBanner'
import { useLearnerSession } from '../../context/LearnerSessionContext'
import { useIsDesktop } from '../../hooks/useMediaQuery'

interface QaTurn {
  question: string
  answer: string
}

export function AssistantDrawer() {
  const { learnerId } = useLearnerSession()
  const [open, setOpen] = useState(false)
  const [question, setQuestion] = useState('')
  const [turns, setTurns] = useState<QaTurn[]>([])
  const [error, setError] = useState<string | null>(null)
  const isDesktop = useIsDesktop()
  const askQuestion = useAskQuestion(learnerId)

  if (!learnerId) return null

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return
    setError(null)
    askQuestion.mutate(q, {
      onSuccess: (data) => {
        setTurns((prev) => [...prev, { question: q, answer: data.answer }])
        setQuestion('')
      },
      onError: (err) => setError(errorMessage(err)),
    })
  }

  return (
    <>
      {!open && (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full bg-coral px-4 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-coral-dark"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          Ask AI mentor
        </button>
      )}

      {open && (
        <div
          className={
            isDesktop
              ? 'fixed bottom-5 right-5 z-40 flex h-[32rem] w-96 flex-col overflow-hidden rounded-2xl border border-border bg-bg-raised shadow-2xl'
              : 'fixed inset-0 z-40 flex flex-col bg-bg-raised'
          }
        >
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <span className="text-sm font-semibold">Ask about your plan</span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close assistant"
              className="flex h-7 w-7 items-center justify-center rounded-full border border-border"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
            {turns.length === 0 && (
              <p className="text-sm text-fg-muted">
                Ask why a step is in your roadmap, what a skill gap means, or anything else about your plan.
              </p>
            )}
            {turns.map((turn, i) => (
              <div key={i} className="space-y-1.5">
                <div className="ml-auto max-w-[85%] rounded-2xl rounded-br-sm bg-navy px-3 py-2 text-sm text-white">
                  {turn.question}
                </div>
                <div className="mr-auto max-w-[85%] rounded-2xl rounded-bl-sm bg-border/50 px-3 py-2 text-sm">
                  {turn.answer}
                </div>
              </div>
            ))}
            {askQuestion.isPending && <p className="text-sm text-fg-muted">Thinking…</p>}
            {error && <p className="text-sm text-danger">{error}</p>}
          </div>

          <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-border p-3">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question…"
              className="flex-1 rounded-full border border-border bg-bg px-3.5 py-2 text-sm outline-none focus:border-navy"
            />
            <button
              type="submit"
              disabled={askQuestion.isPending || !question.trim()}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-navy text-white disabled:opacity-40"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
          </form>
        </div>
      )}
    </>
  )
}
