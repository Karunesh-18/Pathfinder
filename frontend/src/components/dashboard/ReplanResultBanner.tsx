import type { ReplanResult } from '../../api/types'

export function ReplanResultBanner({ result, onDismiss }: { result: ReplanResult; onDismiss: () => void }) {
  const delta = result.total_gap_before - result.total_gap_after

  return (
    <div
      className={`flex items-start justify-between gap-3 rounded-xl border p-4 text-sm ${
        result.replan_triggered
          ? 'border-success/30 bg-success/10 text-success'
          : 'border-border bg-bg-raised text-fg-muted'
      }`}
    >
      <div>
        <p className="font-semibold">
          {result.replan_triggered
            ? `Roadmap rebuilt — ${result.new_path_step_count} steps remaining`
            : 'Progress saved — no replan needed yet'}
        </p>
        <p className="mt-0.5 text-xs opacity-80">
          Skill gap score: {result.total_gap_before.toFixed(1)} → {result.total_gap_after.toFixed(1)}
          {delta > 0 ? ` (−${delta.toFixed(1)})` : ''}
        </p>
        {result.skill_updates.length > 0 && (
          <p className="mt-0.5 text-xs opacity-80">
            Updated: {result.skill_updates.map((u) => `${u.skill} → ${u.level}`).join(', ')}
          </p>
        )}
      </div>
      <button type="button" onClick={onDismiss} aria-label="Dismiss" className="shrink-0 opacity-60 hover:opacity-100">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
      </button>
    </div>
  )
}
