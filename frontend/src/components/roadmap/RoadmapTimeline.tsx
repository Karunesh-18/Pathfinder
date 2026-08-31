import type { PathStep } from '../../api/types'
import { StepCard } from './StepCard'

export function RoadmapTimeline({
  steps,
  rationaleByCourseId,
}: {
  steps: PathStep[]
  rationaleByCourseId: Record<string, string>
}) {
  if (steps.length === 0) {
    return <p className="text-sm text-fg-muted">No roadmap built yet.</p>
  }

  return (
    <div>
      {steps.map((step) => (
        <StepCard key={step.step_index} step={step} rationale={rationaleByCourseId[step.course_id]} />
      ))}
    </div>
  )
}
