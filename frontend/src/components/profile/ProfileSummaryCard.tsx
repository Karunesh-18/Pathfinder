import type { Profile } from '../../api/types'
import { ExtractionMethodBadge } from './ExtractionMethodBadge'
import { SkillList } from './SkillList'

export function ProfileSummaryCard({ profile }: { profile: Profile }) {
  return (
    <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Your profile</h2>
        <ExtractionMethodBadge method={profile.extraction_method} />
      </div>

      <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-fg-muted">Target role</dt>
          <dd className="mt-1 text-sm">{profile.target_role ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-fg-muted">Time budget</dt>
          <dd className="mt-1 text-sm">
            {profile.time_budget_hours_per_week != null ? `${profile.time_budget_hours_per_week} hrs/week` : '—'}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-fg-muted">Format preference</dt>
          <dd className="mt-1 text-sm capitalize">{profile.format_preference ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-fg-muted">Completed courses</dt>
          <dd className="mt-1 text-sm">{profile.completed_courses.length}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="mb-1.5 text-xs font-medium uppercase tracking-wide text-fg-muted">Current skills</dt>
          <dd>
            <SkillList skills={profile.current_skills} />
          </dd>
        </div>
      </dl>
    </div>
  )
}
