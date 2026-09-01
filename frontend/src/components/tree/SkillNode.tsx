import { Handle, Position } from '@xyflow/react'
import type { NodeProps } from '@xyflow/react'
import { Link } from 'react-router-dom'

import type { SkillTreeNode } from '../../api/types'
import { Badge } from '../common/Badge'

const LEVEL_TONE = {
  advanced: 'success',
  intermediate: 'navy',
  beginner: 'warning',
} as const

export function SkillNode({ data }: NodeProps) {
  const skill = data.skill as SkillTreeNode

  return (
    <div className="w-60 rounded-xl border border-border bg-bg-raised p-3 shadow-sm">
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !border-none !bg-navy" />

      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="text-sm font-semibold">{skill.skill}</span>
        <Badge tone={LEVEL_TONE[skill.required_level as keyof typeof LEVEL_TONE] ?? 'neutral'}>
          {skill.required_level}
        </Badge>
      </div>

      <div className="max-h-28 space-y-1 overflow-y-auto pr-1">
        {skill.courses.length === 0 && <p className="text-xs text-fg-muted">No course in the catalog yet.</p>}
        {skill.courses.map((c) => (
          <Link
            key={c.id}
            to={`/courses/${c.id}`}
            title={c.title}
            className="block truncate rounded-md bg-bg px-2 py-1 text-xs hover:underline"
          >
            {c.title}
          </Link>
        ))}
      </div>

      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !border-none !bg-navy" />
    </div>
  )
}
