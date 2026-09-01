import type { SummaryStats } from '../../api/types'

export function ProgressSummaryBar({ summary }: { summary: SummaryStats }) {
  const pct = Math.max(0, Math.min(100, summary.overall_progress_pct))

  return (
    <div className="rounded-2xl border border-border bg-bg-raised p-4 sm:p-5">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-sm font-semibold">{pct.toFixed(0)}% complete</span>
        <span className="text-xs text-fg-muted">
          {summary.completed_courses} done · {summary.remaining_steps} remaining
          {summary.weeks_remaining != null ? ` · ~${summary.weeks_remaining} weeks left` : ''}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-border/60">
        <div className="h-full rounded-full bg-coral transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
