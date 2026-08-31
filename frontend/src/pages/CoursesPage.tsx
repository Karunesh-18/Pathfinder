import { useCourses } from '../api/dashboardApi'
import { CourseGrid } from '../components/courses/CourseGrid'
import { ErrorBanner, errorMessage } from '../components/common/ErrorBanner'
import { LoadingSkeleton } from '../components/common/LoadingSkeleton'
import { useLearnerSession } from '../context/LearnerSessionContext'

export function CoursesPage() {
  const { targetRole } = useLearnerSession()
  const coursesQuery = useCourses()

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-1 text-2xl font-semibold">Browse resources</h1>
      <p className="mb-6 text-sm text-fg-muted">Courses currently seeded for {targetRole}.</p>

      {coursesQuery.isLoading && <LoadingSkeleton lines={6} />}
      {coursesQuery.isError && (
        <ErrorBanner message={errorMessage(coursesQuery.error)} onRetry={() => coursesQuery.refetch()} />
      )}
      {coursesQuery.data && <CourseGrid courses={coursesQuery.data.courses} />}
    </div>
  )
}
