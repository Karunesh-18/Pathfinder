import { Link } from 'react-router-dom'

import type { Course } from '../../api/types'
import { Badge } from '../common/Badge'

export function CourseCard({ course }: { course: Course }) {
  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-bg-raised p-4">
      <div className="flex items-start justify-between gap-2">
        <Link to={`/courses/${course.id}`} className="text-sm font-semibold hover:underline">
          {course.title}
        </Link>
        {course.level && <Badge tone="neutral">{course.level}</Badge>}
      </div>
      <p className="mt-0.5 text-xs text-fg-muted">
        {course.provider}
        {course.format ? ` · ${course.format}` : ''}
        {course.estimated_hours != null ? ` · ${course.estimated_hours}h` : ''}
      </p>
      <p className="mt-2 flex-1 text-sm text-fg-muted line-clamp-3">{course.description}</p>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {course.skills_taught.slice(0, 5).map((skill) => (
          <Badge key={skill} tone="navy">
            {skill}
          </Badge>
        ))}
      </div>
      {course.url && (
        <a
          href={course.url}
          target="_blank"
          rel="noreferrer"
          className="mt-3 text-xs font-semibold text-navy hover:underline dark:text-navy-light"
        >
          View course →
        </a>
      )}
    </div>
  )
}
