import { useQuery } from '@tanstack/react-query'

import { apiClient } from './client'
import type { Course, Dashboard } from './types'

export function getDashboard(learnerId: string) {
  return apiClient.get<Dashboard>(`/api/dashboard/${learnerId}`)
}

export function getCourses() {
  return apiClient.get<{ courses: Course[] }>('/api/courses')
}

export function useDashboard(learnerId: string | null) {
  return useQuery({
    queryKey: ['dashboard', learnerId],
    queryFn: () => getDashboard(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useCourses() {
  return useQuery({
    queryKey: ['courses'],
    queryFn: getCourses,
  })
}
