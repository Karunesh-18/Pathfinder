import { useEffect, useState } from 'react'

import { useCourseTree, useRoles } from '../api/coursesApi'
import { useProfile } from '../api/learnerApi'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { CourseTreeGraph } from '../components/tree/CourseTreeGraph'
import { useAuth } from '../context/AuthContext'

export function CourseTreePage() {
  const { learnerId } = useAuth()
  const profileQuery = useProfile(learnerId)
  const rolesQuery = useRoles()
  const [selectedRole, setSelectedRole] = useState<string | null>(null)

  const targetRole = selectedRole ?? profileQuery.data?.target_role ?? rolesQuery.data?.roles[0]?.role ?? null
  const treeQuery = useCourseTree(targetRole)

  // Once the profile/roles load, adopt the learner's own target role as
  // the default selection (only if the visitor hasn't already picked one).
  useEffect(() => {
    if (selectedRole === null && profileQuery.data?.target_role) {
      setSelectedRole(profileQuery.data.target_role)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileQuery.data?.target_role])

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold">Skill tree</h1>
        {rolesQuery.data && (
          <select
            value={targetRole ?? ''}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus:border-navy"
          >
            {rolesQuery.data.roles.map((r) => (
              <option key={r.role} value={r.role}>
                {r.role}
              </option>
            ))}
          </select>
        )}
      </div>
      <p className="mb-6 text-sm text-fg-muted">
        How skills for {targetRole ?? 'this role'} build on each other, and which courses teach each one. Left to
        right is earlier to later.
      </p>

      {(treeQuery.isLoading || rolesQuery.isLoading) && <LoadingSkeleton lines={6} />}
      {treeQuery.isError && <ErrorBanner message={errorMessage(treeQuery.error)} onRetry={() => treeQuery.refetch()} />}
      {treeQuery.data && <CourseTreeGraph skills={treeQuery.data.skills} />}
    </div>
  )
}
