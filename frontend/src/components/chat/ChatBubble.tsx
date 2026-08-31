import type { ReactNode } from 'react'

export function ChatBubble({ role, children }: { role: 'user' | 'assistant'; children: ReactNode }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed sm:max-w-[70%] ${
          isUser
            ? 'rounded-br-sm bg-navy text-white'
            : 'rounded-bl-sm border border-border bg-bg-raised text-fg'
        }`}
      >
        {children}
      </div>
    </div>
  )
}
