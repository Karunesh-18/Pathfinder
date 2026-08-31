import type { HistoryItem, TimelineStep } from '../../api/types'
import { Badge } from '../common/Badge'

export function CompletedHistoryList({ items }: { items: HistoryItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-fg-muted">Nothing completed yet — your progress will show up here.</p>
  }
  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li
          key={item.course_id}
          className="flex items-center justify-between gap-3 rounded-lg border border-success/25 bg-success/5 px-3 py-2 text-sm"
        >
          <span className="flex items-center gap-2">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              className="shrink-0 text-success"
            >
              <path d="M5 12l5 5L20 7" />
            </svg>
            {item.title}
          </span>
          <span className="text-xs text-fg-muted">{item.provider}</span>
        </li>
      ))}
    </ul>
  )
}

export function RemainingTimelineList({ items }: { items: TimelineStep[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-fg-muted">Path complete — nothing remaining.</p>
  }
  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li
          key={item.step_index}
          className="flex items-center justify-between gap-3 rounded-lg border border-border bg-bg-raised px-3 py-2 text-sm"
        >
          <span>{item.title}</span>
          <span className="flex items-center gap-2 text-xs text-fg-muted">
            {item.milestone && <Badge tone="coral">Milestone</Badge>}
            {item.estimated_completion_week != null && <span>~week {item.estimated_completion_week}</span>}
          </span>
        </li>
      ))}
    </ul>
  )
}
