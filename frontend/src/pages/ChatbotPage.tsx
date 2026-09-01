import { useState } from 'react'

import { useChatReply } from '../api/chatApi'
import type { ChatMessage } from '../components/chat/ChatWindow'
import { ChatWindow } from '../components/chat/ChatWindow'
import { errorMessage } from '../components/common/ErrorBanner'

const GREETING =
  "Hi! I'm the PathFinder assistant. Ask me anything about your learning plan, courses, or tech careers in general."

export function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([{ role: 'assistant', text: GREETING }])
  const [error, setError] = useState<string | null>(null)
  const chat = useChatReply()

  function handleSend(text: string) {
    setError(null)
    const history = messages.map((m) => ({ role: m.role, text: m.text }))
    setMessages((prev) => [...prev, { role: 'user', text }])
    chat.mutate(
      { message: text, history },
      {
        onSuccess: (data) => setMessages((prev) => [...prev, { role: 'assistant', text: data.reply }]),
        onError: (err) => setError(errorMessage(err)),
      },
    )
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-semibold">Chatbot</h1>
      <p className="mb-5 text-sm text-fg-muted">
        A general-purpose assistant — ask about your plan, specific courses, or anything else on your mind.
      </p>
      <ChatWindow messages={messages} onSend={handleSend} disabled={chat.isPending} placeholder="Ask me anything…" />
      {error && <p className="mt-3 text-sm text-danger">{error}</p>}
    </div>
  )
}
