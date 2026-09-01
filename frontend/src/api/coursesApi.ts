import { useQuery } from '@tanstack/react-query'

import { apiClient } from './client'
import type { Course, CourseTree, Role } from './types'

export function getCourses() {
  // Deliberately unfiltered — CoursesPage fetches the full catalog once
  // (a few dozen rows across every role) and filters client-side, which
  // is simpler than adding server-side search at this dataset size.
  return apiClient.get<{ courses: Course[] }>('/api/courses')
}

export function getCourse(courseId: string) {
  return apiClient.get<Course>(`/api/courses/${courseId}`)
}

export function getCourseTree(targetRole: string) {
  return apiClient.get<CourseTree>(`/api/courses/tree?target_role=${encodeURIComponent(targetRole)}`)
}

export function getRoles() {
  return apiClient.get<{ roles: Role[] }>('/api/roles')
}

export function useCourses() {
  return useQuery({
    queryKey: ['courses'],
    queryFn: getCourses,
  })
}

export function useCourse(courseId: string | null) {
  return useQuery({
    queryKey: ['course', courseId],
    queryFn: () => getCourse(courseId as string),
    enabled: !!courseId,
  })
}

export function useCourseTree(targetRole: string | null) {
  return useQuery({
    queryKey: ['course-tree', targetRole],
    queryFn: () => getCourseTree(targetRole as string),
    enabled: !!targetRole,
  })
}

export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: getRoles,
  })
}
