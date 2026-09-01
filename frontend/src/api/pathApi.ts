import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from './client'
import type { PathStep } from './types'

export function buildPath(learnerId: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.post<{ steps: PathStep[] }>(`/api/path/${learnerId}${qs}`)
}

export function getPath(learnerId: string) {
  return apiClient.get<{ steps: PathStep[] }>(`/api/path/${learnerId}`)
}

export function usePath(learnerId: string | null) {
  return useQuery({
    queryKey: ['path', learnerId],
    queryFn: () => getPath(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useBuildPath() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ learnerId, targetRole }: { learnerId: string; targetRole?: string }) =>
      buildPath(learnerId, targetRole),
    onSuccess: (data, { learnerId }) => {
      queryClient.setQueryData(['path', learnerId], data)
      queryClient.invalidateQueries({ queryKey: ['explain', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', learnerId] })
    },
  })
}
