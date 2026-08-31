import { useMutation, useQueryClient } from '@tanstack/react-query'

import { apiClient } from './client'
import type { ReplanResult } from './types'

export function submitProgress(learnerId: string, rawText: string) {
  return apiClient.post<ReplanResult>(`/api/progress/${learnerId}`, { raw_text: rawText })
}

export function useSubmitProgress(learnerId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rawText: string) => submitProgress(learnerId as string, rawText),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['path', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['explain', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['gaps', learnerId] })
      queryClient.invalidateQueries({ queryKey: ['profile', learnerId] })
    },
  })
}
