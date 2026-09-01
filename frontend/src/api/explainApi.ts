import { useMutation, useQuery } from '@tanstack/react-query'

import { apiClient } from './client'
import type { ExplainedStep } from './types'

export function getExplanations(learnerId: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.get<{ explained_steps: ExplainedStep[] }>(`/api/explain/${learnerId}${qs}`)
}

export function askQuestion(learnerId: string, question: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.post<{ answer: string }>(`/api/explain/${learnerId}/ask${qs}`, { question })
}

export function useExplanations(learnerId: string | null, targetRole?: string) {
  return useQuery({
    queryKey: ['explain', learnerId, targetRole],
    queryFn: () => getExplanations(learnerId as string, targetRole),
    enabled: !!learnerId,
  })
}

export function useAskQuestion(learnerId: string | null, targetRole?: string) {
  return useMutation({
    mutationFn: (question: string) => askQuestion(learnerId as string, question, targetRole),
  })
}
