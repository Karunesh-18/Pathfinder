import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from './client'
import type { Profile, SkillGap } from './types'

export function createOrUpdateProfile(rawText: string, learnerId: string | null) {
  return apiClient.post<Profile>('/api/learners', { raw_text: rawText, learner_id: learnerId })
}

export function getProfile(learnerId: string) {
  return apiClient.get<Profile>(`/api/learners/${learnerId}`)
}

export function getGaps(learnerId: string) {
  return apiClient.get<{ gaps: SkillGap[] }>(`/api/learners/${learnerId}/gaps`)
}

export function useProfile(learnerId: string | null) {
  return useQuery({
    queryKey: ['profile', learnerId],
    queryFn: () => getProfile(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useGaps(learnerId: string | null) {
  return useQuery({
    queryKey: ['gaps', learnerId],
    queryFn: () => getGaps(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useCreateOrUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ rawText, learnerId }: { rawText: string; learnerId: string | null }) =>
      createOrUpdateProfile(rawText, learnerId),
    onSuccess: (profile) => {
      queryClient.setQueryData(['profile', profile.learner_id], profile)
      queryClient.invalidateQueries({ queryKey: ['gaps', profile.learner_id] })
    },
  })
}
