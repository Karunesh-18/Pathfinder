import { useMutation, useQueryClient } from '@tanstack/react-query'

import { apiClient } from './client'
import type { ReplanResult } from './types'

export function submitProgress(learnerId: string, rawText: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.post<ReplanResult>(`/api/progress/${learnerId}${qs}`, { raw_text: rawText })
}

export function useSubmitProgress(learnerId: string | null, targetRole?: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rawText: string) => submitProgress(learnerId as string, rawText, targetRole),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['path', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['explain', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['gaps', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['profile', learnerId] })
    },
  })
}
