import { Link, useParams } from 'react-router-dom'

import { useCourse } from '../api/coursesApi'
import { Badge } from '../components/common/Badge'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'

export function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const courseQuery = useCourse(courseId ?? null)

  return (
    <div className="mx-auto max-w-2xl">
      <Link to="/courses" className="mb-4 inline-block text-sm font-medium text-navy hover:underline dark:text-navy-light">
        ← Back to courses
      </Link>

      {courseQuery.isLoading && <LoadingSkeleton lines={6} />}
      {courseQuery.isError && (
        <ErrorBanner message={errorMessage(courseQuery.error)} onRetry={() => courseQuery.refetch()} />
      )}

      {courseQuery.data && (
        <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
          <div className="mb-1 flex flex-wrap items-start justify-between gap-2">
            <h1 className="text-xl font-semibold">{courseQuery.data.title}</h1>
            {courseQuery.data.level && <Badge tone="neutral">{courseQuery.data.level}</Badge>}
          </div>
          <p className="mb-4 text-sm text-fg-muted">
            {courseQuery.data.provider}
            {courseQuery.data.format ? ` · ${courseQuery.data.format}` : ''}
            {courseQuery.data.estimated_hours != null ? ` · ${courseQuery.data.estimated_hours}h` : ''}
          </p>

          <p className="mb-5 text-sm leading-relaxed">{courseQuery.data.description}</p>

          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <dt className="mb-1.5 text-xs font-medium uppercase tracking-wide text-fg-muted">Skills taught</dt>
              <dd className="flex flex-wrap gap-1.5">
                {courseQuery.data.skills_taught.map((s) => (
                  <Badge key={s} tone="navy">
                    {s}
                  </Badge>
                ))}
              </dd>
            </div>

            <div>
              <dt className="mb-1.5 text-xs font-medium uppercase tracking-wide text-fg-muted">Target roles</dt>
              <dd className="flex flex-wrap gap-1.5">
                {courseQuery.data.target_roles.map((r) => (
                  <Badge key={r} tone="coral">
                    {r}
                  </Badge>
                ))}
              </dd>
            </div>

            <div>
              <dt className="mb-1.5 text-xs font-medium uppercase tracking-wide text-fg-muted">Prerequisites</dt>
              <dd className="text-sm">
                {courseQuery.data.prerequisites.length > 0 ? courseQuery.data.prerequisites.join(', ') : 'None'}
              </dd>
            </div>
          </dl>

          {courseQuery.data.url && (
            <a
              href={courseQuery.data.url}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-block text-sm font-semibold text-navy hover:underline dark:text-navy-light"
            >
              View course on {courseQuery.data.provider} →
            </a>
          )}
        </div>
      )}
    </div>
  )
}
