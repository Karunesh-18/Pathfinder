import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

// The only role currently seeded in the taxonomy/course knowledge base —
// surfaced in the UI as a note, not a picker (see backend DEFAULT_TARGET_ROLE).
export const TARGET_ROLE = 'Data Engineer'

const STORAGE_KEY = 'pf_learner_id'

interface LearnerSessionValue {
  learnerId: string | null
  setLearnerId: (id: string) => void
  clearLearnerId: () => void
  targetRole: string
}

const LearnerSessionContext = createContext<LearnerSessionValue | undefined>(undefined)

export function LearnerSessionProvider({ children }: { children: ReactNode }) {
  const [learnerId, setLearnerIdState] = useState<string | null>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY)
    } catch {
      return null
    }
  })

  const setLearnerId = useCallback((id: string) => {
    setLearnerIdState(id)
    try {
      localStorage.setItem(STORAGE_KEY, id)
    } catch {
      // localStorage unavailable (private mode, etc.) — session still
      // works for this page view, just won't persist across reloads.
    }
  }, [])

  const clearLearnerId = useCallback(() => {
    setLearnerIdState(null)
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }, [])

  const value = useMemo(
    () => ({ learnerId, setLearnerId, clearLearnerId, targetRole: TARGET_ROLE }),
    [learnerId, setLearnerId, clearLearnerId],
  )

  return <LearnerSessionContext.Provider value={value}>{children}</LearnerSessionContext.Provider>
}

export function useLearnerSession() {
  const ctx = useContext(LearnerSessionContext)
  if (!ctx) {
    throw new Error('useLearnerSession must be used within a LearnerSessionProvider')
  }
  return ctx
}
