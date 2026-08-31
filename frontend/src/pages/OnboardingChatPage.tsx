import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCreateOrUpdateProfile } from '../api/learnerApi'
import { useBuildPath } from '../api/pathApi'
import type { Profile } from '../api/types'
import type { ChatMessage } from '../components/chat/ChatWindow'
import { ChatWindow } from '../components/chat/ChatWindow'
import { FollowUpQuestionChips } from '../components/chat/FollowUpQuestionChips'
import { errorMessage } from '../components/common/ErrorBanner'
import { useLearnerSession } from '../context/LearnerSessionContext'

const GREETING =
  "Hi! I'm PathFinder. Tell me what you're trying to become and I'll build you a personalized learning roadmap. " +
  'For example: "I want to become a data engineer, I already know some Python and SQL, I can study about 5 hours a week, and I prefer video courses."'

export function OnboardingChatPage() {
  const { learnerId, setLearnerId } = useLearnerSession()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>([{ role: 'assistant', text: GREETING }])
  const [transcript, setTranscript] = useState('')
  const [profile, setProfile] = useState<Profile | null>(null)
  const [error, setError] = useState<string | null>(null)

  const createOrUpdateProfile = useCreateOrUpdateProfile()
  const buildPath = useBuildPath()

  function handleSend(text: string) {
    setMessages((prev) => [...prev, { role: 'user', text }])
    setError(null)
    const nextTranscript = transcript ? `${transcript}\n${text}` : text

    createOrUpdateProfile.mutate(
      { rawText: nextTranscript, learnerId },
      {
        onSuccess: (p) => {
          setTranscript(nextTranscript)
          setProfile(p)
          if (!learnerId) setLearnerId(p.learner_id)

          if (p.missing_fields.length > 0) {
            setMessages((prev) => [
              ...prev,
              { role: 'assistant', text: 'Thanks — a couple more things would help:' },
            ])
          } else {
            setMessages((prev) => [
              ...prev,
              {
                role: 'assistant',
                text: "Great, I have everything I need. Click \"Build my roadmap\" below when you're ready.",
              },
            ])
          }
        },
        onError: (err) => setError(errorMessage(err)),
      },
    )
  }

  function handleBuildPath() {
    if (!learnerId) return
    buildPath.mutate(learnerId, {
      onSuccess: () => navigate('/roadmap'),
      onError: (err) => setError(errorMessage(err)),
    })
  }

  const ready = profile !== null && profile.missing_fields.length === 0

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-semibold">Let's find your path</h1>
      <p className="mb-5 text-sm text-fg-muted">
        Describe your goals in natural language — I'll turn it into a structured plan.
      </p>

      <ChatWindow
        messages={messages}
        onSend={handleSend}
        disabled={createOrUpdateProfile.isPending}
        placeholder="Describe your learning goal…"
        extraContent={
          profile && profile.follow_up_questions.length > 0 ? (
            <FollowUpQuestionChips questions={profile.follow_up_questions} />
          ) : undefined
        }
      />

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      {ready && (
        <button
          type="button"
          onClick={handleBuildPath}
          disabled={buildPath.isPending}
          className="mt-4 w-full rounded-full bg-coral px-4 py-3 text-sm font-semibold text-white transition hover:bg-coral-dark disabled:opacity-50 sm:w-auto"
        >
          {buildPath.isPending ? 'Building your roadmap…' : 'Build my roadmap'}
        </button>
      )}
    </div>
  )
}
