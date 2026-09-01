import type { Role } from '../../api/types'
import { Badge } from '../common/Badge'

interface RoleCardProps {
  role: Role
  isCurrent: boolean
  onSelect: () => void
  isPending: boolean
  canSelect: boolean
}

export function RoleCard({ role, isCurrent, onSelect, isPending, canSelect }: RoleCardProps) {
  return (
    <div className="flex flex-col rounded-2xl border border-border bg-bg-raised p-5">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h3 className="text-base font-semibold">{role.role}</h3>
        {isCurrent && <Badge tone="coral">Your goal</Badge>}
      </div>
      <p className="flex-1 text-sm text-fg-muted">{role.blurb || 'A tech career track with courses in the catalog.'}</p>
      <button
        type="button"
        onClick={onSelect}
        disabled={isCurrent || isPending || !canSelect}
        className="mt-4 self-start rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:bg-bg disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isCurrent ? 'Current goal' : isPending ? 'Setting…' : 'Set as my goal'}
      </button>
    </div>
  )
}
