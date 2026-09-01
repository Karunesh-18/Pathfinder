import { useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError } from '../api/client'
import { useDashboard } from '../api/dashboardApi'
import { useProfile } from '../api/learnerApi'
import type { ReplanResult } from '../api/types'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { CompletedHistoryList, RemainingTimelineList } from '../components/dashboard/TimelineList'
import { NextActionCallout } from '../components/dashboard/NextActionCallout'
import { ProgressUpdateForm } from '../components/dashboard/ProgressUpdateForm'
import { ReplanResultBanner } from '../components/dashboard/ReplanResultBanner'
import { SkillRadarChart } from '../components/dashboard/SkillRadarChart'
import { SummaryStatTiles } from '../components/dashboard/SummaryStatTiles'
import { useAuth } from '../context/AuthContext'

export function DashboardPage() {
  const { learnerId } = useAuth()
  const profileQuery = useProfile(learnerId)
  const targetRole = profileQuery.data?.target_role ?? undefined
  const dashboardQuery = useDashboard(learnerId, targetRole)
  const [replanResult, setReplanResult] = useState<ReplanResult | null>(null)

  const noProfileYet =
    profileQuery.isError && profileQuery.error instanceof ApiError && profileQuery.error.status === 404

  if (noProfileYet) {
    return (
      <div className="mx-auto max-w-lg py-10 text-center">
        <h1 className="mb-2 text-xl font-semibold">Let's get you set up</h1>
        <p className="mb-5 text-sm text-fg-muted">
          You haven't described your learning goal yet — onboarding only takes a minute.
        </p>
        <Link
          to="/onboarding"
          className="inline-block rounded-full bg-coral px-6 py-3 text-sm font-semibold text-white transition hover:bg-coral-dark"
        >
          Start onboarding
        </Link>
      </div>
    )
  }

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
              <ProgressUpdateForm onResult={setReplanResult} targetRole={targetRole} />
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
