import { useState } from 'react'

import { useIsDesktop } from '../../hooks/useMediaQuery'

export function RationalePanel({ rationale }: { rationale: string | undefined }) {
  const [open, setOpen] = useState(false)
  const isDesktop = useIsDesktop()

  if (!rationale) return null

  return (
    <div className="relative mt-2">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 text-xs font-medium text-navy hover:underline dark:text-navy-light"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4M12 8h.01" />
        </svg>
        Why this step?
      </button>

      {open &&
        (isDesktop ? (
          <div className="absolute left-0 top-6 z-10 w-72 rounded-xl border border-border bg-bg-raised p-3 text-sm text-fg-muted shadow-xl">
            {rationale}
          </div>
        ) : (
          <div className="mt-2 rounded-xl border border-border bg-bg/60 p-3 text-sm text-fg-muted">{rationale}</div>
        ))}
    </div>
  )
}
