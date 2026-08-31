import { useMutation, useQuery } from '@tanstack/react-query'

import { apiClient } from './client'
import type { ExplainedStep } from './types'

export function getExplanations(learnerId: string) {
  return apiClient.get<{ explained_steps: ExplainedStep[] }>(`/api/explain/${learnerId}`)
}

export function askQuestion(learnerId: string, question: string) {
  return apiClient.post<{ answer: string }>(`/api/explain/${learnerId}/ask`, { question })
}

export function useExplanations(learnerId: string | null) {
  return useQuery({
    queryKey: ['explain', learnerId],
    queryFn: () => getExplanations(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useAskQuestion(learnerId: string | null) {
  return useMutation({
    mutationFn: (question: string) => askQuestion(learnerId as string, question),
  })
}
