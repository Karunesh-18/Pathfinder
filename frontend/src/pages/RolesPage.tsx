import { Link } from 'react-router-dom'

import { useRoles } from '../api/coursesApi'
import { useProfile, useUpdateProfile } from '../api/learnerApi'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { RoleCard } from '../components/roles/RoleCard'
import { useAuth } from '../context/AuthContext'

export function RolesPage() {
  const { learnerId } = useAuth()
  const rolesQuery = useRoles()
  const profileQuery = useProfile(learnerId)
  const updateProfile = useUpdateProfile(learnerId)

  const hasProfile = !!profileQuery.data

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="mb-1 text-2xl font-semibold">Explore roles</h1>
      <p className="mb-6 text-sm text-fg-muted">
        Browse the career tracks PathFinder currently has courses for, and set which one you're aiming toward.
      </p>

      {!profileQuery.isLoading && !hasProfile && (
        <div className="mb-5 rounded-xl border border-coral/30 bg-coral/10 px-4 py-3 text-sm">
          Complete{' '}
          <Link to="/onboarding" className="font-semibold text-coral-dark underline dark:text-coral-light">
            onboarding
          </Link>{' '}
          first to set a target role.
        </div>
      )}

      {rolesQuery.isLoading && <LoadingSkeleton lines={6} />}
      {rolesQuery.isError && (
        <ErrorBanner message={errorMessage(rolesQuery.error)} onRetry={() => rolesQuery.refetch()} />
      )}

      {rolesQuery.data && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {rolesQuery.data.roles.map((role) => (
            <RoleCard
              key={role.role}
              role={role}
              isCurrent={profileQuery.data?.target_role === role.role}
              canSelect={hasProfile}
              isPending={updateProfile.isPending}
              onSelect={() => updateProfile.mutate({ target_role: role.role })}
            />
          ))}
        </div>
      )}
    </div>
  )
}
