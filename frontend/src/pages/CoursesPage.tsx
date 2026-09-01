import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { useCourses } from '../api/coursesApi'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import type { CourseFilterValues } from '../components/courses/CourseFilters'
import { CourseFilters } from '../components/courses/CourseFilters'
import { CourseGrid } from '../components/courses/CourseGrid'

const EMPTY_FILTERS: CourseFilterValues = { role: '', provider: '', level: '', search: '' }

export function CoursesPage() {
  const coursesQuery = useCourses()
  const [filters, setFilters] = useState<CourseFilterValues>(EMPTY_FILTERS)

  const courses = coursesQuery.data?.courses ?? []

  const { roles, providers, levels } = useMemo(() => {
    const roleSet = new Set<string>()
    const providerSet = new Set<string>()
    const levelSet = new Set<string>()
    for (const c of courses) {
      c.target_roles.forEach((r) => roleSet.add(r))
      providerSet.add(c.provider)
      if (c.level) levelSet.add(c.level)
    }
    return {
      roles: [...roleSet].sort(),
      providers: [...providerSet].sort(),
      levels: [...levelSet].sort(),
    }
  }, [courses])

  const filtered = useMemo(() => {
    const search = filters.search.trim().toLowerCase()
    return courses.filter((c) => {
      if (filters.role && !c.target_roles.includes(filters.role)) return false
      if (filters.provider && c.provider !== filters.provider) return false
      if (filters.level && c.level !== filters.level) return false
      if (search) {
        const haystack = `${c.title} ${c.description} ${c.skills_taught.join(' ')}`.toLowerCase()
        if (!haystack.includes(search)) return false
      }
      return true
    })
  }, [courses, filters])

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-semibold">Browse courses</h1>
        <Link to="/courses/tree" className="text-sm font-medium text-navy hover:underline dark:text-navy-light">
          View as skill tree →
        </Link>
      </div>
      <p className="mb-6 text-sm text-fg-muted">
        {courses.length > 0 ? `${filtered.length} of ${courses.length} courses` : 'Courses across every seeded role.'}
      </p>

      {coursesQuery.isLoading && <LoadingSkeleton lines={6} />}
      {coursesQuery.isError && (
        <ErrorBanner message={errorMessage(coursesQuery.error)} onRetry={() => coursesQuery.refetch()} />
      )}

      {coursesQuery.data && (
        <>
          <CourseFilters roles={roles} providers={providers} levels={levels} values={filters} onChange={setFilters} />
          <CourseGrid courses={filtered} />
        </>
      )}
    </div>
  )
}
