import type { SummaryStats } from '../../api/types'

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-bg-raised p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</p>
      <p className="mt-1 text-xl font-semibold">{value}</p>
    </div>
  )
}

export function SummaryStatTiles({ summary }: { summary: SummaryStats }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Tile label="Progress" value={`${summary.overall_progress_pct.toFixed(0)}%`} />
      <Tile label="Completed" value={`${summary.completed_courses}`} />
      <Tile label="Remaining steps" value={`${summary.remaining_steps}`} />
      <Tile label="Weeks left" value={summary.weeks_remaining != null ? `${summary.weeks_remaining}` : '—'} />
    </div>
  )
}
