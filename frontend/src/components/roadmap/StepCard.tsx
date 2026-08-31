import type { PathStep } from '../../api/types'
import { Badge } from '../common/Badge'
import { MilestoneMarker } from './MilestoneMarker'
import { RationalePanel } from './RationalePanel'

export function StepCard({ step, rationale }: { step: PathStep; rationale?: string }) {
  return (
    <div className="flex gap-3 sm:gap-4">
      <div className="flex flex-col items-center">
        {step.milestone ? (
          <MilestoneMarker />
        ) : (
          <span className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-navy text-xs font-semibold text-navy dark:text-navy-light">
            {step.step_index}
          </span>
        )}
        <span className="mt-1 w-px flex-1 bg-border" />
      </div>

      <div className="flex-1 pb-6">
        <div className="rounded-xl border border-border bg-bg-raised p-4">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold">{step.title}</h3>
              <p className="text-xs text-fg-muted">{step.provider}</p>
            </div>
            {step.milestone && <Badge tone="coral">Milestone</Badge>}
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            <Badge tone="navy">Closes: {step.skill_gap_addressed}</Badge>
            <Badge tone="neutral">{step.estimated_hours}h</Badge>
            {step.estimated_completion_week != null && (
              <Badge tone="neutral">~week {step.estimated_completion_week}</Badge>
            )}
          </div>

          <RationalePanel rationale={rationale} />
        </div>
      </div>
    </div>
  )
}
