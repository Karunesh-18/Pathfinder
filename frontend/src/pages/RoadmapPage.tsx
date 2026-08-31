import { Navigate } from 'react-router-dom'

import { useExplanations } from '../api/explainApi'
import { usePath } from '../api/pathApi'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { RoadmapTimeline } from '../components/roadmap/RoadmapTimeline'
import { useLearnerSession } from '../context/LearnerSessionContext'

export function RoadmapPage() {
  const { learnerId } = useLearnerSession()
  const pathQuery = usePath(learnerId)
  const explainQuery = useExplanations(learnerId)

  if (!learnerId) return <Navigate to="/onboarding" replace />

  const rationaleByCourseId: Record<string, string> = {}
  explainQuery.data?.explained_steps.forEach((item) => {
    rationaleByCourseId[item.step.course_id] = item.rationale
  })

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-2xl font-semibold">Your learning roadmap</h1>
      <p className="mb-6 text-sm text-fg-muted">
        Ordered by prerequisites, with milestones marking every quarter of the journey.
      </p>

      {pathQuery.isLoading && <LoadingSkeleton lines={6} />}
      {pathQuery.isError && <ErrorBanner message={errorMessage(pathQuery.error)} onRetry={() => pathQuery.refetch()} />}
      {pathQuery.data && pathQuery.data.steps.length === 0 && (
        <p className="text-sm text-fg-muted">
          No roadmap built yet — head back to onboarding and click "Build my roadmap".
        </p>
      )}
      {pathQuery.data && pathQuery.data.steps.length > 0 && (
        <RoadmapTimeline steps={pathQuery.data.steps} rationaleByCourseId={rationaleByCourseId} />
      )}
    </div>
  )
}
