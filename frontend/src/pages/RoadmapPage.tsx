import { useDashboard } from '../api/dashboardApi'
import { useExplanations } from '../api/explainApi'
import { useProfile } from '../api/learnerApi'
import { usePath } from '../api/pathApi'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { ProgressSummaryBar } from '../components/roadmap/ProgressSummaryBar'
import { RoadmapTimeline } from '../components/roadmap/RoadmapTimeline'
import { useAuth } from '../context/AuthContext'

export function RoadmapPage() {
  const { learnerId } = useAuth()
  const profileQuery = useProfile(learnerId)
  const targetRole = profileQuery.data?.target_role ?? undefined
  const pathQuery = usePath(learnerId)
  const explainQuery = useExplanations(learnerId, targetRole)
  const dashboardQuery = useDashboard(learnerId, targetRole)

  const rationaleByCourseId: Record<string, string> = {}
  explainQuery.data?.explained_steps.forEach((item) => {
    rationaleByCourseId[item.step.course_id] = item.rationale
  })

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-2xl font-semibold">Your learning roadmap</h1>
      <p className="mb-4 text-sm text-fg-muted">
        Ordered by prerequisites, with milestones marking every quarter of the journey.
      </p>

      {pathQuery.data && pathQuery.data.steps.length > 0 && dashboardQuery.data && (
        <div className="mb-6">
          <ProgressSummaryBar summary={dashboardQuery.data.summary} />
        </div>
      )}

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
