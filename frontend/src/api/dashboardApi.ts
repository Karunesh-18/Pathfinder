import { useQuery } from '@tanstack/react-query'

import { apiClient } from './client'
import type { Dashboard, SystemStatus } from './types'

export function getDashboard(learnerId: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.get<Dashboard>(`/api/dashboard/${learnerId}${qs}`)
}

export function getSystemStatus() {
  return apiClient.get<SystemStatus>('/api/system/status')
}

export function useDashboard(learnerId: string | null, targetRole?: string) {
  return useQuery({
    queryKey: ['dashboard', learnerId, targetRole],
    queryFn: () => getDashboard(learnerId as string, targetRole),
    enabled: !!learnerId,
  })
}
