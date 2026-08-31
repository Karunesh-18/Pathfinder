import { useState } from 'react'
import { Navigate } from 'react-router-dom'

import { useDashboard } from '../api/dashboardApi'
import type { ReplanResult } from '../api/types'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { CompletedHistoryList, RemainingTimelineList } from '../components/dashboard/TimelineList'
import { NextActionCallout } from '../components/dashboard/NextActionCallout'
import { ProgressUpdateForm } from '../components/dashboard/ProgressUpdateForm'
import { ReplanResultBanner } from '../components/dashboard/ReplanResultBanner'
import { SkillRadarChart } from '../components/dashboard/SkillRadarChart'
import { SummaryStatTiles } from '../components/dashboard/SummaryStatTiles'
import { useLearnerSession } from '../context/LearnerSessionContext'

export function DashboardPage() {
  const { learnerId } = useLearnerSession()
  const dashboardQuery = useDashboard(learnerId)
  const [replanResult, setReplanResult] = useState<ReplanResult | null>(null)

  if (!learnerId) return <Navigate to="/onboarding" replace />

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      {dashboardQuery.isLoading && <LoadingSkeleton lines={6} />}
      {dashboardQuery.isError && (
        <ErrorBanner message={errorMessage(dashboardQuery.error)} onRetry={() => dashboardQuery.refetch()} />
      )}

      {dashboardQuery.data && (
        <>
          <SummaryStatTiles summary={dashboardQuery.data.summary} />

          {replanResult && <ReplanResultBanner result={replanResult} onDismiss={() => setReplanResult(null)} />}

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
              <h2 className="mb-3 text-lg font-semibold">Skill development</h2>
              <SkillRadarChart points={dashboardQuery.data.skill_radar} />
            </div>

            <div className="space-y-6">
              <NextActionCallout action={dashboardQuery.data.next_action} />
              <ProgressUpdateForm onResult={setReplanResult} />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
              <h2 className="mb-3 text-lg font-semibold">Completed</h2>
              <CompletedHistoryList items={dashboardQuery.data.completed_history} />
            </div>
            <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
              <h2 className="mb-3 text-lg font-semibold">Remaining</h2>
              <RemainingTimelineList items={dashboardQuery.data.remaining_timeline} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
