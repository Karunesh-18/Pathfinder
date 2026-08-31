import type { NextAction } from '../../api/types'

export function NextActionCallout({ action }: { action: NextAction | null }) {
  if (!action) {
    return (
      <div className="rounded-xl border border-success/30 bg-success/10 p-4 text-sm text-success">
        You've completed every step in your current roadmap. Nice work!
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-coral/30 bg-coral/10 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-coral-dark dark:text-coral-light">
        Next recommended action
      </p>
      <p className="mt-1 text-sm font-semibold">{action.title}</p>
      <p className="text-xs text-fg-muted">
        {action.provider} · closes your {action.skill_gap_addressed} gap
      </p>
    </div>
  )
}
