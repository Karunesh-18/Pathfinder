import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from './client'
import type { Profile, SkillEntry, SkillGap } from './types'

export function createOrUpdateProfile(rawText: string) {
  return apiClient.post<Profile>('/api/learners', { raw_text: rawText })
}

export function getProfile(learnerId: string) {
  return apiClient.get<Profile>(`/api/learners/${learnerId}`)
}

export interface ProfileUpdate {
  target_role?: string | null
  current_skills?: SkillEntry[] | null
  time_budget_hours_per_week?: number | null
  format_preference?: string | null
}

export function updateProfile(learnerId: string, updates: ProfileUpdate) {
  return apiClient.patch<Profile>(`/api/learners/${learnerId}`, updates)
}

export function getGaps(learnerId: string, targetRole?: string) {
  const qs = targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''
  return apiClient.get<{ gaps: SkillGap[] }>(`/api/learners/${learnerId}/gaps${qs}`)
}

export function useProfile(learnerId: string | null) {
  return useQuery({
    queryKey: ['profile', learnerId],
    queryFn: () => getProfile(learnerId as string),
    enabled: !!learnerId,
  })
}

export function useGaps(learnerId: string | null, targetRole?: string) {
  return useQuery({
    queryKey: ['gaps', learnerId, targetRole],
    queryFn: () => getGaps(learnerId as string, targetRole),
    enabled: !!learnerId,
  })
}

export function useCreateOrUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rawText: string) => createOrUpdateProfile(rawText),
    onSuccess: (profile) => {
      queryClient.setQueryData(['profile', profile.learner_id], profile)
      queryClient.invalidateQueries({ queryKey: ['gaps', profile.learner_id] })
    },
  })
}

export function useUpdateProfile(learnerId: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (updates: ProfileUpdate) => updateProfile(learnerId as string, updates),
    onSuccess: (profile) => {
      queryClient.setQueryData(['profile', profile.learner_id], profile)
      queryClient.invalidateQueries({ queryKey: ['gaps', profile.learner_id] })
    },
  })
}
