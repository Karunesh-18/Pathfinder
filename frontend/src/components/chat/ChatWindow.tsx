import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { ChatBubble } from './ChatBubble'

export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
}

interface ChatWindowProps {
  messages: ChatMessage[]
  onSend: (text: string) => void
  disabled?: boolean
  placeholder?: string
  extraContent?: React.ReactNode
}

export function ChatWindow({ messages, onSend, disabled, placeholder, extraContent }: ChatWindowProps) {
  const [draft, setDraft] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || disabled) return
    onSend(text)
    setDraft('')
  }

  return (
    <div className="flex h-[70vh] min-h-[28rem] flex-col overflow-hidden rounded-2xl border border-border bg-bg-raised sm:h-[36rem]">
      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4 sm:p-5">
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role}>
            {m.text}
          </ChatBubble>
        ))}
        {extraContent}
      </div>
      <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-border p-3 sm:p-4">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={placeholder ?? 'Type your message…'}
          disabled={disabled}
          className="flex-1 rounded-full border border-border bg-bg px-4 py-2.5 text-sm outline-none focus:border-navy disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !draft.trim()}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-navy text-white transition disabled:opacity-40"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        </button>
      </form>
    </div>
  )
}
