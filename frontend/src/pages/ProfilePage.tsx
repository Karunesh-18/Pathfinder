import { Navigate } from 'react-router-dom'

import { useGaps, useProfile } from '../api/learnerApi'
import { Badge } from '../components/common/Badge'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { ProfileSummaryCard } from '../components/profile/ProfileSummaryCard'
import { useLearnerSession } from '../context/LearnerSessionContext'

export function ProfilePage() {
  const { learnerId } = useLearnerSession()
  const profileQuery = useProfile(learnerId)
  const gapsQuery = useGaps(learnerId)

  if (!learnerId) return <Navigate to="/onboarding" replace />

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold">Your profile</h1>

      {profileQuery.isLoading && <LoadingSkeleton lines={5} />}
      {profileQuery.isError && (
        <ErrorBanner message={errorMessage(profileQuery.error)} onRetry={() => profileQuery.refetch()} />
      )}
      {profileQuery.data && <ProfileSummaryCard profile={profileQuery.data} />}

      <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
        <h2 className="mb-3 text-lg font-semibold">Skill gaps toward {profileQuery.data?.target_role ?? 'your goal'}</h2>
        {gapsQuery.isLoading && <LoadingSkeleton lines={4} />}
        {gapsQuery.isError && <ErrorBanner message={errorMessage(gapsQuery.error)} onRetry={() => gapsQuery.refetch()} />}
        {gapsQuery.data && gapsQuery.data.gaps.length === 0 && (
          <p className="text-sm text-fg-muted">No gaps left — you meet every tracked requirement.</p>
        )}
        {gapsQuery.data && gapsQuery.data.gaps.length > 0 && (
          <ul className="space-y-2">
            {gapsQuery.data.gaps.map((gap) => (
              <li
                key={gap.skill}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-sm"
              >
                <span className="font-medium">
                  #{gap.priority_rank} {gap.skill}
                </span>
                <span className="flex items-center gap-2 text-xs text-fg-muted">
                  <Badge tone="neutral">have: {gap.current_level}</Badge>
                  <Badge tone="navy">need: {gap.required_level}</Badge>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
