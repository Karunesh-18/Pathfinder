import type { Course } from '../../api/types'
import { CourseCard } from './CourseCard'

export function CourseGrid({ courses }: { courses: Course[] }) {
  if (courses.length === 0) {
    return <p className="text-sm text-fg-muted">No courses found.</p>
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {courses.map((course) => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  )
}
