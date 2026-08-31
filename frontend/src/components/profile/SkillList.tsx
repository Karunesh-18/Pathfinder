import type { SkillEntry } from '../../api/types'
import { Badge } from '../common/Badge'

const LEVEL_TONE = {
  advanced: 'success',
  intermediate: 'navy',
  beginner: 'warning',
  unspecified: 'neutral',
} as const

export function SkillList({ skills }: { skills: SkillEntry[] }) {
  if (skills.length === 0) {
    return <p className="text-sm text-fg-muted">No skills captured yet.</p>
  }

  return (
    <ul className="flex flex-wrap gap-2">
      {skills.map((s) => (
        <li key={s.skill}>
          <Badge tone={LEVEL_TONE[s.level as keyof typeof LEVEL_TONE] ?? 'neutral'}>
            {s.skill} · {s.level}
          </Badge>
        </li>
      ))}
    </ul>
  )
}
