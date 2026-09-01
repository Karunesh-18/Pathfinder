import { useMutation } from '@tanstack/react-query'

import { apiClient } from './client'
import type { ChatMessagePayload } from './types'

export function sendChatMessage(message: string, history: ChatMessagePayload[]) {
  return apiClient.post<{ reply: string }>('/api/chat', { message, history })
}

export function useChatReply() {
  return useMutation({
    mutationFn: ({ message, history }: { message: string; history: ChatMessagePayload[] }) =>
      sendChatMessage(message, history),
  })
}
