import type { ReactNode } from 'react'

type BadgeTone = 'neutral' | 'navy' | 'coral' | 'success' | 'warning' | 'danger'

const TONE_CLASSES: Record<BadgeTone, string> = {
  neutral: 'bg-border/60 text-fg-muted',
  navy: 'bg-navy/10 text-navy dark:text-navy-light',
  coral: 'bg-coral/15 text-coral-dark dark:text-coral-light',
  success: 'bg-success/15 text-success',
  warning: 'bg-warning/15 text-warning',
  danger: 'bg-danger/15 text-danger',
}

export function Badge({ tone = 'neutral', children }: { tone?: BadgeTone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}
    >
      {children}
    </span>
  )
}
